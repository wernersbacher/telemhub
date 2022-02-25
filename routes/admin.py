import os
import traceback
from functools import wraps

from flask import render_template, request, Blueprint, current_app, flash, abort
from flask_login import login_required, current_user
from sqlalchemy import and_
from sqlalchemy.exc import IntegrityError

from database import db

admin = Blueprint("admin", __name__)


def adminuser(f):
	print("test 1")

	@wraps(f)
	def decorated_view(*args, **kwargs):
		print("test2")
		if not current_user.is_admin():
			flash("You do not have permission to view that page", "warning")
			abort(401)

		return f(*args, **kwargs)

	return decorated_view


@admin.route('/admin')
@adminuser
@login_required
def home():
	""" admin page"""

	return render_template('admin/home.html')


@admin.route('/admin/users')
@login_required
def user():
	""" admin page"""

	return render_template('admin/home.html')
