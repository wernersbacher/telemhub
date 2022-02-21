from flask import Flask, render_template
import os

from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect

from database import db
from routes.ajax import ajax
from routes.info import info

from routes.main import main
from routes.member import member
from routes.userspace import userspace

from loginmanager import login_manager
from executor import executor

CURPATH = os.path.abspath(os.path.dirname(__file__))

app = application = Flask(__name__)
app.secret_key = b'j3nr#+38f8fdeadbeef--w'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(CURPATH, 'db', 'app.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['html_base_path'] = os.path.join(app.static_url_path, '')

app.config['UPLOADS'] = os.path.join(CURPATH, 'data', 'files')
app.config['DATA'] = os.path.join(CURPATH, 'data')
db.init_app(app)
migrate = Migrate(app, db, render_as_batch=True)
csrf = CSRFProtect()
csrf.init_app(app)

executor.init_app(app)

login_manager.init_app(app)

app.register_blueprint(main)
app.register_blueprint(member)
app.register_blueprint(userspace)
app.register_blueprint(ajax)
app.register_blueprint(info)


@app.errorhandler(401)
def page_not_found(e):
    # note that we set the 404 status explicitly
    return render_template('401.html'), 401


@app.errorhandler(403)
def page_not_found(e):
    # note that we set the 404 status explicitly
    return render_template('403.html'), 403


@app.errorhandler(404)
def page_not_found(e):
    # note that we set the 404 status explicitly
    return render_template('404.html'), 404


@app.errorhandler(500)
def page_not_found(e):
    # note that we set the 404 status explicitly
    return render_template('500.html'), 500


if __name__ == '__main__':
    if os.name == 'nt':
        app.run(debug=True, port=5100)  # windows
    else:
        app.run(debug=True, host='0.0.0.0', port=5100)
