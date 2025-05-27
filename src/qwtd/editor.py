"""
Class for handling the state of the text editor
"""

import datetime
import os
from sqlite3 import Connection, Cursor

from prompt_toolkit import Application
from prompt_toolkit.application import get_app
from prompt_toolkit.buffer import Buffer
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.filters import Condition
from prompt_toolkit.key_binding import KeyBindings, KeyPressEvent
from prompt_toolkit.key_binding.vi_state import InputMode
from prompt_toolkit.layout import UIControl
from prompt_toolkit.widgets import TextArea


class Editor:
    """
    Handles state of the editor, reading, writing, and keyboard shortcuts
    """

    def __init__(
        self,
        connection: Connection,
        text_area: TextArea,
        note_name_buff: Buffer,
        note_name_completer: WordCompleter,
        export_buff: Buffer,
    ):
        """
        Create a new Editor

        :param connection: Connection to the database
        :type connection: sqlite3.Connection
        :param text_area: Main editor text area
        :type text_area: TextArea
        """

        self.connection: Connection = connection
        self.text_area: TextArea = text_area
        self.note_name_buff: Buffer = note_name_buff
        self.note_name_completer: WordCompleter = note_name_completer
        self.export_buff: Buffer = export_buff

        def handle_command(buff: Buffer) -> bool:
            """
            Handle when enter is pressed in the command line
            """

            self.handle_command(buff.text)

            get_app().layout.focus(self.last_focused)
            get_app().vi_state.input_mode = InputMode.NAVIGATION

            # Always return false to reset the command buffer
            return False

        self.command_buff: Buffer = Buffer(
            accept_handler=handle_command,
            multiline=False,
        )

        self.current_note: str | None = None
        self.last_saved_content: str = ""

        # Should the export dialog be open currently?
        self.is_exporting: bool = False

        self.last_focused: UIControl = self.text_area.control

    def update_name_completer(self):
        """
        Update the list of note names in the note name completer from the database
        """

        res = self.connection.execute(
            "SELECT name FROM notes ORDER BY date_modified DESC"
        )

        self.note_name_completer.words = [tup[0] for tup in res.fetchall()]

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

        get_app().vi_state.input_mode = InputMode.NAVIGATION

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

        return (
            self.current_note is not None
            and self.last_saved_content != self.text_area.text
        )

    def delete(self):
        """
        Delete the currently open note (rename it to Deleted)
        """

        # Delete last "recently deleted" note
        self.connection.execute(
            """
            DELETE FROM notes WHERE name='Deleted'
            """
        )

        self.connection.execute(
            """
            UPDATE notes
            SET name = 'Deleted'
            WHERE name = ?
            """,
            (self.current_note if self.current_note else "",),
        )

        self.connection.execute(
            """
            UPDATE last_deleted SET name = ?
            """,
            (self.current_note if self.current_note else "",),
        )

        self.connection.commit()

    def restore(self):
        """
        Restore the deleted note to its previous location
        """

        last_deleted: str = self.connection.execute(
            "SELECT * FROM last_deleted"
        ).fetchone()[0]

        self.connection.execute(
            """
            UPDATE notes
            SET name = ?
            WHERE name = 'Deleted'
            """,
            (last_deleted,),
        )

        self.connection.commit()

    def start_export(self):
        """
        Start an export (open the export menu)
        """
        self.is_exporting = True

    def finish_export(self):
        """
        Finish an export (write the file to disk)
        """
        self.is_exporting = False

        if os.path.exists(self.export_buff.text):
            print(f"[QWTD] Error: File {self.export_buff.text} already exists.")
            return

        with open(self.export_buff.text, "w+", encoding="utf-8") as file:
            file.write(self.text_area.text)

    def close(self, app: Application):
        """
        Close the current note, prompting the user for a new one
        """

        self.current_note = None
        self.note_name_buff.text = ""
        self.text_area.text = " * in limbo (no note selected) *"

        self.update_name_completer()

        app.layout.focus(self.note_name_buff)
        self.note_name_buff.start_completion(select_first=False)

    def save_and_exit(self, app: Application):
        """
        Save the note and quit the app
        """

        self.write()
        app.exit()

    def exit_without_saving(self, app: Application):
        """
        Quit the app without saving, rolling back the db
        """

        self.connection.rollback()
        app.exit()

    def handle_command(self, command: str):
        """
        Handle a command from the command line input
        """

        command_chars: list[str] = list(reversed(command))

        while len(command_chars) > 0:
            c = command_chars.pop()

            if c == "w":
                self.write()
            elif c == "q":
                if self.unsaved() and len(command_chars):
                    if command_chars.pop() == "!":
                        self.exit_without_saving(get_app())
                elif not self.unsaved():
                    get_app().exit()

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

        @kb.add("c-q")
        def _(event: KeyPressEvent):
            """
            Exit app when c-q is pressed
            """

            self.save_and_exit(event.app)

        @kb.add("c-a", "c-a", "c-a")
        def _(event: KeyPressEvent):
            """
            Exit app when c-a is pressed thrice
            """

            self.exit_without_saving(event.app)

        @kb.add("c-d", "c-d", "c-d")
        def _(event: KeyPressEvent):
            """
            Delete the note when c-d is pressed thrice
            """

            self.delete()
            self.connection.commit()

            self.close(event.app)

        @kb.add("c-r", filter=Condition(lambda: self.current_note == "Deleted"))
        def _(event: KeyPressEvent):
            """
            Restore the note when c-r is pressed in Deleted
            """

            self.restore()
            self.connection.commit()
            print("[QWTD] Restored note.")

            self.close(event.app)

        @kb.add("c-e")
        def _(event: KeyPressEvent):
            """
            Export when c-e is pressed
            """

            self.start_export()

            event.app.layout.focus(self.export_buff)

        @kb.add("enter", filter=Condition(lambda: self.is_exporting))
        def _(event: KeyPressEvent):
            """
            Finish export when enter is pressed
            """

            self.finish_export()

        @kb.add(
            "c-o",
            filter=Condition(
                lambda: self.current_note is not None and not self.unsaved()
            ),
        )
        def _(event: KeyPressEvent):
            """
            Close note to open a new one when c-o is pressed
            """

            self.close(event.app)

        @kb.add(
            ":",
            filter=Condition(
                lambda: get_app().vi_state.input_mode == InputMode.NAVIGATION
            ),
        )
        def _(event: KeyPressEvent):
            """
            Open the command line when : is pressed in normal mode
            """

            # Keep track of where we were
            self.last_focused = event.app.layout.current_control

            event.app.layout.focus(self.command_buff)
            event.app.vi_state.input_mode = InputMode.INSERT
