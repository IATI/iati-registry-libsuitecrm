def test_relationships(crm):
    contact1_id = crm.create_record("Contact", {"last_name": "Contact One"})
    contact2_id = crm.create_record("Contact", {"last_name": "Contact Two"})
    accounta_id = crm.create_record("Account", {"name": "Organisation A"})
    accountb_id = crm.create_record("Account", {"name": "Organisation B"})

    # Create relationship between contacts and accounts.  Organisation A has two
    # contacts, Organisation B has one contact.  We create the relationships
    # and then test that they are correct.
    crm.create_relationship("Accounts", accounta_id, "contacts", "Contacts", contact1_id)
    crm.create_relationship("Accounts", accounta_id, "contacts", "Contacts", contact2_id)
    crm.create_relationship("Accounts", accountb_id, "contacts", "Contacts", contact1_id)

    response = crm.get_relationship("Account", accounta_id, "contacts")
    assert "meta" in response
    assert response["meta"].get("total-records", 0) == 2
    assert "data" in response
    assert isinstance(response["data"], list)
    assert (
        (response["data"][0]["id"] == contact1_id)
        and (response["data"][1]["id"] == contact2_id)
        or (response["data"][0]["id"] == contact2_id)
        and (response["data"][1]["id"] == contact1_id)
    )

    response = crm.get_relationship("Account", accountb_id, "contacts")
    assert "meta" in response
    assert response["meta"].get("total-records", 0) == 1
    assert "data" in response
    assert isinstance(response["data"], list)
    assert response["data"][0]["id"] == contact1_id

    # Test relationship between contacts and report_to in contacts, which has a more complicated link
    # field name (since the link field name for accounts and contacts is basically just the related
    # module name).  Create the relationship and check that it is correct when we get it.
    crm.create_relationship("Contacts", contact2_id, "reports_to_link", "Contacts", contact1_id)

    response = crm.get_relationship("Contacts", contact2_id, "reports_to_link")
    assert "meta" in response
    assert response["meta"].get("total-records", 0) == 1
    assert "data" in response
    assert isinstance(response["data"], list)
    assert response["data"][0]["id"] == contact1_id

    # Remove relationships - each time we check that the relationships are as we expect.
    crm.delete_relationship("Contacts", contact2_id, "reports_to_link", contact1_id)
    response = crm.get_relationship("Contacts", contact2_id, "reports_to_link")
    assert "meta" in response
    assert response["meta"].get("total-records", 0) == 0

    crm.delete_relationship("Account", accountb_id, "contacts", contact1_id)
    response = crm.get_relationship("Account", accountb_id, "contacts")
    assert "meta" in response
    assert response["meta"].get("total-records", 0) == 0

    crm.delete_relationship("Account", accounta_id, "contacts", contact2_id)
    response = crm.get_relationship("Account", accounta_id, "contacts")
    assert "meta" in response
    assert response["meta"].get("total-records", 0) == 1
    assert "data" in response
    assert isinstance(response["data"], list)
    assert response["data"][0]["id"] == contact1_id

    crm.delete_relationship("Account", accounta_id, "contacts", contact1_id)
    response = crm.get_relationship("Account", accounta_id, "contacts")
    assert "meta" in response
    assert response["meta"].get("total-records", 0) == 0

    crm.delete_record("Contact", contact1_id)
    crm.delete_record("Contact", contact2_id)
    crm.delete_record("Account", accounta_id)
    crm.delete_record("Account", accountb_id)
