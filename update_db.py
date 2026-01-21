from app import create_app, db
from app.models.stewardship import CommitteeMember, Audit
from app.models.core import SystemSetting

app = create_app()
with app.app_context():
    db.create_all()
    print("Database updated: All system tables created.")
