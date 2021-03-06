from voteStore2 import db
from datetime import datetime

class Access(db.Model):
  election_id = db.Column(db.String(5),primary_key=True, nullable=False)
  has_access = db.Column(db.Boolean, default=False, nullable=False)
  
  @classmethod
  def is_present(cls, election_id):
    return True if Access.query.filter_by(election_id=election_id).first() else False

  @classmethod
  def get_has_access(cls, election_id):
    access_obj = Access.query.filter_by(election_id=election_id).first()
    if access_obj is not None:
      return access_obj.has_access
    else:
      return False
  
  @classmethod
  def getRecord(cls, election_id):
    return Access.query.filter_by(election_id=election_id).first()

class Share(db.Model):
  share_id = db.Column(db.Integer, primary_key=True)
  election_id = db.Column(db.String(5),  db.ForeignKey('access.election_id'), nullable=False)
  # part_no = db.Column(db.Integer, nullable=False, primary_key=True)
  exponent = db.Column(db.Integer, nullable=False)
  share = db.Column(db.Text, nullable=False)
  create_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

  @classmethod
  def getShares(cls, election_id):
    return Share.query.filter_by(election_id=election_id).order_by(Share.share_id.asc()).all()