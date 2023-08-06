import jinja2

from flask import Blueprint, render_template, current_app

web_app = Blueprint('web_app', __name__,
                        template_folder='templates',
                        static_folder='static',
                        static_url_path='/static')

web_app.jinja_loader = jinja2.ChoiceLoader([
    web_app.jinja_loader,
    jinja2.PackageLoader(__name__)
])


@web_app.route("/", methods=["GET"])
def buildpacks():
    return render_template("buildpack.j2.html", environments=current_app.config["environments"])
