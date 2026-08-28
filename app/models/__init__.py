from datetime import datetime
from uuid import uuid4
from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash
from ..extensions import db

class TimestampMixin:
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

class User(UserMixin, TimestampMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True); full_name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(254), unique=True, index=True, nullable=False); password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default='STUDENT', nullable=False, index=True); is_active = db.Column(db.Boolean, default=True, nullable=False)
    progress_records = db.relationship('Progress', back_populates='user', cascade='all, delete-orphan')
    attempts = db.relationship('QuizAttempt', back_populates='user', cascade='all, delete-orphan')
    def set_password(self, password): self.password_hash = generate_password_hash(password)
    def check_password(self, password): return check_password_hash(self.password_hash, password)
    @property
    def is_admin(self): return self.role == 'ADMIN'

class Module(TimestampMixin, db.Model):
    __tablename__ = 'modules'
    id = db.Column(db.Integer, primary_key=True); title = db.Column(db.String(160), nullable=False); slug = db.Column(db.String(180), unique=True, index=True, nullable=False)
    description = db.Column(db.Text, nullable=False); content = db.Column(db.Text, nullable=False); thumbnail_url = db.Column(db.String(500)); video_url = db.Column(db.String(500)); estimated_minutes = db.Column(db.Integer, default=20, nullable=False); display_order = db.Column(db.Integer, default=0, nullable=False, index=True); published = db.Column(db.Boolean, default=True, nullable=False)
    lessons = db.relationship('Lesson', back_populates='module', cascade='all, delete-orphan', order_by='Lesson.display_order')
    questions = db.relationship('Question', back_populates='module', cascade='all, delete-orphan')

class Lesson(TimestampMixin, db.Model):
    __tablename__ = 'lessons'; id = db.Column(db.Integer, primary_key=True); module_id = db.Column(db.Integer, db.ForeignKey('modules.id', ondelete='CASCADE'), nullable=False, index=True)
    title = db.Column(db.String(180), nullable=False); content = db.Column(db.Text, nullable=False); key_points = db.Column(db.Text); safety_tip = db.Column(db.Text); display_order = db.Column(db.Integer, default=0, nullable=False)
    module = db.relationship('Module', back_populates='lessons')

class Progress(db.Model):
    __tablename__ = 'progress'; __table_args__ = (db.UniqueConstraint('user_id','lesson_id', name='uq_progress_user_lesson'),)
    id = db.Column(db.Integer, primary_key=True); user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True); lesson_id = db.Column(db.Integer, db.ForeignKey('lessons.id', ondelete='CASCADE'), nullable=False, index=True); completed_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    user = db.relationship('User', back_populates='progress_records'); lesson = db.relationship('Lesson')

class Question(TimestampMixin, db.Model):
    __tablename__ = 'questions'; id = db.Column(db.Integer, primary_key=True); module_id = db.Column(db.Integer, db.ForeignKey('modules.id', ondelete='CASCADE'), nullable=False, index=True)
    prompt = db.Column(db.Text, nullable=False); option_a = db.Column(db.String(500), nullable=False); option_b = db.Column(db.String(500), nullable=False); option_c = db.Column(db.String(500), nullable=False); option_d = db.Column(db.String(500), nullable=False); correct_option = db.Column(db.String(1), nullable=False); explanation = db.Column(db.Text, nullable=False); difficulty = db.Column(db.String(20), default='Beginner', nullable=False); active = db.Column(db.Boolean, default=True, nullable=False)
    module = db.relationship('Module', back_populates='questions')

class QuizAttempt(db.Model):
    __tablename__ = 'quiz_attempts'; id = db.Column(db.Integer, primary_key=True); user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True); module_id = db.Column(db.Integer, db.ForeignKey('modules.id', ondelete='CASCADE'), nullable=False, index=True); score = db.Column(db.Integer, nullable=False); total_questions = db.Column(db.Integer, nullable=False); percentage = db.Column(db.Float, nullable=False); passed = db.Column(db.Boolean, nullable=False); submitted_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    user = db.relationship('User', back_populates='attempts'); module = db.relationship('Module'); answers = db.relationship('QuizAnswer', back_populates='attempt', cascade='all, delete-orphan')
class QuizAnswer(db.Model):
    __tablename__ = 'quiz_answers'; id = db.Column(db.Integer, primary_key=True); attempt_id = db.Column(db.Integer, db.ForeignKey('quiz_attempts.id', ondelete='CASCADE'), nullable=False, index=True); question_id = db.Column(db.Integer, db.ForeignKey('questions.id', ondelete='CASCADE'), nullable=False); selected_option = db.Column(db.String(1)); is_correct = db.Column(db.Boolean, nullable=False)
    attempt = db.relationship('QuizAttempt', back_populates='answers'); question = db.relationship('Question')
class Feedback(db.Model):
    __tablename__ = 'feedback'; id = db.Column(db.Integer, primary_key=True); user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False); rating = db.Column(db.Integer, nullable=False); message = db.Column(db.Text, nullable=False); created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    user = db.relationship('User')
class SurveyResponse(db.Model):
    __tablename__ = 'survey_responses'; id = db.Column(db.Integer, primary_key=True); user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), unique=True, nullable=False); overall_experience = db.Column(db.Integer, nullable=False); ease_of_understanding = db.Column(db.Integer, nullable=False); useful_module_id = db.Column(db.Integer, db.ForeignKey('modules.id')); confidence_improvement = db.Column(db.Integer, nullable=False); difficulty = db.Column(db.String(30), nullable=False); suggestions = db.Column(db.Text); created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    user = db.relationship('User'); useful_module = db.relationship('Module')
class ContactMessage(db.Model):
    __tablename__ = 'contact_messages'; id = db.Column(db.Integer, primary_key=True); name = db.Column(db.String(120), nullable=False); email = db.Column(db.String(254), nullable=False, index=True); subject = db.Column(db.String(180), nullable=False); message = db.Column(db.Text, nullable=False); status = db.Column(db.String(20), default='unread', nullable=False, index=True); created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
class Certificate(db.Model):
    __tablename__ = 'certificates'; id = db.Column(db.Integer, primary_key=True); user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), unique=True, nullable=False); certificate_code = db.Column(db.String(40), unique=True, nullable=False, default=lambda: uuid4().hex[:16].upper()); issued_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False); user = db.relationship('User')
