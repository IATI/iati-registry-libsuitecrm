import uuid
from unittest import mock

import pytest
from helpers import make_random_string

import libsuitecrm


def test_crud_in_accounts(crm):
    random_org_name = make_random_string(15)

    new_record = crm.create_record("Account", {"name": random_org_name})
    id = new_record["id"]
    assert isinstance(id, str)

    response = crm.get_record_by_id("Account", id, fields=["name"])
    assert "data" in response
    assert response["data"].get("type", "") == "Account"
    assert "attributes" in response["data"]
    assert response["data"]["attributes"].get("name", "") == random_org_name

    new_random_org_name = make_random_string(15)
    response = crm.update_record("Account", id, {"name": new_random_org_name})
    assert response["id"] == id

    response = crm.get_record_by_id("Account", id, fields=["name"])
    assert "data" in response
    assert response["data"].get("type", "") == "Account"
    assert "attributes" in response["data"]
    assert response["data"]["attributes"].get("name", "") == new_random_org_name

    crm.delete_record("Account", id)
    with pytest.raises(libsuitecrm.exceptions.RequestFailed) as exc_info:
        crm.get_record_by_id("Account", id)
    assert exc_info.value.status_code == 400
    assert "is not found" in exc_info.value.underlying_msg


def test_create_with_id(crm):

    # Make account with specific id and check we get that id back after
    # the account is created.
    random_org_name = make_random_string(15)
    new_id = str(uuid.uuid4())
    new_record = crm.create_record("Account", {"name": random_org_name, "id": new_id})
    created_id = new_record["id"]
    assert isinstance(created_id, str)
    assert new_id == created_id

    # Check we can retrieve by the new_id.
    response = crm.get_record_by_id("Account", created_id, fields=["name"])
    assert "data" in response
    assert response["data"].get("type", "") == "Account"
    assert "attributes" in response["data"]
    assert response["data"]["attributes"].get("name", "") == random_org_name

    # Delete the created organisation.
    response = crm.delete_record("Account", new_id)


@pytest.mark.parametrize("headers", [None, {"X-Custom-Header": "CustomValue"}])
def test_create_custom_headers(crm, headers) -> None:

    org_id = str(uuid.uuid4())
    org_name = make_random_string(15)

    crm._oauth_session = mock.MagicMock()

    request_response = mock.MagicMock()
    request_response.json.return_value = {
        "data": {
            "id": org_id,
            "type": "Account",
            "attributes": {"name": org_name},
        }
    }
    crm._oauth_session.request.return_value = request_response

    crm.create_record("Account", {"name": org_name, "id": org_id}, headers=headers)

    crm._oauth_session.request.assert_called_with(
        "POST", mock.ANY, verify=mock.ANY, params=mock.ANY, json=mock.ANY, headers=headers  # url
    )


@pytest.mark.parametrize("headers", [None, {"X-Custom-Header": "CustomValue"}])
def test_update_custom_headers(crm, headers) -> None:

    org_id = str(uuid.uuid4())
    org_name = make_random_string(15)

    crm._oauth_session = mock.MagicMock()

    request_response = mock.MagicMock()
    request_response.json.return_value = {
        "data": {
            "id": org_id,
            "type": "Account",
            "attributes": {"name": org_name},
        }
    }
    crm._oauth_session.request.return_value = request_response

    crm.update_record("Account", org_id, {"name": org_name}, headers=headers)

    crm._oauth_session.request.assert_called_with(
        "PATCH", mock.ANY, verify=mock.ANY, params=mock.ANY, json=mock.ANY, headers=headers  # url
    )


@pytest.mark.parametrize("headers", [None, {"X-Custom-Header": "CustomValue"}])
def test_delete_custom_headers(crm, headers) -> None:

    org_id = str(uuid.uuid4())
    org_name = make_random_string(15)

    crm._oauth_session = mock.MagicMock()

    request_response = mock.MagicMock()
    request_response.json.return_value = {"meta": {"message": f"Record {org_id} is deleted"}}
    crm._oauth_session.request.return_value = request_response

    crm.delete_record("Account", org_id, headers=headers)

    crm._oauth_session.request.assert_called_with(
        "DELETE", mock.ANY, verify=mock.ANY, params=mock.ANY, json=mock.ANY, headers=headers  # url
    )
