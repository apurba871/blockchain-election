from flask import render_template, url_for, flash, redirect, request
from app import app, db, bcrypt
from app.models import Voter, Candidate, Election, Casted_Vote, Voter_List, Department
from app.forms import RegistrationForm, LoginForm
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
        if user and bcrypt.check_password_hash(user.password, form.password.data):
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

@app.route("/account")
@login_required
def account():
    image_file = url_for('static', filename='profile_pics/' + current_user.imagefile)
    return render_template("account.html", title="Account", image_file = image_file)

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