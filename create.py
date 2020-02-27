import os

from flask import Flask, render_template, request
from models import *

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "postgres://fnaceikrcawgxt:e44504611a26d3968483989b5e633f163f72e23fd377863088e222882cb4dc5a@ec2-52-87-58-157.compute-1.amazonaws.com:5432/d9vfdhmk4r3mle"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)

def main():
    db.create_all()

if __name__ == "__main__":
    with app.app_context():
        main()
