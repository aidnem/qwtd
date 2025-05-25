from ctypes import alignment
from prompt_toolkit.layout import (
    ConditionalContainer,
    FormattedTextControl,
    Window,
    WindowAlign,
)
from prompt_toolkit.widgets import FormattedTextToolbar

from qwtd.editor import Editor


class TitleBar(Window):
    """
    Top status bar to show open file and whether it has unsaved changes
    """

    def __init__(self, editor: Editor):
        def get_text():
            out = [
                ("class:titlebar", f"{editor.current_note}"),
            ]

            if editor.unsaved():
                unsaved_text = ("class:titlebar-unsaved", " * UNSAVED CHANGES * ")
                out.insert(0, unsaved_text)
                out.append(unsaved_text)

            return out

        super().__init__(
            FormattedTextControl(get_text),
            style="class:titlebar",
            char=" ",
            align=WindowAlign.CENTER,
            height=1,
            dont_extend_height=True,
        )
