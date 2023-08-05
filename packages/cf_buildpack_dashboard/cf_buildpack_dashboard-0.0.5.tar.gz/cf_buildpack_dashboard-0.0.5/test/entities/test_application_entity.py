import unittest
import json

from collections.abc import MutableSet

from cf_buildpack_dashboard.entities.application import ApplicationSet, Application, create_application_set
from cf_buildpack_dashboard.entities.exceptions import ApplicationException

mocked_apps_json = '''[
{
  "name": "app1",
  "space_guid": "c0af44b8-8b51-4db5-927e-ccad2e6dab54",
  "buildpack": "python_buildpack",
  "detected_buildpack": "Ruby",
  "running": true,
  "detected_buildpack_guid": "44ec3a97-0d94-4ebb-ad33-e9ee837515bd",
  "space_url": "/v2/spaces/c0af44b8-8b51-4db5-927e-ccad2e6dab54",
  "guid": "11111111-1111-1111-1111-111111111111",
  "meta": {
    "error": false
  },
  "space": "space1",
  "org": "org1"
},
{
  "name": "app2",
  "space_guid": "c0af44b8-8b51-4db5-927e-ccad2e6dab54",
  "buildpack": "ruby_buildpack",
  "running": false,
  "detected_buildpack": "Python",
  "detected_buildpack_guid": "44ec3a97-0d94-4ebb-ad33-e9ee837515bd",
  "space_url": "/v2/spaces/c0af44b8-8b51-4db5-927e-ccad2e6dab54",
  "guid": "22222222-2222-2222-2222-222222222222",
  "meta": {
    "error": false
  },
  "space": "space2",
  "org": "org2"
},
{
  "name": "app3",
  "space_guid": "c0af44b8-8b51-4db5-927e-ccad2e6dab55",
  "buildpack": "ruby_buildpack",
  "running": false,
  "detected_buildpack": "Python",
  "detected_buildpack_guid": "44ec3a97-0d94-4ebb-ad33-e9ee837515b5",
  "space_url": "/v2/spaces/c0af44b8-8b51-4db5-927e-ccad2e6dab55",
  "guid": "33333333-3333-3333-3333-333333333333",
  "meta": {
    "error": true,
    "message": "Cannot get app"
  },
  "space": "space3",
  "org": "org3"
}
]
'''


class TestApplicationSet(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.mocked_apps_dict = json.loads(mocked_apps_json)

    def test_app_set_implements_mutable_dict(self):

        self.assertIsInstance(ApplicationSet(), MutableSet)

    def test_initialising_application_from_app_dictionary(self):

        app_set = create_application_set(self.mocked_apps_dict)

        self.assertEquals(len(app_set), 2)
        self.assertIn("11111111-1111-1111-1111-111111111111", app_set)

        app = app_set["11111111-1111-1111-1111-111111111111"]

        self.assertEquals(app.space, "space1")
        self.assertEquals(app.org, "org1")
        self.assertEquals(app.running, True)

    def test_creating_organisation_view(self):

        app_set = create_application_set(self.mocked_apps_dict)

        org_dict = app_set.group_by_org()
        self.assertEquals(len(org_dict), 2)

        self.assertIn("org1", org_dict)
        self.assertEquals(len(org_dict["org1"]), 1)


    def test_creating_buildpack_view(self):

        app_set = create_application_set(self.mocked_apps_dict)

        buildpack_dict = app_set.group_by_buildpack()

        self.assertIn("python_buildpack", buildpack_dict)
        self.assertIn("ruby_buildpack", buildpack_dict)


class TestApplication(unittest.TestCase):

    def setUp(self):
        self.properties_app_1 = {
          "name": "app1",
          "space_guid": "c0af44b8-8b51-4db5-927e-ccad2e6dab54",
          "buildpack": "python_buildpack",
          "detected_buildpack": "Ruby",
          "running": True,
          "detected_buildpack_guid": "44ec3a97-0d94-4ebb-ad33-e9ee837515bd",
          "space_url": "/v2/spaces/c0af44b8-8b51-4db5-927e-ccad2e6dab54",
          "guid": "11111111-1111-1111-1111-111111111111",
          "meta": {
            "error": False
          },
          "space": "space1",
          "org": "org1"
        }

        self.properties_app_2 = {
          "name": "app2",
          "space_guid": "c0af44b8-8b51-4db5-927e-ccad2e6dab54",
          "buildpack": "ruby_buildpack",
          "running": False,
          "detected_buildpack": "Python",
          "detected_buildpack_guid": "44ec3a97-0d94-4ebb-ad33-e9ee837515bd",
          "space_url": "/v2/spaces/c0af44b8-8b51-4db5-927e-ccad2e6dab54",
          "guid": "22222222-2222-2222-2222-222222222222",
          "meta": {
            "error": False
          },
          "space": "space2",
          "org": "org2"
        }

    def test_app_buildpack_can_be_retrieved(self):


        app = Application(**self.properties_app_1)

        self.assertEquals(app.buildpack, "python_buildpack")
        self.assertEquals(app.name, "app1")
        self.assertEquals(app.org, "org1")
        self.assertEquals(app.space, "space1")
        self.assertEquals(app.running, True)

    def test_app_buildpack_can_be_retrieved_when_it_is_None(self):

        self.properties_app_1["buildpack"] = None
        app = Application(**self.properties_app_1)

        self.assertEquals(app.buildpack, "None")

    def test_app_raises_an_error_when_meta_error_is_true(self):

        self.properties_app_1["meta"]["error"] = True
        self.properties_app_1["meta"]["message"] = "An error message"

        with self.assertRaises(ApplicationException):
            Application(**self.properties_app_1)

    def test_can_compare_two_applications_by_guid(self):
        app1 = Application(**self.properties_app_1)
        app2 = Application(**self.properties_app_2)

        self.assertEquals(app1, app1)
        self.assertNotEquals(app1, app2)

    def test_can_order_applications_alphanumerically_by_name(self):

        app1 = Application(**self.properties_app_1)
        app2 = Application(**self.properties_app_2)

        self.assertTrue(app1 < app2)
        self.assertTrue(app2 > app1)


