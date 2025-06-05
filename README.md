# qwtd

Quick, write that down! Simple terminal note taking to quickly write stuff down.

## Installation

To install, clone from github and install it pip:

```sh
git clone https://github.com/aidnem/qwtd
cd qwtd
pip install -e .
```

## Usage

To run qwtd, just call it from the commandline:

```sh
qwtd
```

This will open the UI, prompting you to select a note.

### Editing

The editor uses VI key bindings (the current VI mode can be seen at the bottom of
the screen, along with other helpful keyboard shortcuts).

Here are some frequently used shortcuts to get you started:

- `Ctrl-Q` - Save and exit
- `Ctrl-W` - Save
- `Ctrl-O` - Open a new note (must save first)
- `Ctrl-A` - (Press 3 times) Abort - Exit without saving
- `Ctrl-D` - Delete a note (moves the note to `Deleted`)

You can also open a (very barebones) commandline like in vim:

Press `:` and then use `w` (write), `q` (quit), `q!` (quit and discard changes).
These commands can be composed: `:wq<Enter>` would save the note and quit.

### Deleting and restoring notes

The currently open note can be deleted with `Ctrl-D`. This will move the note to
the special `Deleted` note. To restore a note that's been deleted, press
`Ctrl-O` (or restart `qwtd`), open `Deleted`, and press `Ctrl-R` to restore it.

_Note_: A deleted note is stored temporarily under `Deleted`, but will be
permanently lost when the next note is deleted, as it will be overwritten.

### Exporting

By default, notes are stored in the user's home directory in a sqlite3 database
called `qwtd.db`. At some point, you may want to export a note as plain text. To
do so, open the note and press `Ctrl+E`.

### Customizing database location

QWTD uses a configuration file in your home directory at `~/.config/qwtd.toml`.
This file is created automatically on app startup if it doesn't already exist.

To change where the database is stored, simply edit the `db` field.
For example, someone using [Syncthing](https://syncthing.net/) may want
store their notes in the sync folder. This could be accomplished like so:

```toml
db = "~/Sync/qwtd.db"
```
