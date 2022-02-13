from flask import Flask
import os

from flask_migrate import Migrate

from database import db

from routes.main import main
from routes.userspace import userspace

from loginmanager import login_manager


CURPATH = os.path.abspath(os.path.dirname(__file__))


app = Flask(__name__)
app.secret_key = b'j3nr#+38f8fdeadbeef--w'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(CURPATH, 'app.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['html_base_path'] = os.path.join(app.static_url_path, '')

app.config['UPLOADS'] = os.path.join(CURPATH, 'data', 'files')
db.init_app(app)
migrate = Migrate(app, db, render_as_batch=True)

login_manager.init_app(app)

app.register_blueprint(main)
app.register_blueprint(userspace)

if __name__ == '__main__':
    if os.name == 'nt':
        app.run(debug=True, port=5100)  # windows
    else:
        app.run(debug=True, host='0.0.0.0', port=5100)
