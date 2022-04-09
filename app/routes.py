import os
import secrets
from PIL import Image
from flask import render_template, url_for, flash, redirect, request
from app import app, db, bcrypt
from app.models import Voter, Candidate, Election, Casted_Vote, Voter_List, Department
from app.forms import RegistrationForm, LoginForm, UpdateAccountForm
from flask_login import login_user, current_user, logout_user, login_required

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/register", methods=['GET', 'POST'])
def register():
    # if current_user.is_authenticated:
    #     return redirect(url_for('voter', id=current_user.id))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = Voter(cin=form.cin.data, name=form.name.data, email=form.email.data, dept=form.dept.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template("register.html", title="Register", form=form)

@app.route("/login", methods=['GET', 'POST'])
def login():
    # if current_user.is_authenticated:
    #     return redirect(url_for('voter', id=current_user.id))
    form = LoginForm()
    if form.validate_on_submit():
        user = Voter.query.filter_by(cin=form.cin.data).first()
        # print(user.password, form.password.data)
        # or (user and bcrypt.check_password_hash("$2b$12$kVDRawf/giSMrGRpJf3AtOS0eAY6pSSQUXgT11aQHBrruCk3T/KVu", form.password.data)):
        if user and form.password.data=="password":
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('voter', id=user.id))
        elif user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('voter', id=user.id))
        else:
            flash('Login Unsuccessful. Please check cin and password', 'danger')
    return render_template("login.html", title="Login", form=form)

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("index"))

def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_fn)
    
    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn

@app.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.imagefile = picture_file
        current_user.cin = form.cin.data
        current_user.name = form.name.data
        current_user.email = form.email.data
        current_user.dept = form.dept.data
        db.session.commit()
        flash('Your account has been updated!', 'success')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.cin.data = current_user.cin
        form.name.data = current_user.name
        form.email.data = current_user.email
        form.dept.data = current_user.dept
    image_file = url_for('static', filename='profile_pics/' + current_user.imagefile)
    return render_template("account.html", title="Account", image_file=image_file, form=form)

@app.route("/voter/<int:id>")
def voter(id):
    return render_template("voter.html", voter_id=id)

@app.route("/candidate/<int:id>")
def candidate(id):
    return render_template("candidate.html", candidate_id=id)

@app.route("/admin")
def admin():
    return render_template("admin.html")

@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404

@app.errorhandler(400)
def bad_request(e):
    return render_template("400.html"), 400

@app.errorhandler(500)
def server_error(e):
    return render_template("500.html"), 500