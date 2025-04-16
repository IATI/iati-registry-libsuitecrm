import time

import pytest
import urllib3
from helpers import add_oauth_client_credentials, is_suitecrm_installed
from parameters import CLIENT_ID, CLIENT_SECRET, CLIENT_SECRET_HASHED

import libsuitecrm


class SuiteCrmReadyTimeout(Exception):
    """Exception raised if SuiteCRM times out when checking if ready"""

    def __init__(self, msg: str):
        self.msg = msg

    def __str__(self):
        return self.msg


@pytest.fixture(scope="session")
def suitecrm_ready():
    """Fixture to wait until SuiteCRM is ready to accept connections

    Raises
    ------
    SuiteCrmReadyTimeout
        If SuiteCRM times out when waiting.
    Exception
        Other exceptions are re-thrown.
    """

    # Wait until SuiteCRM shows a login screen.
    TIMEOUT = 300.0
    PERIOD = 5.0
    PAUSE = 0.0

    time.sleep(PAUSE)
    time_start = time.monotonic()
    duration = 0.0
    installed = False
    while duration < TIMEOUT and not installed:
        duration = time.monotonic() - time_start
        time.sleep(PERIOD - duration % PERIOD)
        if is_suitecrm_installed("http://127.0.0.1:8080"):
            installed = True

    if duration > TIMEOUT:
        raise SuiteCrmReadyTimeout("SuiteCRM timed out; was not ready inside {duration} seconds")

    # Try to add OAuth client credentials to the SuiteCRM database.
    try:
        add_oauth_client_credentials(CLIENT_ID, CLIENT_SECRET_HASHED)
    except Exception as err:
        raise err


@pytest.fixture(scope="module")
def crm(suitecrm_ready):
    """Fixture to wait for SuiteCRM to be available and then create a crm object with an access token"""
    urllib3.disable_warnings()
    _crm = libsuitecrm.SuiteCRM(
        "https://127.0.0.1:8443", client_id=CLIENT_ID, client_secret=CLIENT_SECRET, secure=False
    )
    _crm.fetch_access_token()

    return _crm
