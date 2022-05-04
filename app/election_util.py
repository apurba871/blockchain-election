def update_election_state():
    from app import db
    from app.models import Election
    from datetime import datetime
    elections = Election.query.all()
    for election in elections:
        if election.election_state == 'counting_finished':
            continue
        elif election.start_date <= datetime.now() <= election.end_date:
            election.election_state = 'ongoing'
        elif datetime.now() < election.start_date:
            election.election_state = 'upcoming'
        elif datetime.now() > election.end_date and election.results_published == False:
            election.election_state = 'over'
        elif datetime.now() > election.end_date and election.results_published == True:
            election.election_state = 'past'
    db.session.commit()
    print("Election states updated at", datetime.now())

def get_new_election_id():
    from app import db
    from app.models import Election
    last_record = Election.getLastElectionRecord()
    numeric_id = int(0 if last_record is None else last_record.election_id[1:])
    return f'E{numeric_id+1}'

def get_new_candidate_id(election_id):
    from app import db
    from app.models import CandidateList
    return (0 if CandidateList.getLastCandidateRecord(election_id) is None else CandidateList.getLastCandidateRecord(election_id).id) + 1

def validate_cin(cin):
    from app.models import Voter
    user = Voter.query.filter_by(cin=cin).first()
    if user:
        return False
    else:
        return True

def validate_email(email):
    from app.models import Voter
    user = Voter.query.filter_by(email=email).first()
    if user:
        return False
    else:
        return True

def validateFields(cin, name, dept, join_year, is_admin, email, password, existence=True):
    import validators
    field_errors = []
    if cin == '':
        field_errors.append({'name':'cin', 'status':'Please fill out this field.'})
    elif existence and not validate_cin(cin):
        field_errors.append({'name':'cin', 'status':'CIN already in use. Please enter a different one.'})

    if name == '':
        field_errors.append({'name':'name', 'status':'Please fill out this field.'})
    elif not validators.length(name, min=3, max=255):
        field_errors.append({'name':'name', 'status':'Name length not between 3 and 255'})
    
    if dept == '':
        field_errors.append({'name':'dept', 'status':'Please select a department.'})
    
    if join_year == '':
        field_errors.append({'name':'join_year', 'status':'Please fill out this field.'})
    elif not join_year.isdecimal():
        field_errors.append({'name':'join_year', 'status':'Joining year should be a number'})
    elif not validators.between(int(join_year), min=2016, max=2020):
        field_errors.append({'name':'join_year', 'status':'Joining year should be between 2016 and 2020'})
    
    if is_admin == '':
        field_errors.append({'name':'is_admin', 'status':'Please select an admin right.'})
    
    if email == '':
        field_errors.append({'name':'email', 'status':'Please fill out this field.'})
    elif existence and not validate_email(email):
        field_errors.append({'name':'email', 'status':'This email is already taken. Please enter a new one.'})
    elif not validators.email(email):
        field_errors.append({'name':'email', 'status':'Please enter a valid email.'})
    
    if password == '':
        field_errors.append({'name':'password', 'status':'Please fill out this field.'})

    return field_errors

if __name__ == "__main__":
    print(get_new_election_id())