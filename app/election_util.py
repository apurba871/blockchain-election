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