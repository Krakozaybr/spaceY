from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    SubmitField,
    FileField,
    TextAreaField,
    IntegerField,
)
from wtforms.validators import DataRequired, NumberRange


def task(cls):
    cls.title = StringField("Заголовок", validators=[DataRequired()])
    cls.description = TextAreaField("Краткое описание", validators=[DataRequired()])
    cls.estimation = IntegerField(
        "Рейтинг", validators=[DataRequired(), NumberRange(min=1)]
    )
    return cls


@task
class VideoTaskForm(FlaskForm):
    video = FileField("Видео", validators=[DataRequired()])
    submit = SubmitField("Сохранить", validators=[DataRequired()])


@task
class TextTaskForm(FlaskForm):
    text = TextAreaField("Основной текст", validators=[DataRequired()])
    submit = SubmitField("Сохранить", validators=[DataRequired()])


@task
class TestTaskForm(FlaskForm):
    question = StringField("Вопрос", validators=[DataRequired()])
    submit = SubmitField("Сохранить", validators=[DataRequired()])


@task
class ImageTaskForm(FlaskForm):
    image = FileField("Изображение", validators=[DataRequired()])
    submit = SubmitField("Сохранить", validators=[DataRequired()])
