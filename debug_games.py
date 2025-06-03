#!/usr/bin/env python3
"""
Debug script to check all MLB games and timing issues
"""

import requests
import json
from datetime import datetime, timedelta, timezone
import pytz
import sys
import os

# API Configuration - Use environment variable for security
API_KEY = os.getenv('THE_ODDS_API_KEY')
if not API_KEY:
    print("❌ Error: THE_ODDS_API_KEY environment variable not set")
    print("Please set your API key: export THE_ODDS_API_KEY='your-api-key-here'")
    sys.exit(1)

BASE_URL = "https://api.the-odds-api.com/v4"

def get_all_mlb_games():
    """Get ALL MLB games for today with proper timezone handling"""
    # Get current time in EST
    eastern = pytz.timezone('US/Eastern')
    today_est = datetime.now(eastern)
    
    print(f"🕐 Current time (EST): {today_est.strftime('%Y-%m-%d %I:%M %p %Z')}")
    
    # Get start of day and end of day in UTC for API
    start_of_day = today_est.replace(hour=0, minute=0, second=0, microsecond=0)
    end_of_day = today_est.replace(hour=23, minute=59, second=59, microsecond=999999)
    
    start_utc = start_of_day.astimezone(pytz.UTC)
    end_utc = end_of_day.astimezone(pytz.UTC)
    
    print(f"🌍 Searching from: {start_utc.strftime('%Y-%m-%dT%H:%M:%SZ')}")
    print(f"🌍 Searching to:   {end_utc.strftime('%Y-%m-%dT%H:%M:%SZ')}")
    print()
    
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
        games = response.json()
        
        print(f"📊 Total games found: {len(games)}")
        print()
        
        # Process and display all games with correct timezone
        eastern = pytz.timezone('US/Eastern')
        
        for i, game in enumerate(games, 1):
            # Parse the UTC time and convert to Eastern
            utc_time = datetime.fromisoformat(game['commence_time'].replace('Z', '+00:00'))
            eastern_time = utc_time.astimezone(eastern)
            
            print(f"{i:2d}. {game['away_team']} @ {game['home_team']}")
            print(f"    UTC: {utc_time.strftime('%Y-%m-%d %I:%M %p %Z')}")
            print(f"    EST: {eastern_time.strftime('%Y-%m-%d %I:%M %p %Z')}")
            print(f"    Game ID: {game['id']}")
            print()
            
        return games
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Error fetching games: {e}")
        return []

def check_broader_timeframe():
    """Check a broader timeframe to see if we're missing games"""
    print("🔍 Checking broader timeframe (yesterday to tomorrow)...")
    
    eastern = pytz.timezone('US/Eastern')
    today_est = datetime.now(eastern)
    
    # Check from yesterday to tomorrow
    start_time = (today_est - timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
    end_time = (today_est + timedelta(days=1)).replace(hour=23, minute=59, second=59, microsecond=999999)
    
    start_utc = start_time.astimezone(pytz.UTC)
    end_utc = end_time.astimezone(pytz.UTC)
    
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
        games = response.json()
        
        print(f"📊 Total games in 3-day window: {len(games)}")
        print()
        
        # Group by date
        games_by_date = {}
        eastern = pytz.timezone('US/Eastern')
        
        for game in games:
            utc_time = datetime.fromisoformat(game['commence_time'].replace('Z', '+00:00'))
            eastern_time = utc_time.astimezone(eastern)
            date_key = eastern_time.strftime('%Y-%m-%d')
            
            if date_key not in games_by_date:
                games_by_date[date_key] = []
            games_by_date[date_key].append((game, eastern_time))
        
        for date, games_list in sorted(games_by_date.items()):
            print(f"📅 {date}:")
            for game, eastern_time in games_list:
                print(f"  {eastern_time.strftime('%I:%M %p')} - {game['away_team']} @ {game['home_team']}")
            print()
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Error: {e}")

def main():
    print("🔍 MLB Games Debug - Tuesday, June 3, 2025")
    print("=" * 60)
    print()
    
    # Check today's games with proper timezone
    games = get_all_mlb_games()
    
    print("=" * 60)
    print()
    
    # Check broader timeframe to see if we're missing anything
    check_broader_timeframe()

if __name__ == "__main__":
    main() 