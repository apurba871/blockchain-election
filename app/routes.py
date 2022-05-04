import email
from ntpath import join
import os
import secrets
import app.util as util
from flask_sqlalchemy import SQLAlchemy
import app.election_util as election_util
import app.paillier_utils as paillier
import math, random, json
from PIL import Image
from flask import jsonify, render_template, url_for, flash, redirect, request
from app import app, db, bcrypt, mail
from app.models import Voter, CandidateList, Election, Casted_Vote, Voter_List, Department, ResetPassword
from app.forms import (RegistrationForm, LoginForm, UpdateAccountForm, NewElectionForm, 
                        NewAdminForm, RequestResetForm, ResetPasswordForm)
from flask_login import login_user, current_user, logout_user, login_required
from flask_mail import Message
from .permissions import AdminPermission
from datetime import datetime

# Send a password reset link to user's registered e-mail
def send_reset_email(user, expires_sec=1800):
    token = ResetPassword.get_reset_token(user)
    msg = Message('Password Reset Request', 
                    sender = 'blockchainvoting7@gmail.com', 
                    recipients = [user.email])
    msg.html = (    "To reset your password, visit the following link:<br>" +
                    f"{url_for('reset_token', token=token, _external=True)}<br>" +
                    f"This token is only valid for the next: {expires_sec // 60} minute(s).<br>" +
                    "If you did not make this request then simply ignore this email and no changes will be made"
               )
    mail.send(msg)

@app.route("/reset_password", methods=['GET', 'POST'])
def reset_request():
    """
    Description:    Request a password reset
    Endpoint:       /reset_password
    Parameters:     None
    Uses Template:  reset_request.html
    """
    if current_user.is_authenticated:
        if current_user.is_admin:
            return redirect(url_for("home"))
        else:
            return redirect(url_for("voter"))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = Voter.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash('An email has been sent with instructions to reset your password', 'info')
        return redirect('login')
    return render_template('reset_request.html', title='Reset Password', form=form)

@app.route("/reset_password/<token>", methods=['GET', 'POST'])
def reset_token(token):
    """
    Description:    Form to set new password
    Endpoint:       /reset_password/<token>
    Parameters:     token (Type: Str)
    Uses Template:  reset_token.html
    """
    form = ResetPasswordForm()
    if current_user.is_authenticated:
        if current_user.is_admin:
            return redirect(url_for("home"))
        else:
            return redirect(url_for("voter"))
    elif request.method == "GET":
        reset_data = ResetPassword.verify_reset_token(token)
        if reset_data["status"] == False:
            flash(reset_data["message"], 'warning')
            return redirect(url_for('reset_request'))
    elif form.validate_on_submit():
        user = ResetPassword.verify_reset_token(token)["user"]
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        flash('Your password has been updated! You are now able to log in', 'success')
        return redirect(url_for('login'))

    return render_template('reset_token.html', title='Reset Password', form=form)

@app.route("/register", methods=['GET', 'POST'])
def register():
    """
    Description:    User Registration form route, adds a new user to DB
    Endpoint:       /register
    Parameters:     None
    Uses Template:  register.html
    """
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
    """
    Description:    User/Admin Login form route, logs in a registered user
    Endpoint:       /login
    Parameters:     None
    Uses Template:  login.html
    """
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = Voter.query.filter_by(cin=form.cin.data).first()
        if user and user.is_admin and bcrypt.check_password_hash(user.password, form.password.data): # Admin login
            login_user(user, remember=form.remember.data)
            flash("Logged in as admin!", "success")
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('admin'))
        else:
            if user and bcrypt.check_password_hash(user.password, form.password.data): # Already registered users login
                login_user(user, remember=form.remember.data)
                next_page = request.args.get('next')
                if next_page == "/election/new":
                    flash("Please login as admin to access this page", "danger")
                else:
                    return redirect(next_page) if next_page else redirect(url_for('voter'))
            elif user and bcrypt.check_password_hash(user.password, form.password.data): # new users login
                login_user(user, remember=form.remember.data)
                next_page = request.args.get('next')
                if next_page == "/election/new":
                    flash("Please login as admin to access this page", "danger")
                else:
                    return redirect(next_page) if next_page else redirect(url_for('voter'))
            else:
                flash('Login Unsuccessful. Please check CIN and Password', 'danger')
    return render_template("login.html", title="Login", form=form)

@app.route("/logout")
def logout():
    """
    Description:    Logs out the current user from the application
    Endpoint:       /logout
    Parameters:     None
    Uses Template:  None
    """
    logout_user()
    return redirect(url_for("home"))

def save_picture(form_picture):
    """
    Description:    Helper function to resize and save user profile photo
    Endpoint:       None
    Parameters:     None
    Uses Template:  None
    """
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
    """
    Description:    Shows current user's details, user can update and save this information to DB
    Endpoint:       /account
    Parameters:     None
    Uses Template:  account.html
    """
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
@AdminPermission()
def new_election():
    """
    Description:    New Election creation form, enables admin to create and schedule upcoming elections
    Endpoint:       /election/new
    Parameters:     None
    Uses Template:  create_election.html
    """
    num_elections = Election.query.count()
    election_id = num_elections + 1
    prefixed_election_id = 'E' + str(election_id) 
    form = NewElectionForm()
    if request.method == 'GET':
        flash('Please Save the Private Key before proceeding.', 'info')
        pubkey, privkey = paillier.generate_key_pair()
        pubkey_json = json.loads(pubkey)
        privkey_json = json.loads(privkey)
        form.public_key.data = pubkey_json["n"]
        form.private_key_p.data = privkey_json["p"]
        form.private_key_q.data = privkey_json["q"]
        return render_template("create_election.html", title="New Election", form=form, private_key=privkey, election_id=prefixed_election_id)
    # Validate the form on submit and check if submit button was clicked
    elif request.method == 'POST' and form.validate_on_submit() and form.submit.data:  
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
        # After the election has been created, the admin is redirected to the generate_voter_list
        # route
        return redirect(url_for('gen_voter_list', election_id=prefixed_election_id))
    return "Bad request", 400
@app.route("/election/<id>/view", methods=['GET', 'POST'])
@login_required
def view_election(id):
    """
    Description:    Election page of a particular election
    Endpoint:       /election/<id>/view
    Parameters:     id (Type: String)
    Uses Template:  modify_election.html, admin_ongoing_election.html
    """
    curr_election = Election.query.where(Election.election_id==id).first()
    # Generate the background color of the Election Status Text
    if curr_election.election_state == 'upcoming':
        bg_color_election_state = "bg-primary"
    elif curr_election.election_state == 'ongoing':
        bg_color_election_state = "bg-warning"
    elif curr_election.election_state == "over":
        bg_color_election_state = "bg-info"
    elif curr_election.election_state == "past":
        bg_color_election_state = "bg-success"
    elif curr_election.election_state == "counting_finished":
        bg_color_election_state = "bg-danger"
    # If the current user is admin and the election is an upcoming election
    if current_user.is_admin and curr_election.election_state == 'upcoming':
        form = NewElectionForm(obj=curr_election)
        # Check the form for valid data
        if form.validate_on_submit():
            # If the submit button was pressed, set the update the new
            # data in the current election row and commit to database
            if form.submit.data:
                curr_election.election_title = form.election_title.data
                curr_election.start_date=form.start_date.data
                curr_election.max_attempt=form.max_attempt.data
                curr_election.public_key=form.public_key.data
                db.session.commit()
                flash('Election Modified Successfully!', 'success')
                return redirect(url_for('gen_voter_list', election_id=curr_election.election_id))
            # If the generate_keys button was pressed, generate new keys and display them
            elif form.generate_keys.data:
                pubkey, privkey = paillier.generate_key_pair()
                pubkey_json = json.loads(pubkey)
                privkey_json = json.loads(privkey)
                form.public_key.data = pubkey_json["n"]
                form.private_key_p.data = privkey_json["p"]
                form.private_key_q.data = privkey_json["q"]
                return render_template("modify_election.html", private_key=privkey, election_id=curr_election.election_id, bg_color_election_state=bg_color_election_state, election_state=curr_election.election_state, title="Modify Election", form=form)
            # If the delete_election button was pressed from modal, delete that election and commit changes to DB 
            elif form.delete_election.data:
                Election.query.filter_by(election_id=curr_election.election_id).delete()
                db.session.commit()
                flash('Successfully Deleted that Election!', 'success')
                return redirect(url_for('home'))
        else:
            return render_template("modify_election.html", election_id=curr_election.election_id, bg_color_election_state=bg_color_election_state, election_state=curr_election.election_state,title="Modify Election", form=form)
    # If the current user is admin and the election state is ongoing
    elif current_user.is_admin and curr_election.election_state == 'ongoing':
        # Create a new form and populate it with existing data
        form = NewElectionForm(obj=curr_election)
        # If the home button is pressed, redirect to the home route
        if form.home.data:
            return redirect(url_for('home'))
        # If the end election button is pressed, end the election
        elif form.end_election.data:
            curr_election.election_state = 'over'
            curr_election.end_date = datetime.now()
            db.session.commit()
            flash('Election Terminated the Election', 'success')
            return redirect(url_for('home'))
            # return "End election"
        # Disable all form fields
        for field in form:
            field.render_kw = {"readonly": True}
        # Show the current status of the election
        # TODO: Generate the current vote count dynamically in admin_ongoing_election.html page
        return render_template("admin_ongoing_election.html", election_id=curr_election.election_id, bg_color_election_state=bg_color_election_state, election_state=curr_election.election_state, title="Ongoing Election", form=form)

    # If the current user is admin and the election is over, flash a message that the voting phase
    # is over and ask to start the counting phase
    elif current_user.is_admin and curr_election.election_state == 'over':
        # Display the form with existing data
        form = NewElectionForm(obj=curr_election)
        if form.home.data:
            return redirect(url_for('home'))
        elif form.start_counting.data:
            # TODO: Write code for starting the counting process
            return "Start Counting"
        # Disable all the form fields
        for field in form:
            field.render_kw = {"readonly": True}
        flash('Voting phase has finished. Please start the counting phase.', 'warning')
        return render_template("modify_election.html", election_id=curr_election.election_id, bg_color_election_state=bg_color_election_state, election_state=curr_election.election_state, title="Modify Election", form=form)
    # If the current user is admin and the counting phase is over, flash a message that the counting phase
    # is over and ask to publish the results
    elif current_user.is_admin and curr_election.election_state == 'counting_finished':
        # Display the form with existing data
        form = NewElectionForm(obj=curr_election)
        if form.home.data:
            return redirect(url_for('home'))
        elif form.publish_results.data:
            # TODO: Write code for publishing the results by accepting the PRIVATE KEY as input in a form
            # and write the logic to decrypt the count 
            return "Publishing results"
        # Disable all the form fields
        for field in form:
            field.render_kw = {"readonly": True}
        flash('Counting phase has finished. Please publish the results.', 'warning')
        return render_template("modify_election.html", election_id=curr_election.election_id, bg_color_election_state=bg_color_election_state, election_state=curr_election.election_state, title="Modify Election", form=form)
    # If the current user is admin or non-admin, display the summary page
    elif curr_election.election_state == 'past':
        # TODO: Create summary page template
        return "Summary page"
    # If the current user is non-admin, and election is upcoming, display a registration
    # form if the user isn't registered yet, otherwise display a message that the election
    # will start on the start_date, only if the user is eligible for this election.
    # If the user is not eligible for this election, display the appropriate error message.
    elif not current_user.is_admin and curr_election.election_state == 'upcoming':
        # Check if the admin has generated the voter list
        is_voter_list_generated = Voter_List.query.filter_by(election_id=curr_election.election_id).first()
        if not is_voter_list_generated:
            # Show him the election name and start time and inform that the admin has not yet generated
            # the voter list and that he will be able to vote if the votre list has his name and he has
            # registered for voting
            return render_template("voterlist_not_generated.html", voter_id=current_user.id, election_title=curr_election.election_title, start_date=curr_election.start_date)
        else:
            # If the voter list is generated, check if the voter is in the list
            is_voter_in_voter_list = Voter_List.getVoterRecord(curr_election.election_id, current_user.id)
            # print(is_voter_in_voter_list)
            if not is_voter_in_voter_list:
                return render_template("voter_not_in_voterlist.html", voter_id=current_user.id)
            else:
                # if the voter has not registered for the vote, show him the register_for_vote.html page
                if is_voter_in_voter_list.is_registered == False:
                    return render_template("register_for_vote.html", election_id=curr_election.election_id, election_title=curr_election.election_title, start_date=curr_election.start_date, election_state=curr_election.election_state)
                # else show him that he has registered for the vote and the election start time
                else:
                    return render_template("already_registered.html", voter_id=current_user.id, election_title=curr_election.election_title, start_date=curr_election.start_date)
    # If the user is a non-admin user, and election is ongoing, check if the user has registered
    # for the vote, if not, display the registration page, only if the user is eligible for voting.
    # After the voter eligibility is verified, redirect to the voting screen. If the voter is not
    # eligible for the current election, display an appropriate error message.
    elif not current_user.is_admin and curr_election.election_state == 'ongoing':
        # Check if the admin has generated the voter list
        is_voter_list_generated = Voter_List.query.filter_by(election_id=curr_election.election_id).first()
        if not is_voter_list_generated:
            # Show him the election name and start time and inform that the admin has not yet generated
            # the voter list and that he will be able to vote if the votre list has his name and he has
            # registered for voting
            return render_template("voterlist_not_generated.html", voter_id=current_user.id, election_title=curr_election.election_title, start_date=curr_election.start_date)
        else:
            # If the voter list is generated, check if the voter is in the list
            is_voter_in_voter_list = Voter_List.getVoterRecord(curr_election.election_id, current_user.id)
            # print(is_voter_in_voter_list)
            if not is_voter_in_voter_list:
                return render_template("voter_not_in_voterlist.html", voter_id=current_user.id)
            else:
                # if the voter has not registered for the vote, show him the register_for_vote.html page
                if is_voter_in_voter_list.is_registered == False:
                    return render_template("register_for_vote.html", election_id=curr_election.election_id, election_title=curr_election.election_title, start_date=curr_election.start_date, election_state=curr_election.election_state)
                # else authenticate the voter by asking for the OTP
                else:
                    return redirect(url_for("cast_vote", election_id=curr_election.election_id))
                    # curr_voter = Voter_List.getVoterRecord(curr_election.election_id, current_user.id)
                    # return render_template("enter_otp.html", election_id=curr_election.election_id, election_title=curr_election.election_title, start_date=curr_election.start_date, tries=curr_voter.tries, max_attempt=curr_election.max_attempt)
    # If the user is non-admin, and the election is over, display a message that it is over.
    elif not current_user.is_admin and curr_election.election_state == 'over' or curr_election.election_state == 'counting_finished':
        # TODO: Create the template to display the below message
        return "Results are yet to be published"

@app.route("/cast_vote/<election_id>", methods=['GET', 'POST'])
@login_required
def cast_vote(election_id):
    """
    Description:    Voting page, enables a registered voter to cast their vote
    Endpoint:       /cast_vote/<election_id>
    Parameters:     election_id (Type: String)
    Uses Template:  cast_your_vote.html, debar_from_voting.html
    """
    if request.method == "GET":
        if util.checkDebarStatus(election_id, current_user.id):
            # if max_attempt reached then debar him from the voting process
            return render_template("debar_from_voting.html", voter_id=current_user.id)
        else:
            curr_voter = Voter_List.getVoterRecord(election_id, current_user.id)
            curr_election = Election.getElectionRecord(election_id)
            return render_template("enter_otp.html", 
                                    election_id=curr_election.election_id, 
                                    election_title=curr_election.election_title, 
                                    start_date=curr_election.start_date, 
                                    tries=curr_voter.tries, 
                                    max_attempt=curr_election.max_attempt)
    elif request.method == "POST":
        # Check if the OTP entered by the voter is valid
        user_otp = request.form['user_otp']
        return util.checkOTPAndRedirect(user_otp, election_id)
    # # print("OTP: ", user_otp)
    # # otp = Voter_List.query.where(Voter_List.id==current_user.id).first().token
    # otp = Voter_List.getVoterToken(current_user.id)
    # # tries = Voter_List.query.where(Voter_List.id==current_user.id).first().tries
    # tries = Voter_List.getVoterTries(current_user.id)
    # if user_otp == otp:
    #     # Voter_List.query.where(Voter_List.id==current_user.id).first().tries += 1
    #     # db.session.commit()
    #     # if valid then take him to the voting page
    #     return render_template("cast_your_vote.html")
    # else:
    #     # increase tries count by 1 and ask him to enter the correct token again until tries reaches max_attempts
    #     curr_election = Election.query.where(Election.election_id==election_id).first()
    #     # Voter_List.query.where(Voter_List.id==current_user.id).first().tries += 1
    #     Voter_List.incrementVoterTries(current_user.id)
    #     util.checkTriesAndRedirect(tries, curr_election)
        # if tries < curr_election.max_attempt:
        #     db.session.commit()
        #     return redirect(url_for("view_election", id=curr_election.election_id))
        # else:
        #     # if max_attempt reached then debar him from the voting process
        #     return render_template("debar_from_voting.html")

@app.route("/thanks", methods=['GET', 'POST'])
@login_required
def thanks():
    """
    Description:    Show a message, thanks for voting a particular candidate
    Endpoint:       /thanks
    Parameters:     None
    Uses Template:  thanks.html
    """
    print(request.form["selected-candidate-id"], request.form["selected-candidate-name"])
    return render_template("thanks.html", voter_id=current_user.id, candidate_id=request.form["selected-candidate-id"], 
                            candidate_name=request.form["selected-candidate-name"], candidate_cin=request.form["selected-candidate-cin"])

# function to generate 6-digit OTP
def generateOTP():
    digits = "0123456789"
    OTP = ""
    for _ in range(6) :
        OTP += digits[math.floor(random.random() * 10)]
    return OTP

@app.route("/register_voter_and_send_otp/<election_id>", methods=['GET', 'POST'])
@login_required
def register_voter_and_send_otp(election_id):
    """
    Description:    Register the current voter in the selected election and send an OTP to their registered e-mail address
    Endpoint:       /register_voter_and_send_otp
    Parameters:     election_id (Type: String)
    Uses Template:  register_voter_and_send_otp.html
    """
    curr_election = Election.getElectionRecord(election_id=election_id)
    # Register the current voter
    curr_voter = Voter_List.getVoterRecord(election_id=curr_election.election_id, voter_id=current_user.id)
    # print("Before: ", curr_voter.is_registered)
    if curr_voter is None:
        return render_template("voter_not_in_voterlist.html", voter_id=current_user.id)
    elif curr_voter.is_registered:
        return render_template("already_registered.html", voter_id=current_user.id, election_title=curr_election.election_title, start_date=curr_election.start_date)
    elif not curr_voter.is_registered:
        curr_voter.is_registered = True
        otp = generateOTP()
        curr_voter.token = otp
        db.session.commit()
        # print("After: ", Voter_List.query.where(Voter_List.id==current_user.id).first().is_registered)
        # Send an OTP to their registered e-mail address
        user_email = Voter.getVoterRecord(current_user.id).email
        # print(user_email)
        msg = Message('Secret OTP for voting', sender = 'blockchainvoting7@gmail.com', recipients = [user_email])
        msg.html = f'''<h1>Election Title: {curr_election.election_title}</h1><br/> 
                    <h1>Election Start Time: {curr_election.start_date}</h1><br/> 
                    <h1>Status: You are registered for the election.</h1><br/> 
                    <h1>Your OTP: {otp}</h1><br/> 
                    '''
        mail.send(msg)
        flash('An O.T.P. has been sent to your registered e-mail address.', 'success')
        return render_template("register_voter_and_send_otp.html", otp=otp, election_id=curr_election.election_id, election_title=curr_election.election_title, start_date=curr_election.start_date, election_state=curr_election.election_state)

@app.route("/publish_results")
@login_required
@AdminPermission()
def publish_results():
    """
    Description:    Shows those elections for which results need to be published
    Endpoint:       /publish_results
    Parameters:     None
    Uses Template:  results.html
    """
    elections = Election.query.order_by(Election.create_date.desc()).all()
    return render_template("results.html", elections=elections)

@app.route("/election/<election_id>/generate/voter_list", methods=['GET', 'POST'])
@login_required
@AdminPermission()
def gen_voter_list(election_id):
    """
    Description:    Generate Voter List page, admin can use this to generate the voter list
    Endpoint:       /election/<election_id>/generate/voter_list
    Parameters:     election_id (Type: String)
    Uses Template:  generate_voter_list.html
    """
    election = Election.getElectionRecord(election_id)
    if election.election_state == 'upcoming':
        if request.method == 'POST':
            for vid in request.form.getlist('id'):
                voter_list_entry = Voter_List(election_id=election_id, 
                                            id=vid)
                db.session.add(voter_list_entry)
            db.session.commit()
            flash('Voter List Updated Successfully!', 'success')
        existing_voter_list = [voter.to_dict() for voter in Voter_List.getVotersInList(election_id=election_id)]
        existing_voter_dict = {"data": existing_voter_list}
        return render_template("generate_voter_list.html", election_id=election_id, 
                               existing_voter_list=existing_voter_dict if existing_voter_list != [] else None)
    else:
        existing_voter_list = [voter.to_dict() for voter in Voter_List.getVotersInList(election_id=election_id)]
        existing_voter_dict = {"data": existing_voter_list}
        return render_template("generate_voter_list.html", election_id=election_id, 
                                existing_voter_list=existing_voter_dict if existing_voter_list != [] else None,
                                view_only=True)

@app.route("/election/<election_id>/generate/candidate_list", methods=['GET', 'POST'])
@login_required
@AdminPermission()
def gen_candidate_list(election_id):
    """
    Description:    Generate Candidate List page, admin can use this to generate the candidate list
    Endpoint:       /election/<election_id>/generate/candidate_list
    Parameters:     election_id (Type: String)
    Uses Template:  generate_candidate_list.html
    """
    election = Election.getElectionRecord(election_id)
    if election.election_state == 'upcoming':
        if request.method == 'POST':
            for vid in request.form.getlist('id'):
                candidate_id = CandidateList.getCandidateCount(election_id) + 1
                candidate_list_entry = CandidateList(election_id=election_id,
                                                    id=candidate_id, 
                                                    voter_id=vid)
                db.session.add(candidate_list_entry)
            db.session.commit()
            flash('Candidate List Updated Successfully!', 'success')
        existing_candidate_list = [candidate.to_dict() for candidate in CandidateList.getCandidatesInList(election_id=election_id)]
        existing_candidate_dict = {"data": existing_candidate_list}
        return render_template("generate_candidate_list.html", election_id=election_id, 
                               existing_candidate_list=existing_candidate_dict if existing_candidate_list != [] else None)
    else:
        existing_candidate_list = [candidate.to_dict() for candidate in CandidateList.getCandidatesInList(election_id=election_id)]
        existing_candidate_dict = {"data": existing_candidate_list}
        return render_template("generate_candidate_list.html", election_id=election_id, 
                               existing_candidate_list=existing_candidate_dict if existing_candidate_list != [] else None,
                                view_only=True)

@app.route('/api/data/voters/<election_id>')
@AdminPermission()
def get_voters(election_id):
    """
    Description:    Returns a JSON list of voters, who are not present in the voter list of the election
                    having id as election_id
    Endpoint:       /api/data/voters/<election_id>
    Parameters:     election_id (Type: String)
    Returns:        {'data': [
                        {'id': 8, 'cin': '2-09-16-0309', 'name': 'Craig Andrew Boila Gomes', 
                        'email': '2-09-16-0309@email.com', 'dept': 'BAGG', 'imagefile': 'default.jpg', 
                        'join_year': 2016, 'is_admin': False}, 
                        {'id': 9, 'cin': '2-09-16-0310', 'name': 'J Lalthafamkima', 
                        'email': '2-09-16-0310@email.com', 'dept': 'BAGG', 
                        'imagefile': 'default.jpg', 'join_year': 2016, 'is_admin': False}, ...
                    ]}
    """
    existing_voters = Voter.query.join(Voter_List.query.filter(Voter_List.election_id == election_id))
    voter_data = {'data': [voter.to_dict() for voter in Voter.query.except_(existing_voters).filter(Voter.is_admin == False)]}
    return voter_data

@app.route('/api/data/candidates/<election_id>')
@AdminPermission()
def get_candidates(election_id):
    """
    Description:    Returns a JSON list of candidates, who are not present in the candidate list of the election
                    having id as election_id
    Endpoint:       /api/data/candidates/<election_id>
    Parameters:     election_id (Type: String)
    Returns:        {'data': [
                        {'id': 8, 'cin': '2-09-16-0309', 'name': 'Craig Andrew Boila Gomes', 
                        'email': '2-09-16-0309@email.com', 'dept': 'BAGG', 'imagefile': 'default.jpg', 
                        'join_year': 2016, 'is_admin': False}, 
                        {'id': 9, 'cin': '2-09-16-0310', 'name': 'J Lalthafamkima', 
                        'email': '2-09-16-0310@email.com', 'dept': 'BAGG', 
                        'imagefile': 'default.jpg', 'join_year': 2016, 'is_admin': False}, ...
                    ]}
    """
    existing_candidates = Voter.query.join(CandidateList.query.filter(CandidateList.election_id == election_id))
    candidate_data = {'data': [candidate.to_dict() for candidate in Voter.query.except_(existing_candidates).filter(Voter.is_admin == False)]}
    return candidate_data

@app.route('/api/data/voterList/delete/<election_id>', methods=['GET', 'POST'])
@AdminPermission()
def remove_from_voter_list(election_id):
    """
    Description:    Deletes voter records from the voter list
    Endpoint:       /api/data/voterList/delete/<election_id>
    Parameters:     election_id (Type: String)
    Returns:        {} on success and {"error":"Only removal from voter list is permitted"}
                    on failure
    """
    if request.method == "POST" and request.form["action"] == "remove":
        remove_voter_ids = []
        for key,value in request.form.items():
            if "[id]" in key:
                remove_voter_ids.append(value)
        Voter_List.query.filter(Voter_List.election_id == election_id, 
                                Voter_List.id.in_(remove_voter_ids)).delete(synchronize_session=False)
        db.session.commit()
        return {}
    else:
        return {"error":"Only removal from voter list is permitted"}

@app.route('/api/data/candidateList/delete/<election_id>', methods=['GET', 'POST'])
@AdminPermission()
def remove_from_candidate_list(election_id):
    """
    Description:    Deletes voter records from the candidate list
    Endpoint:       /api/data/candidateList/delete/<election_id>
    Parameters:     election_id (Type: String)
    Returns:        {} on success and {"error":"Only removal from voter list is permitted"}
                    on failure
    """
    if request.method == "POST" and request.form["action"] == "remove":
        print(request.form)
        remove_candidate_ids = []
        for key,value in request.form.items():
            if "[id]" in key:
                remove_candidate_ids.append(value)
        CandidateList.query.filter(CandidateList.election_id == election_id, 
                               CandidateList.voter_id.in_(remove_candidate_ids)).delete(synchronize_session=False)
        db.session.commit()
        return {}
    else:
        return {"error":"Only removal from voter list is permitted"}

@app.route('/api/data/user/manage', methods=['GET', 'POST'])
@AdminPermission()
def user_crud():
    if request.method == "POST":
        print(request.form)
        if "action" in request.form:
            if request.form["action"] == "create":
                cin = request.form["data[0][cin]"]
                name = request.form["data[0][name]"]
                dept = request.form["data[0][dept]"]
                password = request.form["data[0][password]"]
                email = request.form["data[0][email]"]
                join_year = request.form["data[0][join_year]"]
                is_admin = request.form["data[0][is_admin]"] 
                field_errors = election_util.validateFields(cin, name, dept, join_year, is_admin, email, password)
                if len(field_errors) == 0:
                    voter = Voter(  
                                    cin=cin, 
                                    name=name, 
                                    email=email,
                                    dept=dept,
                                    password=bcrypt.generate_password_hash(password).decode('utf-8'),
                                    join_year=join_year,
                                    is_admin=True if is_admin == 'true' else False
                                )
                    db.session.add(voter)
                    db.session.commit()
                    print("Saved to DB")
                    return jsonify({"data": [ Voter.getVoterByEmail(email).to_dict() ]})
                else:
                    return jsonify({"fieldErrors": field_errors})
            elif request.form["action"] == "edit":
                for key, value in request.form.items():
                    if "[id]" in key:
                        voter_id = value
                        break
                cin = request.form[f"data[{voter_id}][cin]"]
                name = request.form[f"data[{voter_id}][name]"]
                dept = request.form[f"data[{voter_id}][dept]"]
                password = request.form[f"data[{voter_id}][password]"]
                email = request.form[f"data[{voter_id}][email]"]
                join_year = request.form[f"data[{voter_id}][join_year]"]
                is_admin = request.form[f"data[{voter_id}][is_admin]"] 
                field_errors = election_util.validateFields(cin, name, dept, join_year, is_admin, email, password, existence=False)
                if len(field_errors) == 0:
                    voter = Voter.getVoterByID(voter_id)
                    voter.cin=cin 
                    voter.name=name 
                    voter.email=email
                    voter.dept=dept
                    voter.password=bcrypt.generate_password_hash(password).decode('utf-8')
                    voter.join_year=join_year
                    voter.is_admin=True if is_admin == 'true' else False
                    db.session.commit()
                    print("Saved to DB")
                    return jsonify({"data": [ Voter.getVoterByEmail(email).to_dict() ]})
                else:
                    return jsonify({"fieldErrors": field_errors})
            elif request.form["action"] == "remove":
                remove_user_ids = []
                for key,value in request.form.items():
                    if "[id]" in key:
                        remove_user_ids.append(value)
                Voter.query.filter(Voter.id.in_(remove_user_ids)).delete(synchronize_session=False)
                db.session.commit()
                return {}
            else:
                return {"error":"Unsuported action"}
        else:
            user_data = {'data': [voter.to_dict() for voter in Voter.query]}
            return user_data
    elif request.method == "GET":
        return render_template("manage_users.html", departments=[{"label": department.getDepartmentString(), "value":department.dept_code} for department in Department.getAllDepartments()])

@app.route("/index2")
def index2():
    """
    Description:    New Landing page of the application
    Endpoint:       /index2
    Parameters:     None
    Uses Template:  index2.html
    """
    return render_template("index2.html")

@app.route("/")
def index():
    """
    Description:    Landing page of the application
    Endpoint:       /
    Parameters:     None
    Uses Template:  index.html
    """
    elections = elections = Election.query.order_by(Election.start_date.desc()).all()
    election_util.update_election_state()
    return render_template("index2.html", elections=elections)

@app.route("/home")
def home():
    """
    Description:    Home page of the application, shows ongoing/upcoming/over/past elections
    Endpoint:       /home
    Parameters:     None
    Uses Template:  home.html
    """
    elections = elections = Election.query.order_by(Election.start_date.desc()).all()
    election_util.update_election_state()
    # print(elections)
    return render_template("home.html", elections=elections)

@app.route("/about")
def about():
    """
    Description:    About page of the application
    Endpoint:       /about
    Parameters:     None
    Uses Template:  about.html
    """
    return render_template("about.html")

# @app.route("/voter/<int:voter_id>")
@app.route("/voter")
@login_required
def voter():
    """
    Description:    Home page of a particular user, shows only those elections in which he is/was eligible
    Endpoint:       /voter
    Parameters:     None
    Uses Template:  voter.html
    """
    elections = Voter_List.getElectionsForVoter(current_user.id)
    voter_elections = CandidateList.getElectionsWhereVoterIsInCandidateList(current_user.id)
    return render_template("voter.html", elections=elections, voter_elections=voter_elections)

# @app.route("/candidate/<id>")
@app.route("/candidate")
@login_required
def candidate():
    """
    Description:    Candidate page of a particular user
    Endpoint:       /candidate
    Parameters:     None
    Uses Template:  candidate.html
    """
    return render_template("candidate.html", candidate_id=current_user.id)

@app.route("/admin")
@login_required
@AdminPermission()
def admin():
    """
    Description:    Admin page, shows content of home.html along with option to Add New User, Create Election, Publish Results
    Endpoint:       /admin
    Parameters:     None
    Uses Template:  admin.html
    """
    elections = elections = Election.query.order_by(Election.start_date.desc()).all()
    election_util.update_election_state()
    return render_template("admin.html", elections=elections)

@app.route("/admin/new", methods=['GET', 'POST'])
@login_required
@AdminPermission()
def new_admin():
    """
    Description:    New admin/user registration page, only be accessed by an existing admin
    Endpoint:       /admin/new
    Parameters:     None
    Uses Template:  new_admin.html
    """
    form = NewAdminForm(request.form)
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        # print(form.is_admin.data)
        # print(request.form)
        user = Voter(cin=form.cin.data, name=form.name.data, email=form.email.data, dept=form.dept.data, imagefile='default.jpg', password=hashed_password, join_year=form.join_year.data, is_admin=form.is_admin.data)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You are now able to log in', 'success')
        # return redirect(url_for('login'))
    return render_template("new_admin.html", title="Add New Admin", form=form)

@app.errorhandler(404)
def page_not_found(e):
    """
    Description:    Page not found
    Endpoint:       None
    Parameters:     None
    Uses Template:  404.html
    """
    return render_template("404.html"), 404

@app.errorhandler(400)
def bad_request(e):
    """
    Description:    Bad request
    Endpoint:       None
    Parameters:     None
    Uses Template:  400.html
    """
    return render_template("400.html"), 400

@app.errorhandler(500)
def server_error(e):
    """
    Description:    Server specific error
    Endpoint:       None
    Parameters:     None
    Uses Template:  500.html
    """
    return render_template("500.html"), 500

# TODO: Add a template for handling 403 Forbidden Access