"""Flask app for User Feedbacks"""
from flask import Flask, jsonify, request, render_template, redirect, session, flash
from flask_bcrypt import Bcrypt
import bcrypt
from flask_debugtoolbar import DebugToolbarExtension
from models import db, connect_db, User, Feedback
from forms import AddUserForm, LoginForm

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///feedback-app'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True

connect_db(app)
db.create_all()

app.config['SECRET_KEY'] = "I'LL NEVER TELL!!"

# Having the Debug Toolbar show redirects explicitly is often useful;
# however, if you want to turn it off, you can uncomment this line:
#
# app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

toolbar = DebugToolbarExtension(app)


@app.route("/")
def homepage():
    """Show homepage with links to site areas."""

    return redirect("/register")


@app.route("/register", methods=["GET", "POST"])
def display_user_form():
    """ Show and accept submission of user form. """

    form = AddUserForm()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        email = form.email.data
        first_name = form.first_name.data
        last_name = form.last_name.data

        user = User.register(username, password, email, first_name, last_name)
        db.session.add(user)
        db.session.commit()

        session["user_username"] = user.username

        return redirect(f"/users/{username}")

    else:
        return render_template("user_form.html", form=form)


@app.route("/login", methods=["GET", "POST"])
def display_login_form():
    """ Show and accept submission of login form. """

    form = LoginForm()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        user = User.authenticate(username, password)

        if user:
            session["user_username"] = user.username
            return redirect(f"/users/{username}")

        else:
            form.username.errors = ["Bad name/password"]

    return render_template("login_form.html", form=form)


@app.route("/users/<username>")
def display_secret_page(username):
    """Shows the secret page to properly logged in users."""

    if "user_username" not in session:
        flash("You must be logged in to view!")
        return redirect("/login")

    else:
        user = User.query.get_or_404(username)
        return render_template("secret.html", user=user)


@app.route("/logout")
def logout():
    """Logs user out and redirects to homepage."""

    session.pop("user_username")

    return redirect("/")


@app.route("/users/<username>/delete")
def delete_user(username):
    """  Allow only an authenticated user to delete themselves """

    if "user_username" not in session:
        flash("You must be logged in to delete yourself!")
        return redirect("/login")

    # get user, delete user & feedback, remove from session
    else:
        user = User.query.get_or_404(username)
        # a list of feedback objects from the user
        Feedback.query.filter(username == user.username).delete()
        db.session.commit()
        db.session.delete(user)
        db.session.commit()
        # taking care of the session too
        session.pop('user_username')
        return redirect('/')
