# 🎯 StrikeoutCenter - MLB Strikeout Props API

A comprehensive system for fetching, analyzing, and distributing MLB strikeout props data with consensus odds from multiple sportsbooks.

## 🚀 Features

- **Real-time Data**: Live odds from 6+ major sportsbooks via The Odds API
- **Consensus Odds**: Mathematically averaged odds across all available books
- **Multiple Formats**: JSON exports optimized for different use cases
- **Public API**: Hosted endpoints for other websites and applications
- **Automatic Updates**: GitHub Actions workflow for scheduled data refreshes
- **Clean Interface**: Beautiful summary views and detailed analysis tools

## 📊 What You Get

### Data Coverage
- All MLB games for today (Eastern timezone)
- Starting pitcher strikeout props with multiple lines (4.5K, 5.5K, 6.5K, etc.)
- Individual sportsbook odds + consensus averages
- Sportsbook availability counts and comparisons

### Export Formats
- **Full Dataset**: Complete odds data with all sportsbooks
- **Summary View**: Game info and pitcher counts (lightweight)
- **Pitcher Focus**: Optimized for pitcher comparison tools
- **Best Odds**: Top value bets ranked by favorability

## 🛠️ Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure API Key (REQUIRED)

**🔐 IMPORTANT: Your API key should be set as an environment variable, never hardcoded.**

Get your API key from [The Odds API](https://the-odds-api.com/), then:

```bash
# Set environment variable (replace with your actual key)
export THE_ODDS_API_KEY="your-api-key-here"
```

For permanent setup, add to your shell profile:
```bash
echo 'export THE_ODDS_API_KEY="your-api-key-here"' >> ~/.zshrc
source ~/.zshrc
```

### 3. Test the Setup
```bash
# Verify environment variable
echo $THE_ODDS_API_KEY

# Test basic functionality
python3 strikeout_summary.py
```

## 🎯 Usage

### Basic Analysis
```bash
# Clean summary view (most commonly offered line per pitcher)
python3 strikeout_summary.py

# Detailed analysis with all available lines
python3 strikeout_odds.py
```

### JSON Export
```bash
# Export to file
python3 export_json_feed.py

# Export with summary
python3 export_json_feed.py --pretty

# Output to stdout (for piping)
python3 export_json_feed.py --stdout
```

### Public API Generation
```bash
# Generate public API endpoints
python3 update_public_feed.py
```

## 📡 Public API

Once deployed, your API provides multiple endpoints:

- `/api/v1/strikeout-props.json` - Full dataset (~95KB)
- `/api/v1/summary.json` - Lightweight summary (~5KB)  
- `/api/v1/pitchers.json` - Pitcher-focused data (~96KB)
- `/api/v1/best-odds.json` - Best odds rankings (~8KB)

### Example Usage
```javascript
fetch('https://your-username.github.io/StrikeoutCenter/api/v1/summary.json')
  .then(response => response.json())
  .then(data => {
    console.log(`${data.summary.total_pitchers} pitchers across ${data.summary.total_games} games`);
  });
```

## 🔄 Automatic Updates

GitHub Actions workflow runs every 2 hours during baseball season (10 AM - 10 PM ET) to:
- Fetch fresh data from The Odds API
- Update JSON endpoints
- Commit changes to repository
- Deploy via GitHub Pages

## 📈 Key Benefits

### For You
- 🔒 **Control API costs** - You decide when to fetch data
- ⚙️ **Process data your way** - Custom consensus calculations
- 📊 **Rich analytics** - Multiple view formats for different needs
- 🚀 **Easy deployment** - One-click GitHub Pages hosting

### For Others  
- 🆓 **Free access** - No API keys needed for consumers
- ⚡ **Fast delivery** - Global CDN via GitHub Pages
- 🌐 **CORS enabled** - Works from any website
- 📱 **Multiple formats** - Choose the right endpoint for your needs

## 🛡️ Security Features

- Environment variable configuration for API keys
- GitHub Secrets integration for automated workflows  
- API key never exposed in public code
- Easy key rotation and management

## 📚 Documentation

- `PUBLIC_API_SETUP.md` - Complete deployment guide
- `SECURITY_SETUP.md` - API key security configuration
- `README_JSON_Export.md` - JSON export system details

## 🎯 Use Cases

**Your Internal Analysis:**
- Daily betting research and value identification
- Sportsbook comparison and line shopping
- Historical tracking and trend analysis

**Public API Consumers:**
- Betting analysis websites and tools
- Fantasy baseball applications  
- Discord bots and notifications
- Mobile apps and dashboards
- Academic research and data visualization

## 📊 Example Output

Shows the most commonly offered line across sportsbooks:

```
🎯 MLB Strikeout Props - Today's Starting Pitchers
============================================================
Date: Tuesday, June 03, 2025

📅 Found 15 MLB games for today

📊 STARTING PITCHER STRIKEOUT PROPS
============================================================

🏟️  Colorado Rockies @ Miami Marlins
    06:40 PM EDT
    --------------------------------------------------
    👨‍⚾ Sandy Alcantara
        Line: 5.5 strikeouts
        Over 5.5: -134  |  Under 5.5: +102
        (6 sportsbooks)
```

## 🔧 Advanced Features

- **Consensus Calculation**: Converts odds to implied probabilities, averages, then back to American odds
- **Multiple Lines**: Handles different strikeout totals for the same pitcher
- **Primary Line Detection**: Shows most commonly offered line across books
- **Error Handling**: Graceful handling of missing props or API issues
- **Timezone Management**: Proper Eastern timezone handling for game times

## 📞 Support

For issues related to:
- **The Odds API**: Contact their support for API-related questions
- **This Tool**: Open an issue in this repository
- **GitHub Pages**: Check GitHub's documentation for hosting issues

Built with ❤️ for the baseball analytics community 