"""
Wrapper around TUI app to ensure the proper closing of the database.
"""

import os
import sqlite3

from qwtd import app
from qwtd import config
from qwtd import db_setup


def run_with_db() -> None:
    """
    Open a connection to the database, run the app, and close connection when done
    """

    db_path = config.get_db_path()

    first_open: bool = not os.path.exists(db_path)

    print(f"[QWTD] Opening database at {db_path}")

    connection = sqlite3.connect(
        db_path, detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES
    )

    try:
        db_setup.ensure_db(connection, first_open)

        db_setup.delete_expired_notes(connection)

        # Launch app
        app.run_app(connection)
    finally:
        print("[QWTD] Closing db connection.")
        connection.close()
