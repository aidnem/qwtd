"""
Wrapper around TUI app to ensure the proper closing of the database.
"""

import sqlite3

from qwtd import app
from qwtd import config


def run_with_db():
    """
    Open a connection to the database, run the app, and close connection when done
    """

    db_path = config.get_db_path()
    print(f"[QWTD] Opening database at {db_path}")

    connection = sqlite3.connect(db_path)

    try:
        # Ensure that table exists
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS notes(name TEXT PRIMARY KEY, content TEXT, date_modified TIMESTAMP)
            """
        )

        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS last_deleted(name TEXT)
            """
        )

        if len(connection.execute("SELECT * FROM last_deleted").fetchall()) == 0:
            connection.execute(
                """
                INSERT INTO last_deleted(name) VALUES('Deleted')
                """
            )

        connection.commit()

        # Launch app
        app.run_app(connection)
    finally:
        print("[QWTD] Closing db connection.")
        connection.close()
