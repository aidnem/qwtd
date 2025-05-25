"""
Class for handling the state of the text editor
"""

import datetime
from sqlite3 import Connection, Cursor

from prompt_toolkit.key_binding import KeyBindings, KeyPressEvent
from prompt_toolkit.widgets import TextArea


class Editor:
    """
    Handles state of the editor, reading, writing, and keyboard shortcuts
    """

    def __init__(self, connection: Connection, text_area: TextArea):
        """
        Create a new Editor

        :param connection: Connection to the database
        :type connection: sqlite3.Connection
        :param text_area: Main editor text area
        :type text_area: TextArea
        """

        self.connection: Connection = connection
        self.text_area: TextArea = text_area

        self.current_note: str | None = None
        self.last_saved_content: str = ""

    def open_note(self, note_name: str):
        """
        Open a note and update its content in the textarea
        """

        cursor: Cursor = self.connection.execute(
            """
            SELECT content FROM notes WHERE name=?
            """,
            (note_name,),
        )

        result: tuple[str] | None = cursor.fetchone()
        if result:
            self.text_area.buffer.text = result[0]
        else:
            self.text_area.buffer.text = f"# {note_name}\n\n"
            self.text_area.control.move_cursor_down()
            self.text_area.control.move_cursor_down()

        self.current_note = note_name
        self.last_saved_content = self.text_area.buffer.text

    def write(self):
        """
        Write the current note to the database
        """
        if self.current_note is None:
            return

        data = {
            "name": self.current_note,
            "content": self.text_area.text,
            "date_modified": datetime.datetime.now(),
        }

        self.connection.execute(
            """
            INSERT OR REPLACE INTO notes (name, content, date_modified)
                VALUES(:name, :content, :date_modified)
            """,
            data,
        )

        self.last_saved_content = self.text_area.text
        self.connection.commit()

    def unsaved(self) -> bool:
        """
        Check whether there are unsaved changes
        """

        return self.last_saved_content != self.text_area.text

    def add_bindings(self, kb: KeyBindings):
        """
        Register editor keybindings

        :param kb: The KeyBindings object to add binds to
        :type kb: KeyBindings
        """

        @kb.add("c-w")
        def _(event: KeyPressEvent):
            """
            Save on c-w
            """

            self.write()

        @kb.add("c-d")
        def _(event: KeyPressEvent):
            """
            Exit app when c-d is pressed
            """

            self.write()
            event.app.exit()

        @kb.add("c-a", "c-a", "c-a")
        def _(event: KeyPressEvent):
            """
            Exit app when c-a is pressed thrice
            """

            self.connection.rollback()
            event.app.exit()
