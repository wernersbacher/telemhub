from flask import render_template
import typing as t

from flask_login import current_user
from sqlalchemy import and_

from database import db
from models.models import Notification


def render_template_extra(template_name_or_list: t.Union[str, t.List[str]], **context: t.Any) -> str:
    """ extends render_template to pass arguments which have to be callled ANYTIME"""
    # get user notifications
    notif_count = db.session.query(Notification).filter(
        and_(Notification.owner == current_user, Notification.read == False)).count()

    return render_template(template_name_or_list, notif_count=notif_count, **context)
