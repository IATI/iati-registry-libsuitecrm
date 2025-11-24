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