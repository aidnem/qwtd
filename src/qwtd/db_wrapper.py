"""
Wrapper around TUI app to ensure the proper closing of the database.
"""

import os
import sqlite3

from qwtd import app


def run_with_db():
    db_path = os.path.join(os.path.expanduser("~"), "qwtd.db")
    print(f"[QWTD] Opening database at {db_path}")

    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()

    try:
        # Ensure that table exists
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS notes(name, content, date_modified)
            """
        )

        # Launch app
        app.run_app(connection, cursor)
    finally:
        connection.close()
