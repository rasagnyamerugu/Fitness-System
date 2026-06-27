from flask import Flask, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from dotenv import load_dotenv
import os
import joblib

load_dotenv()

from groq import Groq
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

db = SQLAlchemy()

BASE_DIR   = os.path.dirname(os.path.abspath(__file__))
MODELS_DIR = os.path.join(BASE_DIR, 'ml_models')

def _load(filename):
    path = os.path.join(MODELS_DIR, filename)
    try:
        obj = joblib.load(path)
        print(f"Loaded: {filename}")
        return obj
    except FileNotFoundError:
        print(f"Not found: {path}")
        return None
    except Exception as e:
        print(f"Failed to load {filename}: {e}")
        return None

meal_model  = _load('logreg_model.pkl')
le_exercise = _load('label_encoder_exercise.pkl')
le_meal     = _load('label_encoder_meal.pkl')


def create_app():
    app = Flask(__name__, template_folder="templates", static_folder='static', static_url_path='/')

     
    db_url = os.getenv('DATABASE_URL', '')
    db_url = db_url.split('?')[0]  
    app.config['SQLALCHEMY_DATABASE_URI']        = db_url
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        
    ca_path = os.path.join(BASE_DIR, 'ca.pem')
    if os.path.exists(ca_path):
        app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
            "connect_args": {
                "ssl_ca": ca_path
            }
        }

     
    app.secret_key = os.getenv('SECRET_KEY')

    db.init_app(app)

    
    login_manager = LoginManager()
    login_manager.init_app(app)

    from models import User

    @login_manager.user_loader
    def load_user(uid):
        return User.query.get(uid)

    @login_manager.unauthorized_handler
    def unauthorized_callback():
        return redirect(url_for('index'))

    bcrypt = Bcrypt(app)

    from routes import register_routes
    register_routes(app, db, bcrypt)

    migrate = Migrate(app, db)

    return app