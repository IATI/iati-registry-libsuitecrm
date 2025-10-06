import logging

from .crm import SuiteCRM
from .exceptions import (
    AuthorisationFailed,
    CannotUnderstandResponse,
    CreateRecordFailed,
    CreateRelationshipFailed,
    DeleteRecordFailed,
    RequestFailed,
    UpdateRecordFailed,
)
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
