import requests

from requests.exceptions import RequestException

from cf_buildpack_dashboard.clients.reply import ClientResponse

class CFLightAPIClient(object):

    apps_endpoint = "/v2/apps"

    def __init__(self):

        self.api_url = None

    def set_api_url(self, api_url):
        self.api_url = api_url

    def make_request(self, endpoint):

        url = '{api_url}{endpoint}'.format(api_url=self.api_url, endpoint=endpoint)

        try:
            res = requests.get(url=url)
        except RequestException as e:
            return ClientResponse(success=False, error=e)

        if res.status_code is not requests.codes.ok:
            return ClientResponse(success=False)

        return ClientResponse(data=res.json(), success=True)

    def get_apps(self):

        apps = None

        res = self.make_request(self.apps_endpoint)
        if res.success:
            apps = res.data

        return apps, res.success

