"""Implementation of CRM interface class"""

import logging
import urllib
from typing import Dict, List, Tuple

import oauthlib.oauth2
import requests
import requests_oauthlib

from .exceptions import (
    AuthorisationFailed,
    CreateRecordFailed,
    CreateRelationshipFailed,
    DeleteRecordFailed,
    RequestFailed,
    UpdateRecordFailed,
)
from .filter import Filter

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


def _format_fields(module_name: str, fields: List[str]) -> dict:
    """Formats a list of fields ready for passing to SuiteCRM

    Parameters
    ----------
    module_name : str
        Module name to format fields for.
    fields : List[str]
        List of fields.

    Returns
    -------
    dict
    """
    if fields is None:
        return []
    if len(fields) == 0:
        return []
    return [(f"fields[{module_name}]", ",".join(fields))]


class SuiteCRM:
    """Class to help call the SuiteCRM REST API v8"""

    def __init__(self, api_base_url: str, client_id: str = None, client_secret: str = None, secure: bool = True):
        """Setup SuiteCRM REST API communication object

        Parameters
        ----------
        api_base_url : str
          URL for the API endpoint (including protocol).
        client_id : str
          Client ID as setup in SuiteCRM.
        client_secret : str
          Client secret as setup in SuiteCRM.
        secure : bool, optional
          If True then requests will be called with verify=False to enable SSL
          requests with self-signed certificates, default True.
        """
        self._client_id = client_id
        self._client_secret = client_secret
        self._secure = secure

        self._api_base_url = api_base_url
        tmp = urllib.parse.urlparse(api_base_url)
        self._api_base = tmp.scheme + "://" + tmp.netloc
        self._api_base_path = tmp.path

        self._oauth_client = oauthlib.oauth2.BackendApplicationClient(client_id=self._client_id)
        self._oauth_session = requests_oauthlib.OAuth2Session(client=self._oauth_client)
        self._access_token = None

    def _get_url(self, path: str) -> str:
        """Make a full URL to an API endpoint

        Parameters
        ----------
        path : str
            Fragment of the API endpoint to combine with the rest of the URL base.

        Returns
        -------
        str
        """
        return self._api_base + self._api_base_path + path

    def fetch_access_token(self):
        """Fetch an access token from SuiteCRM

        Access tokens are required to access the SuiteCRM API.

        Raises
        ------
        CannotFetchAccessToken
            If we couldn't fetch the access token for some reason.
        RequestFailed
            If there was a request failure when trying to fetch the access token.
        """
        self._fetch_access_token("Attempting to fetch access token")

    def _fetch_access_token(self, debug_string: str):  # noqa: C901
        """Internal function to fetch an access token from SuiteCRM with debug logging

        Parameters
        ----------
        debug_string: str
            String used to provide debugging logging.

        Raises
        ------
        CannotFetchAccessToken
            If we couldn't fetch the access token for some reason.
        RequestFailed
            If there was a request failure when trying to fetch the access token.
        """
        url = self._get_url("/Api/access_token")
        logger.debug(f"{debug_string} ({url})")

        try:
            self._access_token = self._oauth_session.fetch_token(
                token_url=url, client_id=self._client_id, client_secret=self._client_secret, verify=self._secure
            )

        except oauthlib.oauth2.rfc6749.errors.MissingTokenError as missing_token_err:
            try:
                response = requests.get(url, verify=self._secure)
                response.raise_for_status()
            except requests.HTTPError:
                logger.error(
                    f"Cannot fetch access token from {url} because "
                    f"the request failed with with {response.status_code} '{response.reason}'"
                )
                raise AuthorisationFailed(f"API Endpoint ({url}) unreachable with HTTP {response.status_code}")

            raise AuthorisationFailed(missing_token_err.description)

        except oauthlib.oauth2.InsecureTransportError as err:
            logger.error(f"Cannot fetch access token from {url} because the connection isn't secure ({err})")
            raise AuthorisationFailed(
                f"Cannot fetch access token from {url} because the connection isn't secure ({err})"
            )

        except requests.exceptions.SSLError as err:
            logger.error(f"Cannot fetch access token from {url} because the connection isn't secure ({err})")
            raise AuthorisationFailed(
                f"Cannot fetch access token from {url} because the connection isn't secure ({err})"
            )

        except ValueError as err:
            logger.error(f"Cannot fetch access token from {url} because '{str(err)}'")
            raise AuthorisationFailed(f"Cannot fetch access token from {url} because '{str(err)}'")

        self._oauth_session.token = self._access_token

    def logout(self):
        """Logs out of SuiteCRM

        Calls the endpoint documented at:
        https://8-x.docs.suitecrm.com/developer/api/developer-setup-guide/json-api/#_logout

        Returns
        -------
        dict
        """
        logger.debug("Logging out of SuiteCRM")
        return self._post("/Api/V8/logout")

    def get_modules(self):
        """Get a list of modules in the SuiteCRM instance

        This could be used to check that the SuiteCRM instance has the IATI extension
        already installed we could check for "IATI_Datasets" in the returned dictionary.

        Calls the endpoint documented at:
        https://8-x.docs.suitecrm.com/developer/api/developer-setup-guide/json-api/#_modules

        Returns
        -------
        dict
        """
        logger.debug("Calling get_modules")
        return self._get("/Api/V8/meta/modules")

    def get_module_fields(self, module_name: str) -> dict:
        """Get a list of fields available in a given module

        This could be used to check that a SuiteCRM module has a field.  For example, if
        the IATI extension has a field in one version but not another, we could
        check that a module in the SuiteCRM instance we are connected to has a field.

        NOTE: this method requires the module_name to be given as the **plural** form,
        e.g., Accounts not Account.

        Calls the endpoint documented at:
        https://8-x.docs.suitecrm.com/developer/api/developer-setup-guide/json-api/#_module_fields

        Returns
        -------
        dict
        """
        logger.debug("Calling get_module_fields")
        return self._get(f"/Api/V8/meta/fields/{module_name}")

    def get_record_by_id(self, module_name: str, id: str, fields: List[str] = None) -> dict:
        """Get a record from a given module in the CRM

        Calls the endpoint documented at:
        https://8-x.docs.suitecrm.com/developer/api/developer-setup-guide/json-api/#_get_a_module_by_id

        Parameters
        ----------
        module_name : str
            Module name to get the record from.
        id : str
            ID Of the record to return
        fields : List[str], optional
            List of fields to return.

        Returns
        -------
        dict
        """
        logger.debug(f"Calling get_record_by_id for module {module_name} and {id}")
        return self._get(f"/Api/V8/module/{module_name}/{id}", params=_format_fields(module_name, fields))

    def get_records(
        self,
        module_name: str,
        fields: List[str] = None,
        page_number: int = None,
        page_size: int = None,
        sort_dir: str = "ascending",
        sort_field: str = None,
        filters: Filter = None,
    ):
        """Get a set of records from a given module in the CRM

        Calls the endpoint documented at:
        https://8-x.docs.suitecrm.com/developer/api/developer-setup-guide/json-api/#_get_collection_of_modules

        Parameters
        ----------
        module_name : str
            Module name to get the record(s) from.
        fields : List[str], optional
            List of fields to return, by default None.
        page_number : int, optional
            Page number to return, when page_size is not None, by default None.
        page_size : int, optional
            Number of records per page, when page_number is not None, by default None.
        sort_dir : str, optional
            Search direction, "ascending" or "descending", by default "ascending".
        sort_field : str, optional
            Field to sort on, by default None.
        filters : Filter, optional
            Filters to filter down records, by default None.

        Returns
        -------
        dict

        Raises
        ------
        ValueError
            If sort direction is invalid.
        """
        params = []
        if fields is not None:
            params += _format_fields(module_name, fields)
        if page_number is not None and page_size is not None:
            params.append(("page[number]", page_number))
            params.append(("page[size]", page_size))
        if sort_field is not None:
            if not (sort_dir == "ascending" or sort_dir == "descending"):
                raise ValueError("Sort direction must be either ascending or descending")
            params.append(("sort", ("-" if sort_dir == "descending" else "") + sort_field))
        if filters is not None:
            [params.append(x) for x in filters.operations]

        response = self._get(f"/Api/V8/module/{module_name}", params=params)

        return response

    def get_all_records(
        self,
        module_name: str,
        fields: List[str] = None,
        page_size: int = 200,
        sort_dir: str = "ascending",
        sort_field: str = None,
        filters: Filter = None,
    ):
        """Get a generator which will iterate over all records for a given module in the CRM.

        Calls the endpoint documented at:
        https://8-x.docs.suitecrm.com/developer/api/developer-setup-guide/json-api/#_get_collection_of_modules
        repeatedly, following the `next` links until there are no more records to return.

        Parameters
        ----------
        module_name : str
            Module name to get the record(s) from.
        fields : List[str], optional
            List of fields to return, by default None.
        page_size : int, optional
            Number of records per page, when page_number is not None, by default 200.
        sort_dir : str, optional
            Search direction, "ascending" or "descending", by default "ascending".
        sort_field : str, optional
            Field to sort on, by default None.
        filters : Filter, optional
            Filters to filter down records, by default None.

        Returns
        -------
        dict

        Raises
        ------
        ValueError
            If sort direction is invalid.
        """
        response = self.get_records(
            module_name=module_name,
            fields=fields,
            page_size=page_size,
            page_number=1,
            sort_dir=sort_dir,
            sort_field=sort_field,
            filters=filters,
        )

        while response is not None and len(response["data"]) > 0:
            for module_record in response["data"]:
                yield module_record

            if response["links"]["next"] is not None:
                response = self._get("/Api/{}".format(response["links"]["next"]), params=[])
            else:
                response = None

    def create_record(self, module_name: str, record_data: dict) -> str:
        """Create a record in a given module in the CRM

        Calls the endpoint documented at:
        https://8-x.docs.suitecrm.com/developer/api/developer-setup-guide/json-api/#_create_a_module_record

        Parameters
        ----------
        module_name : str
            Module name to create the record in.
        record_data : dict
            Record data to store.

        Returns
        -------
        str
            ID of the created record.
        """
        entity_name = module_name[:-1] if module_name.endswith("s") else module_name

        payload = {"data": {"type": module_name, "attributes": record_data}}
        if "id" in record_data:
            payload["data"]["id"] = record_data["id"]
        response = self._post("/Api/V8/module", json=payload)

        if "data" not in response:
            logger.error("Attempt to create record failed: response was missing <data> key")
            raise CreateRecordFailed("Response missing data key")
        if response["data"].get("type", "") != entity_name:
            logger.error(
                "Attempt to create record failed: response module entity type "
                f"'{response["data"].get("type", "")}' does not match request {entity_name} "
                f" from module {module_name}"
            )
            raise CreateRecordFailed("Cannot understand response from server")
        if response["data"].get("id", None) is None:
            logger.error("Attempt to create record failed: id not returned in response")
            raise CreateRecordFailed("Cannot understand response from server")

        return response["data"]["id"]

    def update_record(self, module_name: str, id: str, record_data: dict) -> str:
        """Update a record in a given module in the CRM

        Calls the endpoint documented at:
        https://docs.suitecrm.com/developer/api/developer-setup-guide/json-api/#_update_a_module_record

        Parameters
        ----------
        module_name : str
            Module name to create the record in.
        id : str
            ID of the record
        record_data : dict
            Record data to update

        Returns
        -------
        str
            ID of the returned record
        """
        entity_name = module_name[:-1] if module_name.endswith("s") else module_name

        response = self._patch(
            "/Api/V8/module", json={"data": {"type": module_name, "id": id, "attributes": record_data}}
        )

        if "data" not in response:
            logger.error("Attempt to update record failed: response was missing <data> key")
            raise UpdateRecordFailed("Response missing data key")
        if response["data"].get("type", "") != entity_name:
            logger.error(
                "Attempt to create record failed: response module entity type "
                f"'{response["data"].get("type", "")}' does not match request {entity_name} "
                f" from module {module_name}"
            )
            raise UpdateRecordFailed("Cannot understand response from server")
        if response["data"].get("id", None) is None:
            logger.error("Attempt to update record failed: id not returned in response")
            raise UpdateRecordFailed("Cannot understand response from server")

        return response["data"]["id"]

    def delete_record(self, module_name: str, id: str):
        """Delete a record from a given module in the CRM

        Calls the endpoint documented at:
        https://docs.suitecrm.com/developer/api/developer-setup-guide/json-api/#_delete_a_module_record

        Parameters
        ----------
        module_name : str
            Module name to delete the record from.
        id : str
            ID of the record
        """

        response = self._delete(f"/Api/V8/module/{module_name}/{id}")

        if "meta" not in response:
            logger.error("Attempt to delete record failed: response was missing <meta> key")
            raise DeleteRecordFailed("Response missing meta key")
        if "message" not in response["meta"]:
            logger.error("Attempt to delete record failed: response was missing <meta.message> key")
            raise DeleteRecordFailed("Response missing meta.message key")
        if id not in response["meta"].get("message", ""):
            logger.error(f"Attempt to delete record failed: '{response["meta"]["message"]}'")
            raise DeleteRecordFailed("Cannot understand response from server")
        if "is deleted" not in response["meta"].get("message", ""):
            logger.error(f"Attempt to delete record failed: '{response["meta"]["message"]}'")
            raise DeleteRecordFailed("Cannot understand response from server")

    def create_relationship(self, module_name: str, id: str, related_module: str, related_id: str):
        """Create a relationship between records across modules in the CRM

        Calls the endpoint documented at:
        https://docs.suitecrm.com/developer/api/developer-setup-guide/json-api/#_create_relationship

        Parameters
        ----------
        module_name : str
            Module name to create the relationship from.
        id : str
            ID of the record to create the relationship from.
        related_module : str
            Module name to create the relationship to.
        related_id : str
            ID of the record to create the relationship to.
        """
        response = self._post(
            f"/Api/V8/module/{module_name}/{id}/relationships",
            json={"data": {"type": related_module, "id": related_id}},
        )

        if "meta" not in response:
            logger.error("Attempt to create relationship failed: response was missing <meta> key")
            raise CreateRelationshipFailed("Response missing meta key")
        if "message" not in response["meta"]:
            logger.error("Attempt to create relationship failed: response was missing <meta.message> key")
            raise CreateRelationshipFailed("Response missing meta.message key")
        if (
            response["meta"].get("message", "")
            != f"{related_module} with id {related_id} has been added to {module_name} with id {id}"
        ):
            logger.error(f"Attempt to create relationship failed: '{response["meta"]["message"]}'")
            raise CreateRelationshipFailed("Cannot understand response from server")

    def get_relationship(self, module_name: str, id: str, related_module: str):
        """Get relationships between a record in one module with another module

        Calls the endpoint documented at:
        https://docs.suitecrm.com/developer/api/developer-setup-guide/json-api/#_get_relationship

        Parameters
        ----------
        module_name : str
            Module name to get the relationship from.
        id : str
            ID of the record to get the relationship from.
        related_module : str
            Module name to get the relationship to.
        """
        response = self._get(f"/Api/V8/module/{module_name}/{id}/relationships/{related_module.lower()}")
        return response

    def delete_relationship(self, module_name: str, id: str, related_module: str, related_id: str):
        """Delete relationship between records in different modules

        Calls the endpoint documented at:
        https://docs.suitecrm.com/developer/api/developer-setup-guide/json-api/#_delete_relationship

        Parameters
        ----------
        module_name : str
            Module name to delete the relationship from.
        id : str
            ID of the record to delete the relationship from.
        related_module : str
            Related module name to delete the relationship from.
        related_id : str
            ID of the related record to delete the relationship from.
        """
        self._delete(f"/Api/V8/module/{module_name}/{id}/relationships/{related_module.lower()}/{related_id}")

    def _request(self, method: str, url: str, params: List[Tuple[str, str]] = None, json: Dict = None):  # noqa: C901
        """Internal method to send requests to SuiteCRM which also handles errors

        Parameters
        ----------
        method : str
            Method to call, "GET", "POST", "PATCH", "DELETE"
        url : str
            URL to call.
        params : List[Tuple[str,str]], optional
            Parameters to include in the request, default None.
        params : List[Tuple[str,str]], optional
            Parameters to include in the request, default None.

        Returns
        -------
        dict
            Dictionary containing the response.

        Raises
        ------
        RequestFailed
            If the request failed for some reason.
        """
        try:
            response = self._oauth_session.request(method, url, verify=self._secure, params=params, json=json)
            response.raise_for_status()

        except requests.HTTPError:
            if response.status_code == 401:
                self._fetch_access_token("Refreshing access token")
            try:
                response = self._oauth_session.request(method, url, verify=self._secure, params=params, json=json)
                response.raise_for_status()

            except requests.HTTPError:
                try:
                    resp_json = response.json()
                except requests.JSONDecodeError as err:
                    raise RequestFailed(
                        response.status_code,
                        response.reason,
                        f"Failed {method} from endpoint {urllib.parse.unquote(response.url)} but "
                        f"cannot decode JSON response ({response.text})",
                        str(err),
                    )

                error_detail = ""
                if "errors" in resp_json:
                    error_detail = resp_json["errors"].get("detail", "")
                logger.error(
                    f"Failed {method} from endpoint {urllib.parse.unquote(response.url)} with "
                    f"HTTP {response.status_code} ({error_detail})"
                )
                raise RequestFailed(
                    response.status_code,
                    response.reason,
                    f"Failed {method} from endpoint {urllib.parse.unquote(response.url)}",
                    error_detail,
                )

        except requests.ConnectionError as err:
            raise RequestFailed(
                response.status_code,
                response.reason,
                f"Failed {method} from endpoint {urllib.parse.unquote(response.url)} as there was a connection error",
                str(err),
            )

        try:
            resp_json = response.json()
        except requests.JSONDecodeError as err:
            fh = open("dump.txt", "w")
            fh.write(response.text)
            fh.close()
            raise RequestFailed(
                response.status_code,
                response.reason,
                f"Cannot decode response JSON from {method} to endpoint {url}",
                err.msg,
            )

        return resp_json

    def _get(self, api_endpoint: str, params: List[str] = None):
        """Internal method to send a GET request to SuiteCRM

        This method makes a GET request to an API endpoint
        and returns the JSON result as a dictionary.

        Parameters
        ----------
        api_endpoint : str
            Endpoint to call (which will be added to the base URL)
        params : List[str]
            Parameters to include in the request.

        Returns
        -------
        dict
            Dictionary containing the response.

        Raises
        ------
        RequestFailed
            If the request failed for some reason.
        """
        return self._request("GET", self._get_url(api_endpoint), params=params)

    def _post(self, api_endpoint: str, json=None):
        """Internal method to send a POST request to SuiteCRM

        This method makes a GET request to an API endpoint
        and returns the JSON result as a dictionary.

        Parameters
        ----------
        api_endpoint : str
            Endpoint to call (which will be added to the base URL)
        data : dict, optional
            Dictionary of data to set, default None.

        Returns
        -------
        dict
            Dictionary containing the response.

        Raises
        ------
        RequestFailed
            If the request failed for some reason.
        """
        return self._request("POST", self._get_url(api_endpoint), json=json)

    def _patch(self, api_endpoint, json=None):
        """Internal method to send a PATCH request to SuiteCRM

        This method makes a PATCH request to an API endpoint
        and returns the JSON result as a dictionary.

        Parameters
        ----------
        api_endpoint : str
            Endpoint to call (which will be added to the base URL)
        params : List[str]
            Parameters to include in the request.

        Returns
        -------
        dict
            Dictionary containing the response.

        Raises
        ------
        RequestFailed
            If the request failed for some reason.
        """
        return self._request("PATCH", self._get_url(api_endpoint), json=json)

    def _delete(self, api_endpoint):
        """Internal method to send a DELETE request to SuiteCRM

        This method makes a DELETE request to an API endpoint
        and returns the JSON result as a dictionary.

        Parameters
        ----------
        api_endpoint : str
            Endpoint to call (which will be added to the base URL)

        Returns
        -------
        dict
            Dictionary containing the response.

        Raises
        ------
        RequestFailed
            If the request failed for some reason.
        """
        return self._request("DELETE", self._get_url(api_endpoint))
