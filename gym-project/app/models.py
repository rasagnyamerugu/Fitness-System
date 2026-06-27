from app import db
from flask_login import UserMixin
from datetime import date


class User(db.Model, UserMixin):
    __tablename__ = 'users'
    uid      = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.Text, nullable=False)
    name     = db.Column(db.Text, nullable=False)
    password = db.Column(db.Text, nullable=False)
    email    = db.Column(db.Text, nullable=False)
    personal = db.relationship(
        'Persondetails',
        backref='user',
        uselist=False,
        cascade="all, delete"
    )
    daily_logs = db.relationship(
        'DailyLog',
        backref='user',
        lazy='dynamic',
        cascade="all, delete"
    )
    workout_logs = db.relationship(
        'WorkoutLog',
        backref='user',
        lazy='dynamic',
        cascade="all, delete"
    )

    def __repr__(self):
        return f'<User:{self.username}>'

    def get_id(self):
        return self.uid


class Persondetails(db.Model):
    __tablename__ = 'persondetails'

    uid             = db.Column(db.Integer, db.ForeignKey('users.uid', ondelete='CASCADE'), primary_key=True)
    name            = db.Column(db.Text,    nullable=True)
    age             = db.Column(db.Integer, nullable=True)
    weight          = db.Column(db.Integer, nullable=True)
    height          = db.Column(db.Integer, nullable=True)
    goal_weight     = db.Column(db.Integer, nullable=True)
    going_to_gym    = db.Column(db.Text,    nullable=True)
    level           = db.Column(db.Text,    nullable=True)
    gender          = db.Column(db.Text,    nullable=True)
    waist           = db.Column(db.Float,   nullable=True)
    body_fat        = db.Column(db.Float,   nullable=True)
    phone           = db.Column(db.Text,    nullable=True)
    dob             = db.Column(db.Text,    nullable=True)
    heart_rate      = db.Column(db.Integer, nullable=True)
    activity_level  = db.Column(db.Float,   nullable=True, default=1.55)
    session_len     = db.Column(db.Text,    nullable=True, default='60 min')
    streak          = db.Column(db.Integer, nullable=True, default=0)
    best_streak     = db.Column(db.Integer, nullable=True, default=0)
    goal            = db.Column(db.Text,    nullable=True)
    consistency_score     = db.Column(db.Integer, nullable=True, default=0)
    consistency_feedback  = db.Column(db.Text,    nullable=True)
    score_updated_date    = db.Column(db.Text,    nullable=True)

    def __repr__(self):
        return f'<Persondetails uid={self.uid}>'

    def get_id(self):
        return self.uid


class DailyLog(db.Model):

    __tablename__ = 'daily_logs'

    id          = db.Column(db.Integer, primary_key=True, autoincrement=True)
    uid         = db.Column(db.Integer, db.ForeignKey('users.uid', ondelete='CASCADE'), nullable=False)
    log_date = db.Column(db.Date, nullable=False)  

    pre_submitted     = db.Column(db.Boolean, default=False)
    pre_workout_type  = db.Column(db.Text,    nullable=True)
    pre_energy_level  = db.Column(db.Integer, nullable=True)
    pre_sleep_hours   = db.Column(db.Integer, nullable=True)
    pre_water_intake  = db.Column(db.Integer, nullable=True)   
    pre_mood          = db.Column(db.Text,    nullable=True)
    pre_injuries      = db.Column(db.Text,    nullable=True)
    pre_time          = db.Column(db.Text,    nullable=True)

  
    post_submitted    = db.Column(db.Boolean, default=False)
    post_duration     = db.Column(db.Integer, nullable=True)   
    post_calories     = db.Column(db.Integer, nullable=True)
    post_rating       = db.Column(db.Integer, nullable=True)   
    post_fatigue      = db.Column(db.Integer, nullable=True)   
    post_completion   = db.Column(db.Text,    nullable=True)

  
    steps             = db.Column(db.Integer, nullable=True, default=0)
    llm_feedback      = db.Column(db.Text,    nullable=True)

    __table_args__ = (
        db.UniqueConstraint('uid', 'log_date', name='uq_user_date'),
    )

    def __repr__(self):
        return f'<DailyLog uid={self.uid} date={self.log_date}>'


class WorkoutLog(db.Model):

    __tablename__ = 'workout_logs'

    id            = db.Column(db.Integer, primary_key=True, autoincrement=True)
    uid           = db.Column(db.Integer, db.ForeignKey('users.uid', ondelete='CASCADE'), nullable=False)
    log_date = db.Column(db.Date, nullable=False) 
    exercise_name = db.Column(db.String(100), nullable=False)
    set_index     = db.Column(db.Integer, nullable=False)  
    completed     = db.Column(db.Boolean, default=True)

    __table_args__ = (
        db.UniqueConstraint('uid', 'log_date', 'exercise_name', 'set_index',
                            name='uq_workout_set'),
    )

    def __repr__(self):
        return f'<WorkoutLog uid={self.uid} date={self.log_date} ex={self.exercise_name} set={self.set_index}>'
class WorkoutRecommendation(db.Model):

    __tablename__ = 'workout_recommendations'

    id                = db.Column(db.Integer, primary_key=True, autoincrement=True)
    gender            = db.Column(db.Text, nullable=True)
    goal              = db.Column(db.Text, nullable=True)   
    bmi_category      = db.Column(db.Text, nullable=True)   
    exercise_schedule = db.Column(db.Text, nullable=True)
    meal_plan         = db.Column(db.Text, nullable=True)

    def __repr__(self):
        return f'<WorkoutRecommendation {self.gender} | {self.goal} | {self.bmi_category}>'