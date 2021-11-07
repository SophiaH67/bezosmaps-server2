from flask import Flask

app = Flask(__name__)
app.app_context().push()

from lib.db import db

db.create_all()