from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)

    app.config.from_object("config.Config")

    db.init_app(app)

    from app.credits import bp as credits_bp
    from app.web import bp as web_bp

    app.register_blueprint(credits_bp, url_prefix="/api/credits")

    app.register_blueprint(web_bp, url_prefix="/credits")

    with app.app_context():
        db.create_all()

    return app
