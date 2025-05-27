from prompt_toolkit.application import get_app
from prompt_toolkit.filters import Condition
from prompt_toolkit.layout import (
    BufferControl,
    ConditionalContainer,
    VSplit,
    Window,
)
from prompt_toolkit.layout.processors import BeforeInput
from prompt_toolkit.widgets import FormattedTextToolbar

from qwtd.editor import Editor


class StandardStatusBar(FormattedTextToolbar):
    """
    Standard status bar; displays at all times except for during commands

    Displays vi mode and keyboard shortcuts for the current context
    """

    def __init__(self, editor: Editor):
        def get_text():
            app = get_app()

            vi_display = [
                ("", "qwtd|"),
                ("class:info", app.vi_state.input_mode[3:]),
                ("", "|"),
            ]

            if editor.current_note != "Deleted":
                return vi_display + [
                    ("class:keys", "Ctrl+W"),
                    ("", ": Write|"),
                    ("class:keys", "Ctrl+E"),
                    ("", ": Export|"),
                    ("class:keys", "Ctrl+Q"),
                    ("", ": Save & Exit|"),
                    ("class:keys", "Ctrl+A"),
                    ("", " (x3) : Abandon|"),
                    ("class:keys", "Ctrl+D"),
                    ("", " (x3) : "),
                    ("fg:red", "Delete"),
                ]
            else:
                return vi_display + [
                    ("class:keys", "Ctrl+R"),
                    ("class:info", ": Restore|"),
                    ("class:keys", "Ctrl+A"),
                    ("", " (x3) : Abandon"),
                ]

        super(StandardStatusBar, self).__init__(get_text)


def status_bar(editor: Editor) -> VSplit:
    """
    Layout for the status bar to show vi mode and keyboard shortcuts
    """

    return VSplit(
        [
            ConditionalContainer(
                StandardStatusBar(editor),
                filter=Condition(
                    lambda: not get_app().layout.has_focus(editor.command_buff)
                ),
            ),
            ConditionalContainer(
                Window(
                    BufferControl(
                        buffer=editor.command_buff, input_processors=[BeforeInput(":")]
                    ),
                    height=1,
                ),
                filter=Condition(
                    lambda: get_app().layout.has_focus(editor.command_buff)
                ),
            ),
        ]
    )
