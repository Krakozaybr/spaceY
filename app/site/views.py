from flask import Blueprint

import settings
from .auth.views import blueprint as auth, login_manager
from .users.views import blueprint as users
from .education.views import blueprint as education
from .home.views import blueprint as home

blueprint = Blueprint("site", __name__, template_folder=settings.TEMPLATES_DIR)
blueprint.register_blueprint(auth)
blueprint.register_blueprint(users)
blueprint.register_blueprint(education)
blueprint.register_blueprint(home)
