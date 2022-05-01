# from email.policy import default
from datetime import datetime, timedelta
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from flask_login import current_user
import app.time_util as time_util
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
    # dept = StringField('Dept Code', validators=[DataRequired(), Length(min=4, max=4)])
    all_depts = Department.query.all()
    list_of_depts=[]
    for each_dept in all_depts:
        list_of_depts.append(each_dept.dept_code + "    -    " + each_dept.dept_name)
    dept = SelectField('Dept Code', choices=list_of_depts, validators=[DataRequired()])
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
    start_date = DateTimeLocalField('Election Start Date', default=time_util.hour_rounder(datetime.now()), format='%Y-%m-%dT%H:%M', validators=[DataRequired()])
    end_date = DateTimeLocalField('Election End Date', format='%Y-%m-%dT%H:%M', validators=[DataRequired()])
    public_key = StringField('Public Key', render_kw={'readonly': True})
    private_key = StringField('Private Key', render_kw={'readonly': True})
    max_attempt = IntegerField('Max Retries Allowed', default=3, validators=[DataRequired(), NumberRange(min=3, max=10)])
    submit = SubmitField('Save and Proceed to Generate Voter List')
    generate_keys = SubmitField('Generate New Key Pair')
    home = SubmitField("Home")
    end_election = SubmitField("End Election")
    start_counting = SubmitField("Start Counting Process")
    delete_election = SubmitField("Delete Election")
    publish_results = SubmitField("Publish Results")

    def validate_start_date(self, start_date):
        if start_date.data >= self.end_date.data:
            raise ValidationError('Start date/time cannot be greater than End date/time!')
        if start_date.data <= datetime.now():
            raise ValidationError('New elections can only be set for future.')
    
    def validate_end_date(self, end_date):
        if end_date.data <= datetime.now():
            raise ValidationError('End date/time must be greater than Current date/time!')

# class GenVoterListForm(FlaskForm):
#     all_depts = Department.query.all()
#     list_of_depts = []
#     for each_dept in all_depts:
#         list_of_depts.append(each_dept.dept_code + "    -    " + each_dept.dept_name)
#     dept = SelectField('Dept Code', choices=list_of_depts, validators=[DataRequired()])
#     # After selecting dept, the year field will automatically have those years which contain students
#     # from that particular department (dept). The Oracle SQL query would be:
#     # SELECT DISTINCT join_year FROM voter WHERE dept_id=dept.value
#     # I was not able to extract the data from the dept field, wanted to do something like...
#     # all_years = Voter.query.with_entities(Voter.join_year).filter(Voter.dept == dept.value[0:4]).distinct()
#     all_years = Voter.query.with_entities(Voter.join_year).filter(Voter.dept == 'BAGG').distinct() #works for hardcoded dept only
#     list_of_years = []
#     for each_year in all_years:
#         list_of_years.append(each_year.join_year)
#     join_year = SelectField('Join Year', choices=list_of_years, validators=[DataRequired()])
#     submit = SubmitField('Choose Voters')

class NewAdminForm(FlaskForm):
    cin = StringField('CIN', validators=[DataRequired()])
    name = StringField('Name', validators=[DataRequired(), Length(min=3, max=255)])
    # username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    all_depts = Department.query.all()
    list_of_depts=[]
    for each_dept in all_depts:
        list_of_depts.append(each_dept.dept_code + "    -    " + each_dept.dept_name)
    dept = SelectField('Dept Code', choices=list_of_depts, validators=[DataRequired()])
    # dept = StringField('Dept Code', validators=[DataRequired(), Length(min=4, max=4)])
    join_year = IntegerField('Join Year', validators=[DataRequired(), NumberRange(min=2016, max=2020)])
    is_admin = RadioField('Is Admin?', coerce=int, choices=[(1,'Yes'), (0,'No')])
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