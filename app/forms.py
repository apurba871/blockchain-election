# from email.policy import default
from datetime import datetime
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from flask_login import current_user
from wtforms import StringField, PasswordField, SubmitField, BooleanField, SelectField, DateTimeLocalField, IntegerField, RadioField
# from wtforms.fields import DateTimeField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError, NumberRange
from app.models import Department, Voter
from wtforms_sqlalchemy.fields import QuerySelectField

class RegistrationForm(FlaskForm):
    cin = StringField('CIN', validators=[DataRequired()])
    name = StringField('Name', validators=[DataRequired(), Length(min=3, max=255)])
    # username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    dept = StringField('Dept Code', validators=[DataRequired(), Length(min=4, max=4)])
    join_year = IntegerField('Join Year', validators=[DataRequired(), NumberRange(min=2016, max=2020)])
    is_admin = False
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

class UpdateAccountForm(FlaskForm):
    cin = StringField('CIN', validators=[DataRequired()])
    name = StringField('Name', validators=[DataRequired(), Length(min=3, max=255)])
    # username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    dept = StringField('Dept Code', validators=[DataRequired(), Length(min=4, max=4)])
    picture = FileField('Update Profile Picture', validators=[FileAllowed(['jpg', 'png'])])
    submit = SubmitField('Update')

    def validate_cin(self, cin):
        if cin.data != current_user.cin:
            user = Voter.query.filter_by(cin=cin.data).first()
            if user:
                raise ValidationError('That CIN is already in use. Please choose a different one.')
    
    def validate_email(self, email):
        if email.data != current_user.email:
            user = Voter.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('That Email is taken. Please choose a different one.')

class NewElectionForm(FlaskForm):
    election_title = StringField('Election Title', validators=[DataRequired()])
    start_date = DateTimeLocalField('Election Start Date', default=datetime.now, format='%Y-%m-%dT%H:%M', validators=[DataRequired()])
    end_date = DateTimeLocalField('Election End Date', format='%Y-%m-%dT%H:%M', validators=[DataRequired()])
    public_key = StringField('Public Key', render_kw={'readonly': True})
    private_key = StringField('Private Key', render_kw={'readonly': True})
    max_attempt = IntegerField('Max Retries Allowed', validators=[DataRequired(), NumberRange(min=3, max=10)])
    submit = SubmitField('Save and Proceed to Generate Voter List')
    generate_keys = SubmitField('Generate New Key Pair')
    
    def validate_start_date(self, start_date):
        if start_date.data >= self.end_date.data:
            raise ValidationError('Start date/time cannot be greater than End date/time!')
        if start_date.data <= datetime.now():
            raise ValidationError('New elections can only be set for future.')
    
    def validate_end_date(self, end_date):
        if end_date.data <= datetime.now():
            raise ValidationError('End date/time must be greater than Current date/time!')

class GenVoterListForm(FlaskForm):
    # eligible_depts = [('CMSA', 'Computer Sc. Hons'), ('PHSA', 'Physics Hons')]
    eligible_depts = Department.query.all()
    department = QuerySelectField('Department', choices = eligible_depts, validators=[DataRequired()])
    # eligible_years = [('2016', '2016')]
    # year = SelectField('Year', choices = eligible_years, validators=[DataRequired()])

class NewAdminForm(FlaskForm):
    cin = StringField('CIN', validators=[DataRequired()])
    name = StringField('Name', validators=[DataRequired(), Length(min=3, max=255)])
    # username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    dept = StringField('Dept Code', validators=[DataRequired(), Length(min=4, max=4)])
    join_year = IntegerField('Join Year', validators=[DataRequired(), NumberRange(min=2016, max=2020)])
    is_admin = RadioField('Is Admin?', coerce=bool, choices=[(True,'Yes'), (False,'No')])
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