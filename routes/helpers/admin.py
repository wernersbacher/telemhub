from flask import request, url_for
from flask_admin import AdminIndexView
from flask_admin.contrib import sqla
from flask_login import current_user
from werkzeug.utils import redirect
from wtforms import PasswordField

from forms.auth import CreateUserForm
from models.models import User


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


class UserView(TelehubModelView):

    form_excluded_columns = ('pass_hash',)
    column_exclude_list = ('pass_hash',)
    form_extra_fields = {
        'confirm': PasswordField('New password')
    }

    def __init__(self, session, **kwargs):
        super(UserView, self).__init__(User, session, **kwargs)

    def is_accessible(self):
        return current_user.is_authenticated and current_user.is_admin()

    def inaccessible_callback(self, name, **kwargs):
        # redirect to login page if user doesn't have access
        return redirect(url_for('main.home'))

    def create_form(self, **kwargs):
        form = CreateUserForm(request.form)
        return form

    def on_model_change(self, form, User: User, is_created):
        # set password on creation, but not on other changes
        try:
            if form.confirm.data is not None:
                User.set_pass(form.confirm.data)
        except AttributeError:
            pass

