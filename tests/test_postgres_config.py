"""Database URL checks for NTT-121."""
import runpy
from pathlib import Path

import pytest

CONFIG_PATH = Path(__file__).resolve().parents[1] / "config.py"


@pytest.mark.parametrize(
    ("prefix", "expected"),
    [
        (None, "sqlite:///noted.db"),
        ("sqlite", "sqlite://localhost/noted_test"),
        ("postgres", "postgresql+psycopg://localhost/noted_test"),
        ("postgresql", "postgresql+psycopg://localhost/noted_test"),
        ("postgresql+psycopg", "postgresql+psycopg://localhost/noted_test"),
    ],
)
def test_database_url(monkeypatch, prefix, expected):
    if prefix is None:
        monkeypatch.delenv("DATABASE_URL", raising=False)
    else:
        monkeypatch.setenv("DATABASE_URL", prefix + "://" + "localhost/noted_test")
    config = runpy.run_path(str(CONFIG_PATH))["Config"]
    assert config.SQLALCHEMY_DATABASE_URI == expected
