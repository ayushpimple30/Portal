from flask import Blueprint, flash, redirect, render_template, url_for
from flask_login import current_user, login_user, logout_user
from ..extensions import db
from ..models import User
from .forms import LoginForm, RegisterForm
bp=Blueprint('auth',__name__,url_prefix='/auth')
@bp.route('/register',methods=['GET','POST'])
def register():
 if current_user.is_authenticated:return redirect(url_for('main.home'))
 form=RegisterForm()
 if form.validate_on_submit():
  email=form.email.data.lower().strip()
  if User.query.filter_by(email=email).first(): form.email.errors.append('An account with this email already exists.')
  else:
   user=User(full_name=form.full_name.data.strip(),email=email); user.set_password(form.password.data); db.session.add(user); db.session.commit(); flash('Your account is ready. Please sign in.','success'); return redirect(url_for('auth.login'))
 return render_template('auth/register.html',form=form)
@bp.route('/login',methods=['GET','POST'])
def login():
 if current_user.is_authenticated:return redirect(url_for('admin.dashboard' if current_user.is_admin else 'student.dashboard'))
 form=LoginForm()
 if form.validate_on_submit():
  user=User.query.filter_by(email=form.email.data.lower().strip()).first()
  if not user or not user.check_password(form.password.data) or not user.is_active: flash('Invalid email or password.','danger')
  else: login_user(user,remember=form.remember.data); return redirect(url_for('admin.dashboard' if user.is_admin else 'student.dashboard'))
 return render_template('auth/login.html',form=form)
@bp.post('/logout')
def logout(): logout_user(); flash('You have been signed out.','success'); return redirect(url_for('main.home'))
