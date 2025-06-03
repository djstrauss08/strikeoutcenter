# MLB Strikeout Props JSON Feed Export

This tool exports comprehensive MLB strikeout props data (players, lines, and odds) into a structured JSON format.

## Usage

### Basic Export to File
```bash
python3 export_json_feed.py
```
This creates a file named `mlb_strikeout_props_YYYY-MM-DD.json` with today's date.

### Export with Custom Filename
```bash
python3 export_json_feed.py --output my_strikeout_data.json
```

### Export to Standard Output (for piping/API usage)
```bash
python3 export_json_feed.py --stdout
```

### Export with Summary
```bash
python3 export_json_feed.py --pretty
```

## JSON Structure

The exported JSON contains the following structure:

```json
{
  "metadata": {
    "generated_at": "2025-06-03T17:21:24.725082-04:00",
    "generated_at_formatted": "Tuesday, June 03, 2025 at 05:21 PM EDT",
    "date": "2025-06-03",
    "timezone": "US/Eastern"
  },
  "summary": {
    "total_games": 15,
    "total_pitchers": 104,
    "games_with_props": 15
  },
  "games": [
    {
      "event_id": "unique_api_event_id",
      "away_team": "Colorado Rockies",
      "home_team": "Miami Marlins", 
      "matchup": "Colorado Rockies @ Miami Marlins",
      "game_time": "2025-06-03T18:40:00-04:00",
      "game_time_formatted": "06:40 PM EDT",
      "pitchers": [
        {
          "pitcher_name": "Sandy Alcantara",
          "strikeout_line": 5.5,
          "consensus_odds": {
            "over": -134,
            "under": 102,
            "over_formatted": "-134",
            "under_formatted": "+102"
          },
          "sportsbooks": ["FanDuel", "BetOnline.ag", "BetRivers", "BetMGM", "DraftKings", "Bovada"],
          "sportsbook_count": 6,
          "individual_odds": {
            "FanDuel": {
              "over": -134,
              "under": 106
            },
            "BetOnline.ag": {
              "over": -130,
              "under": 101
            }
            // ... more sportsbooks
          },
          "raw_odds": {
            "over_odds": [-134, -130, -135, -135, -130, -143],
            "under_odds": [106, 101, 100, 100, 100, 108]
          }
        }
        // ... more pitchers
      ]
    }
    // ... more games
  ]
}
```

## Key Data Points Available

### Per Game:
- **Event ID**: Unique identifier for the game
- **Teams**: Away and home team names
- **Game Time**: Both ISO format and human-readable format
- **Matchup**: Formatted team matchup string

### Per Pitcher:
- **Pitcher Name**: Full name of the starting pitcher
- **Strikeout Line**: The over/under line (e.g., 5.5 strikeouts)
- **Consensus Odds**: Averaged odds across all sportsbooks
- **Individual Sportsbook Odds**: Specific odds from each bookmaker
- **Sportsbook Count**: Number of books offering the prop
- **Raw Odds Arrays**: All individual odds for calculations

### Consensus Odds Calculation:
- Odds are converted to implied probabilities
- Probabilities are averaged across all sportsbooks
- Average probability is converted back to American odds
- Both raw numeric and formatted string versions provided

## Integration Examples

### Use as API Feed
```bash
# Output JSON to stdout and pipe to web server
python3 export_json_feed.py --stdout | curl -X POST -H "Content-Type: application/json" -d @- https://your-api.com/strikeout-props
```

### Load in Python Script
```python
import json

# Load the exported data
with open('mlb_strikeout_props_2025-06-03.json', 'r') as f:
    data = json.load(f)

# Access specific data
for game in data['games']:
    print(f"Game: {game['matchup']} at {game['game_time_formatted']}")
    for pitcher in game['pitchers']:
        print(f"  {pitcher['pitcher_name']}: {pitcher['strikeout_line']} K line")
        print(f"    Over: {pitcher['consensus_odds']['over_formatted']}")
        print(f"    Under: {pitcher['consensus_odds']['under_formatted']}")
```

### JavaScript/Web Usage
```javascript
fetch('./mlb_strikeout_props_2025-06-03.json')
  .then(response => response.json())
  .then(data => {
    console.log(`Found ${data.summary.total_pitchers} pitchers across ${data.summary.total_games} games`);
    
    data.games.forEach(game => {
      game.pitchers.forEach(pitcher => {
        console.log(`${pitcher.pitcher_name}: ${pitcher.strikeout_line}K - O${pitcher.consensus_odds.over_formatted}/U${pitcher.consensus_odds.under_formatted}`);
      });
    });
  });
```

## Data Freshness

- Data is fetched live from The Odds API
- Includes today's MLB games only (Eastern timezone)
- Props availability depends on sportsbook posting schedules
- Typically more props available closer to game time

## Notes

- **Multiple Lines**: Some pitchers may have multiple prop lines (e.g., 4.5K, 5.5K, 6.5K)
- **Sportsbook Variations**: Different books may offer different lines
- **Primary Line Selection**: The existing summary script shows the most commonly offered line
- **Consensus Calculation**: Averages odds across all available sportsbooks for each line
- **Error Handling**: Games without available props are still included but with empty pitcher arrays 