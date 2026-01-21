from app import create_app, db
from app.models.core import User, Member
from sqlalchemy import text
import sys

app = create_app()

def migrate():
    with app.app_context():
        print("Starting migration...")
        
        # 1. Add column safely
        try:
            with db.engine.connect() as conn:
                conn.execute(text("ALTER TABLE member ADD COLUMN user_id INT"))
                conn.execute(text("ALTER TABLE member ADD CONSTRAINT fk_member_user FOREIGN KEY (user_id) REFERENCES user(id)"))
                conn.commit()
                print("Added user_id column.")
        except Exception as e:
            print(f"Column addition skipped (likely exists): {str(e)}")

        # 2. Sync Data
        print("Syncing Users...")
        try:
            users = User.query.all()
            count = 0
            for user in users:
                member = Member.query.filter_by(email=user.email).first()
                if member:
                    if member.user_id != user.id:
                        member.user_id = user.id
                        print(f"Linked {user.username}")
                        count += 1
            
            db.session.commit()
            print(f"Synced {count} users.")
        except Exception as e:
            print(f"Data sync error: {e}")

if __name__ == '__main__':
    migrate()
