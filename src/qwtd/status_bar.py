from prompt_toolkit.application import get_app
from prompt_toolkit.widgets import FormattedTextToolbar


class StatusBar(FormattedTextToolbar):
    def __init__(self):
        def get_text():
            app = get_app()

            mode_text: str = app.vi_state.input_mode

            return [
                ("", "qwtd - "),
                ("class:info", mode_text),
                ("", " - "),
                ("class:keys", "Ctrl+W"),
                ("", ": Write | "),
                ("class:keys", "Ctrl+E"),
                ("", ": Export | "),
                ("class:keys", "Ctrl+D"),
                ("", ": Save & Exit | "),
                ("class:keys", "Ctrl+A"),
                ("", ": Abandon"),
            ]

        super(StatusBar, self).__init__(get_text)
