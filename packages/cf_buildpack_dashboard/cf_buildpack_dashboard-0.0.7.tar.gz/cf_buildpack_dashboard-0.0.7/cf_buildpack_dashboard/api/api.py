import json

from flask import Blueprint, request, Response, current_app

from cf_buildpack_dashboard.entities.application import create_application_set
from cf_buildpack_dashboard.clients.light_api import CFLightAPIClient

buidlpack_api = Blueprint("api", __name__)

@buidlpack_api.route("/buildpacks", methods=["GET"])
def buildpacks(cf_api_client: CFLightAPIClient):

    if request.method == "GET":

        by_buildpack = request.args.get('by_buildpack')
        env = request.args.get('environment')
        environment = current_app.config["environments"][env]

        cf_api_client.set_api_url(environment)
        app_list, success = cf_api_client.get_apps()

        if not success:
            r = Response(response=json.dumps({ "error": "Client api error" }), status=500, mimetype="application/json")
            r.headers["Content-Type"] = "application/json; charset=utf-8"
            return r

        app_set = create_application_set(app_list)

        if by_buildpack == "true":
            data = app_set.group_by_buildpack(isSorted=True)
        else:
            data = app_set.group_by_org(isSorted=True)

        r = Response(response=json.dumps(data), status=200, mimetype="application/json")
        r.headers["Content-Type"] = "application/json; charset=utf-8"
        return r
