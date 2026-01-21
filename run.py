from app import create_app, db
from app.models.core import User, Role, Church, Member
from app.models.finance import Tithe, Offering

app = create_app()

@app.shell_context_processor
def make_shell_context():
    return {
        'db': db, 
        'User': User, 
        'Role': Role,
        'Church': Church,
        'Member': Member,
        'Tithe': Tithe,
        'Offering': Offering
    }

if __name__ == '__main__':
    app.run(debug=True)
