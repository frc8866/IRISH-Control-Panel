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
   ## Recommended: Create a reproducible venv (Windows, Python 3.12.7)

   To make development and dependency installation consistent, you can create a Python 3.12.7 virtual environment for this project.

   1. From File Explorer, double-click:
      - `scripts\create_venv_3.12.7.bat` — This will create `.venv-3.12.7` in the repo root and install dependencies from `requirements.txt`. It uses `py -3.12` if available, or `python` on PATH when it is Python 3.12.

   2. To open a new PowerShell window with the venv already activated, double-click:
      - `scripts\open_venv_3.12.7.bat` — This launches PowerShell and runs the virtual environment's `Activate.ps1` file.

   3. OR, from an existing PowerShell session in the project root, run:
      ```powershell
      . .\.venv-3.12.7\Scripts\Activate.ps1
      ```

   Notes:
   - If you don't yet have Python 3.12.7 installed, the create script will prompt you to download and install Python 3.12.7 from https://www.python.org/downloads/release/python-3127/.
   - Some Windows systems prevent PowerShell scripts from executing by default. The batch script launches PowerShell with `-ExecutionPolicy Bypass` so activation can run without changing system policies.
   - The venv is created in `.venv-3.12.7` so you can have multiple venvs for different Python versions.

## Technology Stack

- **Backend**: Flask with Socket.IO
- **Database**: SQLAlchemy with SQLite
- **Frontend**: HTML/CSS/JavaScript
- **Real-time**: WebSocket communication

## Common Runtime Notes & Known Warnings ⚠️

- You may occasionally see stack traces in development logs similar to:
   ```
   ConnectionAbortedError: [WinError 10053] An established connection was aborted by the software in your host machine
   ```
   This typically happens when a client cancels a request (for example, a browser cancels an audio file range download). It is harmless and happens inside the WSGI server (eventlet) while writing a response.

- If you want to reduce or remove these stack traces in logs, the app now suppresses these specific exceptions in server logs. Alternatively, you can:
   - Install/upgrade `eventlet` to the latest version: `pip install --upgrade eventlet`
   - Switch to `gevent` as your async server in `requirements.txt` and set `SocketIO(..., async_mode='gevent')` in `app.py`.

- If you see repeated aborted connections, check:
   - Client behavior (browser or app disconnects, stopping audio playback)
   - Local antivirus or firewall software that might be interrupting connections
   - Network instability that causes clients to drop connections
