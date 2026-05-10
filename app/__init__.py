from flask import Flask
from .extensions import db, migrate, jwt, cors
from .config import Config

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    cors.init_app(app, resources={r"/api/*": {"origins": "*"}})

    from .routes.auth import auth_bp
    from .routes.goals import goals_bp
    from .routes.payments import payments_bp
    from .routes.coach import coach_bp
    from .routes.user import user_bp

    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(goals_bp, url_prefix="/api/goals")
    app.register_blueprint(payments_bp, url_prefix="/api/payments")
    app.register_blueprint(coach_bp, url_prefix="/api/coach")
    app.register_blueprint(user_bp, url_prefix="/api/user")
    
    from . import models

    with app.app_context():
        db.create_all()

    return app