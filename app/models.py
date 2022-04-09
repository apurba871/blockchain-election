from datetime import datetime
from app import db, login_manager
from flask_login import UserMixin

@login_manager.user_loader
def load_user(user_id):
    return Voter.query.get(int(user_id))

class Voter(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    cin = db.Column(db.String(30), unique=True, nullable=False)
    name = db.Column(db.String(255), nullable=False)
    # username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(30), unique=True, nullable=False)
    dept = db.Column(db.String(4), db.ForeignKey('department.dept_code'), nullable=False)
    imagefile = db.Column(db.String(20), nullable=False, default='default.jpg')
    password = db.Column(db.String(60), nullable=False)

    def __repr__(self):
        return f"Voter('{self.name}', '{self.cin}')"

# class Voter(db.Model):
#     voter_id = db.Column(db.Integer, primary_key=True, nullable=False)
#     voter_cin = db.Column(db.String(16), unique=True, nullable=False)
#     voter_name = db.Column(db.String(30), nullable=False)
#     dept_code = db.Column(db.String(4), db.ForeignKey('department.dept_code') ,nullable=False)

#     def __repr__(self):
#         return f"Voter('{self.voter_id}', '{self.voter_name}')"

class Candidate(db.Model):
    election_id = db.Column(db.String(5), db.ForeignKey('election.election_id'), primary_key=True, nullable=False)
    candidate_id = db.Column(db.String(5), primary_key=True, nullable=False)
    id = db.Column(db.Integer, db.ForeignKey('voter.id'), primary_key=True, nullable=False)
    voters = db.relationship('Voter', backref='vote', lazy=True) # one candidate can get votes from many voters, so One-To-Many relationship

    def __repr__(self):
        return f"Candidate('{self.candidate_id}', '{self.id}')"

class Election(db.Model):
    election_id = db.Column(db.String(5), primary_key=True, nullable=False)
    start_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    end_date = db.Column(db.DateTime, nullable=False)
    # is_over = db.Column(db.Boolean, nullable=False)

    def __repr__(self):
        return f"Election('{self.election_id}', '{self.start_date}', '{self.end_date}'"

class Casted_Vote(db.Model):
    election_id = db.Column(db.String(5), db.ForeignKey('election.election_id'), primary_key=True, nullable=False)
    id = db.Column(db.Integer, db.ForeignKey('voter.id'), primary_key=True, nullable=False)
    candidate_id = db.Column(db.String(5), db.ForeignKey('candidate.candidate_id'), nullable=False)

    def __repr__(self):
        return f"Casted_Vote('{self.election_id}', '{self.id}', '{self.candidate_id}')"

class Voter_List(db.Model):
    election_id = db.Column(db.String(5), db.ForeignKey('election.election_id'), primary_key=True, nullable=False)
    id = db.Column(db.Integer, db.ForeignKey('voter.id'), primary_key=True, nullable=False)

    def __repr__(self):
        return f"Voter_List('{self.election_id}', '{self.id}')"

class Department(db.Model):
    dept_code = db.Column(db.String(4), primary_key=True, nullable=False)
    dept_name = db.Column(db.String(50), unique=True, nullable=False)

    def __repr__(self):
        return f"Department('{self.dept_code}', '{self.dept_name}')"
