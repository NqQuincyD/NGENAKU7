from app import create_app, db
from app.models.core import User, Role
import sys

app = create_app()

with app.app_context():
    try:
        # Check tables
        print("Tables in DB:", db.metadata.tables.keys())
        
        # create roles
        roles = ['Admin', 'Director', 'Treasurer', 'Member']
        for role_name in roles:
            if not Role.query.filter_by(name=role_name).first():
                print(f"Creating role: {role_name}")
                role = Role(name=role_name)
                db.session.add(role)
            else:
                print(f"Role exists: {role_name}")
        db.session.commit()

        # create admin user
        admin_role = Role.query.filter_by(name='Admin').first()
        if not User.query.filter_by(username='admin').first():
            print("Creating admin user...")
            u = User(username='admin', email='admin@example.com', role=admin_role)
            u.set_password('password')
            db.session.add(u)
            db.session.commit()
            print("Admin user created.")
        else:
            print("Admin user already exists.")
            
    except Exception as e:
        print(f"Error seeding database: {e}")
        db.session.rollback()
        sys.exit(1)
