from datetime import datetime

from app import db, bcrypt
from flask_login import UserMixin


class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)  # Add this field
    ratings = db.relationship('Rating', back_populates='user', lazy=True)

    @property
    def password(self):
        raise AttributeError('Password is write-only.')

    @password.setter
    def password(self, password):
        self.set_password(password)

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)

    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

class UserProfile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)
    schedule_json = db.Column(db.Text)  # Store schedule as a JSON string
    height = db.Column(db.Float, nullable=False, default=0.0)
    weight = db.Column(db.Float, nullable=False, default=0.0)
    age = db.Column(db.Integer, nullable=False, default=0)
    gender = db.Column(db.String(255), nullable=True)
    pushups = db.Column(db.Integer, nullable=False, default=0)
    squats = db.Column(db.Integer, nullable=False, default=0)
    plank_time = db.Column(db.Float, nullable=False, default=0.0)
    goal = db.Column(db.String(255), nullable=True)
    commitment = db.Column(db.String(255), nullable=True)
    fitness_level = db.Column(db.String(50), default="poor")  # Fitness Level




class Exercise(db.Model):
    __tablename__ = 'exercises'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    image_url = db.Column(db.String(200), nullable=True)

    # One-to-many relationship with Rating
    ratings = db.relationship('Rating', back_populates='exercise', lazy=True)

    def __repr__(self):
        return f"<Exercise {self.name}>"

class Rating(db.Model):
    __tablename__ = 'ratings'

    id = db.Column(db.Integer, primary_key=True)
    exercise_id = db.Column(db.Integer, db.ForeignKey('exercises.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)  # 1-5 rating
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    # Relationships
    exercise = db.relationship('Exercise', back_populates='ratings')
    user = db.relationship('User', back_populates='ratings')

    def __repr__(self):
        return f'<Rating {self.rating} for Exercise {self.exercise_id}>'

class WorkoutPreferences(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True, nullable=False)
    monday = db.Column(db.String(255), default="")
    tuesday = db.Column(db.String(255), default="")
    wednesday = db.Column(db.String(255), default="")
    thursday = db.Column(db.String(255), default="")
    friday = db.Column(db.String(255), default="")
    saturday = db.Column(db.String(255), default="")
    sunday = db.Column(db.String(255), default="")

    user = db.relationship('User', backref=db.backref('workout_preferences', lazy=True))
