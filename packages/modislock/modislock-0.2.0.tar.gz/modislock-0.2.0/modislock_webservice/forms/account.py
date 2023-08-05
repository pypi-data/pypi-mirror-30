# coding: utf-8
from flask_security.forms import LoginForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import Email, InputRequired, Length
from modislock_webservice.models import User


class SigninForm(LoginForm):
    """Form for signin"""
    email = StringField('Email',
                        validators=[
                            InputRequired("Email shouldn't be empty."),
                            Length(min=10, max=50),
                            Email('Email format is not correct')
                        ])

    password = PasswordField('Password',
                             validators=[
                                 InputRequired("Password should not be empty"),
                                 Length(min=5, max=40)
                             ])

    submit = SubmitField("Sign In")

    def validate_email(self, field):
        user = User.query.filter(User.email == self.email.data).first()

        if not user:
            raise ValueError("Account doesn't exist.")

    # def validate_password(self, field):
    #     if self.email.data:
    #         user = User.query.filter(User.email == self.email.data).first()
    #
    #         if not user or not user.check_password(self.password.data):
    #             raise ValueError('Password is not correct.')
    #         else:
    #             self.user = user


# class SignupForm(Form):
#     """Form for signin"""
#     name = StringField('Username',
#                        validators=[DataRequired("Username shouldn't be empty.")])
#
#     email = StringField('Email',
#                         validators=[
#                             DataRequired(message="Email shouldn't be empty."),
#                             Email(message='Email format is not correct.')
#                         ])
#
#     password = PasswordField('Password',
#                              validators=[DataRequired("Password shouldn't be empty.")])
#
#     repassword = PasswordField('Retype password',
#                                validators=[
#                                    DataRequired("Please retype the password."),
#                                    EqualTo('password', message="Passwords must match.")
#                                ])
#
#     def validate_name(self, field):
#         user = User.query.filter(User.name == self.name.data).first()
#         if user:
#             raise ValueError('This username already exists.')
#
#     def validate_email(self, field):
#         user = User.query.filter(User.email == self.email.data).first()
#         if user:
#             raise ValueError('This email already exists.')
