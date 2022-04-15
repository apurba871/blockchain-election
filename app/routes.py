import os
import secrets
from PIL import Image
from flask import render_template, url_for, flash, redirect, request
from app import app, db, bcrypt
from app.models import Voter, Candidate, Election, Casted_Vote, Voter_List, Department
from app.forms import RegistrationForm, LoginForm, UpdateAccountForm, NewElectionForm, NewAdminForm
from flask_login import login_user, current_user, logout_user, login_required

@app.route("/register", methods=['GET', 'POST'])
def register():
    # if current_user.is_authenticated:
    #     return redirect(url_for('voter', id=current_user.id))
    # add another admin... todo
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = Voter(cin=form.cin.data, name=form.name.data, email=form.email.data, dept=form.dept.data, password=hashed_password, join_year=form.join_year.data, is_admin=False)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template("register.html", title="Register", form=form)

@app.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = Voter.query.filter_by(cin=form.cin.data).first()
        if user and user.is_admin: # Admin login
            login_user(user, remember=form.remember.data)
            flash("Logged in as admin!", "success")
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('admin'))
        else:
            if user and form.password.data=="password": # Already registered users login
                login_user(user, remember=form.remember.data)
                next_page = request.args.get('next')
                if next_page == "/election/new":
                    flash("Please login as admin to access this page", "danger")
                else:
                    return redirect(next_page) if next_page else redirect(url_for('voter', id=user.id))
            elif user and bcrypt.check_password_hash(user.password, form.password.data): # new users login
                login_user(user, remember=form.remember.data)
                next_page = request.args.get('next')
                if next_page == "/election/new":
                    flash("Please login as admin to access this page", "danger")
                else:
                    return redirect(next_page) if next_page else redirect(url_for('voter', id=user.id))
            else:
                flash('Login Unsuccessful. Please check CIN and Password', 'danger')
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

@app.route("/election/new", methods=['GET', 'POST'])
@login_required
def new_election():
    form = NewElectionForm()
    if request.method == 'GET':
        flash('Please Save the Private Key before proceeding.', 'info')
        form.public_key.data = secrets.token_urlsafe(16)
        form.private_key.data = secrets.token_urlsafe(16)
    # Validate the form on submit and check if submit button was clicked
    if form.validate_on_submit() and form.submit.data:
        num_elections = Election.query.count()
        election_id = num_elections + 1
        prefixed_election_id = 'E' + str(election_id)   
        new_election = Election(election_id=prefixed_election_id, 
                                election_title=form.election_title.data, 
                                start_date=form.start_date.data, 
                                end_date=form.end_date.data, 
                                public_key=form.public_key.data, 
                                max_attempt=form.max_attempt.data, 
                                election_state='upcoming')
        # print(new_election)
        db.session.add(new_election)
        db.session.commit()
        flash('Election Created Successfully!', 'success')
        return redirect(url_for('home'))
    return render_template("create_election.html", title="New Election", form=form)

@app.route("/election/<id>/view", methods=['GET', 'POST'])
@login_required
def view_election(id):
    curr_election = Election.query.where(Election.election_id==id).first()
    if curr_election.election_state == 'upcoming':
        bg_color_election_state = "bg-primary"
    elif curr_election.election_state == 'ongoing':
        bg_color_election_state = "bg-warning"
    elif curr_election.election_state == "over":
        bg_color_election_state = "bg-info"
    elif curr_election.election_state == "past":
        bg_color_election_state = "bg-success"
    # If the current user is admin and the election is an upcoming election
    if current_user.is_admin and curr_election.election_state == 'upcoming':
        form = NewElectionForm(obj=curr_election)
        if form.validate_on_submit():
            if form.submit.data:
                curr_election.election_title = form.election_title.data
                curr_election.start_date=form.start_date.data
                curr_election.max_attempt=form.max_attempt.data
                curr_election.public_key=form.public_key.data
                db.session.commit()
                flash('Election Modified Successfully!', 'success')
                return redirect(url_for('home'))
            elif form.generate_keys.data:
                print("generate_keys button was pressed")
                form.public_key.data = secrets.token_urlsafe(16)
                form.private_key.data = secrets.token_urlsafe(16)
                return render_template("modify_election.html", bg_color_election_state=bg_color_election_state, election_state=curr_election.election_state, title="Modify Election", form=form)
        else:
            return render_template("modify_election.html", bg_color_election_state=bg_color_election_state, election_state=curr_election.election_state,title="Modify Election", form=form)
    elif current_user.is_admin and curr_election.election_state == 'ongoing':
        form = NewElectionForm(obj=curr_election)
        if form.home.data:
            return redirect(url_for('home'))
        elif form.end_election.data:
            # TODO: Write code for ending the election
            return "End election"
        # Disabled All Fields
        for field in form:
            field.render_kw = {"readonly": True}
        return render_template("modify_election.html", bg_color_election_state=bg_color_election_state, election_state=curr_election.election_state, title="Modify Election", form=form)
    elif current_user.is_admin and curr_election.election_state == 'over':
        form = NewElectionForm(obj=curr_election)
        if form.home.data:
            return redirect(url_for('home'))
        elif form.start_counting.data:
            # TODO: Write code for starting the counting process
            return "Start Counting"
        # Disabled All Fields
        for field in form:
            field.render_kw = {"readonly": True}
        flash('Voting phase has finished. Please start the counting phase.', 'warning')
        return render_template("modify_election.html", bg_color_election_state=bg_color_election_state, election_state=curr_election.election_state, title="Modify Election", form=form)
    elif curr_election.election_state == 'past':
        # TODO: Create summary page template
        return "Summary page"
    elif not current_user.is_admin and curr_election.election_state == 'upcoming':
        start_date = curr_election.start_date
        election_title = curr_election.election_title
        # TODO: Use the above two variables to display a suitable message in a template
        return "Election will start shortly. Please come back later"
    elif not current_user.is_admin and curr_election.election_state == 'ongoing':
        # TODO: Create the voting screen template
        return "Click here to go to voting page"
    elif not current_user.is_admin and curr_election.election_state == 'over':
        # TODO: Create the template to display the below message
        return "Results are yet to be published"

@app.route("/election/generate/voter_list", methods=['GET', 'POST'])
@login_required
def gen_voter_list():
    pass

@app.route("/")
def index():
    elections = Election.query.all()
    return render_template("index.html", elections=elections)

@app.route("/home")
def home():
    elections = Election.query.order_by(Election.start_date).all()
    # print(elections)
    return render_template("home.html", elections=elections)

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/voter/<int:id>")
def voter(id):
    return render_template("voter.html", voter_id=id)

@app.route("/candidate/<int:id>")
def candidate(id):
    return render_template("candidate.html", candidate_id=id)

@app.route("/admin")
@login_required
def admin():
    elections = Election.query.all()
    return render_template("admin.html", elections=elections)

@app.route("/admin/new", methods=['GET', 'POST'])
@login_required
def new_admin():
    form = NewAdminForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        # print(form.is_admin.data)
        user = Voter(cin=form.cin.data, name=form.name.data, email=form.email.data, dept=form.dept.data, imagefile='default.jpg', password=hashed_password, join_year=form.join_year.data, is_admin=form.is_admin.data)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You are now able to log in', 'success')
        # return redirect(url_for('login'))
    return render_template("new_admin.html", title="Add New Admin", form=form)

@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404

@app.errorhandler(400)
def bad_request(e):
    return render_template("400.html"), 400

@app.errorhandler(500)
def server_error(e):
    return render_template("500.html"), 500