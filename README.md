# IRISH 2025 Control Panel

Web-based scoring system for the IRISH off-season robotics event using Python Flask backend with SQLite database.

## Features

- **Real-time Scoring**: Track BUCKET (6/12 pts), HP (3 pts), BENCH (2/6/14 pts), and Fouls (+5/+15 pts) per alliance
- **AND ONE Bonus System**: Count AND ONE achievements and automatically activate 15-second BONUS multiplier (2x) every 3 counts
- **Referee Panel**: Full data entry interface for match officials
- **Audience Display**: Large-screen display with JavaScript polling for real-time updates (1-second refresh)
- **SQLite Database**: Persistent score tracking with automatic initialization

## Installation

1. Clone the repository:
```bash
git clone https://github.com/8866CJ/IRISH-Control-Panel.git
cd IRISH-Control-Panel
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

1. Start the Flask server:
```bash
python app.py
```

2. Access the application:
   - **Referee Panel**: http://localhost:5000/referee
   - **Audience Display**: http://localhost:5000/display

The server will run on `http://0.0.0.0:5000` by default.

## Scoring Rules

### Component Values
- **BUCKET**: 6 or 12 points
- **HP (Human Player)**: 3 points
- **BENCH**: 2, 6, or 14 points
- **Fouls**: +5 or +15 points (awarded to opponent)

### AND ONE Bonus System
- Track AND ONE achievements per alliance
- Every 3 AND ONE counts activates a 15-second BONUS period
- During BONUS: All scores are multiplied by 2x
- Bonus automatically deactivates after 15 seconds

## API Endpoints

### GET /api/score
Retrieve current match scores and status.

**Response:**
```json
{
  "red_bucket": 12,
  "red_hp": 3,
  "red_bench": 0,
  "red_fouls": 0,
  "red_and_one_count": 3,
  "red_bonus_active": 1,
  "red_total": 30,
  "blue_bucket": 6,
  "blue_hp": 0,
  "blue_bench": 0,
  "blue_fouls": 0,
  "blue_and_one_count": 0,
  "blue_bonus_active": 0,
  "blue_total": 6
}
```

### POST /api/score
Update specific score components.

**Request Body:**
```json
{
  "red_bucket": 12,
  "blue_hp": 3
}
```

### POST /api/reset
Reset all scores to zero.

## Project Structure

```
IRISH-Control-Panel/
├── app.py                      # Flask application and API
├── requirements.txt            # Python dependencies
├── irish_scores.db            # SQLite database (auto-created)
├── templates/
│   ├── referee.html           # Referee control panel
│   └── display.html           # Audience display
└── static/
    ├── css/
    │   ├── style.css          # Referee panel styles
    │   └── display.css        # Audience display styles
    └── js/
        ├── referee.js         # Referee panel logic
        └── display.js         # Display polling logic
```

## Development

The application uses:
- **Flask 3.0.0** for the backend
- **SQLite** for data persistence
- **Vanilla JavaScript** with AJAX polling for real-time updates
- **CSS Grid** for responsive layouts

## Screenshots

### Referee Panel
![Referee Panel](https://github.com/user-attachments/assets/d355ca55-e305-4943-bd5e-d1cd9613f055)

The referee panel provides buttons to add/subtract points for all scoring components, track AND ONE counts, and monitor bonus status.

### Audience Display
![Audience Display](https://github.com/user-attachments/assets/d556d41e-b58a-4d1d-b58f-4dcf851e89fb)

The audience display shows live scores with automatic updates every second, featuring large text and alliance-themed colors.

## License

MIT License - feel free to use and modify for your robotics events!
