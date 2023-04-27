from flask import Blueprint, render_template, redirect, abort
from flask_login import LoginManager, login_required, logout_user, login_user

import settings
from app.models.db_session import create_session
from app.models.invite import Invite
from app.models.users.user import User
from app.models.users.user_registrator import UserRegistrator
from app.site.auth.forms import LoginForm, RegistrationForm

site = Blueprint("auth_site", __name__, template_folder=settings.TEMPLATES_DIR)
api = Blueprint("auth_api", __name__)

blueprint = Blueprint("auth", __name__, template_folder=settings.TEMPLATES_DIR)
blueprint.register_blueprint(api)
blueprint.register_blueprint(site)
login_manager = LoginManager()


@blueprint.route("/register", methods=["POST", "GET"])
def register():
    form = RegistrationForm()

    data = {"form": form, "who_registers": "наставника"}

    if form.validate_on_submit():
        registrator = UserRegistrator(form.login.data, form.password.data)

        with create_session() as session:
            user = registrator.register(session)
            if user is not None:
                login_user(user, remember=True)

                return redirect("/")
            data["err"] = registrator.error()

        return render_template("users/register.html", **data)
    return render_template("users/register.html", **data)


@site.route("/invite/<string:url>", methods=["POST", "GET"])
def invite_view(url):
    with create_session() as session:

        invite: Invite = session.query(Invite).filter(Invite.url == url).first()

        if invite is None:
            abort(404)

        professor = invite.professor
        form = RegistrationForm()

        data = {"form": form, "who_registers": "студента"}

        if form.validate_on_submit():

            registrator = UserRegistrator(form.login.data, form.password.data)
            user = registrator.register(session, is_student=True, professor=professor)

            if user is not None:
                login_user(user, remember=True)

                return redirect("/")
            data["err"] = registrator.error()
            return render_template("users/register.html", **data)
        return render_template("users/register.html", **data)


@site.route("/login", methods=["POST", "GET"])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        with create_session() as session:

            user = session.query(User).filter(User.login == form.login.data).first()

            if user is not None and user.check_password(form.password.data):
                login_user(user, remember=form.remember_me.data)

                return redirect("/")

            return render_template(
                "users/login.html",
                message="Неверный логин или пароль",
                title="Авторизация",
                form=form,
            )

    return render_template("users/login.html", title="Авторизация", form=form)


@login_manager.user_loader
def load_user(user_id):
    db_sess = create_session()
    return db_sess.query(User).get(user_id)


@blueprint.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect("/")
