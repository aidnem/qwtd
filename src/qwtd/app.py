"""
Manages the top level of the qwtd app through prompt_toolkit
"""

from sqlite3 import Connection
from prompt_toolkit import Application
from prompt_toolkit.buffer import Buffer
from prompt_toolkit.completion import FuzzyCompleter, WordCompleter
from prompt_toolkit.cursor_shapes import CursorShape
from prompt_toolkit.enums import EditingMode
from prompt_toolkit.filters import Condition
from prompt_toolkit.key_binding import KeyBindings, KeyPressEvent
from prompt_toolkit.layout import (
    BufferControl,
    CompletionsMenu,
    Float,
    FloatContainer,
    FormattedTextControl,
    HSplit,
    VSplit,
    Window,
)
from prompt_toolkit.layout.layout import Layout
from prompt_toolkit.styles import Style
from prompt_toolkit.widgets import Frame, TextArea

from qwtd.editor import Editor
from qwtd.status_bar import StatusBar
from qwtd.titlebar import TitleBar


kb = KeyBindings()


def run_app(connection: Connection):
    """
    Create and run the TUI App
    """
    text_area = TextArea(line_numbers=True, scrollbar=True)

    editor: Editor = Editor(connection, text_area)

    editing_body = HSplit(
        [
            TitleBar(editor),
            text_area,
            StatusBar(editor),
        ]
    )

    res = connection.execute("SELECT name FROM notes ORDER BY date_modified DESC")

    note_name_buff = Buffer(
        completer=FuzzyCompleter(
            WordCompleter([tup[0] for tup in res.fetchall()], sentence=True)
        ),
        complete_while_typing=True,
        multiline=False,
    )

    note_selector = HSplit(
        [
            Window(FormattedTextControl("Select note:", style="class:info")),
            Window(BufferControl(note_name_buff), height=1),
        ]
    )

    root_container = FloatContainer(
        editing_body,
        floats=[
            Float(Frame(note_selector, width=30, height=4)),
            Float(
                CompletionsMenu(scroll_offset=1),
                xcursor=True,
                ycursor=True,
            ),
        ],
    )

    layout = Layout(root_container)

    style = Style(
        [
            ("info", "fg:ansigreen"),
            ("keys", "reverse"),
            ("titlebar", "bg:white fg:black"),
            ("titlebar-unsaved", "bg:white fg:ansired"),
        ]
    )

    app = Application(
        layout=layout,
        key_bindings=kb,
        editing_mode=EditingMode.VI,
        full_screen=True,
        style=style,
        cursor=CursorShape.BLINKING_BLOCK,
        # refresh_interval=0.1,
    )

    @kb.add("enter", filter=Condition(lambda: app.layout.has_focus(note_selector)))
    def _(event: KeyPressEvent):
        """
        Exit the note selector and confirm selection when enter is pressed
        """
        root_container.floats = []

        editor.open_note(note_name_buff.text)

        app.layout.focus(text_area)

        app.invalidate()

    editor.add_bindings(kb)

    def pre_run():
        """
        Initialization to run before the app starts
        """

        app.layout.focus(note_selector)

        note_name_buff.start_completion(select_first=False)

    app.run(pre_run=pre_run)
