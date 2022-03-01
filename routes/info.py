from flask import Blueprint

from routes.helpers.extensions import render_template_extra

info = Blueprint("info", __name__)


@info.route('/info/tos')
def tos():

    return render_template_extra("info/tos.html")


@info.route('/info/privacy')
def privacy():

    return render_template_extra("info/privacy.html")


@info.route('/info/cookies')
def cookies():

    return render_template_extra("info/consent.html")


@info.route('/info/disclaimer')
def disclaimer():

    return render_template_extra("info/disclaimer.html")


@info.route('/info/contact')
def contact():

    return render_template_extra("info/contact.html")

