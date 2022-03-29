from flask import Flask, render_template, make_response
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost/election'
# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost/users'
db = SQLAlchemy(app)

class Voter(db.Model):
    voter_id = db.Column(db.Integer, primary_key=True, nullable=False)
    voter_cin = db.Column(db.String(16), unique=True, nullable=False)
    voter_name = db.Column(db.String(30), nullable=False)
    dept_code = db.Column(db.String(6), db.ForeignKey('department.dept_code') ,nullable=False)

    def __repr__(self):
        return f"Voter('{self.voter_id}', '{self.voter_name}')"

class Candidate(db.Model):
    candidate_id = db.Column(db.String(5), primary_key=True, nullable=False)
    candidate_name = db.Column(db.String(30), unique=True, nullable=False)
    voters = db.relationship('Voter', backref='vote', lazy=True) # one candidate can get votes from many voters, so One-To-Many relationship

    def __repr__(self):
        return f"Candidate('{self.candidate_id}', '{self.candidate_name}')"

class Election(db.Model):
    election_id = db.Column(db.String(5), primary_key=True, nullable=False)
    election_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    is_over = db.Column(db.Boolean, nullable=False)

    def __repr__(self):
        return f"Election('{self.election_id}', '{self.election_date}', '{self.is_over}'"

class Casted_Vote(db.Model):
    election_id = db.Column(db.String(5), db.ForeignKey('election.election_id'), primary_key=True, nullable=False)
    voter_id = db.Column(db.Integer, db.ForeignKey('voter.voter_id'), primary_key=True, nullable=False)
    candidate_id = db.Column(db.String(5), db.ForeignKey('candidate.candidate_id'), nullable=False)

    def __repr__(self):
        return f"Casted_Vote('{self.election_id}', '{self.voter_id}', '{self.candidate_id}')"

class Voter_List(db.Model):
    election_id = db.Column(db.String(5), db.ForeignKey('election.election_id'), primary_key=True, nullable=False)
    voter_id = db.Column(db.Integer, db.ForeignKey('voter.voter_id'), primary_key=True, nullable=False)

    def __repr__(self):
        return f"Voter_List('{self.election_id}', '{self.voter_id}')"

class Department(db.Model):
    dept_code = db.Column(db.String(6), primary_key=True, nullable=False)
    dept_name = db.Column(db.String(50), unique=True, nullable=False)

    def __repr__(self):
        return f"Department('{self.dept_code}', '{self.dept_name}')"


@app.route("/")
def index():
    return render_template("index.html")

@app.route("/voter/<int:id>")
def voter(id):
    return render_template("voter.html", id)

@app.route("/candidate/<int:id>")
def candidate(id):
    return render_template("candidate.html", id)

@app.route("/admin")
def admin():
    return render_template("admin.html")

@app.errorhandler(404)
def page_not_found():
    return make_response(render_template("404.html"), 404)

@app.errorhandler(400)
def bad_request():
    return make_response(render_template("400.html"), 400)

@app.errorhandler(500)
def server_error():
    return make_response(render_template("500.html"), 500)

if __name__ == '__main__':
    app.run(debug=True)