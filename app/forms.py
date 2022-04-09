from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from app.models import Voter

class RegistrationForm(FlaskForm):
    cin = StringField('CIN', validators=[DataRequired()])
    name = StringField('Name', validators=[DataRequired(), Length(min=3, max=255)])
    # username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    dept = StringField('Dept Code', validators=[DataRequired(), Length(min=4, max=4)])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

    def validate_cin(self, cin):
        user = Voter.query.filter_by(cin=cin.data).first()
        if user:
            raise ValidationError('That CIN is already in use. Please choose a different one.')
    
    def validate_email(self, email):
        user = Voter.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('That Email is taken. Please choose a different one.')

class LoginForm(FlaskForm):
    # username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    cin = StringField('CIN', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')