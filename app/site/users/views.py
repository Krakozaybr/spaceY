import uuid

from flask import Blueprint, request, jsonify, render_template, abort
from flask_login import login_required, current_user

import settings
from app.models.db_session import create_session
from app.models.invite import Invite
from app.models.users.user import User
from app.models.users.user_registrator import LoginValidator, PasswordValidator
from app.site.auth.decorators import professor_required
from app.site.auth.forms import AvatarForm, ChangeDescriptionForm, ChangePasswordForm
from app.utils.utils import ImageFormatException, save_image, delete_img

site = Blueprint("users_site", __name__, template_folder=settings.TEMPLATES_DIR)
api = Blueprint("users_api", __name__)

blueprint = Blueprint("users", __name__, template_folder=settings.TEMPLATES_DIR)
blueprint.register_blueprint(api)
blueprint.register_blueprint(site)


@site.route("/profile")
@login_required
def profile():
    return "lolkek"


@api.route("/api/login_available", methods=["POST"])
def login_valid():
    login = request.json.get("login", None)

    validator = LoginValidator(login)

    return jsonify({"is_available": validator.validate(), "error": validator.error()})


@site.route("/students")
@professor_required
@login_required
def students_view():
    with create_session() as session:
        invite = (
            session.query(Invite).filter(Invite.professor_id == current_user.id).first()
        )

        if invite is None:
            invite = Invite()
            invite.professor = current_user
            url = str(uuid.uuid4())

            while session.query(Invite).filter(Invite.url == url).first():
                url = str(uuid.uuid4())
            invite.url = url

            session.add(invite)
            session.commit()
            session.refresh(invite)

        students = (
            session.query(User)
            .filter(User.professor_id == current_user.id)
            .order_by(User.rating.desc())
            .all()
        )

        data = {"students": students, "invite": invite}

        return render_template("users/students.html", **data)


@blueprint.route("/profile", methods=["POST", "GET"])
@login_required
def profile():
    avatar_form = AvatarForm()
    change_description_form = ChangeDescriptionForm()
    change_password_form = ChangePasswordForm()

    with create_session() as session:

        data = {
            "avatar_form": avatar_form,
            "change_description_form": change_description_form,
            "change_password_form": change_password_form,
            "description": current_user.description,
        }

        data_changed = False

        if avatar_form.validate_on_submit():

            data_changed = True

            try:
                filename = save_image(avatar_form.image.data)
            except ImageFormatException:
                return render_template(
                    "users/profile.html",
                    image_error="Расширение не поддерживается",
                    **data
                )

            if current_user.avatar:
                delete_img(current_user.avatar)

            current_user.avatar = filename

        if change_password_form.validate_on_submit():

            data_changed = True

            if not current_user.check_password(change_password_form.password.data):
                return render_template(
                    "users/profile.html",
                    password_error="Указан неверный текущий пароль",
                    **data
                )

            password_validator = PasswordValidator(
                password=change_password_form.new_password.data
            )

            if not password_validator.validate():
                return render_template(
                    "users/profile.html",
                    password_error=password_validator.error(),
                    **data
                )

            current_user.set_password(change_password_form.new_password.data)

        if change_description_form.validate_on_submit():
            data_changed = True
            current_user.description = change_description_form.description.data

        if data_changed:
            session.add(current_user)
            session.commit()

        change_description_form.description.data = current_user.description

        return render_template("users/profile.html", **data)


@blueprint.route("/users/<int:pk>")
@login_required
def user_info(pk):
    with create_session() as session:
        user = session.query(User).filter(User.id == pk).first()

        if user is None:
            abort(404)

        data = {"user": user}

    return render_template("users/user_info.html", **data)
