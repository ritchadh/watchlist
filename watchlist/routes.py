from dataclasses import asdict
import functools
from flask import (
    current_app,
    Blueprint,
    render_template,
    session,
    redirect,
    request,
    url_for,
    abort,
    flash,
)
from watchlist.forms import MovieForm, ExtendedMovieForm, RegisterForm, LoginForm
import uuid
from watchlist.models import Movie, User
from datetime import datetime

# from passlib.hash import pbkdf2_sha256

pages = Blueprint(
    "pages", __name__, template_folder="templates", static_folder="static"
)


def login_required(route):
    @functools.wraps(route)
    def route_wrapper(*args, **kwargs):
        if session.get("email") is None:
            return redirect(url_for(".login"))

        return route(*args, **kwargs)

    return route_wrapper


@pages.route("/")
@login_required
def index():
    # default movie details page which has title, year and director with the button to view the entire movie page
    # 1. fetch movie data with above mentioned details from the Mongo DB

    # get user id from the session
    user_id = session.get("user_id")

    # fetch movies of this particular user_id only
    user = current_app.db.users.find_one({"_id": user_id})
    movie_data = current_app.db.movies.find({"_id": {"$all": user["movies"]}})
    movies = [Movie(**movie) for movie in movie_data]

    return render_template("index.html", title="Movies Watchlist", movies_data=movies)


@pages.route("/add", methods=["GET", "POST"])
@login_required
def add_movie():

    form = MovieForm()

    if form.validate_on_submit():
        # fields to be added - movie title, director & year

        movie = Movie(
            _id=uuid.uuid4().hex,
            title=form.title.data,
            director=form.director.data,
            year=form.year.data,
        )

        # add to MongoDb

        current_app.db.users.update_one(
            {"_id": session.get("user_id")}, {"$push": {"movies": movie._id}}
        )

        current_app.db.movies.insert_one(asdict(movie))

        return redirect(url_for(".index"))

    return render_template(
        "new_movie.html", title="Movies Watchlist -  Add Movie", form=form
    )


@pages.route("/login", methods=["GET", "POST"])
def login():

    # Check if user is already logged in and the email is stored in the session
    
    if session.get("email"):
        return redirect(url_for(".index"))

    form = LoginForm()
    if form.validate_on_submit():

        login_data = current_app.db.users.find_one({"email": form.email.data})

        if not login_data:
            flash("Login credentials not correct", category="danger")
            return redirect(url_for(".login"))

        user = User(**login_data)
        if user and form.password.data == user.password:
            session["user_id"] = user._id
            session["email"] = user.email

            flash("User logged in successfully", "success")
            return redirect(url_for(".index"))

        flash("Login credentials not correct", category="danger")

    return render_template("login.html", form=form)


@pages.route("/register", methods=["GET", "POST"])
def register():
    if session.get("email"):
        return redirect(url_for(".index"))

    form = RegisterForm()

    if form.validate_on_submit():

        user = User(
            _id=uuid.uuid4().hex,
            email=form.email.data,
            password=form.password.data,
        )
        current_app.db.users.insert_one(asdict(user))
        flash("User registered successfully", "success")

        return redirect(url_for(".login"))

    return render_template("register.html", form=form)


@pages.route("/edit/<string:movieId>", methods=["GET", "POST"])
@login_required
def edit_movie(movieId: str):

    movie_data = current_app.db.movies.find_one({"_id": movieId})
    if not movie_data:
        abort(404)
    # convert the movie dictionary that we get from the MongoDB to keyword arguments,
    # unpacking the dictionary and calling dataclass Movie constructor

    movie = Movie(**movie_data)
    form = ExtendedMovieForm(obj=movie)

    if form.validate_on_submit():
        # fields to be added - movie title, director & year
        movie.cast = form.cast.data
        movie.series = form.series.data
        movie.description = form.description.data
        movie.tags = form.tags.data
        movie.video_link = form.video_link.data

        current_app.db.movies.update_one({"_id": movieId}, {"$set": asdict(movie)})

        return redirect(url_for(".view_movie", movieId=movieId))

    return render_template(
        "edit_movie.html",
        title="Movies Watchlist -  Edit Movie",
        movie=movie,
        form=form,
    )


@pages.route("/theme-toggle")
def toggle_theme():

    current_theme = session.get("theme")

    if current_theme == "dark":
        session["theme"] = "light"
    else:
        session["theme"] = "dark"

    # Get redirected to the same page as the user was on, and not just the home page
    # All end points have to return ALWAYS.

    return redirect(request.args.get("current_page"))


@pages.route("/movie/<string:movieId>")
def view_movie(movieId: str):
    # using the movieId, find the complete movie details

    movie_data = current_app.db.movies.find_one({"_id": movieId})
    if not movie_data:
        abort(404)
    # convert the movie dictionary that we get from the MongoDB to keyword arguments,
    # unpacking the dictionary and calling dataclass Movie constructor

    movie = Movie(**movie_data)

    # send movie to be populated on the view_movie page
    return render_template("view_movie.html", movie=asdict(movie))


@pages.route("/movie/<string:movieId>/rate")
@login_required
def rate_movie(movieId):
    rating = int(request.args.get("rating"))

    # add rating to the database

    current_app.db.movies.update_one({"_id": movieId}, {"$set": {"rating": rating}})

    # redirect to the view_movie page
    return redirect(url_for(".view_movie", movieId=movieId))


@pages.route("/movie/<string:movieId>/lastWatched")
@login_required
def last_watched(movieId):

    current_app.db.movies.update_one(
        {"_id": movieId}, {"$set": {"last_watched": datetime.today()}}
    )

    return redirect(url_for(".view_movie", movieId=movieId))


@pages.route("/logout")
def logout():
    session.clear()
    return redirect(url_for(".login"))
