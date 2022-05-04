from voteStore1 import db
from voteStore1.models import Share, Access

def store_vote_helper(election_id, part_no, share):
  if not Access.is_present(election_id=election_id):
    access_obj = Access(election_id=election_id)
    db.session.add(access_obj)
    db.session.commit()
  stored_vote = Share(election_id=election_id, part_no=part_no, share=share)
  db.session.add(stored_vote)
  db.session.commit()

def get_vote_helper(election_id):
  return Share.getShares(election_id)