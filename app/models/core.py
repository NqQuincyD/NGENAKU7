from app.extensions import db, login_manager
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

class Role(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    permissions = db.Column(db.Integer)
    users = db.relationship('User', backref='role', lazy='dynamic')

    def __repr__(self):
        return f'<Role {self.name}>'

class Church(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), index=True)
    type = db.Column(db.String(64)) # Local, Conference, Union, Division
    parent_id = db.Column(db.Integer, db.ForeignKey('church.id'))
    children = db.relationship('Church', backref=db.backref('parent', remote_side=[id]))
    members = db.relationship('Member', backref='church', lazy='dynamic')

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    role_id = db.Column(db.Integer, db.ForeignKey('role.id'))
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @property
    def is_admin(self):
        return self.role and self.role.name == 'Admin'

    @property
    def is_director(self):
        return self.role and self.role.name == 'Director'

    @property
    def is_treasurer(self):
        return self.role and self.role.name == 'Treasurer'

    @property
    def is_staff(self):
        return self.role and self.role.name in ['Admin', 'Director', 'Treasurer']

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))

class Member(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(64))
    last_name = db.Column(db.String(64))
    email = db.Column(db.String(120), unique=True)
    phone = db.Column(db.String(20))
    dob = db.Column(db.Date)
    baptism_date = db.Column(db.Date)
    church_id = db.Column(db.Integer, db.ForeignKey('church.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    
    # Relationships
    user = db.relationship('User', backref=db.backref('member', uselist=False))
    tithes = db.relationship('Tithe', backref='member', lazy='dynamic')
    offerings = db.relationship('Offering', backref='member', lazy='dynamic')
    commitments = db.relationship('Commitment', backref='member', lazy='dynamic')

    def __repr__(self):
        return f'<Member {self.first_name} {self.last_name}>'

class SystemSetting(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    church_name = db.Column(db.String(128), default='Central Tshabalala SDA')
    conference_name = db.Column(db.String(128))
    currency_symbol = db.Column(db.String(10), default='R')
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
