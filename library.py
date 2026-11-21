from flask import Blueprint, render_template,request
from flask_login import current_user, login_required

from models import Composition, db
from sqlalchemy import func
bp = Blueprint("library", __name__, url_prefix="/library")


@bp.get("/")
@login_required
def index():
    q = request.args.get("q", "").strip()

    query = db.select(Composition).where(
        Composition.user_id == current_user.id
    )

    if q:
        query = query.where(
            func.lower(Composition.title).contains(q.lower())
        )

    compositions = db.session.execute(
        query.order_by(
            Composition.updated_at.desc(),
            Composition.id.desc()
        )
    ).scalars().all()

    return render_template(
        "library/index.html",
        compositions=compositions,
    )