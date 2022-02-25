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


@info.route('/info/disclaimer')
def disclaimer():

    return render_template("info/disclaimer.html")


@info.route('/info/contact')
def contact():

    return render_template("info/contact.html")

