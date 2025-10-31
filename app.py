from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit
from models import db, Team, Match, MatchEvent
import os
from datetime import datetime, UTC
import threading
import time

app = Flask(__name__)
app.config['SECRET_KEY'] = 'IRISH-2025'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///irish.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# Global timer variables
current_match_id = None
timer_thread = None
timer_running = False
field_fault_active = False

# Create database tables
with app.app_context():
    db.create_all()

def match_timer():
    """Background timer for match countdown"""
    global timer_running, current_match_id, field_fault_active

    with app.app_context():
        match = db.session.get(Match, current_match_id)
        if not match:
            return

        while timer_running and match.match_time_remaining > 0:
            time.sleep(1)
            
            # Skip timer countdown if field fault is active
            if field_fault_active:
                continue
            
            match.match_time_remaining -= 1

            # Check for endgame (30 seconds left)
            if match.match_time_remaining == 30 and not match.is_endgame:
                match.is_endgame = True
                db.session.commit()
                socketio.emit('endgame_started', {'match_id': current_match_id})

            # Check for red bonus timer
            if match.red_bonus_active and match.red_bonus_time_remaining > 0:
                match.red_bonus_time_remaining -= 1
                if match.red_bonus_time_remaining == 0:
                    match.red_bonus_active = False
                    db.session.commit()
                    socketio.emit('bonus_ended', {
                        'match_id': current_match_id,
                        'alliance': 'red'
                    })
            
            # Check for blue bonus timer
            if match.blue_bonus_active and match.blue_bonus_time_remaining > 0:
                match.blue_bonus_time_remaining -= 1
                if match.blue_bonus_time_remaining == 0:
                    match.blue_bonus_active = False
                    db.session.commit()
                    socketio.emit('bonus_ended', {
                        'match_id': current_match_id,
                        'alliance': 'blue'
                    })

            db.session.commit()

            # Emit timer update every second
            socketio.emit('timer_update', {
                'match_id': current_match_id,
                'time_remaining': match.match_time_remaining,
                'is_endgame': match.is_endgame,
                'red_bonus_active': match.red_bonus_active,
                'red_bonus_time': match.red_bonus_time_remaining if match.red_bonus_active else 0,
                'blue_bonus_active': match.blue_bonus_active,
                'blue_bonus_time': match.blue_bonus_time_remaining if match.blue_bonus_active else 0,
                'field_fault': field_fault_active
            })

        # Match ended
        if timer_running:
            match.status = 'completed'
            match.end_time = datetime.now(UTC)
            calculate_rps(match)
            db.session.commit()
            socketio.emit('match_ended', {'match_id': current_match_id})
            
            # Wait 1 second then clear endgame indicator
            time.sleep(1)
            socketio.emit('clear_endgame', {'match_id': current_match_id})

def calculate_rps(match):
    """Calculate Ranking Points at match end"""
    # Reset all RPs before recalculating
    match.red_win_rp = False
    match.blue_win_rp = False
    match.red_climb_rp = False
    match.blue_climb_rp = False
    
    # Win RP
    if match.red_score > match.blue_score:
        match.red_win_rp = True
    elif match.blue_score > match.red_score:
        match.blue_win_rp = True
    # Tie gives 0 win RPs

    # Tele-op RP (AND ONE bonus activated)
    # Already tracked in real-time

    # Climb RP (combined bench points >= 20)
    red_climb_points = (match.red_park * 2) + (match.red_slight_ramp * 6) + (match.red_climb * 14)
    blue_climb_points = (match.blue_park * 2) + (match.blue_slight_ramp * 6) + (match.blue_climb * 14)

    if red_climb_points >= 20:
        match.red_climb_rp = True
    if blue_climb_points >= 20:
        match.blue_climb_rp = True

# Sample data initialization
def init_sample_data():
    with app.app_context():
        if Team.query.count() == 0:
            # Add sample teams
            teams = [
                Team(number=8866, name='IRISH'),
                Team(number=1234, name='Team A'),
                Team(number=5678, name='Team B'),
                Team(number=9012, name='Team C'),
                Team(number=3456, name='Team D'),
            ]
            db.session.add_all(teams)
            db.session.commit()

            # No sample match - FTA will start with empty fields

init_sample_data()

@app.route('/')
def index():
    # Default to unified display
    return render_template('unified_display.html')

@app.route('/fta')
def fta():
    return render_template('fta_new.html')

@app.route('/referee')
def referee():
    return render_template('referee.html')

@app.route('/api/current_match')
def get_current_match():
    # Get the most relevant match
    match = Match.query.filter_by(status='in_progress').first()
    if not match:
        match = Match.query.filter_by(status='scheduled').first()
    if not match:
        match = Match.query.order_by(Match.id.desc()).first()
    
    if match:
        return jsonify({
            'id': match.id,
            'match_number': match.match_number,
            'red_team1': match.red_team1.number if match.red_team1 else '',
            'red_team2': match.red_team2.number if match.red_team2 else '',
            'blue_team1': match.blue_team1.number if match.blue_team1 else '',
            'blue_team2': match.blue_team2.number if match.blue_team2 else '',
            'red_score': match.red_score,
            'blue_score': match.blue_score,
            'status': match.status,
            'red_bucket_normal': match.red_bucket_normal,
            'red_bucket_bonus': match.red_bucket_bonus,
            'red_human_bucket': match.red_human_bucket,
            'red_park': match.red_park,
            'red_slight_ramp': match.red_slight_ramp,
            'red_climb': match.red_climb,
            'red_fouls': match.red_fouls,
            'red_tech_fouls': match.red_tech_fouls,
            'blue_bucket_normal': match.blue_bucket_normal,
            'blue_bucket_bonus': match.blue_bucket_bonus,
            'blue_human_bucket': match.blue_human_bucket,
            'blue_park': match.blue_park,
            'blue_slight_ramp': match.blue_slight_ramp,
            'blue_climb': match.blue_climb,
            'blue_fouls': match.blue_fouls,
            'blue_tech_fouls': match.blue_tech_fouls,
            'red_win_rp': match.red_win_rp,
            'blue_win_rp': match.blue_win_rp,
            'red_teleop_rp': match.red_teleop_rp,
            'blue_teleop_rp': match.blue_teleop_rp,
            'red_climb_rp': match.red_climb_rp,
            'blue_climb_rp': match.blue_climb_rp
        })
    else:
        return jsonify({
            'match_number': 1,
            'red_team1': '',
            'red_team2': '',
            'blue_team1': '',
            'blue_team2': '',
            'red_score': 0,
            'blue_score': 0,
            'status': 'scheduled'
        })

@app.route('/api/matches')
def get_matches():
    matches = Match.query.all()
    return jsonify([{
        'id': m.id,
        'match_number': m.match_number,
        'red_team1': {'number': m.red_team1.number} if m.red_team1 else None,
        'red_team2': {'number': m.red_team2.number} if m.red_team2 else None,
        'blue_team1': {'number': m.blue_team1.number} if m.blue_team1 else None,
        'blue_team2': {'number': m.blue_team2.number} if m.blue_team2 else None,
        'red_score': m.red_score,
        'blue_score': m.blue_score,
        'status': m.status,
        'time_remaining': m.match_time_remaining,
        'is_endgame': m.is_endgame,
        'red_bonus_active': m.red_bonus_active,
        'red_bonus_time': m.red_bonus_time_remaining,
        'blue_bonus_active': m.blue_bonus_active,
        'blue_bonus_time': m.blue_bonus_time_remaining,
        'red_teleop_rp': m.red_teleop_rp,
        'blue_teleop_rp': m.blue_teleop_rp,
        'red_climb_rp': m.red_climb_rp,
        'blue_climb_rp': m.blue_climb_rp,
        'red_win_rp': m.red_win_rp,
        'blue_win_rp': m.blue_win_rp
    } for m in matches])

@app.route('/api/matches/<int:match_id>', methods=['DELETE'])
def delete_match(match_id):
    """Delete a match and all its associated events"""
    match = db.session.get(Match, match_id)
    if not match:
        return jsonify({'error': 'Match not found'}), 404
    
    # Delete all associated match events first
    MatchEvent.query.filter_by(match_id=match_id).delete()
    
    # Delete the match
    db.session.delete(match)
    db.session.commit()
    
    return jsonify({'success': True, 'message': f'Match {match_id} deleted'})

@app.route('/api/match_events/<int:match_id>')
def get_match_events(match_id):
    """Get all scoring events for a specific match"""
    events = MatchEvent.query.filter_by(match_id=match_id).order_by(MatchEvent.timestamp.asc()).all()
    return jsonify([{
        'id': e.id,
        'match_id': e.match_id,
        'event_type': e.event_type,
        'alliance': e.alliance,
        'points': e.points,
        'timestamp': e.timestamp.isoformat() if e.timestamp else None,
        'details': e.details
    } for e in events])

@socketio.on('connect')
def handle_connect():
    print('Client connected')

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

@socketio.on('start_match')
def handle_start_match(data):
    global current_match_id, timer_thread, timer_running

    match_id = data.get('match_id')
    match = db.session.get(Match, match_id)
    if match:
        # Validate that all teams are assigned before starting match
        if not (match.red_team1 and match.red_team2 and match.blue_team1 and match.blue_team2):
            emit('match_start_error', {
                'error': 'All teams must be assigned before starting the match'
            })
            return

        match.status = 'in_progress'
        match.start_time = datetime.now(UTC)
        match.match_time_remaining = 135  # 0:30 = 30 seconds
        match.is_endgame = False
        match.red_bonus_active = False
        match.red_bonus_time_remaining = 15
        match.blue_bonus_active = False
        match.blue_bonus_time_remaining = 15
        db.session.commit()

        current_match_id = match_id
        timer_running = True
        timer_thread = threading.Thread(target=match_timer)
        timer_thread.daemon = True
        timer_thread.start()

        emit('match_started', {
            'match_id': match_id,
            'red_team1': match.red_team1.number,
            'red_team2': match.red_team2.number,
            'blue_team1': match.blue_team1.number,
            'blue_team2': match.blue_team2.number
        })

@socketio.on('score_event')
def handle_score_event(data):
    match_id = data.get('match_id')
    alliance = data.get('alliance')  # 'red' or 'blue'
    event_type = data.get('event_type')
    points = data.get('points', 0)

    match = db.session.get(Match, match_id)
    if not match:
        return

    # Update match scores and detailed tracking
    if alliance == 'red':
        if event_type == 'bucket_normal':
            match.red_score += points
            match.red_bucket_normal += 1
        elif event_type == 'bucket_bonus':
            match.red_score += points
            match.red_bucket_bonus += 1
        elif event_type == 'human_bucket':
            match.red_score += points
            match.red_human_bucket += 1
        elif event_type == 'park':
            match.red_score += points
            match.red_park += 1
        elif event_type == 'slight_ramp':
            match.red_score += points
            match.red_slight_ramp += 1
        elif event_type == 'climb':
            match.red_score += points
            match.red_climb += 1
        elif event_type == 'foul':
            match.red_fouls += 1
            match.blue_score += 5  # Penalty points go to opponent only
        elif event_type == 'tech_foul':
            match.red_tech_fouls += 1
            match.blue_score += 15  # Penalty points go to opponent only

    elif alliance == 'blue':
        if event_type == 'bucket_normal':
            match.blue_score += points
            match.blue_bucket_normal += 1
        elif event_type == 'bucket_bonus':
            match.blue_score += points
            match.blue_bucket_bonus += 1
        elif event_type == 'human_bucket':
            match.blue_score += points
            match.blue_human_bucket += 1
        elif event_type == 'park':
            match.blue_score += points
            match.blue_park += 1
        elif event_type == 'slight_ramp':
            match.blue_score += points
            match.blue_slight_ramp += 1
        elif event_type == 'climb':
            match.blue_score += points
            match.blue_climb += 1
        elif event_type == 'foul':
            match.blue_fouls += 1
            match.red_score += 5  # Penalty points go to opponent only
        elif event_type == 'tech_foul':
            match.blue_tech_fouls += 1
            match.red_score += 15  # Penalty points go to opponent only

    db.session.commit()

    # Record event
    event = MatchEvent(
        match_id=match_id,
        event_type=event_type,
        alliance=alliance,
        points=points
    )
    db.session.add(event)
    db.session.commit()

    # Broadcast score update to all clients (display, referee, FTA)
    socketio.emit('score_updated', {
        'match_id': match_id,
        'red_score': match.red_score,
        'blue_score': match.blue_score,
        'event_type': event_type,
        'alliance': alliance,
        'points': points
    })

@socketio.on('activate_bonus')
def handle_activate_bonus(data):
    match_id = data.get('match_id')
    alliance = data.get('alliance')

    match = db.session.get(Match, match_id)
    if not match:
        return
    
    # Check if this alliance's bonus is already active
    if alliance == 'red':
        if not match.red_bonus_active:
            match.red_bonus_active = True
            match.red_bonus_time_remaining = 15
            match.red_teleop_rp = True
            db.session.commit()

            socketio.emit('bonus_activated', {
                'match_id': match_id,
                'alliance': 'red',
                'bonus_time': 15
            })
    elif alliance == 'blue':
        if not match.blue_bonus_active:
            match.blue_bonus_active = True
            match.blue_bonus_time_remaining = 15
            match.blue_teleop_rp = True
            db.session.commit()

            socketio.emit('bonus_activated', {
                'match_id': match_id,
                'alliance': 'blue',
                'bonus_time': 15
            })

@socketio.on('end_match')
def handle_end_match(data):
    global timer_running
    match_id = data.get('match_id')
    match = db.session.get(Match, match_id)
    if match:
        timer_running = False
        match.status = 'completed'
        match.end_time = datetime.now(UTC)
        calculate_rps(match)
        db.session.commit()
        emit('match_ended', {'match_id': match_id})

@socketio.on('fta_field_fault')
def handle_field_fault(data):
    """Pause the match timer for a field fault"""
    global field_fault_active
    field_fault_active = True
    socketio.emit('field_fault_started', {'match_id': current_match_id})
    # Immediately notify displays of timer state so banner shows without waiting for next tick
    match = db.session.get(Match, current_match_id)
    socketio.emit('timer_update', {
        'match_id': current_match_id,
        'time_remaining': match.match_time_remaining if match else 0,
        'is_endgame': match.is_endgame if match else False,
        'red_bonus_active': match.red_bonus_active if match else False,
        'red_bonus_time': match.red_bonus_time_remaining if match and match.red_bonus_active else 0,
        'blue_bonus_active': match.blue_bonus_active if match else False,
        'blue_bonus_time': match.blue_bonus_time_remaining if match and match.blue_bonus_active else 0,
        'field_fault': field_fault_active
    })

@socketio.on('fta_resume_match')
def handle_resume_match(data):
    """Resume the match timer after a field fault"""
    global field_fault_active
    field_fault_active = False
    socketio.emit('field_fault_ended', {'match_id': current_match_id})
    # Immediately notify displays of timer state so banner hides without waiting for next tick
    match = db.session.get(Match, current_match_id)
    socketio.emit('timer_update', {
        'match_id': current_match_id,
        'time_remaining': match.match_time_remaining if match else 0,
        'is_endgame': match.is_endgame if match else False,
        'red_bonus_active': match.red_bonus_active if match else False,
        'red_bonus_time': match.red_bonus_time_remaining if match and match.red_bonus_active else 0,
        'blue_bonus_active': match.blue_bonus_active if match else False,
        'blue_bonus_time': match.blue_bonus_time_remaining if match and match.blue_bonus_active else 0,
        'field_fault': field_fault_active
    })

# FTA Socket Handlers
@socketio.on('fta_save_match')
def handle_fta_save_match(data):
    match_id = data.get('match_id')
    match_number = data.get('match_number')
    red_team1_num = data.get('red_team1')
    red_team2_num = data.get('red_team2')
    blue_team1_num = data.get('blue_team1')
    blue_team2_num = data.get('blue_team2')

    # If no match_id provided, create a new match
    if not match_id:
        match = Match(match_number=match_number or 1)
    else:
        match = db.session.get(Match, match_id)
        if not match:
            match = Match(match_number=match_number or 1)

    # Auto-create teams if they don't exist and assign them
    if red_team1_num and red_team1_num.strip():
        red_team1 = Team.query.filter_by(number=int(red_team1_num)).first()
        if not red_team1:
            red_team1 = Team(number=int(red_team1_num), name=f'Team {red_team1_num}')
            db.session.add(red_team1)
        match.red_team1 = red_team1
    else:
        match.red_team1 = None
        
    if red_team2_num and red_team2_num.strip():
        red_team2 = Team.query.filter_by(number=int(red_team2_num)).first()
        if not red_team2:
            red_team2 = Team(number=int(red_team2_num), name=f'Team {red_team2_num}')
            db.session.add(red_team2)
        match.red_team2 = red_team2
    else:
        match.red_team2 = None
        
    if blue_team1_num and blue_team1_num.strip():
        blue_team1 = Team.query.filter_by(number=int(blue_team1_num)).first()
        if not blue_team1:
            blue_team1 = Team(number=int(blue_team1_num), name=f'Team {blue_team1_num}')
            db.session.add(blue_team1)
        match.blue_team1 = blue_team1
    else:
        match.blue_team1 = None
        
    if blue_team2_num and blue_team2_num.strip():
        blue_team2 = Team.query.filter_by(number=int(blue_team2_num)).first()
        if not blue_team2:
            blue_team2 = Team(number=int(blue_team2_num), name=f'Team {blue_team2_num}')
            db.session.add(blue_team2)
        match.blue_team2 = blue_team2
    else:
        match.blue_team2 = None

    # Set match number if provided
    if match_number:
        match.match_number = match_number

    # Add to database if it's a new match
    if not match.id:
        db.session.add(match)

    db.session.commit()

    emit('match_data_saved', {'match_id': match.id})

@socketio.on('fta_update_display')
def handle_fta_update_display(data):
    # Send data directly to display to show in prematch
    socketio.emit('show_prematch', {
        'match_number': data.get('match_number', 1),
        'red_team1': data.get('red_team1', '????'),
        'red_team2': data.get('red_team2', '????'),
        'blue_team1': data.get('blue_team1', '????'),
        'blue_team2': data.get('blue_team2', '????')
    })

@socketio.on('fta_start_match')
def handle_fta_start_match(data):
    global current_match_id, timer_thread, timer_running

    # Save or get the match first
    match_id = data.get('match_id')
    
    # Store team numbers for later use
    team_numbers = {
        'red_team1': data.get('red_team1'),
        'red_team2': data.get('red_team2'),
        'blue_team1': data.get('blue_team1'),
        'blue_team2': data.get('blue_team2')
    }
    
    if not match_id:
        # Create new match
        match = Match(
            match_number=data.get('match_number', 1),
            status='in_progress',
            start_time=datetime.now(UTC),
            match_time_remaining=135,
            is_endgame=False,
            red_bonus_active=False,
            red_bonus_time_remaining=15,
            blue_bonus_active=False,
            blue_bonus_time_remaining=15
        )

        # Assign teams - auto-create them if they don't exist
        for team_key in ['red_team1', 'red_team2', 'blue_team1', 'blue_team2']:
            team_num = data.get(team_key)
            if team_num and str(team_num).strip():
                team = Team.query.filter_by(number=int(team_num)).first()
                if not team:
                    # Create the team if it doesn't exist
                    team = Team(number=int(team_num), name=f'Team {team_num}')
                    db.session.add(team)
                setattr(match, team_key, team)
            else:
                setattr(match, team_key, None)

        db.session.add(match)
        db.session.commit()
        match_id = match.id
    else:
        match = db.session.get(Match, match_id)
        if match:
            match.status = 'in_progress'
            match.start_time = datetime.now(UTC)
            match.match_time_remaining = 135
            match.is_endgame = False
            match.red_bonus_active = False
            match.red_bonus_time_remaining = 15
            match.blue_bonus_active = False
            match.blue_bonus_time_remaining = 15
            db.session.commit()

    if match:
        current_match_id = match_id
        timer_running = True
        timer_thread = threading.Thread(target=match_timer)
        timer_thread.daemon = True
        timer_thread.start()

        # Transition display to live view with team numbers (use stored numbers as fallback)
        socketio.emit('show_live', {
            'match_number': match.match_number,
            'red_team1': match.red_team1.number if match.red_team1 else team_numbers.get('red_team1', '????'),
            'red_team2': match.red_team2.number if match.red_team2 else team_numbers.get('red_team2', '????'),
            'blue_team1': match.blue_team1.number if match.blue_team1 else team_numbers.get('blue_team1', '????'),
            'blue_team2': match.blue_team2.number if match.blue_team2 else team_numbers.get('blue_team2', '????'),
            'red_score': match.red_score,
            'blue_score': match.blue_score
        })
        
        # Update referee panel with new match info
        socketio.emit('match_started', {
            'match_id': match_id,
            'match_number': match.match_number,
            'red_team1': match.red_team1.number if match.red_team1 else team_numbers.get('red_team1', '????'),
            'red_team2': match.red_team2.number if match.red_team2 else team_numbers.get('red_team2', '????'),
            'blue_team1': match.blue_team1.number if match.blue_team1 else team_numbers.get('blue_team1', '????'),
            'blue_team2': match.blue_team2.number if match.blue_team2 else team_numbers.get('blue_team2', '????'),
            'red_score': match.red_score,
            'blue_score': match.blue_score,
            'status': 'in_progress'
        })

        emit('match_started', {'match_id': match_id})

@socketio.on('fta_finalize_match')
def handle_fta_finalize_match(data):
    """Finalize match after review - recalculate RPs with reviewed scores"""
    match_id = data.get('match_id')
    match = db.session.get(Match, match_id)
    if match:
        # Mark match as finalized
        match.status = 'finalized'
        
        # Recalculate ranking points with final reviewed scores
        # (scores have already been updated by score_event/delete_event handlers)
        calculate_rps(match)
        db.session.commit()
        
        print(f"Match {match_id} finalized with reviewed scores.")
        print(f"  Red: {match.red_score} pts, RPs: {match.red_teleop_rp + match.red_climb_rp + match.red_win_rp}")
        print(f"  Blue: {match.blue_score} pts, RPs: {match.blue_teleop_rp + match.blue_climb_rp + match.blue_win_rp}")
        
        # Notify all clients that match is finalized
        socketio.emit('match_finalized', {
            'match_id': match_id,
            'red_score': match.red_score,
            'blue_score': match.blue_score
        })

@socketio.on('fta_show_review')
def handle_fta_show_review(data=None):
    # Show review banner on live display and send match_id to referee
    match_id = data.get('match_id') if data else None
    socketio.emit('show_review', {'match_id': match_id})

@socketio.on('fta_hide_review')
def handle_fta_hide_review(data=None):
    # Hide review banner on live display
    socketio.emit('hide_review')

@socketio.on('delete_event')
def handle_delete_event(data):
    """Delete a scoring event and recalculate match scores"""
    event_id = data.get('event_id')
    match_id = data.get('match_id')
    
    event = db.session.get(MatchEvent, event_id)
    if event and event.match_id == match_id:
        match = db.session.get(Match, match_id)
        if match:
            # Reverse the scoring for this event
            event_type = event.event_type
            alliance = event.alliance
            points = event.points
            
            # Decrease the specific event counter
            if alliance == 'red':
                if event_type == 'bucket_normal':
                    match.red_bucket_normal = max(0, match.red_bucket_normal - 1)
                    match.red_score = max(0, match.red_score - points)
                elif event_type == 'bucket_bonus':
                    match.red_bucket_bonus = max(0, match.red_bucket_bonus - 1)
                    match.red_score = max(0, match.red_score - points)
                elif event_type == 'human_bucket':
                    match.red_human_bucket = max(0, match.red_human_bucket - 1)
                    match.red_score = max(0, match.red_score - points)
                elif event_type == 'park':
                    match.red_park = max(0, match.red_park - 1)
                    match.red_score = max(0, match.red_score - points)
                elif event_type == 'slight_ramp':
                    match.red_slight_ramp = max(0, match.red_slight_ramp - 1)
                    match.red_score = max(0, match.red_score - points)
                elif event_type == 'climb':
                    match.red_climb = max(0, match.red_climb - 1)
                    match.red_score = max(0, match.red_score - points)
                elif event_type == 'foul':
                    match.red_fouls = max(0, match.red_fouls - 1)
                    match.blue_score = max(0, match.blue_score - points)
                elif event_type == 'tech_foul':
                    match.red_tech_fouls = max(0, match.red_tech_fouls - 1)
                    match.blue_score = max(0, match.blue_score - points)
            elif alliance == 'blue':
                if event_type == 'bucket_normal':
                    match.blue_bucket_normal = max(0, match.blue_bucket_normal - 1)
                    match.blue_score = max(0, match.blue_score - points)
                elif event_type == 'bucket_bonus':
                    match.blue_bucket_bonus = max(0, match.blue_bucket_bonus - 1)
                    match.blue_score = max(0, match.blue_score - points)
                elif event_type == 'human_bucket':
                    match.blue_human_bucket = max(0, match.blue_human_bucket - 1)
                    match.blue_score = max(0, match.blue_score - points)
                elif event_type == 'park':
                    match.blue_park = max(0, match.blue_park - 1)
                    match.blue_score = max(0, match.blue_score - points)
                elif event_type == 'slight_ramp':
                    match.blue_slight_ramp = max(0, match.blue_slight_ramp - 1)
                    match.blue_score = max(0, match.blue_score - points)
                elif event_type == 'climb':
                    match.blue_climb = max(0, match.blue_climb - 1)
                    match.blue_score = max(0, match.blue_score - points)
                elif event_type == 'foul':
                    match.blue_fouls = max(0, match.blue_fouls - 1)
                    match.red_score = max(0, match.red_score - points)
                elif event_type == 'tech_foul':
                    match.blue_tech_fouls = max(0, match.blue_tech_fouls - 1)
                    match.red_score = max(0, match.red_score - points)
            
            # Delete the event
            db.session.delete(event)
            db.session.commit()
            
            # Emit updated scores
            socketio.emit('event_deleted', {
                'match_id': match_id,
                'red_score': match.red_score,
                'blue_score': match.blue_score
            })
            socketio.emit('score_updated', {
                'red_score': match.red_score,
                'blue_score': match.blue_score
            })

@socketio.on('update_match_scores')
def handle_update_match_scores(data):
    """Manually update match scores during review"""
    match_id = data.get('match_id')
    red_score = data.get('red_score')
    blue_score = data.get('blue_score')
    
    match = db.session.get(Match, match_id)
    if match:
        match.red_score = red_score
        match.blue_score = blue_score
        db.session.commit()
        
        socketio.emit('scores_updated', {
            'match_id': match_id,
            'red_score': red_score,
            'blue_score': blue_score
        })
        socketio.emit('score_updated', {
            'red_score': red_score,
            'blue_score': blue_score
        })

@socketio.on('fta_show_postmatch')
def handle_fta_show_postmatch(data):
    match_id = data.get('match_id')
    if match_id:
        match = db.session.get(Match, match_id)
    else:
        # Get most recent match
        match = Match.query.order_by(Match.id.desc()).first()
    
    if match:
        # Ensure match is marked as completed and saved to DB
        if match.status != 'completed':
            match.status = 'completed'
            if not match.end_time:
                match.end_time = datetime.now(UTC)
            calculate_rps(match)
            db.session.commit()
        

        socketio.emit('show_postmatch', {
            'match_number': match.match_number,
            'red_team1': match.red_team1.number if match.red_team1 else '????',
            'red_team2': match.red_team2.number if match.red_team2 else '????',
            'blue_team1': match.blue_team1.number if match.blue_team1 else '????',
            'blue_team2': match.blue_team2.number if match.blue_team2 else '????',
            'red_score': match.red_score,
            'blue_score': match.blue_score,
            'red_bucket_normal': match.red_bucket_normal,
            'red_bucket_bonus': match.red_bucket_bonus,
            'red_human_bucket': match.red_human_bucket,
            'red_park': match.red_park,
            'red_slight_ramp': match.red_slight_ramp,
            'red_climb': match.red_climb,
            'red_fouls': match.red_fouls,
            'red_tech_fouls': match.red_tech_fouls,
            'blue_bucket_normal': match.blue_bucket_normal,
            'blue_bucket_bonus': match.blue_bucket_bonus,
            'blue_human_bucket': match.blue_human_bucket,
            'blue_park': match.blue_park,
            'blue_slight_ramp': match.blue_slight_ramp,
            'blue_climb': match.blue_climb,
            'blue_fouls': match.blue_fouls,
            'blue_tech_fouls': match.blue_tech_fouls,
            'red_win_rp': match.red_win_rp,
            'blue_win_rp': match.blue_win_rp,
            'red_teleop_rp': match.red_teleop_rp,
            'blue_teleop_rp': match.blue_teleop_rp,
            'red_climb_rp': match.red_climb_rp,
            'blue_climb_rp': match.blue_climb_rp
        })

@socketio.on('load_match_data')
def handle_load_match_data(data):
    match_id = data.get('match_id')

    if not match_id:
        # No match ID provided, emit empty data
        emit('match_data_loaded', {
            'match_id': None,
            'match_number': 1,
            'red_team1': '',
            'red_team2': '',
            'blue_team1': '',
            'blue_team2': '',
            'status': 'scheduled'
        })
        return

    match = db.session.get(Match, match_id)
    if match:
        emit('match_data_loaded', {
            'match_id': match.id,
            'match_number': match.match_number,
            'red_team1': match.red_team1.number if match.red_team1 else '',
            'red_team2': match.red_team2.number if match.red_team2 else '',
            'blue_team1': match.blue_team1.number if match.blue_team1 else '',
            'blue_team2': match.blue_team2.number if match.blue_team2 else '',
            'status': match.status
        })
    else:
        # Match not found, emit empty data
        emit('match_data_loaded', {
            'match_id': None,
            'match_number': 1,
            'red_team1': '',
            'red_team2': '',
            'blue_team1': '',
            'blue_team2': '',
            'status': 'scheduled'
        })

if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)
