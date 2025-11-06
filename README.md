# IRISH Control Panel

A comprehensive web-based control system for FIRST Robotics Competition (FRC) events, providing real-time match management, scoring, and display capabilities.

## Capabilities

### Match Management
- Complete match setup with team assignments
- Automated 2:15 match timer with endgame indicators
- Field fault handling and timer pause/resume
- Ability to stop match and reset incase of accidental start
- Match review and post-match analysis

### Scoring System
- Real-time teleoperated scoring (buckets, human player)
- Endgame scoring (park, ramp, climb)
- AND ONE bonus period activation and tracking
- Penalty management (fouls, tech fouls)

### Ranking Points
- Automatic calculation of win, tele-op, and climb ranking points
- Real-time RP updates during matches

### Interfaces
- **FTA Panel**: Match setup, timer control, field fault management
- **Referee Panel**: Live scoring controls for both alliances
- **Display Panel**: Real-time scoreboard with pre-match, live, and post-match views

### Data & Communication
- SQLite database for persistent match data
- WebSocket-based real-time updates across all interfaces
- Event logging and match history
- Audio notifications for match events

## Quick Start

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Run the application:
   ```bash
   python app.py
   ```

3. Access interfaces:
   - Main Display: `http://localhost:5000/`
   - FTA Panel: `http://localhost:5000/fta`
   - Referee Panel: `http://localhost:5000/referee`

## Technology Stack

- **Backend**: Flask with Socket.IO
- **Database**: SQLAlchemy with SQLite
- **Frontend**: HTML/CSS/JavaScript
- **Real-time**: WebSocket communication
