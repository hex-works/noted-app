"""Production settings for NTT-122."""
import pytest
from flask import request, url_for
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


def production_app_with_scheme_route(monkeypatch):
    monkeypatch.setenv("APP_ENV", "production")
    monkeypatch.setenv("SECRET_KEY", "a-long-random-production-key")
    app = create_app(TEST_DB)

    @app.get("/_test/scheme")
    def scheme():
        return {
            "scheme": request.scheme,
            "host": request.host,
            "remote_addr": request.remote_addr,
            "health_url": url_for("health", _external=True),
        }

    return app


def test_production_trusts_the_proxy_https_header(monkeypatch):
    app = production_app_with_scheme_route(monkeypatch)
    assert isinstance(app.wsgi_app, ProxyFix)

    data = app.test_client().get(
        "/_test/scheme", headers={"X-Forwarded-Proto": "https"}
    ).get_json()

    assert data["scheme"] == "https"
    assert data["health_url"] == "https://localhost/health"


def test_production_without_the_header_stays_http(monkeypatch):
    app = production_app_with_scheme_route(monkeypatch)
    data = app.test_client().get("/_test/scheme").get_json()
    assert data["scheme"] == "http"


def test_production_ignores_forwarded_for_and_host(monkeypatch):
    app = production_app_with_scheme_route(monkeypatch)
    data = app.test_client().get(
        "/_test/scheme",
        headers={
            "X-Forwarded-Proto": "https",
            "X-Forwarded-For": "203.0.113.9",
            "X-Forwarded-Host": "evil.example",
        },
    ).get_json()

    assert data["host"] == "localhost"
    assert data["remote_addr"] != "203.0.113.9"
    assert data["health_url"] == "https://localhost/health"


def test_development_does_not_add_the_proxy_fix(monkeypatch):
    monkeypatch.delenv("APP_ENV", raising=False)
    app = create_app(TEST_DB)
    assert not isinstance(app.wsgi_app, ProxyFix)
