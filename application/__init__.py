from flask import Flask
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import sessionmaker
from flask_uploads import UploadSet, configure_uploads
from flask_msearch import Search
from flask_login import LoginManager
from flask_migrate import Migrate
import pyrebase

import os

import config


#Setting up App and Database
app = Flask(__name__)
app.config['SECRET_KEY'] = config.secret_key
#url = f"postgresql://postgres:{config.db_pw}@localhost:5432"
url = config.rdb_url
app.config['SQLALCHEMY_DATABASE_URI']=url

#Setting up firebase
fireBaseConfig = config.secret_firebase_config
firebase = pyrebase.initialize_app(fireBaseConfig)
img_storage = firebase.storage()


db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

#Setup search from webpage
search = Search()
search.init_app(app)

#Setup database migration
migrate = Migrate(app, db)
with app.app_context():
    if db.engine.url.drivername == "sqlite":
        migrate.init_app(app, db, render_as_batch=True)
    else:
        migrate.init_app(app, db)

#Setup login_manager for customer
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'customerLogin'
login_manager.needs_refresh_message_category='danger'
login_manager.login_message = "Please login first"
login_manager.login_message_category = "danger"

#Import routes from different folders
from application.admin import routes
from application.products import routes
from application.carts import routes
from application.customer import routes