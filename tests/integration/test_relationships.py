from libsuitecrm import Filter


def test_relationships(crm):
    contact1 = crm.create_record("Contact", {"last_name": "Contact One"})
    contact2 = crm.create_record("Contact", {"last_name": "Contact Two"})
    accounta = crm.create_record("Account", {"name": "Organisation A"})
    accountb = crm.create_record("Account", {"name": "Organisation B"})

    # Create relationship between contacts and accounts.  Organisation A has two
    # contacts, Organisation B has one contact.  We create the relationships
    # and then test that they are correct.
    crm.create_relationship("Accounts", accounta["id"], "contacts", "Contacts", contact1["id"])
    crm.create_relationship("Accounts", accounta["id"], "contacts", "Contacts", contact2["id"])
    crm.create_relationship("Accounts", accountb["id"], "contacts", "Contacts", contact1["id"])

    response = crm.get_relationship("Account", accounta["id"], "contacts")
    assert "meta" in response
    assert response["meta"].get("total-records", 0) == 2
    assert "data" in response
    assert isinstance(response["data"], list)
    assert (
        (response["data"][0]["id"] == contact1["id"])
        and (response["data"][1]["id"] == contact2["id"])
        or (response["data"][0]["id"] == contact2["id"])
        and (response["data"][1]["id"] == contact1["id"])
    )

    response = crm.get_relationship("Account", accountb["id"], "contacts")
    assert "meta" in response
    assert response["meta"].get("total-records", 0) == 1
    assert "data" in response
    assert isinstance(response["data"], list)
    assert response["data"][0]["id"] == contact1["id"]

    # Test relationship between contacts and report_to in contacts, which has a more complicated link
    # field name (since the link field name for accounts and contacts is basically just the related
    # module name).  Create the relationship and check that it is correct when we get it.
    crm.create_relationship("Contacts", contact2["id"], "reports_to_link", "Contacts", contact1["id"])

    response = crm.get_relationship("Contacts", contact2["id"], "reports_to_link")
    assert "meta" in response
    assert response["meta"].get("total-records", 0) == 1
    assert "data" in response
    assert isinstance(response["data"], list)
    assert response["data"][0]["id"] == contact1["id"]

    # Remove relationships - each time we check that the relationships are as we expect.
    crm.delete_relationship("Contacts", contact2["id"], "reports_to_link", contact1["id"])
    response = crm.get_relationship("Contacts", contact2["id"], "reports_to_link")
    assert "meta" in response
    assert response["meta"].get("total-records", 0) == 0

    crm.delete_relationship("Account", accountb["id"], "contacts", contact1["id"])
    response = crm.get_relationship("Account", accountb["id"], "contacts")
    assert "meta" in response
    assert response["meta"].get("total-records", 0) == 0

    crm.delete_relationship("Account", accounta["id"], "contacts", contact2["id"])
    response = crm.get_relationship("Account", accounta["id"], "contacts")
    assert "meta" in response
    assert response["meta"].get("total-records", 0) == 1
    assert "data" in response
    assert isinstance(response["data"], list)
    assert response["data"][0]["id"] == contact1["id"]

    crm.delete_relationship("Account", accounta["id"], "contacts", contact1["id"])
    response = crm.get_relationship("Account", accounta["id"], "contacts")
    assert "meta" in response
    assert response["meta"].get("total-records", 0) == 0

    crm.delete_record("Contact", contact1["id"])
    crm.delete_record("Contact", contact2["id"])
    crm.delete_record("Account", accounta["id"])
    crm.delete_record("Account", accountb["id"])


def _create_account_contacts_and_relationships(crm, num_contacts: int):
    contacts: dict = []
    for contact_idx in range(1, num_contacts + 1):
        contact = crm.create_record("Contact", {"last_name": f"Contact {contact_idx}"})
        contacts.append(contact)

    account = crm.create_record("Account", {"name": "Organisation 1"})

    for contact in contacts:
        crm.create_relationship("Accounts", account["id"], "contacts", "Contacts", contact["id"])

    return account, contacts


def _delete_records(crm, records):
    for record in records:
        crm.delete_record(record["type"], record["id"])


def test_get_relationships_paging_returns_correct_num(crm):
    account, contacts = _create_account_contacts_and_relationships(crm, 9)

    for page_size in [None, 3, 4, 5]:
        relationships = crm.get_relationship("Accounts", account["id"], "contacts", page_size=page_size, page_number=1)
        assert len(relationships["data"]) == 9 if page_size is None else page_size

    _delete_records(crm, [account] + contacts)


def test_get_relationships_paging_returns_correct_content(crm):
    account, contacts = _create_account_contacts_and_relationships(crm, 9)

    relationships = crm.get_relationship(
        "Accounts", account["id"], "contacts", page_size=2, page_number=3, sort_field="last_name", sort_dir="ascending"
    )
    assert relationships["data"][0]["attributes"]["last_name"] == "Contact 5"
    assert relationships["data"][1]["attributes"]["last_name"] == "Contact 6"

    _delete_records(crm, [account] + contacts)


def test_get_relationships_sorting(crm):
    account, contacts = _create_account_contacts_and_relationships(crm, 9)

    relationships = crm.get_relationship(
        "Accounts", account["id"], "contacts", page_size=1, page_number=1, sort_field="last_name", sort_dir="ascending"
    )
    assert relationships["data"][0]["attributes"]["last_name"] == "Contact 1"

    relationships = crm.get_relationship(
        "Accounts",
        account["id"],
        "contacts",
        page_size=1,
        page_number=1,
        sort_field="last_name",
        sort_dir="descending",
    )
    assert relationships["data"][0]["attributes"]["last_name"] == "Contact 9"

    _delete_records(crm, [account] + contacts)


def test_get_relationships_filtering(crm):
    account, contacts = _create_account_contacts_and_relationships(crm, 9)

    relationships = crm.get_relationship(
        "Contacts", contacts[0]["id"], "Accounts", filters=Filter().equal("name", "Organisation 1")
    )

    assert len(relationships["data"]) == 1

    relationships = crm.get_relationship(
        "Contacts", contacts[0]["id"], "Accounts", filters=Filter().equal("name", "Organisation Unknown")
    )

    assert len(relationships["data"]) == 0

    _delete_records(crm, [account] + contacts)
