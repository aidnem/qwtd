"""
Utilities to initialize and update the database to the latest version.
"""

from datetime import datetime, timedelta
from sqlite3 import Connection


"""
This file is intended to manage the multiple database schemas the have/will
exist(ed) over the course of the project. QWTD uses the user_version pragma to
determine the current format of the database to ensure that the user's db is
migrated correctly when a breaking database format change is made.

Version 0:
    This is a hard version to detect, since it could indicate either:
        - The database is brand new, and hasn't been initialized
            -> In this case, the correct behavior is to initialize the latest version
    OR
        - The database is old, and is from before user_version was used
            -> In this case, the correct behavior is to migrate through every version

    This is handled by going directly to latest version initialization if the
    database file doesn't exist according to db_wrapper when it invokes ensure_db

    Format:
        - table notes:
            - name TEXT PRIMARY KEY
            - content TEXT
            - date_modified TIMESTAMP
        - table last_deleted:
            - name TEXT
            last_deleted must always contain exactly one row, by default it is
            initialized to "Deleted".
        - PRAGMA user_version 0
Version 1:
    Database Version 1 introduces a better way of handling deleted notes:
    rather than renaming the deleted note to Deleted, it tracks whether or not
    each note is "deleted" (equivalent to putting a file in the a trash folder)
    and then marks the note to expire 1 week after the note was "deleted". On
    app startup, all notes that have "expired" will be permanently deleted.

    This version removes the need for the last_deleted table.

    Format:
        - table notes:
            - name TEXT PRIMARY KEY
            - content TEXT
            - date_modfied TIMESTAMP
            - deleted INTEGER (boolean)
                A boolean value indicating whether or not this note is deleted
            - expires TIMESTAMP
                If the deleted == 1, expires indicates the time at which this
                note should be permanently deleted.
        - PRAGMA user_version 1
"""


LATEST_DB_VERSION = 1


def ensure_db(connection: Connection, just_created: bool):
    """
    Ensure that the correct tables exist and the structure is up to date

    :param connection: The conection to the database
    :type connection: sqlite3.Connection
    """

    if just_created:
        initialize_latest(connection)
        return

    cur = connection.execute("PRAGMA user_version")
    user_version: int = cur.fetchone()[0]

    while user_version < LATEST_DB_VERSION:
        print(f"[QWTD] Database is outdated (version {user_version}); migrating up")
        user_version = migrate_db(user_version, connection)
    else:
        print(f"[QWTD] Database was already up to date (version {user_version})")


def initialize_latest(connection: Connection):
    """
    Initialize the database with the latest schema.

    This function only runs when a database is brand-new, so it can assume that
    no tables exist before it is executed.
    """

    # Ensure that table exists
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS notes(
            name TEXT PRIMARY KEY,
            content TEXT,
            date_modified TIMESTAMP,
            deleted INTEGER,
            expires TIMESTAMP
        )
        """
    )

    connection.execute(
        """
        PRAGMA user_version=1
        """
    )

    connection.commit()


def migrate_db(version: int, connection: Connection) -> int:
    """
    Migrate a database as far up in version as is possible in 1 step

    It may be necessary to call this function multiple times to get up to date.
    """

    match version:
        case 0:
            return migrate_v0_to_v1(connection)
        # Don't migrate if it's the latest version
        case 1:
            return 1
        case _:
            msg = f"Invalid db version {version} passed to migrate_version\n"
            msg += "  This is most likely QWTD issue, not the user's fault\n"
            msg += "  If this issue is unexpected (e.g. you did not manually\n"
            msg += "  edit the database), please report it on github!\n"
            msg += "  https://github.com/aidnem/qwtd\n"

            raise ValueError(msg)


def migrate_v0_to_v1(connection) -> int:
    """
    Migrate a database from format 0 to format 1
    """

    # First, add the necessary columns to the table
    connection.execute(
        """
        ALTER TABLE notes ADD COLUMN deleted INTEGER DEFAULT 0
        """
    )

    connection.execute(
        f"""
        ALTER TABLE notes
        ADD COLUMN expires TIMESTAMP
        DEFAULT '{datetime.now()}'
        """
    )

    connection.commit()

    # After updating database structure, reformat the deleted note
    last_deleted: str = connection.execute("SELECT * FROM last_deleted").fetchone()[0]

    if last_deleted != "Deleted":
        # last_deleted is initialized to "Deleted" before any note is deleted;
        # The last deleted note only needs to be migrated if a note has been
        # Deleted
        week_from_today = datetime.now() + timedelta(days=7)

        # Move the note from "Deleted" to its real name, with an expiration
        connection.execute(
            """
            UPDATE notes
            SET name = ?,
                deleted = 1,
                expires = ?
            WHERE name = 'Deleted'
            """,
            (last_deleted, week_from_today),
        )

    # Finally, delete the last_deleted database
    connection.execute("DROP TABLE last_deleted")

    connection.execute("PRAGMA user_version=1")

    connection.commit()

    # This results in a user version of 1
    return 1


def delete_expired_notes(connection: Connection):
    """
    The final step of database initialization, delete all notes that have been
    deleted and have expired.
    """

    connection.execute(
        "DELETE FROM notes WHERE deleted == 1 AND expires < ?",
        (datetime.now(),),
    )
