from flask import render_template, url_for, flash, redirect, request, abort
from flask_login import login_user, current_user, logout_user, login_required
from app import app, db, bcrypt
from app.models import Voter, Candidate, Election, Casted_Vote, Voter_List, Department
from app.forms import RegistrationForm, LoginForm, UpdateAccountForm, NewElectionForm, NewAdminForm, GenVoterListForm
from permission import Rule

# Rule to check if any user is currently logged in or not
class UserRule(Rule):
  def check(self):
    # Check if there is an user already logged in
    return current_user.is_authenticated
  
  def deny(self):
    # If the user is not logged in, redirect to the login page
    return redirect(url_for("/login"))

# Rule to check if an user is an admin user
class AdminRule(Rule):
  def base():
    return UserRule()

  def check():
    user_id = current_user.id
    user = Voter.query.filter(Voter.id == user_id).first()
    return user and user.is_admin
  
  def deny():
    abort(403)