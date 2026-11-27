import os

from flask import Flask, render_template
from werkzeug.middleware.proxy_fix import ProxyFix

from config import DEV_SECRET_KEY, Config, is_production
from models import db
from db_cli import register_db_commands


def configure_production(app):
    """Settings for the live server (APP_ENV=production)."""
    secret_key = os.environ.get("SECRET_KEY", "")
    if not secret_key or secret_key == DEV_SECRET_KEY:
        raise RuntimeError(
            "SECRET_KEY must be set to a private value when APP_ENV=production."
        )
    app.config.update(
        SECRET_KEY=secret_key,
        DEBUG=False,
        SESSION_COOKIE_SECURE=True,
        SESSION_COOKIE_SAMESITE="Lax",
        REMEMBER_COOKIE_SECURE=True,
    )
    # Render ends HTTPS at one proxy in front of the app and sets
    # X-Forwarded-Proto to "https". Trust only that header, from one hop, so
    # generated URLs use https. X-Forwarded-For and X-Forwarded-Host are not
    # trusted: the app doesn't need them, and clients can send their own.
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=0, x_proto=1, x_host=0)


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(Config)

    if test_config is not None:
        app.config.update(test_config)

    if is_production():
        configure_production(app)

    os.makedirs(app.instance_path, exist_ok=True)

    db.init_app(app)
    register_db_commands(app)

    from auth import bp as auth_bp, login_manager
    login_manager.init_app(app)
    from compositions import bp as compositions_bp
    from library import bp as library_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(compositions_bp)
    app.register_blueprint(library_bp)

    @app.get("/")
    def index():
        return render_template("index.html")

    @app.get("/health")
    def health():
        return {"status": "ok"}

    return app
