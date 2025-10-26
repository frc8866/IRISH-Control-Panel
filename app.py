"""
Flask backend for IRISH 2025 scoring system.
Tracks BUCKET, HP, BENCH, and Fouls scoring components per alliance.
"""

from flask import Flask, render_template, request, jsonify
import sqlite3
import os
from datetime import datetime

app = Flask(__name__)
DATABASE = 'irish_scores.db'


def get_db():
    """Create a database connection."""
    db = sqlite3.connect(DATABASE)
    db.row_factory = sqlite3.Row
    return db


def init_db():
    """Initialize the database with the scoring schema."""
    db = get_db()
    cursor = db.cursor()
    
    # Create match_state table to track current match state
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS match_state (
            id INTEGER PRIMARY KEY CHECK (id = 1),
            red_bucket INTEGER DEFAULT 0,
            red_hp INTEGER DEFAULT 0,
            red_bench INTEGER DEFAULT 0,
            red_fouls INTEGER DEFAULT 0,
            blue_bucket INTEGER DEFAULT 0,
            blue_hp INTEGER DEFAULT 0,
            blue_bench INTEGER DEFAULT 0,
            blue_fouls INTEGER DEFAULT 0,
            red_and_one_count INTEGER DEFAULT 0,
            blue_and_one_count INTEGER DEFAULT 0,
            red_bonus_active INTEGER DEFAULT 0,
            blue_bonus_active INTEGER DEFAULT 0,
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Insert default row if not exists
    cursor.execute('SELECT COUNT(*) FROM match_state WHERE id = 1')
    if cursor.fetchone()[0] == 0:
        cursor.execute('''
            INSERT INTO match_state (id) VALUES (1)
        ''')
    
    db.commit()
    db.close()


def calculate_score(bucket, hp, bench, fouls, bonus_active):
    """
    Calculate alliance score based on components.
    BUCKET: 6 or 12 pts
    HP: 3 pts
    BENCH: 2, 6, or 14 pts
    Fouls: +5 or +15 pts (to opponent)
    Bonus multiplier: 2x when active
    """
    base_score = bucket + hp + bench + fouls
    if bonus_active:
        return base_score * 2
    return base_score


@app.route('/')
def index():
    """Redirect to referee panel."""
    return render_template('referee.html')


@app.route('/referee')
def referee():
    """Referee panel for data entry."""
    return render_template('referee.html')


@app.route('/display')
def display():
    """Audience display for viewing scores."""
    return render_template('display.html')


@app.route('/api/score', methods=['GET'])
def get_score():
    """API endpoint to get current match scores."""
    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT * FROM match_state WHERE id = 1')
    row = cursor.fetchone()
    db.close()
    
    if row:
        data = dict(row)
        # Calculate total scores
        data['red_total'] = calculate_score(
            data['red_bucket'], data['red_hp'], data['red_bench'],
            data['red_fouls'], data['red_bonus_active']
        )
        data['blue_total'] = calculate_score(
            data['blue_bucket'], data['blue_hp'], data['blue_bench'],
            data['blue_fouls'], data['blue_bonus_active']
        )
        return jsonify(data)
    
    return jsonify({'error': 'No data found'}), 404


@app.route('/api/score', methods=['POST'])
def update_score():
    """API endpoint to update match scores."""
    data = request.json
    db = get_db()
    cursor = db.cursor()
    
    # Build update query dynamically based on provided fields
    updates = []
    params = []
    
    for field in ['red_bucket', 'red_hp', 'red_bench', 'red_fouls',
                  'blue_bucket', 'blue_hp', 'blue_bench', 'blue_fouls',
                  'red_and_one_count', 'blue_and_one_count',
                  'red_bonus_active', 'blue_bonus_active']:
        if field in data:
            updates.append(f'{field} = ?')
            params.append(data[field])
    
    if updates:
        params.append(datetime.now().isoformat())
        query = f"UPDATE match_state SET {', '.join(updates)}, last_updated = ? WHERE id = 1"
        cursor.execute(query, params)
        db.commit()
    
    db.close()
    return get_score()


@app.route('/api/reset', methods=['POST'])
def reset_scores():
    """API endpoint to reset all scores to zero."""
    db = get_db()
    cursor = db.cursor()
    cursor.execute('''
        UPDATE match_state 
        SET red_bucket = 0, red_hp = 0, red_bench = 0, red_fouls = 0,
            blue_bucket = 0, blue_hp = 0, blue_bench = 0, blue_fouls = 0,
            red_and_one_count = 0, blue_and_one_count = 0,
            red_bonus_active = 0, blue_bonus_active = 0,
            last_updated = ?
        WHERE id = 1
    ''', (datetime.now().isoformat(),))
    db.commit()
    db.close()
    return get_score()


if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0', port=5000)
