from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Length, URL
from flask_wtf.file import FileField, FileAllowed, FileRequired


class PublicUniversityForm(FlaskForm):
    name = StringField("უნივერსიტეტის სახელი", validators=[DataRequired(), Length(min=2, max=220)])
    description = TextAreaField("აღწერა", validators=[DataRequired(), Length(min=10)])
    link = StringField("ოფიციალური ლინკი", validators=[DataRequired(), URL(message="ჩაწერე სწორი URL")])

    image = FileField(
        "ფოტო",
        validators=[
            FileRequired(message="ფოტო აუცილებელია"),
            FileAllowed(["jpg", "jpeg", "png", "webp"], "მხოლოდ jpg/jpeg/png/webp")
        ]
    )

    submit = SubmitField("დამატება")


class EditUniversityForm(FlaskForm):
    name = StringField("უნივერსიტეტის სახელი", validators=[DataRequired(), Length(min=2, max=220)])
    description = TextAreaField("აღწერა", validators=[DataRequired(), Length(min=10)])
    link = StringField("ოფიციალური ლინკი", validators=[DataRequired(), URL(message="ჩაწერე სწორი URL")])

 
    image = FileField("ახალი ფოტო (optional)", validators=[FileAllowed(["jpg", "jpeg", "png", "webp"], "მხოლოდ jpg/jpeg/png/webp")])

    submit = SubmitField("შენახვა")


class LoginForm(FlaskForm):
    username = StringField("მომხმარებელი", validators=[DataRequired(), Length(min=2, max=120)])
    password = PasswordField("პაროლი", validators=[DataRequired(), Length(min=3, max=200)])
    submit = SubmitField("შესვლა")


class RegisterForm(FlaskForm):
    username = StringField("მომხმარებელი", validators=[DataRequired(), Length(min=2, max=120)])
    password = PasswordField("პაროლი", validators=[DataRequired(), Length(min=3, max=200)])
    submit = SubmitField("რეგისტრაცია")
