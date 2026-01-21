from flask import Flask
from config import Config
from app.extensions import db, migrate, login_manager

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize Flask extensions
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    # Register Blueprints
    from app.routes.main import bp as main_bp
    app.register_blueprint(main_bp)

    from app.routes.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')

    from app.routes.members import bp as members_bp
    app.register_blueprint(members_bp, url_prefix='/members')
    
    from app.routes.finance import bp as finance_bp
    app.register_blueprint(finance_bp, url_prefix='/finance')

    from app.routes.reports import bp as reports_bp
    app.register_blueprint(reports_bp, url_prefix='/reports')

    from app.routes.stewardship import bp as stewardship_bp
    app.register_blueprint(stewardship_bp, url_prefix='/stewardship')

    return app
