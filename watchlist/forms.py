from flask_wtf import FlaskForm
from wtforms import (
    IntegerField,
    StringField,
    SubmitField,
    TextAreaField,
    URLField,
    PasswordField,
)
from wtforms.validators import InputRequired, NumberRange, Email, Length, EqualTo


class LoginForm(FlaskForm):

    email = StringField("Email", validators=[InputRequired(), Email()])
    password = PasswordField("Password", validators=[InputRequired()])
    submit = SubmitField("Login")


class RegisterForm(FlaskForm):

    email = StringField("Email", validators=[InputRequired(), Email()])
    password = PasswordField(
        "Password",
        validators=[
            InputRequired(),
            Length(
                min=4,
                max=20,
                message="Your message must be between 4 and 20 characters long",
            ),
        ],
    )

    confirm_password = PasswordField(
        "Confirm Password",
        validators=[
            InputRequired(),
            EqualTo("password", message="The passwords do not match"),
            Length(
                min=4,
                max=20,
                message="Your message must be between 4 and 20 characters long",
            ),
        ],
    )

    submit = SubmitField("Register")


class MovieForm(FlaskForm):
    # FlaskForm provides the added functionality to protect us from the CSRF vulnerability attacks.

    title = StringField("Title", validators=[InputRequired()])
    director = StringField("Director", validators=[InputRequired()])
    year = IntegerField(
        "Year",
        validators=[
            InputRequired(),
            NumberRange(
                min=1878, max=2023, message="Please enter a year in the format YYYY"
            ),
        ],
    )

    submit = SubmitField("Add Movie")


class StringListField(TextAreaField):
    def _value(self):
        if self.data:
            return "\n".join(self.data)
        else:
            return ""

    def process_formdata(self, valuelist):

        if valuelist and valuelist[0]:
            self.data = [line.strip() for line in valuelist[0].split("\n")]

        else:
            self.data = []


class ExtendedMovieForm(MovieForm):

    cast = StringListField("Cast")
    series = StringListField("Series")
    tags = StringListField("Tags")
    description = TextAreaField("Description")
    video_link = URLField("Video Link")

    submit = SubmitField("Submit")
