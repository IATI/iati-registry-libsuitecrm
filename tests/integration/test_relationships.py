def test_relationships(crm):
    contact1_id = crm.create_record("Contact", {"last_name": "Contact One"})
    contact2_id = crm.create_record("Contact", {"last_name": "Contact Two"})
    accounta_id = crm.create_record("Account", {"name": "Organisation A"})
    accountb_id = crm.create_record("Account", {"name": "Organisation B"})

    crm.create_relationship("Account", accounta_id, "Contact", contact1_id)
    crm.create_relationship("Account", accounta_id, "Contact", contact2_id)
    crm.create_relationship("Account", accountb_id, "Contact", contact1_id)

    crm.get_relationship("Account", accounta_id, "Contacts")
    crm.get_relationship("Account", accountb_id, "Contacts")

    crm.delete_relationship("Account", accountb_id, "Contacts", contact1_id)
    crm.delete_relationship("Account", accounta_id, "Contacts", contact2_id)
    crm.delete_relationship("Account", accounta_id, "Contacts", contact1_id)

    crm.delete_record("Contact", contact1_id)
    crm.delete_record("Contact", contact2_id)
    crm.delete_record("Account", accounta_id)
    crm.delete_record("Account", accountb_id)
