from flask import Flask

from app.models.core import format_date
from app.site.views import blueprint, login_manager

app = Flask(__name__)

app.config["SECRET_KEY"] = "yandexlyceum1_secret_key"

login_manager.init_app(app)
app.register_blueprint(blueprint)


@app.template_filter()
def date(value):
    return format_date(value)


if __name__ == "__main__":
    app.run()
