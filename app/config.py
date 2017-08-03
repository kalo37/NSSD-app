import os
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_sslify import SSLify


def set_config(app):
    """Set configuration for Flask app
    """

    SSLify(app)
    Bootstrap(app)
    app.config.from_object(os.environ['APP_SETTINGS'])

    # Set up SQLAlchemy DB
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
    db = SQLAlchemy(app)
    return db


max_docs = 500
