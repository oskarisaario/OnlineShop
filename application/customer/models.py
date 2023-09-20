from datetime import datetime
from flask_login import UserMixin
import json

from application import app, db, login_manager

@login_manager.user_loader
def user_loader(user_id):
    return Customer.query.get(user_id)

################################### Model for Customer-user ################################### 
class Customer(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=False, nullable=False)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(50), unique=True, nullable=False)
    contact = db.Column(db.String(50), unique=False, nullable=False)
    password = db.Column(db.String(200), unique=False, nullable=False)

    country = db.Column(db.String(50), unique=False, nullable=False)
    city = db.Column(db.String(50), unique=False, nullable=False)
    address = db.Column(db.String(50), unique=False, nullable=False)
    zipcode = db.Column(db.Integer(), unique=False, nullable=False)
    date_registered = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return '<Customer %r>' % self.username
    

################################### Encodes Json dict from products in Shoppingcart to database ################################### 
class JsonEncodedDict(db.TypeDecorator):
    impl =db.Text

    def process_bind_param(self, value, dialect):
        if value is None:
            return '{}'
        else:
            return json.dumps(value)
        
################################### Loads values from database ###################################     
    def process_result_value(self, value, dialect):
        if value is None:
            return {}
        else:
            return json.loads(value)

###################################  Model for customers order ################################### 
class CustomerOrder(db.Model):
    id =db.Column(db.Integer, primary_key=True)
    invoice = db.Column(db.String(20), unique=True, nullable=False)
    status = db.Column(db.String(20), default='Pending', nullable=False)
    customer_id = db.Column(db.Integer, unique=False, nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    orders = db.Column(JsonEncodedDict)

    def __repr__(self):
        return '<CustomerOrder %r>' % self.invoice


with app.app_context():
    db.create_all()