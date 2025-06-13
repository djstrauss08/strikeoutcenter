#!/usr/bin/env python3
# Updated with new API key - 2025-06-03
"""
MLB Strikeout Props JSON Feed Exporter
Exports today's strikeout props data for players, lines, and odds in JSON format
Updated to persist lines until the following day
"""

import requests
import json
from datetime import datetime, timedelta
import pytz
import sys
import os
from typing import Dict, List, Any, Optional
import pickle

# API Configuration - Use environment variable for security
API_KEY = os.getenv('THE_ODDS_API_KEY')
if not API_KEY:
    print("❌ Error: THE_ODDS_API_KEY environment variable not set")
    print("Please set your API key: export THE_ODDS_API_KEY='your-api-key-here'")
    sys.exit(1)

BASE_URL = "https://api.the-odds-api.com/v4"

# Persistence file for storing game data
PERSISTENT_DATA_FILE = "persistent_game_data.pkl"

def load_persistent_data() -> Dict[str, Any]:
    """Load persistent data from disk"""
    try:
        if os.path.exists(PERSISTENT_DATA_FILE):
            with open(PERSISTENT_DATA_FILE, 'rb') as f:
                return pickle.load(f)
    except Exception as e:
        print(f"Warning: Could not load persistent data: {e}")
    
    return {
        "last_updated": None,
        "games": {},
        "data_date": None
    }

def save_persistent_data(data: Dict[str, Any]):
    """Save persistent data to disk"""
    try:
        with open(PERSISTENT_DATA_FILE, 'wb') as f:
            pickle.dump(data, f)
    except Exception as e:
        print(f"Warning: Could not save persistent data: {e}")

def is_game_started(game_time_str: str) -> bool:
    """Check if a game has started based on its scheduled time"""
    try:
        game_time = datetime.fromisoformat(game_time_str.replace('Z', '+00:00'))
        current_time = datetime.now(pytz.UTC)
        
        # Consider game started if current time is past game time
        return current_time >= game_time
    except Exception:
        return False

def should_use_new_data(current_date: str, stored_date: str) -> bool:
    """Determine if we should use new API data or persist old data"""
    if not stored_date:
        return True
    
    # If it's a new day, use new data
    return current_date != stored_date

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
        'regions': 'us',
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

def calculate_consensus_odds(over_odds_list: List[int], under_odds_list: List[int]) -> tuple:
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

def get_all_strikeout_props_data() -> Dict[str, Any]:
    """Get all strikeout props data and return as structured dictionary"""
    eastern = pytz.timezone('US/Eastern')
    today_est = datetime.now(eastern)
    
    # Get today's games
    games = get_mlb_games()
    
    if not games:
        # Return valid structure instead of error for no games (normal during off-season)
        return {
            "metadata": {
                "generated_at": today_est.isoformat(),
                "generated_at_formatted": today_est.strftime('%A, %B %d, %Y at %I:%M %p %Z'),
                "date": today_est.strftime('%Y-%m-%d'),
                "timezone": "US/Eastern"
            },
            "summary": {
                "total_games": 0,
                "total_pitchers": 0,
                "games_with_props": 0
            },
            "games": []
        }
    
    all_games_data = []
    total_pitchers = 0
    
    for game in games:
        event_id = game['id']
        away_team = game['away_team']
        home_team = game['home_team']
        
        # Convert UTC time to Eastern
        utc_time = datetime.fromisoformat(game['commence_time'].replace('Z', '+00:00'))
        eastern_time = utc_time.astimezone(eastern)
        
        # Get strikeout props for this specific event
        event_data = get_pitcher_strikeouts_for_event(event_id, away_team, home_team)
        
        game_data = {
            "event_id": event_id,
            "away_team": away_team,
            "home_team": home_team,
            "matchup": f"{away_team} @ {home_team}",
            "game_time": eastern_time.isoformat(),
            "game_time_formatted": eastern_time.strftime('%I:%M %p %Z'),
            "pitchers": []
        }
        
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
                                        'pitcher_name': pitcher_name,
                                        'line': line,
                                        'over_odds': [],
                                        'under_odds': [],
                                        'sportsbooks': set(),
                                        'individual_book_odds': {}
                                    }
                                
                                # Store individual book odds
                                if book_name not in pitcher_props[prop_key]['individual_book_odds']:
                                    pitcher_props[prop_key]['individual_book_odds'][book_name] = {}
                                
                                if bet_type == 'Over':
                                    pitcher_props[prop_key]['over_odds'].append(odds)
                                    pitcher_props[prop_key]['individual_book_odds'][book_name]['over'] = odds
                                elif bet_type == 'Under':
                                    pitcher_props[prop_key]['under_odds'].append(odds)
                                    pitcher_props[prop_key]['individual_book_odds'][book_name]['under'] = odds
                                
                                pitcher_props[prop_key]['sportsbooks'].add(book_name)
            
            # Convert to list and add consensus odds
            for prop_key, prop_data in pitcher_props.items():
                # Calculate consensus odds
                consensus_over, consensus_under = calculate_consensus_odds(
                    prop_data['over_odds'], prop_data['under_odds']
                )
                
                # Convert sets to lists for JSON serialization
                sportsbooks_list = list(prop_data['sportsbooks'])
                
                pitcher_data = {
                    "pitcher_name": prop_data['pitcher_name'],
                    "strikeout_line": prop_data['line'],
                    "consensus_odds": {
                        "over": consensus_over,
                        "under": consensus_under,
                        "over_formatted": f"+{consensus_over}" if consensus_over and consensus_over > 0 else str(consensus_over),
                        "under_formatted": f"+{consensus_under}" if consensus_under and consensus_under > 0 else str(consensus_under)
                    },
                    "sportsbooks": sportsbooks_list,
                    "sportsbook_count": len(sportsbooks_list),
                    "individual_odds": prop_data['individual_book_odds'],
                    "raw_odds": {
                        "over_odds": prop_data['over_odds'],
                        "under_odds": prop_data['under_odds']
                    }
                }
                
                game_data["pitchers"].append(pitcher_data)
                total_pitchers += 1
        
        # Sort pitchers alphabetically
        game_data["pitchers"].sort(key=lambda x: x["pitcher_name"])
        
        all_games_data.append(game_data)
    
    # Sort games by game time
    all_games_data.sort(key=lambda x: x["game_time"])
    
    # Prepare final data structure
    final_data = {
        "metadata": {
            "generated_at": datetime.now(eastern).isoformat(),
            "generated_at_formatted": datetime.now(eastern).strftime('%A, %B %d, %Y at %I:%M %p %Z'),
            "date": today_est.strftime('%Y-%m-%d'),
            "timezone": "US/Eastern"
        },
        "summary": {
            "total_games": len(all_games_data),
            "total_pitchers": total_pitchers,
            "games_with_props": len([g for g in all_games_data if g["pitchers"]])
        },
        "games": all_games_data
    }
    
    return final_data

def export_to_json_file(filename: Optional[str] = None) -> str:
    """Export strikeout props data to JSON file"""
    if filename is None:
        today = datetime.now(pytz.timezone('US/Eastern')).strftime('%Y-%m-%d')
        filename = f"mlb_strikeout_props_{today}.json"
    
    data = get_all_strikeout_props_data()
    
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        return filename
    except Exception as e:
        print(f"Error writing JSON file: {e}")
        return None

def print_json_feed():
    """Print the JSON feed to stdout"""
    data = get_all_strikeout_props_data()
    print(json.dumps(data, indent=2, ensure_ascii=False))

def main():
    """Main function - can be called with command line arguments"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Export MLB Strikeout Props to JSON')
    parser.add_argument('--output', '-o', help='Output filename (optional)')
    parser.add_argument('--stdout', action='store_true', help='Output to stdout instead of file')
    parser.add_argument('--pretty', action='store_true', help='Pretty print summary to console')
    
    args = parser.parse_args()
    
    if args.stdout:
        print_json_feed()
    else:
        filename = export_to_json_file(args.output)
        if filename:
            print(f"✅ JSON feed exported to: {filename}")
            
            if args.pretty:
                # Also print a summary
                data = get_all_strikeout_props_data()
                print(f"\n📊 Summary:")
                print(f"   • Total Games: {data['summary']['total_games']}")
                print(f"   • Games with Props: {data['summary']['games_with_props']}")
                print(f"   • Total Pitchers: {data['summary']['total_pitchers']}")
                print(f"   • Generated: {data['metadata']['generated_at_formatted']}")
        else:
            print("❌ Failed to export JSON feed")

if __name__ == "__main__":
    main() 