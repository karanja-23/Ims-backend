from flask import Flask
from models import db
from flask_migrate import Migrate
from dotenv import load_dotenv
from flask_cors import CORS
import os

load_dotenv()
app = Flask(__name__)
CORS(app)

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URI')

db.init_app(app)
migrate = Migrate(app, db)