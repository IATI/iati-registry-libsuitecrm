import time
from datetime import timedelta

import pymysql
import pytest
from parameters import CLIENT_ID, CLIENT_SECRET, DB_HOST, DB_NAME, DB_PASSWORD, DB_USER, SUITECRM_HTTPS_URL

import libsuitecrm


def test_fetch_access_token_okay(suitecrm_ready):
    crm = libsuitecrm.SuiteCRM(SUITECRM_HTTPS_URL, client_id=CLIENT_ID, client_secret=CLIENT_SECRET, secure=False)
    crm.fetch_access_token()
    crm.logout()


def test_fetch_access_token_404(suitecrm_ready):
    with pytest.raises(libsuitecrm.exceptions.AuthorisationFailed) as exc_info:
        crm = libsuitecrm.SuiteCRM(
            SUITECRM_HTTPS_URL + "/wrong_path/", client_id=CLIENT_ID, client_secret=CLIENT_SECRET, secure=False
        )
        crm.fetch_access_token()

    assert "unreachable with HTTP 404" in exc_info.value.msg


def test_fetch_access_token_insecure(suitecrm_ready):
    with pytest.raises(libsuitecrm.exceptions.AuthorisationFailed) as exc_info:
        crm = libsuitecrm.SuiteCRM(SUITECRM_HTTPS_URL, client_id=CLIENT_ID, client_secret=CLIENT_SECRET, secure=True)
        crm.fetch_access_token()

    print(exc_info.value)
    assert "because the connection isn't secure" in exc_info.value.msg


def test_access_token_expiry(suitecrm_ready):
    # Get an access token.
    crm = libsuitecrm.SuiteCRM(SUITECRM_HTTPS_URL, client_id=CLIENT_ID, client_secret=CLIENT_SECRET, secure=False)
    crm.fetch_access_token()

    # Modify the access token inside the SuiteCRM database to expire 1 second after creation.
    try:
        connection = pymysql.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            db=DB_NAME,
            charset="utf8mb4",
            cursorclass=pymysql.cursors.DictCursor,
        )
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT id, date_entered, access_token_expires FROM oauth2tokens ORDER BY date_entered DESC LIMIT 1"
            )
            result = cursor.fetchone()

            if result is None:
                raise ValueError("Cannot find an access token")

            cursor.execute(
                "UPDATE oauth2tokens SET access_token_expires=%s WHERE id=%s",
                (result["date_entered"] + timedelta(seconds=1), result["id"]),
            )
            connection.commit()

            cursor.execute(
                "SELECT id, date_entered, access_token_expires FROM oauth2tokens ORDER BY date_entered DESC LIMIT 1"
            )
            result = cursor.fetchone()

    except Exception as err:
        raise err

    # Wait for the token to expire then call the API.
    time.sleep(2)
    with pytest.raises(libsuitecrm.exceptions.RequestFailed) as exc_info:
        crm.get_modules()

    assert exc_info.value.status_code == 401
