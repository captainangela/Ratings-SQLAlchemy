"""Movie Ratings."""

from jinja2 import StrictUndefined

from flask import Flask, jsonify, render_template, redirect, request, flash, session
from flask_debugtoolbar import DebugToolbarExtension

from model import connect_to_db, db, User, Rating, Movie
from datetime import datetime


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

@app.route('/movies')
def movie_list():
    """Show list of movies."""

    movies = Movie.query.all()
    return render_template("movie_list.html", movies=movies)

@app.route('/movies/<movie_id>', methods=['GET'])
def movie_profile(movie_id):
    """Lists Movie details"""

    movie = Movie.query.get(movie_id)
    user_id = session.get("user_id")

    if user_id:
        user_ratings = Rating.query.filter_by(movie_id=movie_id, user_id=user_id).first()
    else:
        user_ratings = None

    movie_id = movie.movie_id
    title = movie.title
    release_date = datetime.strftime(movie.released_at, "%Y")

    return render_template("movies.html",
                            movie=movie,
                            movie_id=movie_id,
                            title=title,
                            release_date=release_date,
                            user_ratings=user_ratings)


@app.route('/movies/<movie_id>', methods=['POST'])
def movie_detail_process(movie_id):
    """Add/edit a rating."""

    # Get form variables
    score = int(request.form["score"])

    user_id = session.get("user_id")
    if not user_id:
        raise Exception("No user logged in.")

    user_ratings = Rating.query.filter_by(user_id=user_id, movie_id=movie_id).first()

    if user_ratings:
        user_ratings.score = score
        flash("Rating updated.")

    else:
        user_ratings = Rating(user_id=user_id, movie_id=movie_id, score=score)
        flash("Rating added.")
        db.session.add(user_ratings)

    db.session.commit()

    return redirect("/movies/%s" % movie_id)


@app.route('/users/<user_id>')
def user_profile(user_id):
    """Lists user details"""
    # user = User.query.get(user_id)
    user = User.query.filter_by(user_id=user_id).all()
    user_id = user[0].user_id
    email = user[0].email
    zipcode = user[0].zipcode
    age = user[0].age
    user_ratings = Rating.query.filter_by(user_id=user_id).all()

    return render_template("user.html",
                            email=email,
                            age=age,
                            zipcode=zipcode,
                            user_ratings=user_ratings,
                            user=user)


@app.route('/registration-form', methods=['GET'])
def registration_form():
    """Shows registration form."""

    return render_template("registration_form.html")


@app.route('/registration-form', methods=['POST'])
def registration_process():
    """Shows registration form."""

    email = request.form.get('email')
    password = request.form.get('password')
    age = request.form.get('age')
    zipcode = request.form.get('zipcode')

    if User.query.filter_by(email=email).first() is None:
        user = User(email=email,
                    password=password,
                    age=age,
                    zipcode=zipcode)
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
                session["user_id"] = sys_email.user_id
                return redirect('/users/%s' % sys_email.user_id)
            else:
                flash('That is not your password. Try again')
                return redirect('/login-form')

    return render_template('login.html')


@app.route('/logout')
def logout():
    """Log out."""

    del session['user_id']
    flash('Logged out.')
    return redirect('/')


if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the
    # point that we invoke the DebugToolbarExtension
    app.debug = True
    app.jinja_env.auto_reload = app.debug  # make sure templates, etc. are not cached in debug mode

    connect_to_db(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)


    
    app.run(port=5000, host='0.0.0.0')
