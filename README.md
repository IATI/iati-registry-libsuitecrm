# IATI Registry SuiteCRM Python Library

## Summary

| Product          | IATI Registry SuiteCRM Python Library                        |
| ---------------- | ------------------------------------------------------------ |
| Description      | This repository contains a Python interface library to interact with a [SuiteCRM](https://github.com/salesagility/SuiteCRM) instance via its [REST API](https://docs.suitecrm.com/developer/api/developer-setup-guide/json-api/). |
| Website          | None                                                         |
| Related          | To setup a local instance of the IATI Registry you can use the local development environment: [IATI Registry Local Development Environment](https://github.com/iati/iati-registry-localdev).<br />To test the registry you will need to install the [IATI Registry SuiteCRM Extension](https://github.com/IATI/iati-registry-suitecrm-extension). |
| Documentation    | Rest of README.md                                            |
| Technical Issues | [GitHub issues page](https://github.com/IATI/iati-registry-libsuitecrm/issues) |
| Support          | [IATI Support Website](https://iatistandard.org/en/guidance/get-support/) |

## High-level requirements

* Docker.
* Docker Compose.
* Python 3.12.3 or above (specified in `.python-version` and `pyproject.toml`)

## Overview

The library can be installed using `pip` which will install the dependencies specified in `pyproject.toml`.

```
pip install .
```

Here is a basic example of using the library to interact with a local SuiteCRM instance:

```
import libsuitecrm

crm = libsuitecrm.SuiteCRM(
    "https://127.0.0.1:8443/",
    client_id="924b0e3f-57d8-00c0-f023-67fcde903ca5",
    client_secret="secret-123",
    secure=False,
)
crm.fetch_access_token()

print(crm.create_record("Accounts", {"name": "Org Name"}))
print(crm.get_records("Accounts"))

crm.logout()
```

## Development

Development dependencies can be installed with:

```
pip install -r requirements_dev.txt
```

If any dependencies are added to `pyproject.toml` then the requirements files should be rebuilt using:

```
pip-compile --extra=dev --output-file=requirements_dev.txt --strip-extras
pip-compile --all-build-deps --strip-extras
```

### Testing

Pytest is used for unit and integration testing of the library.  Most of the testing is an integration test that runs using a local instance of SuiteCRM.  At the moment the local instance must be manually started.  Because this needs to be tested against the IATI fork of SuiteCRM the docker setup has now been removed from this repository.  To test, spin up the test instance from [IATI SuiteCRM](https://github.com/IATI/iati-suitecrm) with ```docker compose up --build``` (run this command from the `dev` directory in that repo) and then run the tests:

```
pytest
```

### Linting and code formatting

Linting and code formatting is setup using `isort`, `black` and `flake8` via settings in `pyproject.toml`.

## License

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.
    
    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.
    
    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
