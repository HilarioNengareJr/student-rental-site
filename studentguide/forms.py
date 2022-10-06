from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField
from flask_wtf.file import FileField, FileAllowed
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from flask_login import current_user
from studentguide.models import User
import phonenumbers


class RegistrationForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired(), Length(min=2, max=20)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')


class LoginForm(FlaskForm):
    email = StringField('Email ', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember me ')
    submit = SubmitField('Cool ')


class UpdateAccountForm(FlaskForm):
    username = StringField('Username',
                           validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    picture = FileField('Update Profile Picture', validators=[FileAllowed(['jpg', 'png'])])
    submit = SubmitField('Update')

    def validate_username(self, username):
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('That username is taken. Please choose a different one.')

    def validate_email(self, email):
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('That email is taken. Please choose a different one.')


class CommentForm(FlaskForm):
    comment = TextAreaField('comment', validators=[
        DataRequired(), Length(min=1, max=140)], render_kw={"placeholder": "Write a Comment"})
    submit = SubmitField('Submit')


class LikeForm(FlaskForm):
    like = TextAreaField('comment', validators=[
        DataRequired(), Length(min=1, max=140)], render_kw={"placeholder": "Write a Comment"})
    submit = SubmitField('Submit')


#
# class PostForm(FlaskForm):
#     images = FileField('Images', validators=[FileAllowed(['jpg', 'png'])])
#     location = StringField('Address', validators=[DataRequired(), Length(min=5, max=140)])
#     city = StringField('District', validators=[DataRequired(), Length(min=5, max=12)])
#     phone_number = StringField('Contact', validators=[DataRequired()])
#     description = TextAreaField('Description', validators=[DataRequired()])
#     submit = SubmitField('Post')

class MyForm(FlaskForm):
    file = FileField('File')
    submit = SubmitField('Submit')
