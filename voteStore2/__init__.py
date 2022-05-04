from flask import Flask
from flask_sqlalchemy import SQLAlchemy
# import flask_mail

# from flask_wtf import FlaskForm
# from wtforms import StringField, SubmitField
# from wtforms.validators import DataRequired

app = Flask(__name__)
# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost/election'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SECRET_KEY'] = '6ed92a393d113812533944e21b26b07a'

db = SQLAlchemy(app)


from voteStore2 import routes