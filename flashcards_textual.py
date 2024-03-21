import pandas as pd
from rich import print
from rich.prompt import Prompt

class FlashcardsCLI:

    def __init__(self, csv_file):
        self.df = pd.read_csv(csv_file)
        self.current_idx = -1
        self.showing_english = True

    def flip_card(self):
        self.showing_english = not self.showing_english

    def next_card(self):
        self.current_idx += 1
        if self.current_idx >= len(self.df):
            self.current_idx = 0
        self.showing_english = True

    def shuffle_cards(self):
        self.df = self.df.sample(frac=1).reset_index(drop=True)
        self.current_idx = -1

    def display_card(self):
        if self.current_idx == -1:
            print("[bold blue] Click 'Next' to start or 'Shuffle' to shuffle cards [/bold blue]")
        else:
            word = self.df.at[self.current_idx, 'English' if self.showing_english else 'French']
            print(f"[bold yellow] {word} [/bold yellow]")
      


    def run(self):
        while True:
            self.display_card()
            action = Prompt.ask("Choose an action", choices=["flip", "next", "shuffle", "quit"], default="next")

            if action == "flip":
                self.flip_card()
            elif action == "next":
                self.next_card()
            elif action == "shuffle":
                self.shuffle_cards()
            elif action == "quit":
                break

if __name__ == "__main__":
    app = FlashcardsCLI('data/translation_sorted_0709.csv')
    app.run()

