from app import create_app, db
from app.models.core import User, Member, Role

app = create_app()

with app.app_context():
    users = User.query.all()
    count = 0
    
    for u in users:
        # Check if Linked Member exists
        member = Member.query.filter_by(email=u.email).first()
        
        if not member:
            print(f"Creating Member for User: {u.username} ({u.email})")
            new_member = Member(first_name=u.username, email=u.email)
            db.session.add(new_member)
            count += 1
            
    if count > 0:
        db.session.commit()
        print(f"Successfully created {count} missing Member records.")
    else:
        print("All users already have associated Member records.")
