# CF Buildpack Dashboard

## Dependencies
In order to run this application you need the [cf-light-api](https://github.com/SpringerPE/cf-light-api) running at
a known endpoint.
Each `cf-light-api` endpoint needs to be provided as a value by populating the `CF_BUILDPACK_DASHBOARD_ENVIRONMENT` env
variable.

## Configuration

The `cf_buildpack_dashboard` application accepts the following configuration parameters passed
by env variables:

- `CF_BUILDPACK_DASHBOARD_ENVIRONMENT`: a json dictionary mapping different environments to their api endpoints. For example ```{"test": "http://cf-light-api-test.example.com", "prod": "https:cf-light-api-prod.example.com"}```
- `PORT`: the port to which the application binds. If running in Cloudfoundry it will be provided by the platform.

## Building for pip

To build the `tar.gz` pip package simply run: ```python setup.py sdist```
from the project root directory.

## Installing and Running

### Pip install
You can install the application from `pypi.org` by running `pip install cf_buildpack_dashboard`. This will install an
executable script that you can call directly `cf_buildpack_dashboard`

### Cloudfoundry manifest
You can target as well a Cloudfoundry installation by providing a manifest as in the following example:

```
applications:
  - name: cf-buildpack-dashboard
    instances: 1
    memory: 256MB
    command: ./run_app.py
    env:
      CF_BUILDPACK_DASHBOARD_ENVIRONMENTS: '{
        "test": "https://cf-api.test.example.com",
        "dev": "https://cf-api.dev.example.com",
        "live": "https://cf-api.live.example.com"
      }'

```
and push with `cf push`

### Provided script
The application can also be run as a simple python application by installing the
requirements and using the provided `run_app.py` script.

## Running the tests

```
nosetests -s
```
