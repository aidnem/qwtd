"""
Manages the top level of the qwtd app through prompt_toolkit
"""

from sqlite3 import Connection
from prompt_toolkit import Application
from prompt_toolkit.buffer import Buffer
from prompt_toolkit.completion import FuzzyCompleter, PathCompleter, WordCompleter
from prompt_toolkit.cursor_shapes import CursorShape
from prompt_toolkit.enums import EditingMode
from prompt_toolkit.filters import Condition
from prompt_toolkit.key_binding import KeyBindings, KeyPressEvent
from prompt_toolkit.layout import (
    BufferControl,
    CompletionsMenu,
    ConditionalContainer,
    Float,
    FloatContainer,
    FormattedTextControl,
    HSplit,
    Window,
)
from prompt_toolkit.layout.layout import Layout
from prompt_toolkit.lexers import PygmentsLexer
from pygments.lexers.markup import MarkdownLexer
from prompt_toolkit.styles import Style, merge_styles
from prompt_toolkit.widgets import Frame, TextArea
from prompt_toolkit.styles.pygments import style_from_pygments_cls
from pygments.styles import get_style_by_name

from qwtd.editor import Editor
from qwtd.status_bar import StatusBar
from qwtd.titlebar import TitleBar


kb = KeyBindings()


def run_app(connection: Connection):
    """
    Create and run the TUI App
    """

    text_area = TextArea(
        line_numbers=True,
        scrollbar=True,
        lexer=PygmentsLexer(MarkdownLexer),
    )

    note_name_completer = WordCompleter([], sentence=True)

    note_name_buff = Buffer(
        completer=FuzzyCompleter(note_name_completer),
        complete_while_typing=True,
        multiline=False,
    )

    export_buff = Buffer(
        completer=PathCompleter(only_directories=True),
        complete_while_typing=True,
        multiline=False,
    )

    editor: Editor = Editor(
        connection, text_area, note_name_buff, note_name_completer, export_buff
    )

    editor.update_name_completer()

    editing_body = HSplit(
        [
            TitleBar(editor),
            text_area,
            StatusBar(editor),
        ]
    )

    note_select_kb = KeyBindings()

    @note_select_kb.add("enter")
    def _(event: KeyPressEvent):
        """
        Exit the note selector and confirm selection when enter is pressed
        """
        editor.open_note(note_name_buff.text)

        app.layout.focus(text_area)

        app.invalidate()

    note_selector = ConditionalContainer(
        Frame(
            HSplit(
                [
                    Window(FormattedTextControl("Select note:", style="class:info")),
                    Window(
                        BufferControl(
                            note_name_buff,
                            key_bindings=note_select_kb,
                        ),
                        height=1,
                    ),
                ]
            ),
            width=30,
            height=4,
        ),
        Condition(lambda: editor.current_note is None),
    )

    export_selector = ConditionalContainer(
        Frame(
            HSplit(
                [
                    Window(FormattedTextControl("Export path:", style="class:info")),
                    Window(BufferControl(export_buff), height=1),
                ]
            ),
            width=30,
            height=4,
        ),
        Condition(lambda: editor.is_exporting),
    )

    root_container = FloatContainer(
        editing_body,
        floats=[
            Float(note_selector),
            Float(export_selector),
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
            ("info", "fg:#41a6b5"),
            ("keys", "reverse"),
            ("titlebar", "bg:white fg:black"),
            ("titlebar-unsaved", "bg:white fg:ansired"),
            ("pygments.generic.heading", "bold fg:#ffaa00"),
            ("completion-menu.completion", "bg:#3d59a1 #a9b1d6"),
            ("completion-menu.completion.current", "#394b70 bg:#a9b1d6"),
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

    editor.add_bindings(kb)

    def pre_run():
        """
        Initialization to run before the app starts
        """

        app.layout.focus(note_selector)

        note_name_buff.start_completion(select_first=False)

    app.run(pre_run=pre_run)
