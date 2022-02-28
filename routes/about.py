from flask import Blueprint, render_template, url_for, request, flash
from flask_login import current_user

from forms.contact import ContactForm

about = Blueprint("about", __name__)


@about.route('/about/faqs')
def faqs():

    FAQ = [
        ("What does this website do?",
         """This website is a hub for sharing sim racing telemetry. Users can upload, compare and download them.
                    It might help you to get faster!"""),
        ("Which games are supported yet?",
         """Currently only Assetto Corsa Competizione. Files from other games might work, but are not officially 
         supported yet."""),
        ("Where can I find my own telemetry data?",
         """Just open your cars setup and set telemetry laps to a number higher than 0.
                    The files will be automatically created in your Documents folder.
                    You have to upload both the <b>*.ld</b> and <b>*.ldx</b> files."""),
        ("How can I contribute?",
         f"""If you want to help Telehub to get better, <a href='{url_for("about.contact")}'>just reach out to me</a>.""")
    ]

    return render_template("about/faqs.html", faq=FAQ)


@about.route('/about/contact', methods=['GET', 'POST'])
def contact():

    form = ContactForm(request.form)

    if form.validate_on_submit():
        print(form.email.data)
        print(form.subject.data)
        print(form.message.data)
        print(form.name.data)
        flash("Email set successfully.", category="success")

    if current_user is not None:
        form.email.data = current_user.email
        form.name.data = current_user.username

    return render_template("about/contact.html", form=form)
