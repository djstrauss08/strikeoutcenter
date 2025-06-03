#!/usr/bin/env python3
"""
MLB Strikeout Props Odds Fetcher
Fetches consensus odds for strikeout props for today's starting pitchers using The Odds API
"""

import requests
import json
from datetime import datetime, timedelta
import pytz
import sys

# API Configuration
API_KEY = "fc2d8ba3268ab0b6e5e08a8344b6e797"
BASE_URL = "https://api.the-odds-api.com/v4"

def get_mlb_games():
    """Get today's MLB games with proper timezone handling"""
    # Get current time in Eastern timezone
    eastern = pytz.timezone('US/Eastern')
    today_est = datetime.now(eastern)
    
    # Get start of day and end of day in Eastern, then convert to UTC
    start_of_day = today_est.replace(hour=0, minute=0, second=0, microsecond=0)
    end_of_day = today_est.replace(hour=23, minute=59, second=59, microsecond=999999)
    
    start_utc = start_of_day.astimezone(pytz.UTC)
    end_utc = end_of_day.astimezone(pytz.UTC)
    
    url = f"{BASE_URL}/sports/baseball_mlb/events"
    params = {
        'apiKey': API_KEY,
        'dateFormat': 'iso',
        'commenceTimeFrom': start_utc.strftime('%Y-%m-%dT%H:%M:%SZ'),
        'commenceTimeTo': end_utc.strftime('%Y-%m-%dT%H:%M:%SZ')
    }
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching games: {e}")
        return []

def get_pitcher_strikeouts_for_event(event_id, away_team, home_team):
    """Get pitcher strikeout props for a specific event"""
    url = f"{BASE_URL}/sports/baseball_mlb/events/{event_id}/odds"
    params = {
        'apiKey': API_KEY,
        'regions': 'us',
        'markets': 'pitcher_strikeouts',
        'oddsFormat': 'american'
    }
    
    try:
        response = requests.get(url, params=params)
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 422:
            print(f"  ⚠️  No pitcher strikeouts available for {away_team} @ {home_team}")
            return None
        else:
            print(f"  ❌ Error {response.status_code} for {away_team} @ {home_team}: {response.text}")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"  ❌ Request error for {away_team} @ {home_team}: {e}")
        return None

def calculate_consensus_odds(over_odds_list, under_odds_list):
    """Calculate consensus odds from multiple bookmakers"""
    def avg_american_odds(odds_list):
        if not odds_list:
            return None
        # Convert to implied probabilities, average, then back to American odds
        probs = []
        for odds in odds_list:
            if odds > 0:
                prob = 100 / (odds + 100)
            else:
                prob = abs(odds) / (abs(odds) + 100)
            probs.append(prob)
        
        avg_prob = sum(probs) / len(probs)
        
        # Convert back to American odds
        if avg_prob >= 0.5:
            return round(-avg_prob / (1 - avg_prob) * 100)
        else:
            return round((1 - avg_prob) / avg_prob * 100)
    
    return avg_american_odds(over_odds_list), avg_american_odds(under_odds_list)

def format_odds(odds):
    """Format odds with proper + sign for positive odds"""
    if odds is None:
        return "N/A"
    return f"+{odds}" if odds > 0 else str(odds)

def main():
    eastern = pytz.timezone('US/Eastern')
    today_est = datetime.now(eastern)
    
    print("🎯 MLB Strikeout Props - Consensus Odds")
    print("=" * 50)
    print(f"Date: {today_est.strftime('%A, %B %d, %Y')}")
    print()
    
    # Get today's games
    games = get_mlb_games()
    
    if not games:
        print("❌ No MLB games found for today")
        return
    
    print(f"📅 Found {len(games)} MLB games for today")
    print("🔍 Checking for pitcher strikeout props...")
    print()
    
    all_strikeout_props = []
    
    for game in games:
        event_id = game['id']
        away_team = game['away_team']
        home_team = game['home_team']
        
        # Convert UTC time to Eastern
        utc_time = datetime.fromisoformat(game['commence_time'].replace('Z', '+00:00'))
        eastern_time = utc_time.astimezone(eastern)
        
        print(f"🔍 Checking: {away_team} @ {home_team}")
        
        # Get strikeout props for this specific event
        event_data = get_pitcher_strikeouts_for_event(event_id, away_team, home_team)
        
        if event_data and event_data.get('bookmakers'):
            print(f"  ✅ Found strikeout props!")
            
            # Process the strikeout data
            pitcher_props = {}  # Dictionary to store props by pitcher and line
            
            for bookmaker in event_data['bookmakers']:
                book_name = bookmaker['title']
                
                for market in bookmaker.get('markets', []):
                    if market['key'] == 'pitcher_strikeouts':
                        for outcome in market['outcomes']:
                            pitcher_name = outcome.get('description', 'Unknown Pitcher')
                            line = outcome.get('point')
                            bet_type = outcome.get('name')  # 'Over' or 'Under'
                            odds = outcome.get('price')
                            
                            if pitcher_name and line is not None and bet_type and odds:
                                # Create unique key for pitcher + line combo
                                prop_key = (pitcher_name, line)
                                
                                if prop_key not in pitcher_props:
                                    pitcher_props[prop_key] = {
                                        'pitcher': pitcher_name,
                                        'line': line,
                                        'over_odds': [],
                                        'under_odds': [],
                                        'books': set()
                                    }
                                
                                if bet_type == 'Over':
                                    pitcher_props[prop_key]['over_odds'].append(odds)
                                elif bet_type == 'Under':
                                    pitcher_props[prop_key]['under_odds'].append(odds)
                                
                                pitcher_props[prop_key]['books'].add(book_name)
            
            # Add processed props to our list
            for prop_key, prop_data in pitcher_props.items():
                prop_data['away_team'] = away_team
                prop_data['home_team'] = home_team
                prop_data['game_time'] = eastern_time
                all_strikeout_props.append(prop_data)
        
        print()
    
    if not all_strikeout_props:
        print("❌ No pitcher strikeout props found for any of today's games")
        print("\n💡 This could mean:")
        print("  - Props haven't been posted yet (usually available closer to game time)")
        print("  - It's the offseason or no games scheduled")
        print("  - Props are limited on your API plan")
        return
    
    # Sort by game time, then by pitcher name
    all_strikeout_props.sort(key=lambda x: (x['game_time'], x['pitcher']))
    
    # Display results
    print(f"📊 Found {len(all_strikeout_props)} pitcher strikeout props:")
    print()
    
    current_game = None
    total_pitchers = 0
    
    for prop in all_strikeout_props:
        game_key = f"{prop['away_team']} @ {prop['home_team']}"
        
        if current_game != game_key:
            current_game = game_key
            game_time = prop['game_time'].strftime('%I:%M %p %Z')
            print(f"🏟️  {game_key} ({game_time})")
            print("-" * 45)
        
        total_pitchers += 1
        pitcher = prop['pitcher']
        line = prop['line']
        
        # Calculate consensus odds
        consensus_over, consensus_under = calculate_consensus_odds(
            prop['over_odds'], prop['under_odds']
        )
        
        print(f"  👨‍⚾ {pitcher}")
        print(f"    Line: {line} strikeouts")
        
        if consensus_over is not None:
            print(f"    Over {line}: {format_odds(consensus_over)} (avg of {len(prop['over_odds'])} books)")
        
        if consensus_under is not None:
            print(f"    Under {line}: {format_odds(consensus_under)} (avg of {len(prop['under_odds'])} books)")
        
        if prop['books']:
            print(f"    Sportsbooks: {', '.join(sorted(prop['books']))}")
        
        print()
    
    print(f"✅ Total starting pitchers with strikeout props: {total_pitchers}")
    print("\n💡 Odds shown are consensus averages from available sportsbooks")
    print("📈 Lines typically represent over/under total strikeouts for the game")

if __name__ == "__main__":
    main() 