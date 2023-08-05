import json
import logging
import sys

from os import environ

from flask import Flask
from flask_injector import FlaskInjector
from injector import singleton

from cf_buildpack_dashboard.api.api import buidlpack_api
from cf_buildpack_dashboard.api.web import web_app
from cf_buildpack_dashboard.clients.light_api import CFLightAPIClient

def configure_api(binder):

    binder.bind(
        CFLightAPIClient,
        to=CFLightAPIClient(),
        scope=singleton,
    )

def create_app():
    app = Flask(__name__)

    app.register_blueprint(buidlpack_api, url_prefix="/api")
    app.register_blueprint(web_app)

    FlaskInjector(app=app, modules=[configure_api])

    try:
        env = environ.get("CF_BUILDPACK_DASHBOARD_ENVIRONMENTS")
    except KeyError as ke:
        logging.fatal(str(ke))
        sys.exit(1)

    try:
        app.config['environments'] = json.loads(env)
    except TypeError as te:
        logging.fatal(str(te))
        sys.exit(1)

    app.endpoint
    return app

application = create_app()

def main_app():

    port = environ.get("PORT", 5000)
    application.run("0.0.0.0", int(port))
