from datetime import datetime
from flask import Blueprint, abort, flash, redirect, render_template, url_for
from flask_login import current_user, login_required
from flask_wtf import FlaskForm
from wtforms import IntegerField, SelectField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, NumberRange, Optional, Length
from ..extensions import db
from ..models import Certificate, Feedback, Lesson, Module, Progress, Question, QuizAnswer, QuizAttempt, SurveyResponse
from ..utils import completion, eligible
bp=Blueprint('student',__name__,url_prefix='/learn')
class FeedbackForm(FlaskForm): rating=IntegerField('Rating (1–5)',validators=[DataRequired(),NumberRange(1,5)]);message=TextAreaField('Feedback',validators=[DataRequired(),Length(max=3000)]);submit=SubmitField('Send feedback')
class SurveyForm(FlaskForm):
 overall_experience=IntegerField('Overall experience (1–5)',validators=[DataRequired(),NumberRange(1,5)]);ease_of_understanding=IntegerField('Ease of understanding (1–5)',validators=[DataRequired(),NumberRange(1,5)]);useful_module_id=SelectField('Most useful module',coerce=int,validators=[DataRequired()]);confidence_improvement=IntegerField('Confidence improvement (1–5)',validators=[DataRequired(),NumberRange(1,5)]);difficulty=SelectField('Difficulty',choices=[('Too easy','Too easy'),('Appropriate','Appropriate'),('Challenging','Challenging')]);suggestions=TextAreaField('Suggestions',validators=[Optional(),Length(max=3000)]);submit=SubmitField('Submit survey')
def student_only():
 if current_user.is_admin: abort(403)
@bp.route('/dashboard')
@login_required
def dashboard():
 student_only(); done,total,pct=completion(current_user); attempts=QuizAttempt.query.filter_by(user_id=current_user.id).order_by(QuizAttempt.submitted_at.desc()).all(); completed_lessons={p.lesson_id for p in current_user.progress_records}; next_lesson=Lesson.query.filter(~Lesson.id.in_(completed_lessons)).join(Module).filter(Module.published.is_(True)).order_by(Module.display_order,Lesson.display_order).first() if completed_lessons else Lesson.query.join(Module).filter(Module.published.is_(True)).order_by(Module.display_order,Lesson.display_order).first()
 return render_template('student/dashboard.html',done=done,total=total,pct=pct,attempts=attempts,next_lesson=next_lesson,certificate=eligible(current_user))
@bp.route('/modules')
@login_required
def modules(): student_only(); return render_template('student/modules.html',modules=Module.query.filter_by(published=True).order_by(Module.display_order).all(),completed={p.lesson_id for p in current_user.progress_records})
@bp.route('/modules/<slug>')
@login_required
def module(slug):
 student_only(); module=Module.query.filter_by(slug=slug,published=True).first_or_404(); completed={p.lesson_id for p in current_user.progress_records}; return render_template('student/module.html',module=module,completed=completed)
@bp.route('/lessons/<int:lesson_id>')
@login_required
def lesson(lesson_id):
 student_only(); lesson=Lesson.query.get_or_404(lesson_id); module=lesson.module
 if not module.published: abort(404)
 ordered=module.lessons; i=ordered.index(lesson); return render_template('student/lesson.html',lesson=lesson,module=module,previous=ordered[i-1] if i else None,next_lesson=ordered[i+1] if i+1<len(ordered) else None,completed=Progress.query.filter_by(user_id=current_user.id,lesson_id=lesson.id).first())
@bp.post('/lessons/<int:lesson_id>/complete')
@login_required
def complete_lesson(lesson_id):
 student_only(); lesson=Lesson.query.get_or_404(lesson_id)
 if not Progress.query.filter_by(user_id=current_user.id,lesson_id=lesson.id).first(): db.session.add(Progress(user_id=current_user.id,lesson_id=lesson.id)); db.session.commit(); flash('Lesson marked complete. Your progress is updated.','success')
 return redirect(url_for('student.lesson',lesson_id=lesson.id))
@bp.route('/modules/<slug>/quiz',methods=['GET','POST'])
@login_required
def quiz(slug):
 student_only(); module=Module.query.filter_by(slug=slug,published=True).first_or_404(); questions=Question.query.filter_by(module_id=module.id,active=True).order_by(Question.id).all()
 if not questions: flash('This module has no active quiz questions yet.','warning'); return redirect(url_for('student.module',slug=slug))
 if __import__('flask').request.method=='POST':
  correct=0; attempt=QuizAttempt(user_id=current_user.id,module_id=module.id,score=0,total_questions=len(questions),percentage=0,passed=False); db.session.add(attempt); db.session.flush()
  for q in questions:
   answer=__import__('flask').request.form.get(f'q_{q.id}'); ok=answer==q.correct_option; correct+=ok; db.session.add(QuizAnswer(attempt_id=attempt.id,question_id=q.id,selected_option=answer,is_correct=ok))
  attempt.score=correct; attempt.percentage=round(correct/len(questions)*100,2); attempt.passed=attempt.percentage>=70; db.session.commit(); return redirect(url_for('student.result',attempt_id=attempt.id))
 return render_template('student/quiz.html',module=module,questions=questions)
@bp.route('/results/<int:attempt_id>')
@login_required
def result(attempt_id):
 student_only(); attempt=QuizAttempt.query.get_or_404(attempt_id)
 if attempt.user_id!=current_user.id: abort(403)
 return render_template('student/result.html',attempt=attempt)
@bp.route('/history')
@login_required
def history(): student_only(); return render_template('student/history.html',attempts=QuizAttempt.query.filter_by(user_id=current_user.id).order_by(QuizAttempt.submitted_at.desc()).all())
@bp.route('/certificate')
@login_required
def certificate():
 student_only()
 if not eligible(current_user): flash('Complete every lesson and pass each module quiz to unlock your certificate.','warning'); return redirect(url_for('student.dashboard'))
 cert=Certificate.query.filter_by(user_id=current_user.id).first()
 if not cert: cert=Certificate(user_id=current_user.id);db.session.add(cert);db.session.commit()
 return render_template('student/certificate.html',cert=cert)
@bp.route('/feedback',methods=['GET','POST'])
@login_required
def feedback():
 student_only();form=FeedbackForm()
 if form.validate_on_submit(): db.session.add(Feedback(user_id=current_user.id,rating=form.rating.data,message=form.message.data.strip()));db.session.commit();flash('Feedback received. Thank you.','success');return redirect(url_for('student.feedback'))
 return render_template('student/form.html',form=form,title='Share feedback',intro='Help us improve the learning experience.')
@bp.route('/survey',methods=['GET','POST'])
@login_required
def survey():
 student_only()
 if SurveyResponse.query.filter_by(user_id=current_user.id).first(): flash('You have already completed the learning survey.','info');return redirect(url_for('student.dashboard'))
 form=SurveyForm();form.useful_module_id.choices=[(m.id,m.title) for m in Module.query.filter_by(published=True).all()]
 if form.validate_on_submit(): db.session.add(SurveyResponse(user_id=current_user.id,overall_experience=form.overall_experience.data,ease_of_understanding=form.ease_of_understanding.data,useful_module_id=form.useful_module_id.data,confidence_improvement=form.confidence_improvement.data,difficulty=form.difficulty.data,suggestions=form.suggestions.data));db.session.commit();flash('Survey submitted. Thank you.','success');return redirect(url_for('student.dashboard'))
 return render_template('student/form.html',form=form,title='Learning survey',intro='Tell us how the course worked for you.')
