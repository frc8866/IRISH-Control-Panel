# IRISH Robotics Control Panel

A comprehensive Flask-based web application for managing FTA, Scoreboard, and referee systems for FIRST Robotics Competition events.

## Features

- **Real-time Match Timer**: 2:15 countdown with automatic endgame indicator at 30 seconds
- **BONUS Timer**: 15-second countdown activated by referees for AND ONE bonus periods
- **Detailed Scoring System**: Complete implementation of FRC scoring mechanics
- **Ranking Point Calculation**: Automatic RP tracking (Win, Tele-op, Climb)
- **Real-time Communication**: WebSocket-based updates between referees and displays
- **Database Storage**: SQLite database for all match data and events
- **Multiple Display Views**: Pre-match, Live Match, Post-match with RP display

## Scoring System

### Teleoperated Scoring
- **BUCKET Score**: 6 points (normal), 12 points (during BONUS period)
- **HUMAN PLAYER BUCKET**: 3 points
- **AND ONE Activation**: Triggers 15-second BONUS timer

### Endgame Scoring (BENCH)
- **PARK**: 2 points
- **Slight Ramp**: 6 points
- **Climb**: 14 points

### Penalties
- **Foul**: +5 points to opponent
- **Tech Foul**: +15 points to opponent
- **BENCH Contact Foul**: Robot disablement

## Ranking Points
- **Win RP**: 2 RPs for winning alliance
- **Tele-op RP**: 1 RP if AND ONE BONUS activated
- **Climb RP**: 1 RP if combined BENCH points ≥ 20

## Installation

1. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Run the application:
   ```bash
   python app.py
   ```

3. Open your browser to `http://localhost:5000`

## Usage

- **Display**: `http://localhost:5000/` - Live scoreboard with timer
- **Pre-match**: `http://localhost:5000/prematch` - Upcoming match preview
- **Post-match**: `http://localhost:5000/postmatch` - Match results with final RPs
- **Referee Panel**: `http://localhost:5000/referee` - Complete control interface

## Architecture

- **Backend**: Flask with Socket.IO for real-time communication and threading for timer management
- **Database**: SQLite with SQLAlchemy ORM
- **Frontend**: HTML/CSS/JS with Socket.IO client for live updates

## Database Models

- **Team**: Team information
- **Match**: Comprehensive match data including timer states, scores, and RPs
- **MatchEvent**: Detailed event logging for all scoring actions

## API Endpoints

- `GET /api/matches` - Retrieve all matches with full details
- Socket events: `start_match`, `score_event`, `activate_bonus`, `end_match`

## Development

The application uses WebSockets for real-time updates. Multiple clients can connect simultaneously for distributed refereeing.
