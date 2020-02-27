import os
import sys
import requests
import json

from flask import Flask, session, request, jsonify, redirect, url_for, abort
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

from sqlalchemy.sql.expression import cast
import sqlalchemy

from flask import render_template
from flask_table import Table, Col

app = Flask(__name__)
app.secret_key = "1234"


from data import *
from models import *
'''
# Check for environment variable
if not os.getenv("postgres://mgfiexsidkjjcz:e7120423339984e7d419f4d8cc9377d6de227c7832a5b9cd36965c68735eb4be@ec2-34-235-108-68.compute-1.amazonaws.com:5432/d20jiml8va0i09"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)
'''
# Set up database

app.config["SQLALCHEMY_DATABASE_URI"] = "postgres://fnaceikrcawgxt:e44504611a26d3968483989b5e633f163f72e23fd377863088e222882cb4dc5a@ec2-52-87-58-157.compute-1.amazonaws.com:5432/d9vfdhmk4r3mle"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)


@app.route("/", methods = ["GET", "POST"])
def index():
    if not session.get('logged_in'):
        return render_template("homepage.html")
    else:
        comments = Comment.query.filter().all()
        return render_template("signedin.html", name=session.get('username'), comments=comments)

@app.route("/home", methods = ["GET","POST"])
def home():
    #name = request.form.get("name")
    if not session.get('logged_in'):
        return render_template("homepage.html")
    comments = Comment.query.filter().all()
    return render_template("signedin.html", name=session.get('username'), comments = comments)

@app.route("/signup", methods = ["GET","POST"])
def signup():
    return render_template("signup.html")

@app.route("/signedin", methods = ["POST"])
def signedin():

    if request.method == 'POST':
        session['username'] = request.form.get("name")
        session['password'] = request.form.get("password")
        check_username = accounts.query.filter(accounts.username.like(session.get('username'))).first()
    else:
        return render_template("homepage.html")

    if (check_username == None) or (check_username.username == session.get('username') and check_username.password != session.get('password')):
        session.pop('username', None)
        return render_template("incorrect_login.html", check_user=check_username)
    else:
        session['logged_in'] = True
        comments = Comment.query.filter().all()
        return render_template("signedin.html", name=session.get('username'), comments=comments)
    

@app.route("/books", methods = ["GET", "POST"])
def bookpage():
    book = books.query.filter().all()
    table = Data(book)

    if not session.get('logged_in'):
        return render_template("signup.html")
    
    return render_template("books.html", table=table)

@app.route("/results", methods = ["GET", "POST"])
def results():
    qry=request.form.get("query")
    
    result = books.query.filter((books.isbn.contains(qry)) | (books.title.contains(qry)) | (books.author.contains(qry)) | (cast(books.published, sqlalchemy.String).contains(qry))).all()
    selected_book = result
    result=Data(result)

    return render_template("results.html",query=qry, result=result, selected_book=selected_book)

@app.route("/created_account", methods = ["POST"])
def created_account():
    user = request.form.get("username")
    password = request.form.get("password")
    
    check_user = accounts.query.filter(accounts.username.like(user)).first()

    if check_user == None:
        new_account = accounts(username=user, password=password)
        db.session.add(new_account)
        db.session.commit()
        return render_template("created_account.html", name=user)
    else:
        return render_template("incorrect_login.html", check_user=check_user)

@app.route("/loggedout", methods = ["GET", "POST"])
def loggedout():
    session.clear()
    return render_template("loggedout.html")

@app.route("/gen_comments", methods = ["POST"])
def gen_comments():

    if not session.get('logged_in'):
        return render_template("signup.html")
    else:
        comment = request.form.get("comment")
        new_comment = Comment(name=session.get('username'), body=comment, timestamp=datetime.datetime.now())
        db.session.add(new_comment)
        db.session.commit()
    
    
        new_comment = Comment.query.filter().all()
        table = commentdis(new_comment)

        return render_template("signedin.html", table=table, name=session.get('username'), comments=new_comment)

@app.route('/bookpage/<string:isbn>', methods = ["GET", "POST"])
def book_page(isbn):

    current_book = books.query.filter(books.isbn.like(isbn)).first()

    res = requests.get("https://www.goodreads.com/book/review_counts.json",
                       params={"key": "7iJBoUJSG11DyPiJl1aUwQ", "isbns": isbn})        

    average_rating=res.json()['books'][0]['average_rating']
    work_ratings_count=res.json()['books'][0]['work_ratings_count']
    
    if not session.get('logged_in'):
        return render_template("signup.html")


    if request.method=="POST":
        check_review = bookComments.query.filter(bookComments.name.like(session.get('username')), bookComments.isbn.like(isbn)).first()
        if check_review == None:
            body = request.form.get("book_comment")
            rating = request.form.get("rating")
            new_review = bookComments(name=session.get('username'), body=body, rating=rating, isbn=isbn)
            db.session.add(new_review)
            db.session.commit()
            book_comment = bookComments.query.filter(bookComments.isbn.like(isbn)).all()
            return render_template("goodreads.html", current_book=current_book, average_rating=average_rating, work_ratings_count=work_ratings_count, book_comment=book_comment)
        else:
            if check_review.name==session.get('username') and check_review.isbn==isbn:
                return jsonify("error: Already gave a review for the book"), 422
    else:
        book_comment = bookComments.query.filter(bookComments.isbn.like(isbn)).all()
        return render_template("goodreads.html", current_book=current_book, average_rating=average_rating, work_ratings_count=work_ratings_count, book_comment=book_comment)
    


@app.route("/api/<string:isbn>", methods = ["GET", "POST"])
def api(isbn):
    current_book = books.query.filter(books.isbn.like(isbn)).first()
    if current_book==None:
        return render_template("404.html")

    res = requests.get("https://www.goodreads.com/book/review_counts.json",
                       params={"key": "7iJBoUJSG11DyPiJl1aUwQ", "isbns": isbn})        

    average_rating=res.json()['books'][0]['average_rating']
    work_ratings_count=res.json()['books'][0]['work_ratings_count']

    book = {
        "title": current_book.title,
        "author": current_book.author,
        "year": current_book.published,
        "isbn": current_book.isbn,
        "review_count": work_ratings_count,
        "average_score": average_rating
    }

    api = json.dumps(book)
    return render_template("api.json", api=api)

