from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Team(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    number = db.Column(db.Integer, unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)

class Match(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    match_number = db.Column(db.Integer, nullable=False)
    match_type = db.Column(db.String(20), default='Qualification') # qualification, playoff, final
    red_team1_id = db.Column(db.Integer, db.ForeignKey('team.id'), nullable=True)
    red_team2_id = db.Column(db.Integer, db.ForeignKey('team.id'), nullable=True)
    blue_team1_id = db.Column(db.Integer, db.ForeignKey('team.id'), nullable=True)
    blue_team2_id = db.Column(db.Integer, db.ForeignKey('team.id'), nullable=True)

    # Scores
    red_score = db.Column(db.Integer, default=0)
    blue_score = db.Column(db.Integer, default=0)

    # Match status and timing
    status = db.Column(db.String(20), default='scheduled')  # scheduled, in_progress, completed
    start_time = db.Column(db.DateTime)
    end_time = db.Column(db.DateTime)
    match_time_remaining = db.Column(db.Integer, default=135)  # seconds (2:15 = 135 seconds)
    is_endgame = db.Column(db.Boolean, default=False)
    
    # Separate bonus tracking for each alliance
    red_bonus_active = db.Column(db.Boolean, default=False)
    red_bonus_time_remaining = db.Column(db.Integer, default=15)
    blue_bonus_active = db.Column(db.Boolean, default=False)
    blue_bonus_time_remaining = db.Column(db.Integer, default=15)

    # RP tracking
    red_teleop_rp = db.Column(db.Boolean, default=False)  # AND ONE bonus activated
    blue_teleop_rp = db.Column(db.Boolean, default=False)
    red_climb_rp = db.Column(db.Boolean, default=False)  # Combined bench points >= 20
    blue_climb_rp = db.Column(db.Boolean, default=False)
    red_win_rp = db.Column(db.Boolean, default=False)
    blue_win_rp = db.Column(db.Boolean, default=False)

    # Detailed scoring breakdown
    red_bucket_normal = db.Column(db.Integer, default=0)  # 6 points each
    red_bucket_bonus = db.Column(db.Integer, default=0)   # 12 points each
    red_human_bucket = db.Column(db.Integer, default=0)   # 3 points each
    red_park = db.Column(db.Integer, default=0)           # 2 points each
    red_slight_ramp = db.Column(db.Integer, default=0)    # 6 points each
    red_climb = db.Column(db.Integer, default=0)          # 14 points each

    blue_bucket_normal = db.Column(db.Integer, default=0)
    blue_bucket_bonus = db.Column(db.Integer, default=0)
    blue_human_bucket = db.Column(db.Integer, default=0)
    blue_park = db.Column(db.Integer, default=0)
    blue_slight_ramp = db.Column(db.Integer, default=0)
    blue_climb = db.Column(db.Integer, default=0)

    # Penalty tracking
    red_fouls = db.Column(db.Integer, default=0)          # +5 to opponent each
    red_tech_fouls = db.Column(db.Integer, default=0)     # +15 to opponent each
    blue_fouls = db.Column(db.Integer, default=0)
    blue_tech_fouls = db.Column(db.Integer, default=0)

    red_team1 = db.relationship('Team', foreign_keys=[red_team1_id])
    red_team2 = db.relationship('Team', foreign_keys=[red_team2_id])
    blue_team1 = db.relationship('Team', foreign_keys=[blue_team1_id])
    blue_team2 = db.relationship('Team', foreign_keys=[blue_team2_id])

class MatchEvent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    match_id = db.Column(db.Integer, db.ForeignKey('match.id'), nullable=False)
    event_type = db.Column(db.String(50), nullable=False)  # score_update, foul, timer, etc.
    alliance = db.Column(db.String(10))  # 'red' or 'blue'
    team_id = db.Column(db.Integer, db.ForeignKey('team.id'))
    points = db.Column(db.Integer, default=0)
    timestamp = db.Column(db.DateTime, default=db.func.current_timestamp())
    details = db.Column(db.String(200))  # Additional details like scoring type

    match = db.relationship('Match', backref=db.backref('events', lazy=True))
    team = db.relationship('Team')