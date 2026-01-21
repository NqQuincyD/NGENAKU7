from app.extensions import db
from datetime import datetime

class Commitment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    member_id = db.Column(db.Integer, db.ForeignKey('member.id'))
    type = db.Column(db.String(64)) # Time, Talent, Treasure (Pledge)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(64)) # Active, Completed
    
    status = db.Column(db.String(64)) # Active, Completed

class Resource(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128))
    type = db.Column(db.String(64)) # Video, PDF, Sermon
    url = db.Column(db.String(256))
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)

class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128))
    date = db.Column(db.DateTime)
    location = db.Column(db.String(128))
    type = db.Column(db.String(64)) # Seminar, Stewardship Sabbath
    description = db.Column(db.Text)

class CommitteeMember(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    member_id = db.Column(db.Integer, db.ForeignKey('member.id'))
    role = db.Column(db.String(64)) # Chairperson, Secretary, Member
    term_start = db.Column(db.Date)
    term_end = db.Column(db.Date, nullable=True)
    status = db.Column(db.String(32), default='Active')

    member = db.relationship('Member', backref='committee_roles', lazy=True)

class Audit(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    year = db.Column(db.Integer)
    quarter = db.Column(db.Integer) # 1, 2, 3, 4
    date = db.Column(db.Date)
    auditor = db.Column(db.String(128))
    status = db.Column(db.String(64)) # Scheduled, Pending, Completed, Compliant, Non-Compliant
    findings = db.Column(db.Text)
    recommendations = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
