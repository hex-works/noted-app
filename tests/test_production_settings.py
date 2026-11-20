"""Production settings for NTT-122."""
import pytest
from werkzeug.middleware.proxy_fix import ProxyFix

from app import create_app
from config import DEV_SECRET_KEY

TEST_DB = {"SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:", "TESTING": True}


def test_development_keeps_the_dev_defaults(monkeypatch):
    monkeypatch.delenv("APP_ENV", raising=False)
    app = create_app(TEST_DB)
    assert app.config["SESSION_COOKIE_SECURE"] is False
    assert app.debug is False


@pytest.mark.parametrize("secret", [None, "", DEV_SECRET_KEY])
def test_production_refuses_to_start_without_a_real_secret_key(monkeypatch, secret):
    monkeypatch.setenv("APP_ENV", "production")
    if secret is None:
        monkeypatch.delenv("SECRET_KEY", raising=False)
    else:
        monkeypatch.setenv("SECRET_KEY", secret)
    with pytest.raises(RuntimeError, match="SECRET_KEY"):
        create_app(TEST_DB)


def test_production_settings(monkeypatch):
    monkeypatch.setenv("APP_ENV", "Production")
    monkeypatch.setenv("SECRET_KEY", "a-long-random-production-key")
    app = create_app(TEST_DB)
    assert app.config["SECRET_KEY"] == "a-long-random-production-key"
    assert app.debug is False
    assert app.config["SESSION_COOKIE_SECURE"] is True
    assert app.config["REMEMBER_COOKIE_SECURE"] is True
    assert app.config["SESSION_COOKIE_SAMESITE"] == "Lax"


def test_production_trusts_the_proxy_https_header(monkeypatch):
    monkeypatch.setenv("APP_ENV", "production")
    monkeypatch.setenv("SECRET_KEY", "a-long-random-production-key")
    app = create_app(TEST_DB)
    assert isinstance(app.wsgi_app, ProxyFix)


def test_development_does_not_add_the_proxy_fix(monkeypatch):
    monkeypatch.delenv("APP_ENV", raising=False)
    app = create_app(TEST_DB)
    assert not isinstance(app.wsgi_app, ProxyFix)
