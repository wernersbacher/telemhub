from sys import platform

from flask import Flask, render_template
import os

from logger import logger_app as logger

from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect

from database import db
from models.models import User, Track, Car, File
from routes.ajax import ajax
from routes.helpers.admin import TelehubModelView, DashboardView, UserView, FileView
from routes.info import info

from routes.main import main
from routes.member import member
from routes.userspace import userspace

from loginmanager import login_manager
from executor import executor

from flask_admin import Admin


CURPATH = os.path.abspath(os.path.dirname(__file__))


app = application = Flask(__name__)
app.secret_key = b'j3nr#+38f8fdeadbeef--w'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(CURPATH, 'db', 'app.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['html_base_path'] = os.path.join(app.static_url_path, '')
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100mb upload limit

app.config['UPLOADS'] = os.path.join(CURPATH, 'data', 'files')
if platform == "linux":  # if under linux aka production, change file directory to external drive
    app.config['UPLOADS'] = "/var/www/files"
app.config['DATA'] = os.path.join(CURPATH, 'data')
db.init_app(app)
migrate = Migrate(app, db, render_as_batch=True)
csrf = CSRFProtect()
csrf.init_app(app)

executor.init_app(app)

login_manager.init_app(app)

admin = Admin(app, name='admin', template_mode='bootstrap3', index_view=DashboardView())
admin.add_view(UserView(db.session))
admin.add_view(FileView(db.session))
admin.add_view(TelehubModelView(Track, db.session))
admin.add_view(TelehubModelView(Car, db.session))

app.register_blueprint(main)
app.register_blueprint(member)
app.register_blueprint(userspace)
app.register_blueprint(ajax)
app.register_blueprint(info)

logger.info("Starting Telemhub Flask App.")
logger.info(f"Configured Files path: {app.config['UPLOADS']}")
logger.info(f"Configured DB path: {app.config['SQLALCHEMY_DATABASE_URI']}")


@app.errorhandler(401)
def error401(e):
    # note that we set the 404 status explicitly
    return render_template('401.html'), 401


@app.errorhandler(403)
def error403(e):
    # note that we set the 404 status explicitly
    return render_template('403.html'), 403


@app.errorhandler(404)
def error404(e):
    # note that we set the 404 status explicitly
    return render_template('404.html'), 404


@app.errorhandler(413)
def error413(e):
    # note that we set the 404 status explicitly
    return render_template('413.html'), 404


@app.errorhandler(500)
def error500(e):
    # note that we set the 404 status explicitly
    return render_template('500.html'), 500


if __name__ == '__main__':
    if os.name == 'nt':
        app.run(debug=True, port=5100)  # windows
    else:
        app.run(debug=True, host='0.0.0.0', port=5100)
