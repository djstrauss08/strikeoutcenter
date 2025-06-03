# 🚀 Public MLB Strikeout Props API Setup Guide

This guide shows you how to create a public JSON API feed that other websites can consume while keeping your API calls under control.

## 🎯 What This Solves

**Problem:** Other websites want your strikeout props data, but you don't want them hitting The Odds API directly (expensive/rate-limited).

**Solution:** You control the API calls, generate JSON feeds, and host them publicly for others to consume.

## 📋 Architecture Overview

```
Your Script → The Odds API → JSON Generation → Public Hosting → Other Websites
    |              |              |               |              |
 (Controlled)  (Expensive)    (Your Data)    (Free CDN)    (No API costs)
```

## 🛠️ Setup Options

### Option 1: GitHub Pages (Recommended - Free & Easy)

#### Step 1: Initial Setup
```bash
# Run the public feed generator
python3 update_public_feed.py
```

#### Step 2: Commit to GitHub
```bash
git add public/
git add .github/
git commit -m "Add public API feed"
git push origin main
```

#### Step 3: Enable GitHub Pages
1. Go to your GitHub repo settings
2. Scroll to "Pages" section
3. Source: "Deploy from a branch"
4. Branch: `main`
5. Folder: `/ (root)`
6. Save

#### Step 4: Your API is Live! 🎉
Your API will be available at:
```
https://your-username.github.io/StrikeoutCenter/
```

**API Endpoints:**
- `https://your-username.github.io/StrikeoutCenter/api/v1/strikeout-props.json` - Full data
- `https://your-username.github.io/StrikeoutCenter/api/v1/summary.json` - Lightweight summary
- `https://your-username.github.io/StrikeoutCenter/api/v1/pitchers.json` - Pitcher-focused data
- `https://your-username.github.io/StrikeoutCenter/api/v1/best-odds.json` - Best odds rankings

### Option 2: Manual Updates

If you prefer manual control:

```bash
# Update the feed when you want
python3 update_public_feed.py

# Commit and push
git add public/ && git commit -m "Update feed" && git push
```

### Option 3: Advanced Hosting

For higher traffic or custom domains:

1. **Netlify**: Drag & drop the `public/` folder to Netlify
2. **Vercel**: Connect your GitHub repo to Vercel  
3. **AWS S3 + CloudFront**: Professional CDN setup
4. **Your own web server**: Upload `public/` contents

## 📡 API Endpoints Explained

### 1. Full Data (`/api/v1/strikeout-props.json`)
- **Size:** ~95KB
- **Content:** Complete dataset with all odds, sportsbooks, individual book odds
- **Use case:** Full analysis, comprehensive dashboards
- **Update frequency:** Every 2 hours during baseball season

### 2. Summary (`/api/v1/summary.json`)  
- **Size:** ~5KB
- **Content:** Game info and pitcher counts (no odds)
- **Use case:** Quick overview, mobile apps, initial page loads

### 3. Pitchers Only (`/api/v1/pitchers.json`)
- **Size:** ~96KB  
- **Content:** All pitcher props with game context
- **Use case:** Pitcher comparison tools, search interfaces

### 4. Best Odds (`/api/v1/best-odds.json`)
- **Size:** ~8KB
- **Content:** Top 20 best odds for overs/unders
- **Use case:** Finding value bets, odds comparison

## 🤝 How Other Websites Use Your API

### Example: JavaScript Website
```javascript
// Fetch summary data (lightweight)
fetch('https://your-username.github.io/StrikeoutCenter/api/v1/summary.json')
  .then(response => response.json())
  .then(data => {
    console.log(`${data.summary.total_pitchers} pitchers today`);
    displayGames(data.games);
  });

// Fetch full data for detailed analysis
fetch('https://your-username.github.io/StrikeoutCenter/api/v1/strikeout-props.json')
  .then(response => response.json())
  .then(data => {
    data.games.forEach(game => {
      game.pitchers.forEach(pitcher => {
        console.log(`${pitcher.pitcher_name}: ${pitcher.strikeout_line}K`);
        console.log(`Over: ${pitcher.consensus_odds.over_formatted}`);
      });
    });
  });
```

### Example: Python Analysis
```python
import requests

# Other websites can easily fetch your data
response = requests.get('https://your-username.github.io/StrikeoutCenter/api/v1/pitchers.json')
data = response.json()

# Find all pitchers with 5.5K lines
pitchers_5_5 = [p for p in data['pitchers'] if p['strikeout_line'] == 5.5]
print(f"Found {len(pitchers_5_5)} pitchers with 5.5K lines")
```

## ⚡ Automatic Updates

The GitHub Actions workflow automatically:

- **Runs every 2 hours** from 10 AM to 10 PM ET
- **Fetches fresh data** from The Odds API
- **Updates JSON files** in the public directory  
- **Commits and pushes** changes to GitHub
- **Publishes updates** via GitHub Pages

### Manual Trigger
You can also trigger updates manually:
1. Go to Actions tab in GitHub
2. Select "Update MLB Strikeout Props Feed"  
3. Click "Run workflow"

## 🔒 API Control & Benefits

### What You Control:
- ✅ **API Call Frequency** - You decide when to fetch new data
- ✅ **Data Processing** - You control consensus calculations  
- ✅ **API Costs** - Only your script calls The Odds API
- ✅ **Data Format** - You design the JSON structure
- ✅ **Availability** - You control when the service is active

### What Others Get:
- ✅ **Free Access** - No API keys needed for consumers
- ✅ **Fast CDN Delivery** - GitHub Pages is globally distributed
- ✅ **Reliable Data** - Cached and always available  
- ✅ **CORS Support** - Works from any website
- ✅ **Multiple Formats** - Different endpoints for different needs

## 📊 Usage Analytics

To track who's using your API:

### Option 1: GitHub Traffic Stats
- Go to repo Insights → Traffic
- See page views and unique visitors

### Option 2: Add Analytics (Optional)
You can add Google Analytics to the documentation page for more detailed tracking.

## 🛡️ Rate Limiting & Fair Use

Since you're providing free data:

### Built-in Protection:
- **Static Files** - No server load, CDN handles traffic
- **Caching** - GitHub Pages caches content globally  
- **No Authentication** - Simple for others to use

### Fair Use Guidelines:
Consider adding to your documentation:
```
Please be respectful:
- Cache responses for at least 5 minutes
- Don't make requests more than once per minute
- Link back to our project if possible
```

## 🔧 Customization Options

### Add More Endpoints
Edit `update_public_feed.py` to create custom endpoints:

```python
# Example: Team-specific endpoint
def create_team_endpoint(data, team_name, public_dir):
    team_data = {
        "team": team_name,
        "games": [g for g in data["games"] 
                 if team_name in [g["away_team"], g["home_team"]]],
        "metadata": data["metadata"]
    }
    
    with open(f"{public_dir}/api/v1/team-{team_name.lower().replace(' ', '-')}.json", 'w') as f:
        json.dump(team_data, f, indent=2)
```

### Custom Update Schedule
Edit `.github/workflows/update-feed.yml` to change timing:

```yaml
schedule:
  # Every hour during game days
  - cron: '0 * * * *'
  
  # Only on weekdays at 2 PM
  - cron: '0 18 * * 1-5'
```

## 📈 Success Metrics

Track your API's success:

- **GitHub Stars** - Community interest
- **Traffic Stats** - Usage volume
- **Issues/Feedback** - User engagement  
- **Forks** - Other developers building on your work

## 🎯 Example Use Cases

Other websites might use your API for:

- **Betting Analysis Tools** - Compare odds across books
- **Fantasy Baseball Apps** - Pitcher performance insights
- **News Websites** - Automated props reporting
- **Discord Bots** - Real-time props notifications
- **Mobile Apps** - Quick game overviews
- **Data Visualization** - Charts and graphs
- **Academic Research** - Sports betting analysis

Your API becomes the reliable data source that powers the entire ecosystem! 🚀 