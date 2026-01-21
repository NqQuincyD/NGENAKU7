from app import create_app, db
from app.models.stewardship import CommitteeMember, Audit
from app.models.core import SystemSetting

from app.models.core import Role, User

app = create_app()
with app.app_context():
    db.create_all()
    print("Database updated: All system tables created.")

    # Seed Roles
    roles = ['Admin', 'Director', 'Treasurer', 'Member']
    for role_name in roles:
        if not Role.query.filter_by(name=role_name).first():
            role = Role(name=role_name)
            db.session.add(role)
            print(f"   Created role: {role_name}")
    
    db.session.commit()

    # Seed Default Admin
    admin_role = Role.query.filter_by(name='Admin').first()
    if not User.query.filter_by(username='admin7').first():
        user = User(username='admin7', email='admin@example.com', role=admin_role)
        user.set_password('Admin7#')
        db.session.add(user)
        print("   Created default admin: admin7")
    
    db.session.commit()
