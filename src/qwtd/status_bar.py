from prompt_toolkit.application import get_app
from prompt_toolkit.layout import FormattedTextControl, Window, WindowAlign
from prompt_toolkit.widgets import FormattedTextToolbar

from qwtd.editor import Editor


class StatusBar(FormattedTextToolbar):
    """
    Bottom status bar to show vi mode and keyboard shortcuts
    """

    def __init__(self, editor: Editor):
        def get_text():
            app = get_app()

            mode_text: str = app.vi_state.input_mode

            if editor.current_note != "Deleted":
                return [
                    ("", "qwtd - "),
                    ("class:info", mode_text),
                    ("", " - "),
                    ("class:keys", "Ctrl+W"),
                    ("", ": Write | "),
                    ("class:keys", "Ctrl+E"),
                    ("", ": Export | "),
                    ("class:keys", "Ctrl+Q"),
                    ("", ": Save & Exit | "),
                    ("class:keys", "Ctrl+A"),
                    ("", " (x3) : Abandon | "),
                    ("class:keys", "Ctrl+D"),
                    ("", " (x3) : "),
                    ("fg:red", "Delete"),
                ]
            else:
                return [
                    ("", "qwtd - "),
                    ("class:info", mode_text),
                    ("", " - "),
                    ("class:keys", "Ctrl+R"),
                    ("class:info", ": Restore | "),
                    ("class:keys", "Ctrl+A"),
                    ("", " (x3) : Abandon"),
                ]

        super(StatusBar, self).__init__(get_text)
