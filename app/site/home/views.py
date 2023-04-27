from flask import Blueprint, request, jsonify, render_template
from flask_login import login_required

import settings
from app.models.users.user_registrator import LoginValidator

site = Blueprint("home_site", __name__, template_folder=settings.TEMPLATES_DIR)
api = Blueprint("home_api", __name__)

blueprint = Blueprint("home", __name__, template_folder=settings.TEMPLATES_DIR)
blueprint.register_blueprint(api)
blueprint.register_blueprint(site)


@site.route("/")
@login_required
def home():
    return render_template("home.html")
