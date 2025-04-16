import pytest
from helpers import make_random_string

import libsuitecrm


def test_crud_in_accounts(crm):
    random_org_name = make_random_string(15)

    id = crm.create_record("Account", {"name": random_org_name})
    assert isinstance(id, str)

    response = crm.get_record_by_id("Account", id, fields=["name"])
    assert "data" in response
    assert response["data"].get("type", "") == "Account"
    assert "attributes" in response["data"]
    assert response["data"]["attributes"].get("name", "") == random_org_name

    new_random_org_name = make_random_string(15)
    response = crm.update_record("Account", id, {"name": new_random_org_name})
    assert response == id

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
