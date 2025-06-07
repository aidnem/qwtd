"""
Top status bar to show open file and whether it has unsaved changes
"""

from datetime import datetime
from prompt_toolkit.layout import (
    FormattedTextControl,
    Window,
    WindowAlign,
)

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

            if editor.current_note_deleted:
                days_until_expiration = (
                    editor.current_expiration - datetime.now()
                ).days
                expiration_text = (
                    "class:titlebar-unsaved",
                    f" DELETED: Expires in {days_until_expiration} days",
                )

                out.append(expiration_text)

            if editor.unsaved():
                unsaved_text = (
                    "class:titlebar-unsaved",
                    " * UNSAVED CHANGES * ",
                )

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
