import os
from datetime import datetime
import pandas as pd
from textual.app import ComposeResult
from textual.widgets import Header, Footer, Static, Button, RichLog, Input
from textual.containers import Container
from textual.screen import Screen
from textual import events

class FlashcardScreen(Screen):
    """Screen for flashcard testing."""
    
    BINDINGS = [("ctrl+r", "exit_flashcards", "Exit Flashcard Mode")]

    def __init__(self, df: pd.DataFrame, french_col: int, english_col: int) -> None:
        super().__init__()
        self.df = df
        self.french_col = french_col
        self.english_col = english_col
        self.current_index = 0
        self.word_stats = {}  # For tracking correct/incorrect answers

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield Static("Flashcard Testing", classes="title")
        yield Static("", id="flashcard_display")
        yield Input(placeholder="Type your translation guess here", id="guess_input")
        with Container():
            yield Button("Show Translation", id="show_translation", variant="primary")
            yield Button("Next Card", id="next_card", variant="success")
            yield Button("Save Stats", id="save_stats", variant="warning")
        yield Static("Press Ctrl+R to exit flashcard mode", id="exit_instructions")
        yield RichLog(id="debug_log")
        yield Footer()

    async def on_mount(self) -> None:
        self.query_one("#debug_log", RichLog).write("[blue]FlashcardScreen mounted.[/blue]")
        self.display_flashcard()

    def display_flashcard(self) -> None:
        if self.current_index >= len(self.df):
            self.current_index = 0  # Restart if at end.
        row = self.df.iloc[self.current_index]
        french_word = str(row.iloc[self.french_col]).strip()
        self.query_one("#flashcard_display", Static).update(f"French: {french_word}")
        self.query_one("#debug_log", RichLog).write(f"[blue]Displaying card {self.current_index+1}/{len(self.df)}[/blue]")
        guess_input = self.query_one("#guess_input", Input)
        guess_input.value = ""

    async def on_input_submitted(self, event: Input.Submitted) -> None:
        if event.input.id == "guess_input":
            guess = event.value.strip().lower()
            row = self.df.iloc[self.current_index]
            correct_translation = str(row.iloc[self.english_col]).strip().lower()
            french_word = str(row.iloc[self.french_col]).strip()
            if french_word not in self.word_stats:
                self.word_stats[french_word] = {'correct': 0, 'incorrect': 0, 'trans_correct': 0, 'trans_incorrect': 0}
            if guess == correct_translation:
                self.word_stats[french_word]['correct'] += 1
                self.query_one("#debug_log", RichLog).write(f"[green]Correct! {french_word} -> {correct_translation}[/green]")
            else:
                self.word_stats[french_word]['incorrect'] += 1
                self.query_one("#debug_log", RichLog).write(f"[red]Incorrect! {french_word} -> {correct_translation}. Your answer: {event.value}[/red]")
            event.input.value = ""

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "show_translation":
            row = self.df.iloc[self.current_index]
            correct_translation = str(row.iloc[self.english_col]).strip()
            french_word = str(row.iloc[self.french_col]).strip()
            self.query_one("#flashcard_display", Static).update(f"French: {french_word}\nEnglish: {correct_translation}")
            self.query_one("#debug_log", RichLog).write("[green]Translation shown.[/green]")
        elif event.button.id == "next_card":
            self.current_index += 1
            self.display_flashcard()
        elif event.button.id == "save_stats":
            self.save_results()
            self.query_one("#debug_log", RichLog).write("[blue]Stats saved.[/blue]")

    def save_results(self) -> None:
        stats_dir = "stats_textual_app"
        os.makedirs(stats_dir, exist_ok=True)
        records = []
        for word, stats in self.word_stats.items():
            records.append({
                "Word": word,
                "Correct": stats.get("correct", 0),
                "Incorrect": stats.get("incorrect", 0),
                "Trans Correct": stats.get("trans_correct", 0),
                "Trans Incorrect": stats.get("trans_incorrect", 0)
            })
        if records:
            df_stats = pd.DataFrame(records)
            date_str = datetime.now().strftime("%T_%d_%m_%Y").replace(":", "-")
            file_path = os.path.join(stats_dir, f"stats_{date_str}.csv")
            df_stats.to_csv(file_path, index=False)
        else:
            self.query_one("#debug_log", RichLog).write("[yellow]No stats to save.[/yellow]")

    async def action_exit_flashcards(self) -> None:
        self.query_one("#debug_log", RichLog).write("[yellow]Exiting flashcard mode...[/yellow]")
        await self.app.pop_screen()

    async def on_suspend(self) -> None:
        # Clear heavy state if necessary.
        self.df = None
        self.word_stats.clear()
