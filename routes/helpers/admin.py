from flask import request, url_for
from flask_admin import AdminIndexView
from flask_admin.contrib import sqla
from flask_login import current_user
from werkzeug.utils import redirect


class TelehubModelView(sqla.ModelView):

    def is_accessible(self):
        return current_user.is_authenticated and current_user.is_admin()

    def inaccessible_callback(self, name, **kwargs):
        # redirect to login page if user doesn't have access
        return redirect(url_for('main.home'))


class DashboardView(AdminIndexView):

    def is_accessible(self):
        return current_user.is_authenticated and current_user.is_admin()

    def is_visible(self):
        # This view won't appear in the menu structure
        return False

    def inaccessible_callback(self, name, **kwargs):
        # redirect to login page if user doesn't have access
        return redirect(url_for('main.home'))
