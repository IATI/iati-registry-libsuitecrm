import libsuitecrm


def test_fields_formatting():
    result = libsuitecrm.crm._format_fields("Account", ["name", "date_entered"])
    assert result[0][0] == "fields[Account]"
    assert result[0][1] == "name,date_entered"


def test_operators():
    filters = (
        libsuitecrm.Filter()
        .notequal("a", "0")
        .op_or()
        .equal("b", "A")
        .op_and()
        .gt("c", 5)
        .op_and()
        .gte("d", 0)
        .op_or()
        .lt("e", 10)
        .op_or()
        .lte("f", 100)
        .operations
    )
    assert filters[0] == ("filter[a][neq]", "0")
    assert filters[1] == ("filter[operator]", "or")
    assert filters[2] == ("filter[b][eq]", "A")
    assert filters[3] == ("filter[operator]", "and")
    assert filters[4] == ("filter[c][gt]", 5)
    assert filters[5] == ("filter[operator]", "and")
    assert filters[6] == ("filter[d][gte]", 0)
    assert filters[7] == ("filter[operator]", "or")
    assert filters[8] == ("filter[e][lt]", 10)
    assert filters[9] == ("filter[operator]", "or")
    assert filters[10] == ("filter[f][lte]", 100)
