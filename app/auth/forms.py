from flask_wtf import FlaskForm
from wtforms import BooleanField, PasswordField, StringField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Length
class RegisterForm(FlaskForm):
 full_name=StringField('Full name',validators=[DataRequired(),Length(max=120)]); email=StringField('Email',validators=[DataRequired(),Email(),Length(max=254)]); password=PasswordField('Password',validators=[DataRequired(),Length(min=8,max=128)]); confirm_password=PasswordField('Confirm password',validators=[DataRequired(),EqualTo('password')]); submit=SubmitField('Create account')
class LoginForm(FlaskForm):
 email=StringField('Email',validators=[DataRequired(),Email()]); password=PasswordField('Password',validators=[DataRequired()]); remember=BooleanField('Remember me'); submit=SubmitField('Sign in')
