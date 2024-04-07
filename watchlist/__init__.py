import os
from flask import Flask
from dotenv import load_dotenv
from pymongo import MongoClient

from watchlist.routes import pages

# Load environment variables - for mongoDB and secret passkey
load_dotenv()


# Create a function create_app which sets MongoDB_URI app config from the environment variable
# Mongo Default Database and registers blueprint pages.

def create_app():

    app = Flask(__name__)
    app.config['MONGODB_URI'] = os.environ.get('MONGODB_URI')
    app.config["SECRET_KEY"] = os.environ.get(
        "SECRET_KEY", "pf9Wkove4IKEAXvy-cQkeDPhv9Cb3Ag-wyJILbq_dFw"
    )
    app.db = MongoClient(app.config['MONGODB_URI']).get_default_database()

    app.register_blueprint(pages)

    return app