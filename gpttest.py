import os
import time
import random
import pandas as pd

from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Static, Button, DataTable, RichLog, Input
from textual.containers import Container
from textual.screen import Screen
from textual import events


# ---------------------------
# Screen 1: File Picker Screen
# ---------------------------
class FilePickerScreen(Screen):
    """Screen for browsing directories and selecting a CSV file."""
    
    def __init__(self) -> None:
        super().__init__()
        self.current_dir = os.path.expanduser("~")
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

    async def on_mount(self) -> None:
        self.load_directory(self.current_dir)
        self.query_one("#file_table", DataTable).focus()
        self.last_click_time = 0
        self.last_click_row = None
        self.query_one("#debug_log", RichLog).write("[green]FilePickerScreen mounted.[/green]")

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
        # Directories first, then files, sorted alphabetically.
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

    async def on_key(self, event: events.Key) -> None:
        if event.key == "enter":
            table: DataTable = self.query_one("#file_table", DataTable)
            if table.cursor_row is not None:
                self._process_selection(table.cursor_row)

    async def on_mouse_down(self, event: events.MouseDown) -> None:
        if event.button == 1:  # Left click.
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

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "up_button":
            parent = os.path.dirname(self.current_dir)
            if parent and parent != self.current_dir:
                self.load_directory(parent)
        elif event.button.id == "select_button":
            if self.selected_file:
                self.query_one("#debug_log", RichLog).write(f"[green]File selected: {self.selected_file}[/green]")
                await self.app.push_screen(CSVLoaderScreen(self.selected_file))
            else:
                self.query_one("#debug_log", RichLog).write("[red]Error: No file selected.[/red]")


# ---------------------------
# Screen 2: CSV Loader & Column Selection Screen
# ---------------------------
class CSVLoaderScreen(Screen):
    """Screen to load the CSV file, preview it, and choose French/English columns."""
    
    BINDINGS = [("r", "return_to_picker", "Return to File Picker")]

    def __init__(self, file_path: str) -> None:
        super().__init__()
        self.file_path = file_path

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield Static("CSV Preview & Column Selection", classes="title")
        yield Static("", id="selected_file_display")
        yield Button("Change File", id="change_file", variant="warning")
        yield DataTable(id="csv_preview")
        yield Static("Enter French Column (1-indexed):", id="french_prompt")
        yield Input(placeholder="e.g., 2", id="french_col")
        yield Static("Enter English Column (1-indexed):", id="english_prompt")
        yield Input(placeholder="e.g., 1", id="english_col")
        yield Button("Start Flashcards", id="start_flashcards", variant="success")
        yield RichLog(id="debug_log")
        yield Footer()

    async def on_mount(self) -> None:
        self.query_one("#selected_file_display", Static).update(f"Selected File: {self.file_path}")
        self.query_one("#debug_log", RichLog).write(f"[blue]Loading CSV: {self.file_path}[/blue]")
        if not os.path.exists(self.file_path):
            self.query_one("#debug_log", RichLog).write(f"[red]Error: File does not exist: {self.file_path}[/red]")
            return
        if not self.file_path.lower().endswith(".csv"):
            self.query_one("#debug_log", RichLog).write(f"[yellow]Warning: File is not a CSV: {self.file_path}[/yellow]")
        try:
            self.df = pd.read_csv(self.file_path)
            self.query_one("#debug_log", RichLog).write("[green]CSV loaded successfully.[/green]")
        except Exception as e:
            self.query_one("#debug_log", RichLog).write(f"[red]Error loading CSV: {e}[/red]")
            return
        # Limit preview to 100 rows and at most 5 columns.
        num_cols = min(5, self.df.shape[1])
        preview_df = self.df.iloc[:100, :num_cols]
        table: DataTable = self.query_one("#csv_preview", DataTable)
        table.clear(columns=True)
        for col in preview_df.columns:
            table.add_column(str(col))
        for _, row in preview_df.iterrows():
            table.add_row(*[str(item) for item in row])
        self.query_one("#debug_log", RichLog).write(f"[blue]Preview loaded: {preview_df.shape[0]} rows, {preview_df.shape[1]} columns.[/blue]")

    async def action_return_to_picker(self) -> None:
        self.query_one("#debug_log", RichLog).write("[yellow]Returning to FilePickerScreen...[/yellow]")
        await self.app.pop_screen()

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "change_file":
            await self.app.pop_screen()
        elif event.button.id == "start_flashcards":
            try:
                french_index = int(self.query_one("#french_col", Input).value.strip()) - 1
                english_index = int(self.query_one("#english_col", Input).value.strip()) - 1
                self.query_one("#debug_log", RichLog).write(f"[blue]Selected columns: French={french_index+1}, English={english_index+1}[/blue]")
            except ValueError:
                self.query_one("#debug_log", RichLog).write("[red]Error: Invalid column numbers.[/red]")
                return
            if not hasattr(self, "df"):
                self.query_one("#debug_log", RichLog).write("[red]Error: CSV not loaded properly.[/red]")
                return
            if french_index < 0 or french_index >= self.df.shape[1] or english_index < 0 or english_index >= self.df.shape[1]:
                self.query_one("#debug_log", RichLog).write("[red]Error: Column numbers out of range.[/red]")
                return
            self.app.french_col = french_index
            self.app.english_col = english_index
            await self.app.push_screen(FlashcardScreen(self.df, french_index, english_index))


# ---------------------------
# Screen 3: Flashcard Testing Screen
# ---------------------------
class FlashcardScreen(Screen):
    """Screen for flashcard testing."""
    
    BINDINGS = [("9", "exit_flashcards", "Exit Flashcard Mode")]

    def __init__(self, df, french_col: int, english_col: int) -> None:
        super().__init__()
        self.df = df
        self.french_col = french_col
        self.english_col = english_col
        self.current_index = 0
        self.word_stats = {}  # For tracking correct/incorrect answers (optional)

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield Static("Flashcard Testing", classes="title")
        yield Static("", id="flashcard_display")
        with Container():
            yield Button("Show Translation", id="show_translation", variant="primary")
            yield Button("Next Card", id="next_card", variant="success")
        yield RichLog(id="debug_log")
        yield Footer()

    async def on_mount(self) -> None:
        self.query_one("#debug_log", RichLog).write("[blue]FlashcardScreen mounted.[/blue]")
        self.display_flashcard()

    def display_flashcard(self) -> None:
        if self.current_index >= len(self.df):
            self.current_index = 0  # Restart if at end.
        row = self.df.iloc[self.current_index]
        french_word = str(row.iloc[self.french_col])
        self.query_one("#flashcard_display", Static).update(f"French: {french_word}")
        self.query_one("#debug_log", RichLog).write(f"[blue]Displaying card {self.current_index+1}/{len(self.df)}[/blue]")

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "show_translation":
            row = self.df.iloc[self.current_index]
            translation = str(row.iloc[self.english_col])
            self.query_one("#flashcard_display", Static).update(f"French: {str(row.iloc[self.french_col])}\nEnglish: {translation}")
            self.query_one("#debug_log", RichLog).write("[green]Translation shown.[/green]")
        elif event.button.id == "next_card":
            self.current_index += 1
            self.display_flashcard()

    async def action_exit_flashcards(self) -> None:
        self.query_one("#debug_log", RichLog).write("[yellow]Exiting flashcard mode...[/yellow]")
        await self.app.pop_screen()


# ---------------------------
# Main Application
# ---------------------------
class CSVApp(App):
    CSS = """
    Screen {
        align: center middle;
        border: round white;
        padding: 1;
    }
    .title {
        padding: 1 0;
        text-align: center;
        color: yellow;
        border: heavy green;
    }
    DataTable {
        height: 10;
        width: 80%;
        margin: 1 0;
        border: round blue;
    }
    Button {
        width: 50%;
        margin: 1 0;
        border: round cyan;
    }
    RichLog {
        height: 5;
        width: 80%;
        margin: 1 0;
        border: round red;
    }
    Static#current_dir {
        border: round magenta;
        width: 80%;
        margin: 1 0;
    }
    """

    async def on_mount(self) -> None:
        await self.push_screen(FilePickerScreen())


if __name__ == "__main__":
    CSVApp().run()
