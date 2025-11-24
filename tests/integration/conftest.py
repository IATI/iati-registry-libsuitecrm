import time

import pymysql
import pytest
import urllib3
from helpers import add_oauth_client_credentials, is_suitecrm_installed
from parameters import (
    CLIENT_ID,
    CLIENT_SECRET,
    CLIENT_SECRET_HASHED,
    DB_HOST,
    DB_NAME,
    DB_PASSWORD,
    DB_USER,
    SUITECRM_HTTP_URL,
    SUITECRM_HTTPS_URL,
)

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
        if is_suitecrm_installed(SUITECRM_HTTP_URL):
            installed = True

    if not installed and duration > TIMEOUT:
        raise SuiteCrmReadyTimeout("SuiteCRM timed out; was not ready inside {duration} seconds")

    # Try to add OAuth client credentials to the SuiteCRM database.
    try:
        add_oauth_client_credentials(CLIENT_ID, CLIENT_SECRET_HASHED, DB_NAME, DB_HOST, DB_USER, DB_PASSWORD)
    except Exception as err:
        raise err


@pytest.fixture(scope="function", autouse=True)
def clear_tables_used_by_tests(suitecrm_ready) -> None:
    """Fixture to clear tables used by tests before each test function"""
    try:
        connection = pymysql.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME,
            charset="utf8mb4",
        )
        with connection.cursor() as cursor:
            cursor.execute("SET sql_safe_updates = 0")
            cursor.execute("DELETE FROM accounts_cstm")
            cursor.execute("DELETE FROM accounts_contacts")
            cursor.execute("DELETE FROM accounts")
            cursor.execute("DELETE FROM oauth2tokens")
            connection.commit()
    except Exception as err:
        raise err


@pytest.fixture()
def crm(clear_tables_used_by_tests):
    """Fixture to wait for SuiteCRM to be available and then create a crm object with an access token"""
    urllib3.disable_warnings()
    _crm = libsuitecrm.SuiteCRM(SUITECRM_HTTPS_URL, client_id=CLIENT_ID, client_secret=CLIENT_SECRET, secure=False)
    _crm.fetch_access_token()

    return _crm
