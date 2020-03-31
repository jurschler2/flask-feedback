"""Forms for creating a user."""

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import InputRequired, Length


class AddUserForm(FlaskForm):
    """ Form for adding pets """

    username = StringField("Username",
                           validators=[InputRequired(), Length(max=20)])

    password = PasswordField("Password",
                             validators=[InputRequired()])

    email = StringField("Email",
                        validators=[InputRequired(), Length(max=50)])

    first_name = StringField("First Name",
                             validators=[InputRequired(), Length(max=30)])

    last_name = StringField("Last Name",
                            validators=[InputRequired(), Length(max=30)])


class LoginForm(FlaskForm):
    """ Form for handling the logging in of a user. """

    username = StringField("Username",
                           validators=[InputRequired(), Length(max=20)])

    password = PasswordField("Password",
                             validators=[InputRequired()])
