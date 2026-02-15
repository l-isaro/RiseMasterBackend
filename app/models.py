from datetime import datetime
import uuid
from app.extensions import db

class User(db.Model):
    __tablename__ = 'users'
    user_id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    class_level = db.Column(db.String(10), nullable=False)  # S1, S2, S3, S4, S5, S6
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    mastery_states = db.relationship('MasteryState', backref='user', lazy=True)
    interactions = db.relationship('Interaction', backref='user', lazy=True)


class Problem(db.Model):
    __tablename__ = 'problems'
    problem_id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    skill_name = db.Column(db.String(100), nullable=False)
    topic = db.Column(db.String(100))
    target_exam_level = db.Column(db.String(10), nullable=False)
    difficulty = db.Column(db.Integer, default=3)
    question_text = db.Column(db.Text, nullable=False)
    correct_answer = db.Column(db.String(200), nullable=False)
    explanation = db.Column(db.Text)
    source = db.Column(db.String(100))
    
    concept_intro = db.Column(db.Text)  
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Interaction(db.Model):
    __tablename__ = 'interactions'
    interaction_id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.user_id'), nullable=False)
    problem_id = db.Column(db.String(36), db.ForeignKey('problems.problem_id'), nullable=False)
    correctness = db.Column(db.Integer)                             
    hints_used = db.Column(db.Integer, default=0)
    time_taken = db.Column(db.Float)                                
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    step_id = db.Column(db.String(36), db.ForeignKey('steps.step_id'), nullable=True)


class MasteryState(db.Model):
    __tablename__ = 'mastery_states'
    mastery_id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.user_id'), nullable=False)
    skill_name = db.Column(db.String(100), nullable=False)
    learn_rate = db.Column(db.Float, default=0.15)
    guess_rate = db.Column(db.Float, default=0.25)
    slip_rate = db.Column(db.Float, default=0.10)
    forget_rate = db.Column(db.Float, default=0.05)
    current_mastery_prob = db.Column(db.Float, default=0.0)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (db.UniqueConstraint('user_id', 'skill_name', name='unique_user_skill'),)

class Step(db.Model):
    __tablename__ = 'steps'
    step_id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    problem_id = db.Column(db.String(36), db.ForeignKey('problems.problem_id'), nullable=False)
    order = db.Column(db.Integer, nullable=False)             
    instruction_text = db.Column(db.Text, nullable=False) 
    input_type = db.Column(db.String(50), default='text')       
    correct_answer = db.Column(db.String(200), nullable=False)
    explanation = db.Column(db.Text)                           
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    hints = db.relationship('Hint', backref='step', lazy=True, cascade="all, delete-orphan")


class Hint(db.Model):
    __tablename__ = 'hints'
    hint_id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    step_id = db.Column(db.String(36), db.ForeignKey('steps.step_id'), nullable=False)
    level = db.Column(db.Integer, nullable=False)               # 1 = subtle, 2 = medium, 3 = explicit
    hint_text = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)