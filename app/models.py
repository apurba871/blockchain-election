from datetime import datetime
import itsdangerous
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from app import db, login_manager, app
from flask_login import UserMixin

# from sqlalchemy import CheckConstraint

@login_manager.user_loader
def load_user(user_id):
    return Voter.query.get(int(user_id))

class ResetPassword(db.Model):
    user_id = db.Column(db.Integer, db.ForeignKey('voter.id'), primary_key=True, nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    token = db.Column(db.Text, primary_key=True, nullable=False)
    is_valid = db.Column(db.Boolean, default=True, nullable=False)

    @classmethod
    def get_reset_token(cls, user, expires_sec=1800):
        s = Serializer(app.config['SECRET_KEY'], expires_sec)
        timestamp = datetime.utcnow()
        token_data = {'user_id':user.id, 'timestamp':timestamp.strftime('%Y-%m-%dT%H:%M')}
        token = s.dumps(token_data).decode('utf-8')
        reset_obj = ResetPassword(user_id=token_data['user_id'], timestamp=timestamp, token=token)
        db.session.add(reset_obj)
        db.session.commit()
        return token

    @classmethod
    def getToken(cls, user_id, token):
        return ResetPassword.query.filter_by(user_id=user_id, token=token).first()

    @staticmethod
    def verify_reset_token(token):
        s = Serializer(app.config['SECRET_KEY'])
        try:
            token_data = s.loads(token)
            token_from_db = ResetPassword.getToken(token_data['user_id'], token)
            if not token_from_db.is_valid:
                return {"status": False, "message":"Reset token has already been used.", "user":Voter.getVoterRecord(token_data['user_id'])}
            else:
                token_from_db.is_valid = False
                db.session.commit()
        except itsdangerous.exc.SignatureExpired:
            return {"status": False, "message":"Reset token has expired.", "user":None}
        return {"status":True, "message":"Password reset successful!", "user":Voter.getVoterRecord(token_data['user_id'])}

class Voter(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    cin = db.Column(db.String(30), unique=True, nullable=False)
    name = db.Column(db.String(255), nullable=False)
    # username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(30), unique=True, nullable=False)
    dept = db.Column(db.String(4), db.ForeignKey('department.dept_code'), nullable=False)
    imagefile = db.Column(db.String(20), nullable=False, default='default.jpg')
    password = db.Column(db.String(60), nullable=False)
    join_year = db.Column(db.Integer, nullable=False, default=2016)
    is_admin = db.Column(db.Boolean, default=False, nullable=False)

    def __repr__(self):
        return f"Voter('{self.name}', '{self.cin}')"
    
    def to_dict(self):
        return {
            'id' : self.id,
            'cin': self.cin,
            'name': self.name,
            'email': self.email,
            'dept': self.dept,
            'imagefile': self.imagefile,
            'join_year': self.join_year,
            'is_admin': self.is_admin
        }
    
    @classmethod
    def getVoterRecord(cls, voter_id):
        return Voter.query.where(Voter.id==voter_id).first()

    @classmethod    
    def getVoterByEmail(cls, email):
        return Voter.query.filter_by(email=email).first()
    
    @classmethod
    def getVoterByID(cls, id):
        return Voter.query.filter_by(id=id).first()

class CandidateList(db.Model):
    election_id = db.Column(db.String(5), db.ForeignKey('election.election_id'), primary_key=True, nullable=False)
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    voter_id = db.Column(db.Integer, db.ForeignKey('voter.id'), primary_key=True, nullable=False)
    voter = db.relationship('Voter', backref='vote', lazy=True) # one candidate refers to one voter details

    def __repr__(self):
        return f"Candidate('{self.id}', '{self.voter_id}')"
    
    @classmethod
    def getCandidatesInList(cls, election_id):
        return Voter.query.join(CandidateList.query.filter(CandidateList.election_id == election_id)).all()
    
    @classmethod
    def getAllCandidates(cls, election_id):
        return ( CandidateList.query 
                            .filter(CandidateList.election_id == election_id) 
                            .join(Voter)
                            .order_by(CandidateList.id.asc())
                            .all() )
    
    @classmethod
    def getElectionsWhereVoterIsInCandidateList(cls, voter_id):
        return Election.query.join(CandidateList.query.filter(CandidateList.voter_id == voter_id)).all()

    @classmethod
    def getCandidateCount(cls, election_id):
        return CandidateList.query.filter_by(election_id=election_id).count()

    def to_dict(self):
        return {
            'id' : self.id,
            'election_id': self.election_id,
            'voter_id': self.voter_id,
        }

class Election(db.Model):
    election_id = db.Column(db.String(5), primary_key=True, nullable=False)
    election_title = db.Column(db.String(255), nullable=False)
    create_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    start_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    end_date = db.Column(db.DateTime, db.CheckConstraint("end_date > start_date"), nullable=False)
    public_key = db.Column(db.Text, nullable=False, unique=True)
    max_attempt = db.Column(db.Integer, nullable=False, default=3)
    election_state = db.Column(db.String(30), db.CheckConstraint("election_state in ('upcoming', 'ongoing', 'over', 'counting_finished','past')"))
    results_published = db.Column(db.Boolean, nullable=False, default=False)
    # is_over = db.Column(db.Boolean, nullable=False)

    def __repr__(self):
        return f"Election('{self.election_id}', '{self.election_title}', '{self.start_date}', '{self.end_date}'"
    
    @classmethod
    def getElectionRecord(cls, election_id):
        return Election.query.where(Election.election_id == election_id).first()


class Casted_Vote(db.Model):
    election_id = db.Column(db.String(5), db.ForeignKey('election.election_id'), primary_key=True, nullable=False)
    id = db.Column(db.Integer, db.ForeignKey('voter.id'), primary_key=True, nullable=False)
    # candidate_id = db.Column(db.String(5), db.ForeignKey('candidate.candidate_id'), nullable=False)

    def __repr__(self):
        return f"Casted_Vote('{self.election_id}', '{self.id}', '{self.candidate_id}')"

class Voter_List(db.Model):
    election_id = db.Column(db.String(5), db.ForeignKey('election.election_id'), primary_key=True, nullable=False)
    id = db.Column(db.Integer, db.ForeignKey('voter.id'), primary_key=True, nullable=False)
    tries = db.Column(db.Integer, default=0, nullable=False)
    token = db.Column(db.String(255), unique=True, nullable=True)
    is_registered = db.Column(db.Boolean, nullable=False, default=False)

    def __repr__(self):
        return f"VoterList('{self.election_id}', '{self.id}')"

    @classmethod
    def getVotersInList(cls, election_id):
        return Voter.query.join(Voter_List.query.filter(Voter_List.election_id == election_id)).all()

    @classmethod
    def getVoterRecord(cls, election_id, voter_id):
        return Voter_List.query.filter_by(id=voter_id, election_id = election_id).first()

    @classmethod
    def getVoterToken(cls, election_id, voter_id):
        return Voter_List.query.filter_by(id=voter_id,election_id=election_id).first().token

    @classmethod
    def getVoterTries(cls, election_id, voter_id):
        print(f"election_id: {election_id}, voter_id:{voter_id}")
        return Voter_List.query.filter_by(id=voter_id,election_id=election_id).first().tries

    @classmethod
    def incrementVoterTries(cls, election_id, voter_id):
        Voter_List.getVoterRecord(election_id, voter_id).tries += 1

    @classmethod
    def getElectionsForVoter(cls, voter_id):
        return Election.query.join(Voter_List.query.filter(Voter_List.id == voter_id)).all()

class Department(db.Model):
    dept_code = db.Column(db.String(4), primary_key=True, nullable=False)
    dept_name = db.Column(db.String(50), unique=True, nullable=False)

    def __repr__(self):
        return f"Department('{self.dept_code}', '{self.dept_name}')"

    @classmethod
    def getAllDepartments(cls):
        return Department.query.all()

    def getDepartmentString(self):
        return f"{self.dept_code}    -    {self.dept_name}"

class Results(db.Model):
    election_id = db.Column(db.String(5), db.ForeignKey('election.election_id'), primary_key=True, nullable=False)
    candidate_id = db.Column(db.String(5), db.ForeignKey('candidate.candidate_id'), primary_key=True, nullable=False)
    total_votes = db.Column(db.Integer, nullable=False, default=0)

    def __repr__(self):
        return f"Results('{self.election_id}', '{self.candidate_id}', '{self.total_votes}')"