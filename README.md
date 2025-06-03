# MLB Strikeout Props Analyzer

This project fetches and analyzes consensus odds for MLB pitcher strikeout props using The Odds API.

## Features

- ✅ Fetches real-time strikeout prop odds for today's MLB starting pitchers
- ✅ Calculates consensus odds from multiple sportsbooks
- ✅ Shows both detailed and summary views
- ✅ Covers all major US sportsbooks (FanDuel, DraftKings, BetMGM, etc.)
- ✅ Displays game times, lines, and odds in an easy-to-read format

## Files

### `strikeout_odds.py`
The comprehensive script that shows ALL available strikeout lines for each pitcher. This includes:
- Multiple lines per pitcher (e.g., 4.5, 5.5, 6.5 strikeouts)
- Alternate odds from different sportsbooks
- Detailed breakdown of which books offer each line

### `strikeout_summary.py`
A cleaner summary version that shows only the PRIMARY line for each pitcher:
- Shows the most commonly offered line across sportsbooks
- Cleaner, more readable output
- Perfect for quick daily analysis

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Your API key is already configured in the scripts:
```
API_KEY = "fc2d8ba3268ab0b6e5e08a8344b6e797"
```

## Usage

### Get Detailed Odds (All Lines)
```bash
python3 strikeout_odds.py
```

### Get Summary (Primary Lines Only)
```bash
python3 strikeout_summary.py
```

## Sample Output

The scripts will show:

```
🎯 MLB Strikeout Props - Today's Starting Pitchers
============================================================
Date: Tuesday, June 03, 2025

🏟️  Cleveland Guardians @ New York Yankees
    11:05 PM ET
    --------------------------------------------------
    👨‍⚾ Carlos Rodon
        Line: 6.5 strikeouts
        Over 6.5: -131  |  Under 6.5: +100
        (6 sportsbooks)

    👨‍⚾ Tanner Bibee
        Line: 5.5 strikeouts
        Over 5.5: +117  |  Under 5.5: -153
        (6 sportsbooks)
```

## Key Information

- **Lines**: Represent total strikeouts for the pitcher in the entire game
- **Consensus Odds**: Averaged from multiple sportsbooks using implied probabilities
- **Sportsbooks Included**: FanDuel, DraftKings, BetMGM, BetRivers, Bovada, BetOnline.ag, and more
- **Update Frequency**: The Odds API updates odds frequently throughout the day

## API Details

This project uses [The Odds API](https://the-odds-api.com/) which provides:
- Real-time betting odds from 40+ sportsbooks
- Player props for MLB (and other sports)
- Both American and decimal odds formats
- Historical odds data

### API Limits
- Free tier: 500 requests per month
- Paid tiers available for higher usage

## Notes

- Props are typically posted closer to game time
- Not all games may have strikeout props available
- Lines can vary throughout the day as odds move
- The consensus calculation converts odds to implied probabilities, averages them, then converts back

## Troubleshooting

If you see "No strikeout props found":
1. Check if there are MLB games scheduled today
2. Props might not be posted yet (usually available 1-3 hours before games)
3. Some games might not have pitcher props available
4. Verify your API key is working

## Future Enhancements

Potential improvements:
- Add email notifications for favorable lines
- Track line movement over time
- Add more advanced statistical analysis
- Include pitcher stats and matchup data
- Export to CSV/Excel format 