import os
from flask import Flask, redirect, render_template, url_for, flash
from flask_login import LoginManager, login_user, current_user, logout_user
from flask_socketio import SocketIO, send, join_room, leave_room
from flask_assets import Environment, Bundle
from time import localtime, strftime
from sqlalchemy.inspection import inspect

from wtform_fields import *
from models import *


# Configure app
app = Flask(__name__)
assets = Environment(app)
app.secret_key = os.environ.get("SECRET")

# Bundle assets
js = Bundle('scripts/constants.js', 'scripts/socketio.js', 'scripts/ui-interaction.js',
 filters='jsmin', output='gen/main.js')
assets.register('js_main', js)

css = Bundle('scss/resets.scss', 'scss/login-backdrop.scss', 
    'scss/login-register.scss', 'scss/chat-page-layout.scss',
    'scss/chat-header.scss', 'scss/chat-rooms-list.scss', 
    'scss/chat-rightside-panel.scss',
    filters='pyscss,cssmin', output='gen/main.css')
assets.register('css_main', css)

# Configure database
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DATABASE_URL").replace("postgres://", "postgresql://", 1)
db = SQLAlchemy(app)

engine = db.create_engine(app.config['SQLALCHEMY_DATABASE_URI'], {})
inspector =  inspect(engine)

if not inspector.has_table("users"):
    with app.app_context():
        db.drop_all()
        db.create_all()
        app.logger.info('Initialized the database!')
else:
    app.logger.info('Database already contains the users table.')

# Initialize flask-socketio
socketio = SocketIO(app)
ROOMS = ["general", "news", "games", "coding"]


# Configure flask login
login = LoginManager(app)
login.init_app(app)


@login.user_loader
def load_user(id):
    return User.query.get(int(id))


@app.route('/', methods=['GET', 'POST'])
def index():
    reg_form = RegistrationForm()

    if reg_form.validate_on_submit():
        username = reg_form.username.data
        password = reg_form.password.data

        # Hash password
        hashed_pswd = pbkdf2_sha256.hash(password)

        # Add user to db
        user = User(username=username, password=hashed_pswd)
        db.session.add(user)
        db.session.commit()

        flash("Registered successfully. Please log in.", "success")
        return redirect(url_for('login'))

    return render_template("register.html", form=reg_form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    login_form = LoginForm()

    # Allow login in validation success
    if login_form.validate_on_submit():
        user_object = User.query.filter_by(username=login_form.username.data).first()
        login_user(user_object)
        return redirect(url_for("chat"))

    return render_template("login.html", form=login_form)


@app.route("/chat", methods=['GET', 'POST'])
def chat():

    if not current_user.is_authenticated:
        flash("Please login.", "error")
        return redirect(url_for("login"))
    
    return render_template("chat.html", username=current_user.username, rooms=ROOMS)


@app.route("/logout", methods=['GET'])
def logout():
    logout_user()
    flash("You have logged out successfully.", "success")
    return redirect(url_for("login"))


@socketio.on('message')
def message(data):
    print(data)
    send({'msg': data['msg'], 'username': data['username'], 
        'time_stamp': strftime('%b-%d %I:%M%p', localtime())},
        room=data['room'])


@socketio.on('join')
def join(data):
    join_room(data['room'])
    send({'msg': data['username'] + " has joined " + data['room']}, room=data['room'])


@socketio.on('leave')
def leave(data):
    leave_room(data['room'])
    send({'msg': data['username'] + " has left " + data['room']}, room=data['room'])


if __name__ == '__main__':
    app.run()
