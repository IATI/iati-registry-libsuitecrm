def test_get_modules(crm):
    modules = crm.get_modules()
    assert "Accounts" in modules["data"]["attributes"]


def test_get_module_fields(crm):
    account_fields = crm.get_module_fields("Accounts")
    assert "billing_address_street" in account_fields["data"]["attributes"]
