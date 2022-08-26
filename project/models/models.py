from flask_sqlalchemy import SQLAlchemy
from datetime import datetime # get dates & times

Db = SQLAlchemy()


class User(Db.Model):
    __tablename__ = 'users'
    uid = Db.Column(Db.Integer, primary_key=True, autoincrement=True)
    username = Db.Column(Db.String(64), unique=True, nullable=False)
    password = Db.Column(Db.String(128), nullable=False) # Note the max length of password
    date_registered = Db.Column( Db.DateTime, nullable = True, default = datetime.now() )


class Image(Db.Model):
    __tablename__ = 'image_information'
    image_id = Db.Column(Db.Integer, primary_key=True, autoincrement=True)
    uid = Db.Column(Db.Integer, Db.ForeignKey('users.uid'), nullable=False)
    image_name = Db.Column(Db.String(1024), nullable=False) # Note the max length of a string
    image_submitted_date = Db.Column( Db.DateTime, nullable = True, default = datetime.now() )
    image_classification_id = Db.Column(Db.Integer, Db.ForeignKey('classification_treatment_information.id'), nullable=False)
    classification_name = Db.Column(Db.String(1024), nullable=True)
    username = Db.Column(Db.String(1024), nullable=True)


class Classification(Db.Model):
    __tablename__ = 'classification_treatment_information'
    id = Db.Column(Db.Integer, primary_key=True, autoincrement=True)
    classification_name = Db.Column(Db.String(1024), nullable=False) # Note the max length of a string
    background_info = Db.Column(Db.String(1024), nullable=False) # Note the max length of a string
    treatment_info = Db.Column(Db.String(1024), nullable=False) # Note the max length of a string
    sources = Db.Column(Db.String(1024), nullable=False) # Note the max length of a string
