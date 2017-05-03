"""Movie Ratings."""

from jinja2 import StrictUndefined

from flask import Flask, jsonify, render_template, redirect, request, flash, session
from flask_debugtoolbar import DebugToolbarExtension

from model import connect_to_db, db, User, Rating, Movie


app = Flask(__name__)

# Required to use Flask sessions and the debug toolbar
app.secret_key = "ABC"

# Normally, if you use an undefined variable in Jinja2, it fails
# silently. This is horrible. Fix this so that, instead, it raises an
# error.
app.jinja_env.undefined = StrictUndefined


@app.route('/')
def index():
    """Homepage."""
    # a = jsonify([1,3])
    # return a
    return render_template("homepage.html")


@app.route('/users')
def user_list():
    """Show list of users."""

    users = User.query.all()
    return render_template("user_list.html", users=users)


@app.route('/registration-form', methods=['GET'])
def registration_form():
    """Shows registration form."""

    return render_template("registration_form.html")


@app.route('/registration-form', methods=['POST'])
def registration_process():
    """Shows registration form."""

    email = request.form.get('email')
    password = request.form.get('password')

    if User.query.filter_by(email=email).first() is None:
        user = User(email=email,
                    password=password)
        db.session.add(user)
        db.session.commit()
        flash('You were successfully added')
    else:
        flash('Oops, you are already in the database! Try again.')
        return redirect('/registration-form')

    return redirect('/')


@app.route('/login-form', methods=['GET', 'POST'])
def login():
    """Allow user to login with password"""

    email = request.form.get('email')
    password = request.form.get('password')

    sys_email = User.query.filter_by(email=email).first()

    if request.method == 'POST':
        if sys_email is None:
            flash('Invalid credentials')
            return redirect('/login-form')
        elif email == sys_email.email:
            if password == sys_email.password:
                flash('You were successfully logged in')
                return redirect('/login-form')
            else:
                flash('That is not your password. Try again')
                return redirect('/login-form')

    return render_template('login.html')


if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the
    # point that we invoke the DebugToolbarExtension
    app.debug = True
    app.jinja_env.auto_reload = app.debug  # make sure templates, etc. are not cached in debug mode

    connect_to_db(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)


    
    app.run(port=5000, host='0.0.0.0')
