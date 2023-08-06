import unittest
import requests
import requests_mock

from cf_buildpack_dashboard.clients.light_api import CFLightAPIClient


mocked_apps_response = '''[{
  "name": "app_name",
  "space_guid": "c0af44b8-8b51-4db5-927e-ccad2e6dab54",
  "buildpack": null,
  "buildpack_name": "ruby buildpack",
  "detected_buildpack": "Ruby",
  "detected_buildpack_guid": "44ec3a97-0d94-4ebb-ad33-e9ee837515bd",
  "space_url": "/v2/spaces/c0af44b8-8b51-4db5-927e-ccad2e6dab54",
  "guid": "ba623c5c-18e1-4d6e-b331-aedf244cb493",
  "meta": {
    "error": false
  },
  "space": "space name",
  "org": "org name"
}]
'''


class TestLightApi(unittest.TestCase):

    light_api_url = "https://cf-light-api.test.com"

    def setUp(self):
        pass

    def test_make_request_happy_path(self):

        light_api_client = CFLightAPIClient()
        light_api_client.set_api_url(self.light_api_url)

        with requests_mock.mock() as m:
            m.get(self.light_api_url + "/v2/apps", json=mocked_apps_response)

            apps = light_api_client.get_apps()
            self.assertIsNotNone(apps[0])
            self.assertTrue(apps[1])

    def test_make_request_happy_path(self):

        light_api_client = CFLightAPIClient()
        light_api_client.set_api_url(self.light_api_url)

        with requests_mock.mock() as m:
            m.get(self.light_api_url + "/v2/apps", json=mocked_apps_response)

            apps = light_api_client.get_apps()
            self.assertIsNotNone(apps[0])
            self.assertTrue(apps[1])

    def test_make_request_expection_raised(self):

        light_api_client = CFLightAPIClient()
        light_api_client.set_api_url(self.light_api_url)

        with requests_mock.mock() as m:
            m.get(self.light_api_url + "/v2/apps", exc=requests.exceptions.RequestException)

            apps = light_api_client.get_apps()
            self.assertIsNone(apps[0])
            self.assertFalse(apps[1])

