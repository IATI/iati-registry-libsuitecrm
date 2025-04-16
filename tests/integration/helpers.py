import random
import string
import urllib

import pymysql
import requests
from requests.exceptions import ConnectionError


def make_random_string(length: int) -> str:
    """Make a random string of letters

    Parameters
    ----------
    length : int
        Number of letters in the string.

    Returns
    -------
    str
    """
    return "".join(random.choices(string.ascii_letters, k=length))


def is_suitecrm_installed(url_base: str) -> bool:
    """Check to see if SuiteCRM has been installed

    We check to see if the index page loads with HTTP 200 and if
    so make sure that the web page is displaying a login form.

    Parameters
    ----------
    url_base : str
        Base of the URL to SuiteCRM.

    Returns
    -------
    bool
    """
    try:
        response = requests.get(urllib.parse.urljoin(url_base, "index.php"))
        if response.status_code == 200 and "loginform" in response.text:
            return True
        return False

    except ConnectionError:
        return False


def add_oauth_client_credentials(client_id: str, client_secret_hashed: str):
    """Add SuiteCRM OAuth2 Client credentials directly into the database

    Parameters
    ----------
    client_id : str
        Client ID to add.
    client_secret_hashed : str
        Pre-hashed version of the client secret to add.
    """
    try:
        connection = pymysql.connect(
            host="localhost",
            user="root",
            password="rootpassword",
            db="suitecrm",
            charset="utf8mb4",
            cursorclass=pymysql.cursors.DictCursor,
        )
        with connection.cursor() as cursor:
            cursor.execute("SELECT id, name from oauth2clients")
            result = cursor.fetchone()

            if result is not None:
                cursor.execute(f"DELETE FROM oauth2clients WHERE id='{client_id}'")
                connection.commit()

            sql = (
                "INSERT INTO oauth2clients (id,name,secret,allowed_grant_type"
                ",duration_value,duration_amount,duration_unit,assigned_user_id)"
                " VALUES (%s,%s,%s,%s,%s,%s,%s,%s)"
            )
            cursor.execute(
                sql,
                (
                    client_id,
                    "test_client",
                    client_secret_hashed,
                    "client_credentials",
                    60,
                    1,
                    "minute",
                    "1",
                ),
            )

            connection.commit()

    except Exception as err:
        raise err
