from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@localhost/election'
db = SQLAlchemy(app)

class Voter(db.Model):
    voter_id = db.Column(db.Integer, primary_key=True, nullable=False)
    voter_cin = db.Column(db.String(16), unique=True, nullable=False)
    voter_name = db.Column(db.String(30), nullable=False)
    dept_code = db.Column(db.String(5), nullable=False)

    def __repr__(self):
        return f"Voter('{self.voter_id}', '{self.voter_name}')"



@app.route("/")
def hello_world():
    return "<p>Hello, World2!</p>"

app.run(debug=True)