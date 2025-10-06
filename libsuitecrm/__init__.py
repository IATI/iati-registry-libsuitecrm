import logging

from .crm import SuiteCRM
from .exceptions import CannotUnderstandResponse, RequestFailed, AuthorisationFailed, CreateRecordFailed, UpdateRecordFailed, DeleteRecordFailed, CreateRelationshipFailed
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
