from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@localhost/election'
db = SQLAlchemy(app)

@app.route("/")
def hello_world():
    return "<p>Hello, World2!</p>"

app.run(debug=True)