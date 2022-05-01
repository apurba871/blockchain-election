from flask import url_for,redirect, abort
from flask_login import current_user
from app.models import Voter
from permission import Rule

# Rule to check if any user is currently logged in or not
class UserRule(Rule):
  def check(self):
    # Check if there is an user already logged in
    return current_user.is_authenticated
  
  def deny(self):
    # If the user is not logged in, redirect to the login page
    return redirect(url_for("login"))

# Rule to check if an user is an admin user
class AdminRule(Rule):
  def base(self):
    return UserRule()

  def check(self):
    user_id = current_user.id
    user = Voter.query.filter(Voter.id == user_id).first()
    return user and user.is_admin
  
  def deny(self):
    abort(403)