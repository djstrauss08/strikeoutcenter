#!/usr/bin/env python3
"""
MLB Strikeout Props Summary
Clean summary of consensus odds for strikeout props for today's starting pitchers
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
        else:
            return None
    except requests.exceptions.RequestException as e:
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

def get_primary_line(pitcher_props):
    """Get the most commonly offered line for a pitcher"""
    # Count how many books offer each line
    line_counts = {}
    for prop in pitcher_props:
        line = prop['line']
        book_count = len(prop['books'])
        if line in line_counts:
            line_counts[line] += book_count
        else:
            line_counts[line] = book_count
    
    # Return the line with the most books offering it
    if line_counts:
        primary_line = max(line_counts.keys(), key=lambda x: line_counts[x])
        # Find the prop data for this line
        for prop in pitcher_props:
            if prop['line'] == primary_line:
                return prop
    
    return pitcher_props[0] if pitcher_props else None

def main():
    eastern = pytz.timezone('US/Eastern')
    today_est = datetime.now(eastern)
    
    print("🎯 MLB Strikeout Props - Today's Starting Pitchers")
    print("=" * 60)
    print(f"Date: {today_est.strftime('%A, %B %d, %Y')}")
    print()
    
    # Get today's games
    games = get_mlb_games()
    
    if not games:
        print("❌ No MLB games found for today")
        return
    
    print(f"📅 Found {len(games)} MLB games for today")
    print()
    
    game_props = []
    
    for game in games:
        event_id = game['id']
        away_team = game['away_team']
        home_team = game['home_team']
        
        # Convert UTC time to Eastern
        utc_time = datetime.fromisoformat(game['commence_time'].replace('Z', '+00:00'))
        eastern_time = utc_time.astimezone(eastern)
        
        # Get strikeout props for this specific event
        event_data = get_pitcher_strikeouts_for_event(event_id, away_team, home_team)
        
        if event_data and event_data.get('bookmakers'):
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
            
            # Group props by pitcher
            pitchers = {}
            for prop_key, prop_data in pitcher_props.items():
                pitcher_name = prop_data['pitcher']
                if pitcher_name not in pitchers:
                    pitchers[pitcher_name] = []
                pitchers[pitcher_name].append(prop_data)
            
            # Store game data with primary lines for each pitcher
            game_data = {
                'away_team': away_team,
                'home_team': home_team,
                'game_time': eastern_time,
                'pitchers': {}
            }
            
            for pitcher_name, props in pitchers.items():
                primary_prop = get_primary_line(props)
                if primary_prop:
                    game_data['pitchers'][pitcher_name] = primary_prop
            
            if game_data['pitchers']:
                game_props.append(game_data)
    
    if not game_props:
        print("❌ No pitcher strikeout props found for any of today's games")
        return
    
    # Sort by game time
    game_props.sort(key=lambda x: x['game_time'])
    
    # Display results
    print("📊 STARTING PITCHER STRIKEOUT PROPS")
    print("=" * 60)
    print()
    
    total_pitchers = 0
    
    for game in game_props:
        game_time = game['game_time'].strftime('%I:%M %p %Z')
        print(f"🏟️  {game['away_team']} @ {game['home_team']}")
        print(f"    {game_time}")
        print("    " + "-" * 50)
        
        # Sort pitchers alphabetically
        for pitcher_name in sorted(game['pitchers'].keys()):
            prop = game['pitchers'][pitcher_name]
            total_pitchers += 1
            
            line = prop['line']
            
            # Calculate consensus odds
            consensus_over, consensus_under = calculate_consensus_odds(
                prop['over_odds'], prop['under_odds']
            )
            
            book_count = len(prop['books'])
            
            print(f"    👨‍⚾ {pitcher_name}")
            print(f"        Line: {line} strikeouts")
            
            over_str = format_odds(consensus_over) if consensus_over else "N/A"
            under_str = format_odds(consensus_under) if consensus_under else "N/A"
            
            print(f"        Over {line}: {over_str}  |  Under {line}: {under_str}")
            print(f"        ({book_count} sportsbooks)")
            print()
        
        print()
    
    print("=" * 60)
    print(f"✅ Total Games: {len(game_props)}")
    print(f"✅ Total Starting Pitchers: {total_pitchers}")
    print()
    print("💡 Notes:")
    print("   • Odds shown are consensus averages from available sportsbooks")
    print("   • Primary line displayed (most commonly offered across books)")
    print("   • Lines represent over/under total strikeouts for the entire game")
    print("   • Data updates throughout the day as games approach")

if __name__ == "__main__":
    main() 