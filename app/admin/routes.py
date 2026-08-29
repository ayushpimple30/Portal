from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import login_required
from flask_wtf import FlaskForm
from wtforms import BooleanField, IntegerField, SelectField, StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Length, NumberRange, URL
from sqlalchemy import func
from ..extensions import db
from ..models import ContactMessage, Feedback, Lesson, Module, Question, QuizAttempt, SurveyResponse, User
from ..utils import admin_required
bp=Blueprint('admin',__name__,url_prefix='/admin')
class ModuleForm(FlaskForm):
 title=StringField('Title',validators=[DataRequired(),Length(max=160)]);slug=StringField('URL slug',validators=[DataRequired(),Length(max=180)]);description=TextAreaField('Description',validators=[DataRequired()]);content=TextAreaField('Module overview',validators=[DataRequired()]);video_url=StringField('Video URL',validators=[Length(max=500)]);estimated_minutes=IntegerField('Estimated minutes',validators=[DataRequired(),NumberRange(1,600)]);display_order=IntegerField('Display order',validators=[DataRequired(),NumberRange(0,999)]);published=BooleanField('Published');submit=SubmitField('Save module')
class LessonForm(FlaskForm): title=StringField('Title',validators=[DataRequired()]);content=TextAreaField('Content',validators=[DataRequired()]);key_points=TextAreaField('Key points');safety_tip=TextAreaField('Safety tip');display_order=IntegerField('Order',validators=[DataRequired(),NumberRange(0,999)]);submit=SubmitField('Save lesson')
class QuestionForm(FlaskForm):
 module_id=SelectField('Module',coerce=int,validators=[DataRequired()]);prompt=TextAreaField('Question',validators=[DataRequired()]);option_a=StringField('Option A',validators=[DataRequired()]);option_b=StringField('Option B',validators=[DataRequired()]);option_c=StringField('Option C',validators=[DataRequired()]);option_d=StringField('Option D',validators=[DataRequired()]);correct_option=SelectField('Correct option',choices=[('A','A'),('B','B'),('C','C'),('D','D')]);explanation=TextAreaField('Explanation',validators=[DataRequired()]);difficulty=SelectField('Difficulty',choices=[('Beginner','Beginner'),('Intermediate','Intermediate'),('Advanced','Advanced')]);active=BooleanField('Active');submit=SubmitField('Save question')
def page(query): return query.paginate(page=request.args.get('page',1,type=int),per_page=10,error_out=False)
def choices(form):form.module_id.choices=[(m.id,m.title) for m in Module.query.order_by(Module.display_order)]
@bp.route('/')
@login_required
@admin_required
def dashboard():
 attempts = QuizAttempt.query.all()
 stats = {'students': User.query.filter_by(role='STUDENT').count(), 'modules': Module.query.count(), 'lessons': Lesson.query.count(), 'questions': Question.query.count(), 'attempts': len(attempts), 'feedback': Feedback.query.count(), 'unread': ContactMessage.query.filter_by(status='unread').count()}
 stats['average'] = round(sum(a.percentage for a in attempts) / len(attempts), 1) if attempts else 0
 total_lessons = Lesson.query.filter_by(published=True).count()
 completed = __import__('app.models', fromlist=['Progress']).Progress.query.count()
 stats['completion_rate'] = round(completed / (total_lessons * stats['students']) * 100, 1) if total_lessons and stats['students'] else 0
 module_labels = []; module_completion = []; module_scores = []
 for module in Module.query.order_by(Module.display_order):
  module_labels.append(module.title); possible = len(module.lessons) * stats['students']; module_completion.append(round(__import__('app.models', fromlist=['Progress']).Progress.query.join(Lesson).filter(Lesson.module_id == module.id).count() / possible * 100, 1) if possible else 0)
  scores = [a.percentage for a in attempts if a.module_id == module.id]; module_scores.append(round(sum(scores) / len(scores), 1) if scores else 0)
 ratings = [Feedback.query.filter_by(rating=value).count() for value in range(1, 6)]
 return render_template('admin/dashboard.html', stats=stats, chart_data={'labels': module_labels, 'completion': module_completion, 'scores': module_scores, 'ratings': ratings})
@bp.route('/students')
@login_required
@admin_required
def students():
 q=request.args.get('q','').strip();sort=request.args.get('sort','created_at');column=getattr(User,sort,User.created_at);query=User.query.filter_by(role='STUDENT');query=query.filter((User.full_name.ilike(f'%{q}%'))|(User.email.ilike(f'%{q}%'))) if q else query;return render_template('admin/students.html',students=page(query.order_by(column.desc())),q=q)
@bp.post('/students/<int:user_id>/toggle')
@login_required
@admin_required
def toggle_student(user_id):
 user=User.query.filter_by(id=user_id,role='STUDENT').first_or_404();user.is_active=not user.is_active;db.session.commit();flash('Student account status updated.','success');return redirect(url_for('admin.students'))
@bp.route('/modules')
@login_required
@admin_required
def modules(): return render_template('admin/modules.html',modules=Module.query.order_by(Module.display_order).all())
@bp.route('/modules/new',methods=['GET','POST'])
@login_required
@admin_required
def module_new(): return module_edit(None)
@bp.route('/modules/<int:module_id>/edit',methods=['GET','POST'])
@login_required
@admin_required
def module_edit(module_id):
 obj=Module.query.get(module_id) if module_id else Module();form=ModuleForm(obj=obj)
 if form.validate_on_submit():
  duplicate=Module.query.filter(Module.slug==form.slug.data.strip(),Module.id!=obj.id).first()
  if duplicate:form.slug.errors.append('This slug is already used.')
  else:
   form.populate_obj(obj);obj.slug=obj.slug.strip().lower();db.session.add(obj);db.session.commit();flash('Module saved.','success');return redirect(url_for('admin.modules'))
 return render_template('admin/entity_form.html',form=form,title='Edit module' if module_id else 'Create module')
@bp.post('/modules/<int:module_id>/delete')
@login_required
@admin_required
def module_delete(module_id): db.session.delete(Module.query.get_or_404(module_id));db.session.commit();flash('Module deleted.','success');return redirect(url_for('admin.modules'))
@bp.route('/modules/<int:module_id>/lessons/new',methods=['GET','POST'])
@login_required
@admin_required
def lesson_new(module_id): return lesson_edit(module_id, None)
@bp.route('/modules/<int:module_id>/lessons/<int:lesson_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def lesson_edit(module_id, lesson_id):
 module=Module.query.get_or_404(module_id); obj=Lesson.query.filter_by(id=lesson_id, module_id=module.id).first_or_404() if lesson_id else Lesson(module_id=module.id); form=LessonForm(obj=obj)
 if form.validate_on_submit():
  form.populate_obj(obj); db.session.add(obj); db.session.commit(); flash('Lesson saved.', 'success'); return redirect(url_for('admin.modules'))
 return render_template('admin/entity_form.html', form=form, title=('Edit lesson — ' if lesson_id else 'Add lesson — ') + module.title)
@bp.post('/lessons/<int:lesson_id>/delete')
@login_required
@admin_required
def lesson_delete(lesson_id):
 db.session.delete(Lesson.query.get_or_404(lesson_id)); db.session.commit(); flash('Lesson deleted.', 'success'); return redirect(url_for('admin.modules'))
@bp.route('/questions')
@login_required
@admin_required
def questions(): return render_template('admin/questions.html',questions=page(Question.query.order_by(Question.created_at.desc())))
@bp.route('/questions/new',methods=['GET','POST'])
@login_required
@admin_required
def question_new(): return question_edit(None)
@bp.route('/questions/<int:question_id>/edit',methods=['GET','POST'])
@login_required
@admin_required
def question_edit(question_id):
 obj=Question.query.get(question_id) if question_id else Question();form=QuestionForm(obj=obj);choices(form)
 if form.validate_on_submit():form.populate_obj(obj);db.session.add(obj);db.session.commit();flash('Question saved.','success');return redirect(url_for('admin.questions'))
 return render_template('admin/entity_form.html',form=form,title='Edit question' if question_id else 'Add question')
@bp.post('/questions/<int:question_id>/delete')
@login_required
@admin_required
def question_delete(question_id):db.session.delete(Question.query.get_or_404(question_id));db.session.commit();flash('Question deleted.','success');return redirect(url_for('admin.questions'))
@bp.route('/attempts')
@login_required
@admin_required
def attempts():return render_template('admin/attempts.html',attempts=page(QuizAttempt.query.order_by(QuizAttempt.submitted_at.desc())))
@bp.route('/feedback')
@login_required
@admin_required
def feedback():return render_template('admin/feedback.html',feedback=page(Feedback.query.order_by(Feedback.created_at.desc())),surveys=SurveyResponse.query.order_by(SurveyResponse.created_at.desc()).all())
@bp.route('/contacts')
@login_required
@admin_required
def contacts():
 q=request.args.get('q','');query=ContactMessage.query;query=query.filter((ContactMessage.name.ilike(f'%{q}%'))|(ContactMessage.subject.ilike(f'%{q}%'))) if q else query;return render_template('admin/contacts.html',contacts=page(query.order_by(ContactMessage.created_at.desc())),q=q)
@bp.post('/contacts/<int:message_id>/<status>')
@login_required
@admin_required
def contact_status(message_id,status):
 if status not in ('read','resolved'):return redirect(url_for('admin.contacts'))
 msg=ContactMessage.query.get_or_404(message_id);msg.status=status;db.session.commit();return redirect(url_for('admin.contacts'))
@bp.post('/contacts/<int:message_id>/delete')
@login_required
@admin_required
def contact_delete(message_id):db.session.delete(ContactMessage.query.get_or_404(message_id));db.session.commit();flash('Contact message deleted.','success');return redirect(url_for('admin.contacts'))

@bp.route('/students/<int:user_id>')
@login_required
@admin_required
def student_detail(user_id):
    student = User.query.filter_by(id=user_id, role='STUDENT').first_or_404()
    completed = {record.lesson_id for record in student.progress_records}
    modules_data = []
    for module in Module.query.order_by(Module.display_order):
        lesson_ids = [lesson.id for lesson in module.lessons if lesson.published]
        done = sum(item in completed for item in lesson_ids)
        modules_data.append((module, done, len(lesson_ids), round(done / len(lesson_ids) * 100) if lesson_ids else 0))
    attempts = QuizAttempt.query.filter_by(user_id=student.id).order_by(QuizAttempt.submitted_at.desc()).all()
    return render_template('admin/student_detail.html', student=student, modules_data=modules_data, attempts=attempts, average=round(sum(item.percentage for item in attempts) / len(attempts), 1) if attempts else None, best=max((item.percentage for item in attempts), default=None), certificate=__import__('app.models', fromlist=['Certificate']).Certificate.query.filter_by(user_id=student.id).first())
