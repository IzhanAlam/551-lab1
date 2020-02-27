from flask_sqlalchemy import SQLAlchemy
from flask import Flask, render_template, request
import datetime

db = SQLAlchemy()

class accounts(db.Model):
    __tablename__ = "accounts"
    #id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, primary_key=True)
    password = db.Column(db.String, nullable=False)

    def __init__(self, username, password):
        self.username = username
        self.password = password

    def get_id(self):
        return self.username
    
    def is_unique(self):
        return True


    def is_active(self):
        return True
    def is_anon(self):
        return False

    


class books(db.Model):
    __tablename__ = "books"
    isbn = db.Column(db.String, primary_key=True)
    #isbn = db.Column(db.Integer, nullable=False)
    title = db.Column(db.String, nullable=False)
    author = db.Column(db.String, nullable=False)
    published = db.Column(db.Integer, nullable=False)


class Comment(db.Model):
    __tablename__ = "gen_comments"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable = False)
    body = db.Column(db.String)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.datetime.now)
    

    def __init__(self, name, body, timestamp):
        self.name = name
        self.body = body
        self.timestamp = timestamp

class bookComments(db.Model):
    __tablename__ = "book_comments"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable = False)
    body = db.Column(db.String)
    rating = db.Column(db.String, nullable = False)
    isbn = db.Column(db.String, nullable=False)
    
    def __init__(self, name, body, rating, isbn):
        self.name = name
        self.body = body
        self.rating = rating
        self.isbn = isbn
