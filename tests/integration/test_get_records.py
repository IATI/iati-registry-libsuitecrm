import pytest

import libsuitecrm


def test_get_record_failures(crm):
    with pytest.raises(libsuitecrm.exceptions.RequestFailed) as exc_info:
        crm.get_record_by_id("Account", "id-that-will-fail")
    assert exc_info.value.status_code == 400

    record = crm.create_record("Account", {"name": "Org Name"})
    assert isinstance(record["id"], str)
    with pytest.raises(libsuitecrm.exceptions.RequestFailed) as exc_info:
        crm.get_record_by_id("Account", record["id"], fields=["non_existant_field_name"])
    assert exc_info.value.status_code == 400
    crm.delete_record("Account", record["id"])


def test_get_multiple_records(crm):
    records = [crm.create_record("Account", {"name": x}) for x in ["A", "B", "C", "D", "E"]]
    response = crm.get_records("Accounts", fields=["name", "deleted"], sort_dir="ascending", sort_field="name")

    assert "data" in response
    assert isinstance(response["data"], list)
    for index, record in enumerate(response["data"]):
        assert record.get("type", "") == "Account"
        assert record.get("id", "") == records[index]["id"]
    [crm.delete_record("Accounts", record["id"]) for record in records]


def test_filters(crm):
    test_records = [
        {"name": "UK Person A", "country": "UK", "description": "Text 1"},
        {"name": "UK Person B", "country": "UK", "description": "Text 1"},
        {"name": "UK Person C", "country": "UK", "description": "Text 2"},
        {"name": "German Person D", "country": "Germany", "description": "Text 1"},
        {"name": "German Person E", "country": "Germany", "description": "Text 1"},
        {"name": "German Person F", "country": "Germany", "description": "Text 2"},
    ]

    for index, record in enumerate(test_records):
        test_records[index]["id"] = crm.create_record(
            "Account",
            {
                "name": record["name"],
                "billing_address_country": record["country"],
                "description": record["description"],
            },
        )["id"]

    response = crm.get_records(
        "Accounts",
        fields=["name", "description", "billing_address_country"],
        sort_dir="ascending",
        sort_field="name",
        filters=libsuitecrm.Filter().equal("billing_address_country", "UK").op_and().equal("description", "Text 1"),
    )
    assert "data" in response
    assert isinstance(response["data"], list)
    # print(test_records)
    # [print(x["id"]) for x in response["data"]]
    assert len(response["data"]) == 2
    assert response["data"][0]["id"] == test_records[0]["id"]
    assert response["data"][1]["id"] == test_records[1]["id"]

    response = crm.get_records(
        "Accounts",
        fields=["name", "description", "billing_address_country"],
        sort_dir="ascending",
        sort_field="name",
        filters=libsuitecrm.Filter()
        .equal("billing_address_country", "Germany")
        .op_and()
        .notequal("description", "Text 1"),
    )
    assert "data" in response
    assert isinstance(response["data"], list)
    # print(test_records)
    # [print(x["id"]) for x in response["data"]]
    assert len(response["data"]) == 1
    assert response["data"][0]["id"] == test_records[5]["id"]

    [crm.delete_record("Accounts", record["id"]) for record in test_records]
