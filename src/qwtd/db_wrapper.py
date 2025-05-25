"""
Wrapper around TUI app to ensure the proper closing of the database.
"""

import os
import sqlite3

from qwtd import app


def run_with_db():
    """
    Open a connection to the database, run the app, and close connection when done
    """

    db_path = os.path.join(os.path.expanduser("~"), "qwtd.db")
    print(f"[QWTD] Opening database at {db_path}")

    connection = sqlite3.connect(db_path)

    try:
        # Ensure that table exists
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS notes(name TEXT PRIMARY KEY, content TEXT, date_modified TIMESTAMP)
            """
        )

        # Launch app
        app.run_app(connection)
    finally:
        print("[QWTD] Closing db connection.")
        connection.close()
