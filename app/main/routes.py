from flask import Blueprint, render_template, request, flash, redirect, url_for, Response
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Email, Length
from ..extensions import db
from ..models import ContactMessage, Module
bp=Blueprint('main',__name__)
class ContactForm(FlaskForm):
 name=StringField('Name',validators=[DataRequired(),Length(max=120)]);email=StringField('Email',validators=[DataRequired(),Email()]);subject=StringField('Subject',validators=[DataRequired(),Length(max=180)]);message=TextAreaField('Message',validators=[DataRequired(),Length(max=5000)]);submit=SubmitField('Send message')
@bp.route('/')
def home(): return render_template('main/home.html',modules=Module.query.filter_by(published=True).order_by(Module.display_order).all())
@bp.route('/contact',methods=['GET','POST'])
def contact():
 form=ContactForm()
 if form.validate_on_submit():
  db.session.add(ContactMessage(name=form.name.data.strip(),email=form.email.data.lower().strip(),subject=form.subject.data.strip(),message=form.message.data.strip())); db.session.commit(); flash('Thanks — your message has been sent.','success'); return redirect(url_for('main.contact'))
 return render_template('main/contact.html',form=form)
@bp.route('/robots.txt')
def robots(): return Response('User-agent: *\nAllow: /\n',mimetype='text/plain')
@bp.route('/sitemap.xml')
def sitemap(): return Response(render_template('main/sitemap.xml',modules=Module.query.filter_by(published=True).all()),mimetype='application/xml')
