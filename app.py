"""Flask app for User Feedbacks"""
from flask import Flask, jsonify, request, render_template, redirect, session, flash
from flask_bcrypt import Bcrypt
import bcrypt
from flask_debugtoolbar import DebugToolbarExtension
from models import db, connect_db, User, Feedback
from forms import AddUserForm, LoginForm, FeedbackForm

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
    """Shows the secret page to properly logged in users.
    We're going to let other users LOOK at each other's profiles
    and feedback. Everything else below should prevent editing someone
    else's feedback.
    """

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


# TSK TSK silly rabbit, it's a delete, not a POST
@app.route("/users/<username>/delete", methods=["DELETE"])
def delete_user(username):
    """  Allow only an authenticated user to delete themselves """
    user = User.query.get_or_404(username)

    if "user_username" not in session:
        flash("You must be logged in to delete yourself!")
        return redirect("/login")
    elif session['user_username'] != user.username:
        flash("You can't edit someone else's feedback")
        return redirect('/')

    # get user, delete user & feedback, remove from session
    else:
        # a list of feedback objects from the user
        Feedback.query.filter(username == user.username).delete()
        db.session.commit()
        db.session.delete(user)
        db.session.commit()
        # taking care of the session too
        session.pop('user_username')
        return redirect('/')


@app.route("/users/<username>/feedback/add", methods=["GET", "POST"])
def display_add_feedback_form(username):
    """ GET show form for adding feedback as a logged in user
        POST take the form data
     """

    if "user_username" not in session:
        flash("You must be logged in to give feedback! Put your name on it!")
        return redirect("/login")
    elif session['user_username'] != username:
        flash("You can't edit someone else's feedback")
        return redirect('/')
    else:
        form = FeedbackForm()
        if form.validate_on_submit():
            username = username
            title = form.title.data
            content = form.content.data
            feedback = Feedback(title=title,
                                content=content, username=username)

            db.session.add(feedback)
            db.session.commit()
            return redirect(f'/users/{username}')
        else:
            return render_template("feedback.html", form=form)


# POST in instructions became PATCH, because we're sticklers for the rules
# but then POST worked. Why come? was PATCH just for APIs?
@app.route("/feedback/<feedback_id>/update", methods=["GET", "POST"])
def show_update_feedback_form(feedback_id):
    """ Let's logged in users update their previous feedback """
    # TODO jay: come back through and make this a function taking
    # flash message and redirect
    previous = Feedback.query.get_or_404(feedback_id)

    if "user_username" not in session:
        flash("You must be logged in to give feedback! Put your name on it!")
        return redirect("/login")
    elif session['user_username'] != previous.username:
        flash("You can't edit someone else's feedback")
        return redirect('/')
    else:
        # pulls current version of feedback
        # passing obj of previous into FeedbackForm to auto fill values
        form = FeedbackForm(obj=previous)

        if form.validate_on_submit():
            title = form.title.data
            content = form.content.data

            previous.title = title
            previous.content = content

            db.session.commit()
            return redirect(f'/users/{previous.username}')

        else:
            return render_template('edit_feedback.html', form=form)

# why does this work as GET&POST? but not just DELETE? or POST?
@app.route("/feedback/<feedback_id>/delete", methods=["GET", "POST"])
def delete_feedback(feedback_id):
    """ deletes feedback from user list when hitting delete button """
    feedback = Feedback.query.get_or_404(feedback_id)
    username = feedback.username

    if "user_username" not in session:
        flash("You must be logged in to give feedback! Put your name on it!")
        return redirect("/login")
    elif session['user_username'] != feedback.username:
        flash("You can't delete someone else's feedback")
        return redirect('/')
    else:
        db.session.delete(feedback)
        db.session.commit()
        return redirect(f'/users/{username}')
