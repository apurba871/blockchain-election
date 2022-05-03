from app import db
from app.models import Voter_List, Election, CandidateList
from flask import redirect, url_for, render_template
from flask_login import current_user

# Returns True if voter_id is debarred from election_id, False otherwise
def checkDebarStatus(election_id, voter_id):
    voter_tries = Voter_List.getVoterTries(election_id, voter_id)
    election_max_attempt = Election.getElectionRecord(election_id).max_attempt
    return voter_tries == election_max_attempt

def checkOTPAndRedirect(user_otp, election_id):
    otp = Voter_List.getVoterToken(election_id, current_user.id)
    tries = Voter_List.getVoterTries(election_id, current_user.id)
    candidates = CandidateList.getAllCandidates(election_id)
    if user_otp == otp:
        # if valid then take him to the voting page
        return render_template("cast_your_vote.html", candidates=candidates)
    else:
        # increase tries count by 1 and ask him to enter the correct token again until tries reaches max_attempts
        curr_election = Election.query.where(Election.election_id==election_id).first()
        Voter_List.incrementVoterTries(election_id, current_user.id)
        db.session.commit()
        if tries < curr_election.max_attempt - 1:
            return redirect(url_for("view_election", id=curr_election.election_id))
        else:
            # if max_attempt reached then debar him from the voting process
            return render_template("debar_from_voting.html", voter_id=current_user.id)