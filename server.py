"""Movie Ratings."""

from jinja2 import StrictUndefined

from flask import Flask, render_template, redirect, request, flash, session
from flask_debugtoolbar import DebugToolbarExtension

from model import connect_to_db, db, User, Movie, Rating


app = Flask(__name__)

# Required to use Flask sessions and the debug toolbar
app.secret_key = "moosemovie"

# Normally, if you use an undefined variable in Jinja2, it fails
# silently. This is horrible. Fix this so that, instead, it raises an
# error.
app.jinja_env.undefined = StrictUndefined


@app.route('/')
def index():
    """Homepage."""
    return render_template("homepage.html")


@app.route('/register', methods=["GET", "POST"])
def add_user():
    """Add user to database."""

    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        # Where does the null go
        age = int(request.form.get("age"))
        # where does the null go
        zipcode = request.form.get("zipcode")

        new_user = User(email=email, password=password, age=age, zipcode=zipcode)

        db.session.add(new_user)
        db.session.commit()

        flash(f"User {email} added")
        # Redirect to /login for better UX
        return redirect("/")
    else:
        return render_template("register_form.html")


@app.route('/login', methods=["GET"])
def login_form():
    """Login in form."""

    return render_template("login_form.html")


@app.route('/login', methods=["POST"])
def login_user():
    """Logs in user."""

    email = request.form["email"]
    password = request.form["password"]

    user = User.query.filter_by(email=email).first()

    if not user:
        flash("No such user")
        return redirect("/login")

    if user.password != password:
        flash("Wrong password")
        return redirect("/login")

    session["user_id"] = user.user_id
    flash("Logged in")

    return redirect(f"/users/{user.user_id}")


@app.route('/users')
def user_list():
    """User List."""

    users = User.query.all()
    return render_template("user_list.html", users=users)


@app.route('/users/<int:user_id>')
def user_detail(user_id):
    """User details."""

    user = User.query.get(user_id)

    return render_template("user.html", user=user)


@app.route('/movies')
def movie_list():
    """Movie List."""

    movies = Movie.query.order_by(Movie.title).all()
    return render_template("movie_list.html", movies=movies)


@app.route('/movies/<int:movie_id>', methods=["POST"])
def movie_detail(movie_id):
    """Movie details."""
    if 'user_id' not in session:

        movie = Movie.query.get(movie_id)

        return render_template("movie.html", movie=movie)

    else:
        # Put SQL queries in here for update/new rating
        movie = Movie.query.get(movie_id)
        return render_template("rating_form.html", movie=movie)


if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the
    # point that we invoke the DebugToolbarExtension
    app.debug = True
    # make sure templates, etc. are not cached in debug mode
    app.jinja_env.auto_reload = app.debug

    connect_to_db(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)

    app.run(port=5000, host='0.0.0.0')
