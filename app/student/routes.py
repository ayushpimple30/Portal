from datetime import datetime, timezone
from random import sample
from secrets import token_urlsafe
from flask import Blueprint, abort, flash, redirect, render_template, request, session, url_for
from flask_login import current_user, login_required
from flask_wtf import FlaskForm
from wtforms import IntegerField, SelectField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Length, NumberRange, Optional
from ..extensions import db
from ..models import Certificate, Feedback, Lesson, Module, Progress, Question, QuizAnswer, QuizAttempt, SurveyResponse
from ..utils import completion, eligible

bp = Blueprint('student', __name__, url_prefix='/learn')
PASS_MARK = 70
QUIZ_SECONDS = 15 * 60

class FeedbackForm(FlaskForm):
    rating = IntegerField('Rating (1–5)', validators=[DataRequired(), NumberRange(1, 5)])
    message = TextAreaField('Feedback', validators=[DataRequired(), Length(max=3000)])
    submit = SubmitField('Send feedback')

class SurveyForm(FlaskForm):
    overall_experience = IntegerField('Overall experience (1–5)', validators=[DataRequired(), NumberRange(1, 5)])
    ease_of_understanding = IntegerField('Ease of understanding (1–5)', validators=[DataRequired(), NumberRange(1, 5)])
    useful_module_id = SelectField('Most useful module', coerce=int, validators=[DataRequired()])
    confidence_improvement = IntegerField('Confidence improvement (1–5)', validators=[DataRequired(), NumberRange(1, 5)])
    difficulty = SelectField('Difficulty', choices=[('Too easy', 'Too easy'), ('Appropriate', 'Appropriate'), ('Challenging', 'Challenging')])
    suggestions = TextAreaField('Suggestions', validators=[Optional(), Length(max=3000)])
    submit = SubmitField('Submit survey')

def student_only():
    if current_user.is_admin:
        abort(403)

def module_progress(module, completed_ids):
    lessons = [lesson for lesson in module.lessons if lesson.published]
    done = sum(lesson.id in completed_ids for lesson in lessons)
    return {'done': done, 'total': len(lessons), 'percent': round(done / len(lessons) * 100) if lessons else 0}

@bp.route('/dashboard')
@login_required
def dashboard():
    student_only()
    done, total, percent = completion(current_user)
    attempts = QuizAttempt.query.filter_by(user_id=current_user.id).order_by(QuizAttempt.submitted_at.desc()).all()
    completed_ids = {record.lesson_id for record in current_user.progress_records}
    modules = Module.query.filter_by(published=True).order_by(Module.display_order).all()
    next_lesson = next((lesson for module in modules for lesson in module.lessons if lesson.published and lesson.id not in completed_ids), None)
    module_data = [(module, module_progress(module, completed_ids)) for module in modules]
    latest_score = attempts[0].percentage if attempts else None
    best_score = max((attempt.percentage for attempt in attempts), default=None)
    return render_template('student/dashboard.html', done=done, total=total, pct=percent, attempts=attempts, next_lesson=next_lesson, certificate=eligible(current_user), module_data=module_data, latest_score=latest_score, best_score=best_score)

@bp.route('/modules')
@login_required
def modules():
    student_only()
    completed = {record.lesson_id for record in current_user.progress_records}
    catalog = [(module, module_progress(module, completed)) for module in Module.query.filter_by(published=True).order_by(Module.display_order)]
    return render_template('student/modules.html', catalog=catalog)

@bp.route('/modules/<slug>')
@login_required
def module(slug):
    student_only()
    current_module = Module.query.filter_by(slug=slug, published=True).first_or_404()
    completed = {record.lesson_id for record in current_user.progress_records}
    return render_template('student/module.html', module=current_module, completed=completed, progress=module_progress(current_module, completed))

@bp.route('/lessons/<int:lesson_id>')
@login_required
def lesson(lesson_id):
    student_only()
    current_lesson = Lesson.query.get_or_404(lesson_id)
    if not current_lesson.published or not current_lesson.module.published:
        abort(404)
    lessons = [item for item in current_lesson.module.lessons if item.published]
    position = lessons.index(current_lesson)
    completed = Progress.query.filter_by(user_id=current_user.id, lesson_id=current_lesson.id).first()
    completed_ids = {record.lesson_id for record in current_user.progress_records}
    return render_template('student/lesson.html', lesson=current_lesson, module=current_lesson.module, previous=lessons[position - 1] if position else None, next_lesson=lessons[position + 1] if position + 1 < len(lessons) else None, completed=completed, progress=module_progress(current_lesson.module, completed_ids))

@bp.post('/lessons/<int:lesson_id>/complete')
@login_required
def complete_lesson(lesson_id):
    student_only()
    current_lesson = Lesson.query.get_or_404(lesson_id)
    if not current_lesson.published or not current_lesson.module.published:
        abort(404)
    if not Progress.query.filter_by(user_id=current_user.id, lesson_id=current_lesson.id).first():
        db.session.add(Progress(user_id=current_user.id, lesson_id=current_lesson.id))
        db.session.commit()
        flash('Lesson completed successfully. Your learning progress has been updated.', 'success')
    else:
        flash('This lesson was already marked as complete.', 'info')
    return redirect(url_for('student.lesson', lesson_id=current_lesson.id))

@bp.route('/modules/<slug>/quiz', methods=['GET', 'POST'])
@login_required
def quiz(slug):
    student_only()
    current_module = Module.query.filter_by(slug=slug, published=True).first_or_404()
    available = Question.query.filter_by(module_id=current_module.id, active=True).all()
    if not available:
        flash('This module does not have an active quiz yet.', 'warning')
        return redirect(url_for('student.module', slug=slug))
    key = f'quiz-{current_module.id}'
    if request.method == 'POST':
        state = session.pop(key, None)
        if not state or request.form.get('submission_token') != state['token']:
            flash('This quiz submission has already been processed or has expired. Start a new attempt.', 'warning')
            return redirect(url_for('student.quiz', slug=current_module.slug))
        elapsed = min(QUIZ_SECONDS, max(0, int(datetime.now(timezone.utc).timestamp() - state['started_at'])))
        selected_questions = Question.query.filter(Question.id.in_(state['question_ids'])).all()
        by_id = {question.id: question for question in selected_questions}
        ordered = [by_id[item_id] for item_id in state['question_ids'] if item_id in by_id]
        attempt = QuizAttempt(user_id=current_user.id, module_id=current_module.id, score=0, total_questions=len(ordered), percentage=0, passed=False, started_at=datetime.fromtimestamp(state['started_at']), duration_seconds=elapsed)
        db.session.add(attempt); db.session.flush(); correct = 0
        for question in ordered:
            selected = request.form.get(f'q_{question.id}')
            is_correct = selected == question.correct_option; correct += is_correct
            db.session.add(QuizAnswer(attempt_id=attempt.id, question_id=question.id, selected_option=selected, is_correct=is_correct))
        attempt.score = correct; attempt.percentage = round(correct / len(ordered) * 100, 2); attempt.passed = attempt.percentage >= PASS_MARK
        db.session.commit(); return redirect(url_for('student.result', attempt_id=attempt.id))
    questions = sample(available, len(available))
    token = token_urlsafe(24); started_at = int(datetime.now(timezone.utc).timestamp())
    session[key] = {'token': token, 'started_at': started_at, 'question_ids': [question.id for question in questions]}
    return render_template('student/quiz.html', module=current_module, questions=questions, token=token, quiz_seconds=QUIZ_SECONDS)

@bp.route('/results/<int:attempt_id>')
@login_required
def result(attempt_id):
    student_only()
    attempt = QuizAttempt.query.get_or_404(attempt_id)
    if attempt.user_id != current_user.id:
        abort(403)
    message = 'Excellent work — you demonstrated solid understanding.' if attempt.passed else 'Review the explanations, revisit the lesson, then try again when ready.'
    return render_template('student/result.html', attempt=attempt, incorrect=attempt.total_questions-attempt.score, message=message)

@bp.route('/history')
@login_required
def history():
    student_only()
    module_id = request.args.get('module', type=int)
    query = QuizAttempt.query.filter_by(user_id=current_user.id)
    if module_id: query = query.filter_by(module_id=module_id)
    return render_template('student/history.html', attempts=query.order_by(QuizAttempt.submitted_at.desc()).all(), modules=Module.query.filter_by(published=True).all(), selected_module=module_id)

@bp.route('/certificate')
@login_required
def certificate():
    student_only()
    if not eligible(current_user):
        flash('Complete every published lesson and pass each module quiz to unlock your certificate.', 'warning')
        return redirect(url_for('student.dashboard'))
    cert = Certificate.query.filter_by(user_id=current_user.id).first()
    if not cert:
        cert = Certificate(user_id=current_user.id); db.session.add(cert); db.session.commit()
    return render_template('student/certificate.html', cert=cert)

@bp.route('/feedback', methods=['GET', 'POST'])
@login_required
def feedback():
    student_only(); form = FeedbackForm()
    if form.validate_on_submit():
        db.session.add(Feedback(user_id=current_user.id, rating=form.rating.data, message=form.message.data.strip())); db.session.commit()
        flash('Feedback received. Thank you for helping improve NetWise.', 'success'); return redirect(url_for('student.feedback'))
    return render_template('student/form.html', form=form, title='Share feedback', intro='Tell us what worked well and what could be clearer.')

@bp.route('/survey', methods=['GET', 'POST'])
@login_required
def survey():
    student_only()
    if SurveyResponse.query.filter_by(user_id=current_user.id).first():
        flash('You have already completed the learning survey.', 'info'); return redirect(url_for('student.dashboard'))
    form = SurveyForm(); form.useful_module_id.choices = [(module.id, module.title) for module in Module.query.filter_by(published=True).all()]
    if form.validate_on_submit():
        db.session.add(SurveyResponse(user_id=current_user.id, overall_experience=form.overall_experience.data, ease_of_understanding=form.ease_of_understanding.data, useful_module_id=form.useful_module_id.data, confidence_improvement=form.confidence_improvement.data, difficulty=form.difficulty.data, suggestions=form.suggestions.data)); db.session.commit()
        flash('Survey submitted. Thank you for your thoughtful response.', 'success'); return redirect(url_for('student.dashboard'))
    return render_template('student/form.html', form=form, title='Learning survey', intro='Your answers help us assess and improve this course.')

class ProfileForm(FlaskForm):
    full_name = TextAreaField('Full name', validators=[DataRequired(), Length(max=120)])
    submit = SubmitField('Save profile')

@bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    student_only(); form = ProfileForm(obj=current_user)
    if form.validate_on_submit():
        current_user.full_name = form.full_name.data.strip(); db.session.commit(); flash('Your profile was updated.', 'success'); return redirect(url_for('student.profile'))
    done, total, percent = completion(current_user); attempts = QuizAttempt.query.filter_by(user_id=current_user.id).all()
    return render_template('student/profile.html', form=form, done=done, total=total, percent=percent, attempts=attempts, average=round(sum(item.percentage for item in attempts)/len(attempts), 1) if attempts else None, best=max((item.percentage for item in attempts), default=None), certificate=Certificate.query.filter_by(user_id=current_user.id).first())
