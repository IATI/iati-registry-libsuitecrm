import logging

from .crm import SuiteCRM
from .exceptions import CannotUnderstandResponse, RequestFailed
from .filter import Filter

__all__ = [
    "SuiteCRM",
    "Filter",
    "RequestFailed",
    "CannotUnderstandResponse",
    "AuthorisationFailed",
    "CreateRecordFailed",
    "UpdateRecordFailed",
    "DeleteRecordFailed",
    "CreateRelationshipFailed",
]

logging.getLogger(__name__).addHandler(logging.NullHandler())
