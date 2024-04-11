from flask import Flask

app = Flask(__name__)

app.config['SECRET_KEY'] = 'thisisaLLCMSwebapp'

from app import authentication
from app import connect
from app import views
from app import register
from app import member_views
from app import manage_users
from app import manager_views
from app import utility
from app import tutor_views
from app import forms