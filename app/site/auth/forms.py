from flask_wtf import FlaskForm
from wtforms import (
    PasswordField,
    StringField,
    BooleanField,
    SubmitField,
    FileField,
    TextAreaField,
)
from wtforms.validators import DataRequired


class LoginForm(FlaskForm):
    login = StringField("Логин", validators=[DataRequired()])
    password = PasswordField("Пароль", validators=[DataRequired()])
    remember_me = BooleanField("Запомнить", default=False)
    submit = SubmitField("Войти")


class RegistrationForm(FlaskForm):
    login = StringField("Логин", validators=[DataRequired()])
    password = PasswordField("Пароль", validators=[DataRequired()])
    password_repeat = PasswordField("Повторите пароль", validators=[DataRequired()])
    submit = SubmitField("Зарегистрироваться")


class AvatarForm(FlaskForm):
    image = FileField("Изменить аватарку", validators=[DataRequired()])
    submit = SubmitField("Загрузить")


class ChangeDescriptionForm(FlaskForm):
    description = TextAreaField("Описание")
    submit = SubmitField("Сохранить")


class ChangePasswordForm(FlaskForm):
    password = PasswordField("Текущий пароль", validators=[DataRequired()])
    new_password = PasswordField("Новый пароль", validators=[DataRequired()])
    submit = SubmitField("Изменить")
