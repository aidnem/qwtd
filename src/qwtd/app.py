"""
Manages the top level of the qwtd app through prompt_toolkit
"""

from sqlite3 import Connection, Cursor
from prompt_toolkit import Application
from prompt_toolkit.buffer import Buffer
from prompt_toolkit.completion import FuzzyCompleter, WordCompleter
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
    Window,
)
from prompt_toolkit.layout.containers import VSplit
from prompt_toolkit.layout.layout import Layout
from prompt_toolkit.styles import Style
from prompt_toolkit.widgets import Frame, TextArea

from qwtd.editor import Editor
from qwtd.status_bar import StatusBar


kb = KeyBindings()


def run_app(connection: Connection):
    """
    Create and run the TUI App
    """
    text_area = TextArea(line_numbers=True, scrollbar=True)

    editing_body = HSplit(
        [
            text_area,
            VSplit(
                [StatusBar()],
                height=1,
            ),
        ]
    )

    res = connection.execute("SELECT name FROM notes")

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
                CompletionsMenu(max_height=8, scroll_offset=1),
                xcursor=True,
                ycursor=True,
            ),
        ],
    )

    layout = Layout(root_container)

    style = Style([("info", "fg:ansigreen"), ("keys", "reverse")])

    app = Application(
        layout=layout,
        key_bindings=kb,
        editing_mode=EditingMode.VI,
        full_screen=True,
        style=style,
        # refresh_interval=0.1,
    )

    editor: Editor = Editor(connection, text_area)

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

    app.run(pre_run=pre_run)
