from flask import Blueprint, render_template, url_for, request, flash
from flask_login import current_user
from flask_mail import Message
from forms.contact import ContactForm

import cred
from mail import mail

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
        ("How do i compare the telemetry?",
         """
         When you have downloaded a telemetry file, 
         just extract it and open it in <a target='_blank' href='https://www.motec.com.au/i2/i2downloads/'>Motec Pro</a>.
         You can then load your own telemetry file and compare the data.
         <br/>
         If you are logged in and uploaded your own data, you can also just use the web telemetry viewer. 
         It is just for the basics, but can help to find the telemetry data you want much faster. 
         """),
        ("Where can I find my own telemetry data?",
         """Just open your cars setup and set telemetry laps to a number higher than 0.
                    The files will be automatically created in your Documents folder.
                    You have to upload both the <b>*.ld</b> and <b>*.ldx</b> files."""),
        ("How can I contribute to the Telehub project?",
         f"""If you want to help Telehub to get better, <a href='{url_for("about.contact")}'>just reach out to me</a>.""")
    ]

    return render_template("about/faqs.html", faq=FAQ)


@about.route('/about/contact', methods=['GET', 'POST'])
def contact():
    form = ContactForm(request.form)

    if form.validate_on_submit():

        message = f""" 
        New mail from your contact form!
        From '{form.name.data}' ({form.email.data}): 

        {form.message.data}
        """

        subject = f"Contact Form: {form.subject.data}"
        msg = Message(body=message,
                      subject=subject,
                      recipients=cred.CONTACT_FORM_RECV)
        print("Created message object.")
        mail.send(msg)
        print("Sent email")
        flash("Email send successfully.", category="success")

    if current_user is not None and current_user.is_authenticated:
        form.email.data = current_user.email
        form.name.data = current_user.username

    return render_template("about/contact.html", form=form)
