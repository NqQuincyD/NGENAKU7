from app import create_app, db
from app.models.core import User, Member

app = create_app()

with app.app_context():
    users = User.query.all()
    members = Member.query.all()
    
    print(f"Total Users: {len(users)}")
    print(f"Total Members: {len(members)}")
    
    print("\nUsers without Member records:")
    for u in users:
        # Check if email matches
        member = Member.query.filter_by(email=u.email).first()
        if not member:
            print(f"- {u.username} ({u.email}) [Role: {u.role.name}]")
