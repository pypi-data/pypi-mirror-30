# CF Buildpack Dashboard

## Configuration

The `cf_buildpack_dashboard` application accepts the following configuration parameters passed
by env variables:

- `CF_BUILDPACK_DASHBOARD_ENVIRONMENT`: a json dictionary mapping different environments to their api endpoints. For example ```{"test": "http://cf-light-api-test.example.com", "prod": "https:cf-light-api-prod.example.com"}```
- `PORT`: the port to which the application binds. If running in Cloudfoundry it will be provided by the platform.

## Building for pip

To build the `tar.gz` pip package simply run: ```python setup.py sdist```
from the project root directory.

## Running and provisioning

The application can also be run as a simple python application by installing the
requirements and using the provided `run_app.py` script.

## Running the tests

```
nosetests -s
```
