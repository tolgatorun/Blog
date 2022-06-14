#view function responds requests of application
#Flask gives URL to responsible view from that request then view returns data after that Flask turns that data into outgoing response
#group of views and other code organized with blueprints
#views -> blueprint -> application
import functools 

from flask import ( Blueprint, flash, g, redirect, render_template, request, session, url_for)
from werkzeug.security import check_password_hash, generate_password_hash
from flaskr.db import get_db

bp = Blueprint('auth',__name__, url_prefix='/auth')

@bp.route('/register', methods=('GET', 'POST')) #/auth/register URL associated with register function|it'll use return value as response
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None

        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'

        if error is None:
            try:
                db.execute(#execute takes a SQL query
                    "INSERT INTO user (username, password) VALUES (?, ?)",
                    (username, generate_password_hash(password)),#passwords should be hashes and only hash should be stored
                )
                db.commit()#save changes
            except db.IntegrityError:#if username already exists IntegrityError will occur
                error = f"User {username} is already registered."
            else:
                return redirect(url_for("auth.login"))#url_for generates URL for login view based on its name|redirect generates a redirected response to generated URL

        flash(error)#saves message at end of a request

    return render_template('auth/register.html')


@bp.route('/login', methods=('GET', 'POST')) #/auth/login URL associated with login function
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None
        user = db.execute(
            'SELECT * FROM user WHERE username = ?', (username,)
        ).fetchone()#fetchone returns one row from query|if query returned no results,it returns None 

        if user is None:
            error = 'Incorrect username.'
        elif not check_password_hash(user['password'], password):#check_password_hash hashes enteres password and compares with stored hash. match -> valid password
            error = 'Incorrect password.'

        if error is None:
            session.clear()#session(dict) stores data across requests.User's id is stored in new session
            session['user_id'] = user['id'] #user's id is stored in session|data stored in a cookie sent to browser,browser sends it back with subsequent requests
            return redirect(url_for('index'))

        flash(error)

    return render_template('auth/login.html')\


@bp.before_app_request#registers a function that runs before every URL view
def load_logged_in_user():#checks for id in session.If there is -> store it in g.user if there isn't g.user gets None
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute(
            'SELECT * FROM user WHERE id = ?', (user_id,)
        ).fetchone()

@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

#for edit,create and delete blog posts user has to be logged in. Decorator can be used for check this
#wraps original view it's applied to|check for g.user if there isn't redirect to login page 
#blog views
def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))#prepend blueprint name to function name

        return view(**kwargs)

    return wrapped_view