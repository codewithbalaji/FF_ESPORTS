from flask import Flask
from pymongo import MongoClient
from pymongo.server_api import ServerApi
from config import Config

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize MongoDB
    client = MongoClient(app.config['MONGO_URI'], server_api=ServerApi('1'))
    app.db = client['esports_db']

    from app.routes import bp as main_bp
    app.register_blueprint(main_bp)

    return app