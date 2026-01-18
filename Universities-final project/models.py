from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()


class University(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(220), nullable=False)
    description = db.Column(db.Text, nullable=False)
    image = db.Column(db.String(500), nullable=False)
    link = db.Column(db.String(500), nullable=False)

    approved = db.Column(db.Boolean, default=False, nullable=False)


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    is_admin = db.Column(db.Boolean, default=False, nullable=False)
