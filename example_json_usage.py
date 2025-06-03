#!/usr/bin/env python3
"""
Example script showing how to consume the exported MLB strikeout props JSON data
"""

import json
from datetime import datetime

def load_strikeout_data(filename):
    """Load JSON data from file"""
    with open(filename, 'r') as f:
        return json.load(f)

def find_best_odds(data):
    """Find the best odds (most favorable) for over and under bets"""
    best_overs = []
    best_unders = []
    
    for game in data['games']:
        for pitcher in game['pitchers']:
            # For overs, we want the highest positive odds or least negative odds
            over_odds = pitcher['consensus_odds']['over']
            under_odds = pitcher['consensus_odds']['under']
            
            if over_odds:
                best_overs.append({
                    'pitcher': pitcher['pitcher_name'],
                    'game': game['matchup'],
                    'line': pitcher['strikeout_line'],
                    'odds': over_odds,
                    'formatted': pitcher['consensus_odds']['over_formatted'],
                    'sportsbook_count': pitcher['sportsbook_count']
                })
            
            if under_odds:
                best_unders.append({
                    'pitcher': pitcher['pitcher_name'],
                    'game': game['matchup'],
                    'line': pitcher['strikeout_line'],
                    'odds': under_odds,
                    'formatted': pitcher['consensus_odds']['under_formatted'],
                    'sportsbook_count': pitcher['sportsbook_count']
                })
    
    # Sort by most favorable odds
    best_overs.sort(key=lambda x: x['odds'], reverse=True)  # Highest odds first
    best_unders.sort(key=lambda x: x['odds'], reverse=True)  # Highest odds first
    
    return best_overs[:10], best_unders[:10]

def find_most_available_props(data):
    """Find props available at the most sportsbooks"""
    all_props = []
    
    for game in data['games']:
        for pitcher in game['pitchers']:
            all_props.append({
                'pitcher': pitcher['pitcher_name'],
                'game': game['matchup'],
                'line': pitcher['strikeout_line'],
                'over_odds': pitcher['consensus_odds']['over_formatted'],
                'under_odds': pitcher['consensus_odds']['under_formatted'],
                'sportsbook_count': pitcher['sportsbook_count'],
                'sportsbooks': pitcher['sportsbooks']
            })
    
    # Sort by sportsbook count
    all_props.sort(key=lambda x: x['sportsbook_count'], reverse=True)
    return all_props[:15]

def find_props_by_line(data, target_line):
    """Find all props for a specific strikeout line"""
    matching_props = []
    
    for game in data['games']:
        for pitcher in game['pitchers']:
            if pitcher['strikeout_line'] == target_line:
                matching_props.append({
                    'pitcher': pitcher['pitcher_name'],
                    'game': game['matchup'],
                    'game_time': game['game_time_formatted'],
                    'over_odds': pitcher['consensus_odds']['over_formatted'],
                    'under_odds': pitcher['consensus_odds']['under_formatted'],
                    'sportsbook_count': pitcher['sportsbook_count']
                })
    
    return matching_props

def summary_by_game(data):
    """Create a summary showing pitcher counts by game"""
    game_summaries = []
    
    for game in data['games']:
        game_summaries.append({
            'matchup': game['matchup'],
            'game_time': game['game_time_formatted'],
            'pitcher_count': len(game['pitchers']),
            'pitchers': [p['pitcher_name'] for p in game['pitchers']]
        })
    
    return game_summaries

def main():
    # Load the data
    try:
        data = load_strikeout_data('mlb_strikeout_props_2025-06-03.json')
    except FileNotFoundError:
        print("❌ JSON file not found. Run 'python3 export_json_feed.py' first.")
        return
    
    print("🎯 MLB Strikeout Props Analysis")
    print("=" * 50)
    print(f"Data generated: {data['metadata']['generated_at_formatted']}")
    print(f"Total games: {data['summary']['total_games']}")
    print(f"Total pitchers: {data['summary']['total_pitchers']}")
    print()
    
    # Find best odds
    print("💰 BEST ODDS ANALYSIS")
    print("-" * 30)
    best_overs, best_unders = find_best_odds(data)
    
    print("🔥 Top 5 Over Bets (Best Odds):")
    for i, prop in enumerate(best_overs[:5], 1):
        print(f"  {i}. {prop['pitcher']} Over {prop['line']}K: {prop['formatted']} ({prop['sportsbook_count']} books)")
        print(f"     {prop['game']}")
    
    print("\n🔥 Top 5 Under Bets (Best Odds):")
    for i, prop in enumerate(best_unders[:5], 1):
        print(f"  {i}. {prop['pitcher']} Under {prop['line']}K: {prop['formatted']} ({prop['sportsbook_count']} books)")
        print(f"     {prop['game']}")
    
    # Most widely available props
    print("\n\n📊 MOST WIDELY AVAILABLE PROPS")
    print("-" * 35)
    most_available = find_most_available_props(data)
    
    for i, prop in enumerate(most_available[:8], 1):
        print(f"{i:2d}. {prop['pitcher']} {prop['line']}K: O{prop['over_odds']}/U{prop['under_odds']}")
        print(f"     {prop['game']} ({prop['sportsbook_count']} books)")
        print(f"     Books: {', '.join(prop['sportsbooks'][:3])}{'...' if len(prop['sportsbooks']) > 3 else ''}")
        print()
    
    # Props by specific line
    print("\n🎯 PITCHERS WITH 5.5K LINE")
    print("-" * 25)
    props_5_5 = find_props_by_line(data, 5.5)
    
    for prop in props_5_5[:8]:
        print(f"• {prop['pitcher']} - O{prop['over_odds']}/U{prop['under_odds']} ({prop['sportsbook_count']} books)")
        print(f"  {prop['game']} at {prop['game_time']}")
    
    # Game summary
    print(f"\n\n🏟️  GAMES SUMMARY")
    print("-" * 20)
    game_summaries = summary_by_game(data)
    
    for game in game_summaries:
        print(f"🏟️  {game['matchup']} ({game['game_time']})")
        print(f"    {game['pitcher_count']} pitchers with props: {', '.join(game['pitchers'])}")
        print()

if __name__ == "__main__":
    main() 