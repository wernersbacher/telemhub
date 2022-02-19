from flask import Blueprint, render_template

info = Blueprint("info", __name__)


@info.route('/info/tos')
def tos():

    return render_template("info/tos.html")


@info.route('/info/privacy')
def privacy():

    return render_template("info/privacy.html")


@info.route('/info/cookies')
def cookies():

    return render_template("info/consent.html")

