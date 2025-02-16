import os
import pandas as pd
from textual.app import ComposeResult
from textual.widgets import Header, Footer, Static, Button, DataTable, RichLog, Input
from textual.containers import Container
from textual.screen import Screen
from textual import events

#from screens.file_picker import FilePickerScreen

class CSVLoaderScreen(Screen):
    """Screen to load and preview the CSV file, and select French/English columns."""
    
    BINDINGS = [("r", "return_to_picker", "Return to File Picker")]

    def __init__(self, file_path: str) -> None:
        super().__init__()
        self.file_path = file_path
        self.df = None  # will be set when the CSV is loaded

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

    def on_mount(self) -> None:
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
        num_cols = min(5, self.df.shape[1])
        preview_df = self.df.iloc[:100, :num_cols]
        table: DataTable = self.query_one("#csv_preview", DataTable)
        table.clear(columns=True)
        for col in preview_df.columns:
            table.add_column(str(col))
        for _, row in preview_df.iterrows():
            table.add_row(*[str(item) for item in row])
        self.query_one("#debug_log", RichLog).write(
            f"[blue]Preview loaded: {preview_df.shape[0]} rows, {preview_df.shape[1]} columns.[/blue]")

    def action_return_to_picker(self) -> None:
        self.query_one("#debug_log", RichLog).write("[yellow]Returning to FilePickerScreen...[/yellow]")
        self.app.pop_screen()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "change_file":
            # Instead of awaiting directly, schedule the return action:
            self.call_later(self.action_return_to_picker)
        elif event.button.id == "start_flashcards":
            try:
                french_index = int(self.query_one("#french_col", Input).value.strip()) - 1
                english_index = int(self.query_one("#english_col", Input).value.strip()) - 1
                self.query_one("#debug_log", RichLog).write(
                    f"[blue]Selected columns: French={french_index+1}, English={english_index+1}[/blue]")
            except ValueError:
                self.query_one("#debug_log", RichLog).write("[red]Error: Invalid column numbers.[/red]")
                return
            if self.df is None:
                self.query_one("#debug_log", RichLog).write("[red]Error: CSV not loaded properly.[/red]")
                return
            if french_index < 0 or french_index >= self.df.shape[1] or english_index < 0 or english_index >= self.df.shape[1]:
                self.query_one("#debug_log", RichLog).write("[red]Error: Column numbers out of range.[/red]")
                return
            self.app.french_col = french_index
            self.app.english_col = english_index
            from screens.flashcard import FlashcardScreen
            self.app.push_screen(FlashcardScreen(self.df, french_index, english_index))


    def on_suspend(self) -> None:
        self.query_one("#debug_log", RichLog).write("[yellow]CSVLoaderScreen suspended, releasing state...[/yellow]")
        self.df = None
