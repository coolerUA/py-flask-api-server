"""This is init module."""

from flask import Flask
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
from werkzeug.contrib.fixers import ProxyFix
from bson import ObjectId
import json
import datetime


class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        return json.JSONEncoder.default(self, o)


UPLOAD_FOLDER = '/opt/dashboard/flask/static'

# Place where app is defined
app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = 'secret'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = datetime.timedelta(days=1)
app.wsgi_app = ProxyFix(app.wsgi_app)
flask_bcrypt = Bcrypt(app)
jwt = JWTManager(app)
app.json_encoder = JSONEncoder
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

from app import auth
from app import usersData
from app import teamsData
from app import pictures
from app import queue
from app import campaigns
from app.controllers import *
