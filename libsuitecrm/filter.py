"""Filter class to specify filtering of records when getting sets of records"""


class Filter:
    def __init__(self):
        self._operations = []

    def equal(self, field: str, value: str):
        self._operations.append((f"filter[{field}][eq]", value))
        return self

    def notequal(self, field: str, value: str):
        self._operations.append((f"filter[{field}][neq]", value))
        return self

    def gt(self, field: str, value: str):
        self._operations.append((f"filter[{field}][gt]", value))
        return self

    def gte(self, field: str, value: str):
        self._operations.append((f"filter[{field}][gte]", value))
        return self

    def lt(self, field: str, value: str):
        self._operations.append((f"filter[{field}][lt]", value))
        return self

    def lte(self, field: str, value: str):
        self._operations.append((f"filter[{field}][lte]", value))
        return self

    def like(self, field: str, value: str):
        self._operations.append((f"filter[{field}][like]", value))
        return self

    def op_and(self):
        self._operations.append(("filter[operator]", "and"))
        return self

    def op_or(self):
        self._operations.append(("filter[operator]", "or"))
        return self

    @property
    def operations(self):
        return self._operations
