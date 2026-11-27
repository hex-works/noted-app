"""Tests for searching My Library."""

from models import Composition, User, db
from werkzeug.security import generate_password_hash


def test_search_is_case_insensitive(logged_in_client, test_user):
    db.session.add_all([
        Composition(
            user_id=test_user.id,
            title="Class Demo",
            key_signature="C major",
            time_signature="4/4",
            tempo=100,
        ),
        Composition(
            user_id=test_user.id,
            title="Another Piece",
            key_signature="C major",
            time_signature="4/4",
            tempo=100,
        ),
    ])
    db.session.commit()

    response = logged_in_client.get("/library/?q=dEmO")

    assert response.status_code == 200

    html = response.get_data(as_text=True)

    assert "Class Demo" in html
    assert "Another Piece" not in html


def test_search_no_results(logged_in_client, test_user):
    piece = Composition(
        user_id=test_user.id,
        title="Class Demo",
        key_signature="C major",
        time_signature="4/4",
        tempo=100,
    )

    db.session.add(piece)
    db.session.commit()

    response = logged_in_client.get("/library/?q=xyz999")

    assert response.status_code == 200

    html = response.get_data(as_text=True)

    assert "No compositions match" in html
    assert "Clear search" in html
    assert "Class Demo" not in html
def test_search_only_shows_own_compositions(logged_in_client, test_user):
    other_user = User(
        username="otheruser",
        email="other@example.com",
        password_hash=generate_password_hash("test-password"),
    )
    db.session.add(other_user)
    db.session.flush()

    db.session.add_all([
        Composition(
            user_id=test_user.id,
            title="My Secret Song",
            key_signature="C major",
            time_signature="4/4",
            tempo=100,
        ),
        Composition(
            user_id=other_user.id,
            title="Other Secret Song",
            key_signature="C major",
            time_signature="4/4",
            tempo=100,
        ),
    ])
    db.session.commit()

    response = logged_in_client.get("/library/?q=secret")

    assert response.status_code == 200

    html = response.get_data(as_text=True)

    assert "My Secret Song" in html
    assert "Other Secret Song" not in html
def test_search_special_characters(logged_in_client, test_user):
    db.session.add_all([
        Composition(
            user_id=test_user.id,
            title="100% Music",
            key_signature="C major",
            time_signature="4/4",
            tempo=100,
        ),
        Composition(
            user_id=test_user.id,
            title="My_Song",
            key_signature="C major",
            time_signature="4/4",
            tempo=100,
        ),
        Composition(
            user_id=test_user.id,
            title="Normal Song",
            key_signature="C major",
            time_signature="4/4",
            tempo=100,
        ),
    ])
    db.session.commit()

    response = logged_in_client.get("/library/?q=%25")
    html = response.get_data(as_text=True)

    assert response.status_code == 200
    assert "100% Music" in html
    assert "Normal Song" not in html
    assert "My_Song" not in html

    response = logged_in_client.get("/library/?q=_")
    html = response.get_data(as_text=True)

    assert response.status_code == 200
    assert "My_Song" in html
    assert "Normal Song" not in html
    assert "100% Music" not in html