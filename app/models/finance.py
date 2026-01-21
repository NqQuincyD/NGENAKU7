from app.extensions import db
from datetime import datetime

class Tithe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float)
    currency = db.Column(db.String(3), default='ZAR')
    date = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    member_id = db.Column(db.Integer, db.ForeignKey('member.id'), nullable=True) # Can be anonymous
    method = db.Column(db.String(64)) # Cash, EFT, etc.
    
class Offering(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float)
    currency = db.Column(db.String(3), default='ZAR')
    category = db.Column(db.String(64)) # Local, Conference, Mission, etc.
    description = db.Column(db.String(128))
    date = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    member_id = db.Column(db.Integer, db.ForeignKey('member.id'), nullable=True)
    method = db.Column(db.String(64))
