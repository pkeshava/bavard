import pandas as pd
import random
from datetime import datetime
from rich import print
from rich.prompt import Prompt
import os
from unidecode import unidecode


def load_data(file_path="data/translated_without_theme.csv"):
    try:
        df = pd.read_csv(file_path, header=None)
        return df
    except Exception as e:
        print(f"[red]Error:[/red] {e}")
        return None

def save_statistics(stats):
    date_str = datetime.now().strftime('%Y_%m_%d')
    directory = 'stats'
    file_path = f"stats/flashcard_rich_stats_{date_str}.csv"

    # Check if directory exists
    if not os.path.exists(directory):
        os.makedirs(directory)

    # If the file for the day already exists, read its content and update
    if os.path.exists(file_path):
        existing_stats_df = pd.read_csv(file_path)
        for index, row in existing_stats_df.iterrows():
            word = row['Word']
            if word in stats:
                stats[word]['Correct'] += row['Correct']
                stats[word]['Incorrect'] += row['Incorrect']
            else:
                stats[word] = {'Correct': row['Correct'], 'Incorrect': row['Incorrect']}

    stats_df = pd.DataFrame(stats).T.reset_index()
    stats_df.columns = ['Word', 'Correct', 'Incorrect']
    stats_df.to_csv(file_path, index=False)
    print(f"[cyan]Statistics saved to: {file_path}[/cyan]")


def main():
    words_df = load_data()
    if words_df is None:
        return

    statistics = {}  # key: word, value: {'Correct': count, 'Incorrect': count}
    
    current_idx = 0
    while True:
        english_word = words_df.iloc[current_idx, 1]
        french_word = words_df.iloc[current_idx, 0]
        print(f"\n[bold cyan]Translate:[/bold cyan] {english_word}\n")
        
        user_translation = Prompt.ask("[bold green]Your Translation[/bold green]")
        
        correct_translation = french_word.strip().lower()
        
        if french_word not in statistics:
            statistics[french_word] = {'Correct': 0, 'Incorrect': 0}
        
        # Ignore accents in comparison
        if unidecode(user_translation.strip().lower()) == unidecode(correct_translation):
            print("[bold green]Correct![/bold green]")
            statistics[french_word]['Correct'] += 1
        else:
            print("[bold red]Incorrect![/bold red]")
            statistics[french_word]['Incorrect'] += 1
        
        # Always display the correct translation
        print(f"Correct Translation: {correct_translation}")
        
        next_action = Prompt.ask("\n[bold blue]Choose Action[/bold blue]", choices=["next", "randomize", "exit"], default="next")
        if next_action == "next":
            current_idx += 1
            if current_idx >= len(words_df):
                print("[yellow]You've reached the end of the list![/yellow]")
                current_idx = 0  # reset
        elif next_action == "randomize":
            current_idx = random.randint(0, len(words_df) - 1)
        elif next_action == "exit":
            save_statistics(statistics)  # save the statistics to CSV when exiting
            break

if __name__ == "__main__":
    main()
