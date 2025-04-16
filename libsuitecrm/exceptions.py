class RequestFailed(Exception):
    """Exception raised when request sent to SuiteCRM fails"""

    def __init__(self, status_code: int, status_reason: str, msg: str, underlying_msg: str):
        self.status_code = status_code
        self.status_reason = status_reason
        self.msg = msg
        self.underlying_msg = underlying_msg

    def __str__(self):
        return f"HTTP {self.status_code}: {self.msg} ({self.underlying_msg})"


class CannotUnderstandResponse(Exception):
    """Exception raised when the response from SuiteCRM cannot be understood"""

    def __init__(self, msg: str):
        self.msg = msg


class AuthorisationFailed(Exception):
    """Exception raised when we cannot get an access token to access the API"""

    def __init__(self, msg: str):
        self.msg = msg


class CreateRecordFailed(Exception):
    """Exception raised when a record creation failed"""

    def __init__(self, msg: str):
        self.msg = msg


class UpdateRecordFailed(Exception):
    """Exception raised when a record update failed"""

    def __init__(self, msg: str):
        self.msg = msg


class DeleteRecordFailed(Exception):
    """Exception raised when a record delete failed"""

    def __init__(self, msg: str):
        self.msg = msg


class CreateRelationshipFailed(Exception):
    """Exception raised when a relationship creation failed"""

    def __init__(self, msg: str):
        self.msg = msg
