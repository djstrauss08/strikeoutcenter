#!/usr/bin/env python3
"""
Update Public MLB Strikeout Props Feed
Generates JSON data and updates public directory for web hosting
"""

import json
import os
import shutil
import sys
from datetime import datetime, timedelta
import pytz
from export_json_feed import get_all_strikeout_props_data

def create_public_directory():
    """Create public directory structure"""
    public_dir = "public"
    
    # Create directories
    os.makedirs(public_dir, exist_ok=True)
    os.makedirs(f"{public_dir}/api", exist_ok=True)
    os.makedirs(f"{public_dir}/api/v1", exist_ok=True)
    
    return public_dir

def generate_api_endpoints(data, public_dir):
    """Generate multiple API endpoints from the data"""
    api_dir = f"{public_dir}/api/v1"
    
    # 1. Full data feed
    with open(f"{api_dir}/strikeout-props.json", 'w') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    # 2. Summary only (lightweight)
    summary_data = {
        "metadata": data["metadata"],
        "summary": data["summary"],
        "games": [
            {
                "event_id": game["event_id"],
                "away_team": game["away_team"],
                "home_team": game["home_team"],
                "matchup": game["matchup"],
                "game_time": game["game_time"],
                "game_time_formatted": game["game_time_formatted"],
                "pitcher_count": len(game["pitchers"])
            }
            for game in data["games"]
        ]
    }
    
    with open(f"{api_dir}/summary.json", 'w') as f:
        json.dump(summary_data, f, indent=2, ensure_ascii=False)
    
    # 3. Pitchers only (for quick lookups)
    pitchers_data = {
        "metadata": data["metadata"],
        "pitchers": []
    }
    
    for game in data["games"]:
        for pitcher in game["pitchers"]:
            pitcher_entry = pitcher.copy()
            pitcher_entry["game_info"] = {
                "matchup": game["matchup"],
                "game_time": game["game_time_formatted"],
                "away_team": game["away_team"],
                "home_team": game["home_team"]
            }
            pitchers_data["pitchers"].append(pitcher_entry)
    
    with open(f"{api_dir}/pitchers.json", 'w') as f:
        json.dump(pitchers_data, f, indent=2, ensure_ascii=False)
    
    # 4. Best odds endpoint
    best_overs = []
    best_unders = []
    
    for game in data["games"]:
        for pitcher in game["pitchers"]:
            if pitcher["consensus_odds"]["over"]:
                best_overs.append({
                    "pitcher": pitcher["pitcher_name"],
                    "game": game["matchup"],
                    "line": pitcher["strikeout_line"],
                    "odds": pitcher["consensus_odds"]["over"],
                    "odds_formatted": pitcher["consensus_odds"]["over_formatted"],
                    "sportsbook_count": pitcher["sportsbook_count"]
                })
            
            if pitcher["consensus_odds"]["under"]:
                best_unders.append({
                    "pitcher": pitcher["pitcher_name"],
                    "game": game["matchup"],
                    "line": pitcher["strikeout_line"],
                    "odds": pitcher["consensus_odds"]["under"],
                    "odds_formatted": pitcher["consensus_odds"]["under_formatted"],
                    "sportsbook_count": pitcher["sportsbook_count"]
                })
    
    # Sort by best odds
    best_overs.sort(key=lambda x: x["odds"], reverse=True)
    best_unders.sort(key=lambda x: x["odds"], reverse=True)
    
    best_odds_data = {
        "metadata": data["metadata"],
        "best_overs": best_overs[:20],
        "best_unders": best_unders[:20]
    }
    
    with open(f"{api_dir}/best-odds.json", 'w') as f:
        json.dump(best_odds_data, f, indent=2, ensure_ascii=False)
    
    return {
        "full": f"{api_dir}/strikeout-props.json",
        "summary": f"{api_dir}/summary.json", 
        "pitchers": f"{api_dir}/pitchers.json",
        "best_odds": f"{api_dir}/best-odds.json"
    }

def create_documentation_page(public_dir, endpoints):
    """Create a simple HTML documentation page"""
    
    html_content = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MLB Strikeout Props API</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 1000px; margin: 0 auto; padding: 20px; }
        .endpoint { background: #f5f5f5; padding: 15px; margin: 10px 0; border-radius: 5px; }
        .url { background: #333; color: #fff; padding: 5px 10px; border-radius: 3px; font-family: monospace; }
        code { background: #f0f0f0; padding: 2px 5px; border-radius: 3px; }
        .updated { color: #666; font-style: italic; }
    </style>
</head>
<body>
    <h1>🎯 MLB Strikeout Props JSON API</h1>
    
    <p class="updated">Last updated: <span id="lastUpdated"></span></p>
    
    <h2>📡 Available Endpoints</h2>
    
    <div class="endpoint">
        <h3>Full Strikeout Props Data</h3>
        <div class="url">GET /api/v1/strikeout-props.json</div>
        <p>Complete dataset with all games, pitchers, lines, and odds from multiple sportsbooks.</p>
        <p><strong>Use case:</strong> Full data analysis, comprehensive dashboards</p>
    </div>
    
    <div class="endpoint">
        <h3>Summary Data</h3>
        <div class="url">GET /api/v1/summary.json</div>
        <p>Lightweight summary with game info and pitcher counts (no odds data).</p>
        <p><strong>Use case:</strong> Quick overview, mobile apps, initial page loads</p>
    </div>
    
    <div class="endpoint">
        <h3>Pitchers Only</h3>
        <div class="url">GET /api/v1/pitchers.json</div>
        <p>All pitcher props with game context, optimized for pitcher-focused views.</p>
        <p><strong>Use case:</strong> Pitcher comparison tools, search interfaces</p>
    </div>
    
    <div class="endpoint">
        <h3>Best Odds</h3>
        <div class="url">GET /api/v1/best-odds.json</div>
        <p>Top 20 best odds for overs and unders, sorted by value.</p>
        <p><strong>Use case:</strong> Finding value bets, odds comparison tools</p>
    </div>
    
    <h2>🔄 Data Freshness</h2>
    <ul>
        <li>Data updates multiple times per day</li>
        <li>Includes only today's MLB games (Eastern timezone)</li>
        <li>Consensus odds calculated from 6+ major sportsbooks</li>
        <li>Props availability depends on sportsbook posting schedules</li>
    </ul>
    
    <h2>💻 Usage Examples</h2>
    
    <h3>JavaScript/Fetch</h3>
    <pre><code>fetch('https://your-username.github.io/StrikeoutCenter/api/v1/summary.json')
  .then(response => response.json())
  .then(data => {
    console.log(`${data.summary.total_pitchers} pitchers across ${data.summary.total_games} games`);
  });</code></pre>
    
    <h3>Python</h3>
    <pre><code>import requests

response = requests.get('https://your-username.github.io/StrikeoutCenter/api/v1/strikeout-props.json')
data = response.json()

for game in data['games']:
    print(f"Game: {game['matchup']}")
    for pitcher in game['pitchers']:
        print(f"  {pitcher['pitcher_name']}: {pitcher['strikeout_line']}K")</code></pre>
    
    <h3>cURL</h3>
    <pre><code>curl -H "Accept: application/json" \\
     https://your-username.github.io/StrikeoutCenter/api/v1/best-odds.json</code></pre>
    
    <h2>📊 Response Format</h2>
    <p>All endpoints return JSON with consistent structure:</p>
    <ul>
        <li><code>metadata</code>: Generation timestamp, date, timezone</li>
        <li><code>summary</code>: Total counts and statistics</li>
        <li><code>games</code> or <code>pitchers</code>: Main data arrays</li>
    </ul>
    
    <h2>⚡ Rate Limiting</h2>
    <p>No rate limiting on these endpoints. Data is cached and served statically.</p>
    
    <h2>🔗 CORS</h2>
    <p>All endpoints support CORS for browser-based applications.</p>
    
    <script>
        // Update last updated time
        fetch('./api/v1/summary.json')
            .then(response => response.json())
            .then(data => {
                document.getElementById('lastUpdated').textContent = data.metadata.generated_at_formatted;
            })
            .catch(() => {
                document.getElementById('lastUpdated').textContent = 'Unable to fetch';
            });
    </script>
</body>
</html>"""
    
    with open(f"{public_dir}/index.html", 'w') as f:
        f.write(html_content)

def create_cors_headers(public_dir):
    """Create _headers file for Netlify-style CORS support"""
    headers_content = """/*
  Access-Control-Allow-Origin: *
  Access-Control-Allow-Methods: GET, HEAD, OPTIONS
  Access-Control-Allow-Headers: Content-Type
  Access-Control-Max-Age: 86400

/api/*
  Content-Type: application/json
  Cache-Control: public, max-age=300
"""
    
    with open(f"{public_dir}/_headers", 'w') as f:
        f.write(headers_content)

def update_feed():
    """Main function to update the public feed"""
    try:
        print("🔄 Updating MLB Strikeout Props Public Feed...")
        
        # Get fresh data
        print("📡 Fetching fresh data from The Odds API...")
        data = get_all_strikeout_props_data()
        
        if "error" in data:
            print(f"❌ Error getting data: {data['error']}")
            print("This might be due to:")
            print("- Invalid or expired API key")
            print("- Network connectivity issues")
            print("- No MLB games scheduled for today")
            sys.exit(1)
        
        if data['summary']['total_games'] == 0:
            print("⚠️ No MLB games found for today")
            print("This is normal during off-season or rest days")
            # Create empty but valid JSON files anyway
        
        # Create public directory
        public_dir = create_public_directory()
        
        # Generate API endpoints
        print("📁 Generating API endpoints...")
        endpoints = generate_api_endpoints(data, public_dir)
        
        # Create documentation
        print("📝 Creating documentation page...")
        create_documentation_page(public_dir, endpoints)
        
        # Add CORS headers
        create_cors_headers(public_dir)
        
        # Create a README for the public directory
        readme_content = f"""# MLB Strikeout Props Public Feed

This directory contains the public JSON API endpoints for MLB strikeout props data.

## Generated: {data['metadata']['generated_at_formatted']}

## Files:
- `index.html` - API documentation
- `api/v1/strikeout-props.json` - Full dataset
- `api/v1/summary.json` - Summary data
- `api/v1/pitchers.json` - Pitcher-focused data  
- `api/v1/best-odds.json` - Best odds rankings

## Stats:
- Total Games: {data['summary']['total_games']}
- Total Pitchers: {data['summary']['total_pitchers']}
- Games with Props: {data['summary']['games_with_props']}

## Usage:
These files are designed to be served statically via GitHub Pages, Netlify, or similar hosting.
"""
        
        with open(f"{public_dir}/README.md", 'w') as f:
            f.write(readme_content)
        
        print(f"✅ Public feed updated successfully!")
        print(f"📊 Generated {data['summary']['total_pitchers']} pitchers across {data['summary']['total_games']} games")
        print(f"📁 Files created in: {public_dir}/")
        print()
        print("🚀 Next steps:")
        print("1. Commit the public/ directory to your GitHub repo")
        print("2. Enable GitHub Pages on the repo")
        print("3. Your API will be available at: https://your-username.github.io/StrikeoutCenter/")
        
        return True
        
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        print(f"Error type: {type(e).__name__}")
        import traceback
        print("Full traceback:")
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    success = update_feed()
    if not success:
        sys.exit(1) 