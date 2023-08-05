import logging

from collections import defaultdict, OrderedDict
from collections.abc import MutableSet

from cf_buildpack_dashboard.entities.exceptions import ApplicationException

def create_application_set(apps_list):
    """Return an ApplicationSet object

    :param apps_list -- a dictionary of CF apps
    :return an ApplicationSet object
    """
    app_set = ApplicationSet()

    for app in apps_list:

        try:
            app_object = Application(**app)
        except ApplicationException as ae:
            logging.error(str(ae))
            continue

        app_set[app["guid"]] = app_object

    return app_set

class ApplicationSet(MutableSet):

    def __init__(self):

        self._apps = {}

    def __getitem__(self, key):
        return self._apps[key]

    def __setitem__(self, key, value):
        self._apps[key] = value

    def __delitem__(self, key):
        del self._apps[key]

    def __iter__(self):
        return iter(self._apps.values())

    def __len__(self):
        return len(self._apps)

    def __contains__(self, item):
        return item in self._apps

    def add(self, item):
        if item not in self._apps:
            self._apps[item] = item

    def discard(self, item):
        if item in self._apps:
            del self._apps[item]

    def _sort_nested_dictionary(self, dictionary):

        sorted_dictionary = OrderedDict(sorted(dictionary.items(), key=lambda x: x[0].lower()))

        for buildpack, orgs in sorted_dictionary.items():
            sorted_dictionary[buildpack] = OrderedDict(sorted(orgs.items(), key=lambda x: x[0].lower()))
            for org, apps in orgs.items():
                sorted_dictionary[buildpack][org] = sorted(apps, key=lambda x: x["name"].lower())

        return sorted_dictionary

    def group_by_org(self, isSorted=False):
        """Return the apps grouped by organisation first and buildpack

        :param isSorted: when true the nested dictionaries will be sorted by org name, buildpack name and app name
        :return: a nested dictionary {org: {buildpack: {app}}}
        """
        orgs = defaultdict(list)

        for app in self._apps.values():

            if app.org not in orgs:
                orgs[app.org] = defaultdict()

            if app.buildpack not in orgs[app.org]:
                orgs[app.org][app.buildpack] = list()

            orgs[app.org][app.buildpack].append({"name": app.name, "running": app.running})

        if isSorted:
            return self._sort_nested_dictionary(orgs)
        else:
            return orgs

    def group_by_buildpack(self, isSorted=False):
        """Return the apps grouped by buildpack first and organisation

        :param isSorted: when true the nested dictionaries will be sorted by buildpack name, org name and app name
        :return: a nested dictionary {buildpack: {org: {app}}}
        """
        buildpacks = defaultdict(dict)

        for app in self._apps.values():

            if app.buildpack not in buildpacks:
                buildpacks[app.buildpack] = defaultdict()
            if app.org not in buildpacks[app.buildpack]:
                buildpacks[app.buildpack][app.org] = list()

            buildpacks[app.buildpack][app.org].append({"name": app.name, "running": app.running})

        if isSorted:
            return self._sort_nested_dictionary(buildpacks)
        else:
            return buildpacks

class Application(object):

    def __init__(self, **kwargs):

        if kwargs['meta']['error']:
            raise ApplicationException(kwargs['meta']['message'])

        self.guid = kwargs["guid"]
        self.name = kwargs["name"]
        self.org = kwargs["org"]
        self.space = kwargs["space"]

        if "running" in kwargs:
            self.running = kwargs["running"]
        else:
            self.running = False

        self._buildpack = kwargs["buildpack_name"]

    @property
    def buildpack(self):
        if self._buildpack:
            return self._buildpack
        return "None"

    def __eq__(x, y):
        return x.guid == y.guid

    def __lt__(self, other):
        return self.name.__lt__(other.name)

    def __gt__(self, other):
        return self.name.__gt__(other.name)

    def __hash__(self):
        return hash(self.guid)
