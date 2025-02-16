import os
import time
from textual.app import ComposeResult
from textual.widgets import Header, Footer, Static, Button, DataTable, RichLog
from textual.containers import Container
from textual.screen import Screen
from textual import events

# Import CSVLoaderScreen from the csv_loader module.
from screens.csv_loader import CSVLoaderScreen

class FilePickerScreen(Screen):
    """Screen for browsing directories and selecting a CSV file."""
    
    def __init__(self) -> None:
        super().__init__()
        self.current_dir = os.path.expanduser("~/Documents/Obsidian Vault/français")
        self.selected_file = None

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield Static("File Navigation", classes="title")
        yield Static(f"Current Directory: {self.current_dir}", id="current_dir")
        yield DataTable(id="file_table")
        with Container():
            yield Button("Up", id="up_button", variant="warning")
            yield Button("Select", id="select_button", variant="success")
        yield RichLog(id="debug_log")
        yield Footer()

    def on_mount(self) -> None:
        self.load_directory(self.current_dir)
        self.query_one("#file_table", DataTable).focus()
        self.last_click_time = 0
        self.last_click_row = None
        self.query_one("#debug_log", RichLog).write("[green]FilePickerScreen mounted.[/green]")

    def on_resume(self) -> None:
        # When resuming, reload the directory and reset focus and click state.
        self.load_directory(self.current_dir)
        self.query_one("#file_table", DataTable).focus()
        self.last_click_time = 0
        self.last_click_row = None
        self.query_one("#debug_log", RichLog).write("[green]FilePickerScreen resumed.[/green]")

    def load_directory(self, directory: str) -> None:
        self.current_dir = directory
        self.query_one("#current_dir", Static).update(f"Current Directory: {self.current_dir}")
        table: DataTable = self.query_one("#file_table", DataTable)
        table.clear(columns=True)
        table.add_column("Name")
        table.add_column("Type")
        try:
            items = os.listdir(directory)
            self.query_one("#debug_log", RichLog).write(f"[blue]Loaded directory: {directory}[/blue]")
        except Exception as e:
            self.query_one("#debug_log", RichLog).write(f"[red]Error reading directory: {e}[/red]")
            return
        items = sorted(items, key=lambda x: (not os.path.isdir(os.path.join(directory, x)), x.lower()))
        for item in items:
            full_path = os.path.join(directory, item)
            item_type = "Directory" if os.path.isdir(full_path) else "File"
            table.add_row(item, item_type)

    def _process_selection(self, row_index: int) -> None:
        table: DataTable = self.query_one("#file_table", DataTable)
        row = table.get_row_at(row_index)
        if not row:
            return
        name, item_type = row
        full_path = os.path.join(self.current_dir, name)
        if item_type == "Directory":
            self.query_one("#debug_log", RichLog).write(f"[yellow]Entering directory: {full_path}[/yellow]")
            self.load_directory(full_path)
        else:
            self.selected_file = full_path
            self.query_one("#debug_log", RichLog).write(f"[green]Selected file: {full_path}[/green]")

    def on_key(self, event: events.Key) -> None:
        if event.key == "enter":
            table: DataTable = self.query_one("#file_table", DataTable)
            if table.cursor_row is not None:
                self._process_selection(table.cursor_row)

    def on_mouse_down(self, event: events.MouseDown) -> None:
        if event.button == 1:
            table: DataTable = self.query_one("#file_table", DataTable)
            if table.cursor_row is None:
                return
            current_time = time.time()
            if (self.last_click_row == table.cursor_row and 
                (current_time - self.last_click_time) < 0.3):
                self._process_selection(table.cursor_row)
                self.last_click_time = 0
                self.last_click_row = None
            else:
                self.last_click_time = current_time
                self.last_click_row = table.cursor_row

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "up_button":
            parent = os.path.dirname(self.current_dir)
            if parent and parent != self.current_dir:
                self.load_directory(parent)
        elif event.button.id == "select_button":
            if self.selected_file:
                self.query_one("#debug_log", RichLog).write(f"[green]File selected: {self.selected_file}[/green]")
                self.app.push_screen(CSVLoaderScreen(self.selected_file))
            else:
                self.query_one("#debug_log", RichLog).write("[red]Error: No file selected.[/red]")
