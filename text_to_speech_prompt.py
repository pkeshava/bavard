from datetime import datetime
import os
import random
import pandas as pd
from gtts import gTTS
import pygame
from rich.console import Console
from rich.prompt import Prompt
from rich.table import Table
import random
import argparse
import stats_combine as st

#import plotext as plt

import plotly.graph_objects as go
from plotly.subplots import make_subplots
# Initialize Rich console
console = Console()

# Initialize pygame mixer
pygame.mixer.init()

accents_map = {
    "e'": "é", "E'": "É",
    "e`": "è", "E`": "È",
    "e^": "ê", "E^": "Ê",
    "a^": "â", "A^": "Â",
    "a`": "à", "A`": "À",
    "u`": "ù", "U`": "Ù",
    "u:": "ü", "U:": "Ü",
    "i:": "ï", "I:": "Ï",
    "u^": "û", "U^": "û",
    "c,": "ç", "C,": "Ç",
    # Add more mappings as needed
}
csv_directory = './data/25split/01-12-2023/randomorder'

file_options = {
    1: "aRandomSet.csv",
    2: "./data/25split/01-12-2023/randomorder/list0.csv",
    3: "./data/25split/01-12-2023/randomorder/list1.csv",
    4: "/Users/pouyan/Documents/Obsidian Vault/français/resources/csv/expressions.csv",
    5: "/Users/pouyan/Documents/Obsidian Vault/français/resources/csv/words_2024.csv"
    # Add more files as needed
}

def replace_accents(text):
    for key, value in accents_map.items():
        text = text.replace(key, value)
    return text

def parse_args():
    parser = argparse.ArgumentParser(description="French Word Pronunciation Game")
    parser.add_argument('--no-random', action='store_true', help='Disable word randomization')
    parser.add_argument('--backward', action='store_true', help='Run through list in reverse order')
    parser.add_argument('--stats', action='store_true', help='Run through the list based on previous statistcal performance')
    return parser.parse_args()

## A simple list of French words with articles. You can expand this list.
#french_words = ['le chien', 'la pomme', 'l\'arbre']


def get_random_csv_file_path(directory):
    # List all CSV files in the specified directory
    files = [f for f in os.listdir(directory) if f.endswith('.csv')]
    # Choose a random file
    random_file = random.choice(files)
    console.print("random file chosen for study is: ", random_file, style="bold red")
    #print("random file chosen for study is: ", random_file)
    return os.path.join(directory, random_file)

def load_words_from_csv(file_path):
    # # Load the CSV file
    # df = pd.read_csv(file_path)
    # # Get the second column (assuming the index starts at 0)
    # words = df.iloc[:, 1].tolist()
    # translations = df.iloc[:, 0].tolist()

    # Define a lambda function to strip trailing whitespaces
    strip_trailing_whitespace = lambda x: x.rstrip() if isinstance(x, str) else x

    # Load the CSV file and apply the strip function to all elements in columns 0 and 1
    df = pd.read_csv(file_path, converters={0: strip_trailing_whitespace, 1: strip_trailing_whitespace})

    # Get the words and translations from the DataFrame
    words = df.iloc[:, 1].tolist()
    translations = df.iloc[:, 0].tolist()

    return words, translations

def load_words_from_csv_stats(file_path):

    # Define a lambda function to strip trailing whitespaces
    strip_trailing_whitespace = lambda x: x.rstrip() if isinstance(x, str) else x

    # Load the CSV file and apply the strip function to all elements in columns 0 and 1
    df = pd.read_csv(file_path, converters={0: strip_trailing_whitespace, 1: strip_trailing_whitespace})
    _ , df = st.order_by_stats(file_path)

    # Get the words and translations from the DataFrame
    words = df.iloc[:, 1].tolist()
    translations = df.iloc[:, 0].tolist()

    return words, translations


# Function to play the French word using gTTS and pygame
def speak_word(word):
    tts = gTTS(text=word, lang='fr')
    filename = "word.mp3"
    tts.save(filename)
    # Load and play the mp3 file
    pygame.mixer.music.load(filename)
    pygame.mixer.music.play()
    # Wait for the audio to finish playing
    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)
    # Remove the temporary file
    os.remove(filename)

def display_options(file_dict):
    table = Table(title="Flashcard File Options")
    
    table.add_column("Number", justify="right", style="cyan", no_wrap=True)
    table.add_column("File Name", style="magenta")
    
    for number, file_path in file_dict.items():
        # Extract only the file name from the full file path
        file_name = os.path.basename(file_path)
        table.add_row(str(number), file_name)
    
    console = Console()
    console.print(table)


def main():
    args = parse_args()
    display_options(file_options)
    # Load words and translations from the CSV file
    #words_file_path = 'data/translations_g_sorted_2023-10-14.csv'  # Update the path to your CSV file if needed
    #csv_directory = './data/25split/01-12-2023/randomorder'
    #words_file_path = get_random_csv_file_path(csv_directory)
    #words_file_path = './data/25split/01-12-2023/randomorder/list1.csv'
    #words_file_path = '~/Documents/Obsidian Vault/français/resources/csv/expressions.csv'
    try:
        choice = int(input("Enter the number of the file you want to use: "))
        if choice == 1:
            words_file_path = get_random_csv_file_path(csv_directory)
        else:
            selected_file = file_options[choice]
            words_file_path = os.path.join(os.getcwd(), selected_file)
    except FileNotFoundError:
        console.print("CSV file not found. Please make sure the path is correct.", style="bold red")
        return
    
    if args.stats:
        french_words, english_translations = load_words_from_csv_stats(words_file_path)
    else:
        french_words, english_translations = load_words_from_csv(words_file_path)

    word_stats = {}  # Dictionary to hold the tally of attempts
    if args.backward:
        index = len(french_words) - 1
    else:
        index = 0
    console.print("Welcome to the French Word Pronunciation Game!", style="bold green")
    try:
        while True:
            #index = 0
            if args.no_random:
                console.print("args are: ", args.no_random, style="bold red")
                if index >= len(french_words):  # Reset index if it reaches the end
                    index = 0
                word = french_words[index]
                translation = english_translations[index]
                console.print(f"Word {index+1} of {len(french_words)}", style="bold blue")
                index += 1  # Increment index for the next round
            elif args.backward:
                console.print("args are: ", args.backward, style="bold red")
                if index >= len(french_words):
                    index = len(french_words) - 1
                console.print(f"Word {index+1} of {len(french_words)}", style="bold blue")
                word = french_words[index]
                translation = english_translations[index]
                index -= 1
            elif args.stats:
                console.print("args are: ", args.stats, style="bold red")
                if index >= len(french_words):  # Reset index if it reaches the end
                    index = 0
                word = french_words[index]
                translation = english_translations[index]
                console.print(f"Word {index+1} of {len(french_words)}", style="bold blue")
                index += 1  # Increment index for the next round
            else:
                random_index = random.randint(0, len(french_words) - 1)
                console.print(f"Word {random_index+1} of {len(french_words)}", style="bold blue")
                word = french_words[random_index]
                translation = english_translations[random_index]


            if word not in word_stats:
                word_stats[word] = {'correct': 0, 'incorrect': 0, 'trans_correct': 0, 'trans_incorrect': 0}
            
            speak_word(word)
            user_input = Prompt.ask("Type the French word you heard")
            user_input = replace_accents(user_input)
            
            if user_input.strip().lower() == word:
                console.print("Correct!", style="green")
                word_stats[word]['correct'] += 1
            else:
                console.print(f"Incorrect. The correct word was '{word}'.", style="red")
                word_stats[word]['incorrect'] += 1
            
            # Ask for the translation
            user_translation = Prompt.ask("Type the English translation")
            if user_translation.strip().lower() == translation.lower():
                console.print("Correct translation!", style="green")
                word_stats[word]['trans_correct'] += 1
            else:
                console.print(f"Incorrect translation. The correct translation is '{translation}'.", style="red")
                word_stats[word]['trans_incorrect'] += 1
            
            if Prompt.ask("Try another word? (y/n)").lower() == 'n':
                break

            if args.no_random and index >= len(french_words):
                index = 0
    finally:
        save_results(word_stats)
        show_results_table(word_stats)
        #plot_data(word_stats)  # Add this line to plot the data
        stats_dir = 'stats'  # Assuming you have the 'stats' directory path here
        plots_dir = 'plots'  # Assuming you have the 'plots' directory path here
        plot_data_with_plotly(word_stats, plots_dir)


def save_results(word_stats):
    # Ensure stats directory exists
    os.makedirs('stats', exist_ok=True)
    # Convert the word_stats dictionary to a list of dictionaries suitable for a DataFrame
    records = [{'Word': word,
                'Correct': stats['correct'],
                'Incorrect': stats['incorrect'],
                'Trans Correct': stats['trans_correct'],
                'Trans Incorrect': stats['trans_incorrect']}
               for word, stats in word_stats.items()]
    # Create a DataFrame from the records
    df = pd.DataFrame(records)
    # Save to CSV
    date_str = datetime.now().strftime('%T_%d_%m_%Y').replace(':', '-')
    df.to_csv(f'stats/date_{date_str}.csv', index=False)

def show_results_table(word_stats):
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Word", style="dim", width=12)
    table.add_column("Correct", justify="right")
    table.add_column("Incorrect", justify="right")
    table.add_column("Trans Correct", justify="right")
    table.add_column("Trans Incorrect", justify="right")
    for word, stats in word_stats.items():
        table.add_row(word,
                      str(stats['correct']),
                      str(stats['incorrect']),
                      str(stats['trans_correct']),
                      str(stats['trans_incorrect']))
    console.print(table)

def plot_data_with_plotly(word_stats, plots_dir):
    words = list(word_stats.keys())
    correct_counts = [word_stats[word]['correct'] for word in words]
    incorrect_counts = [word_stats[word]['incorrect'] for word in words]
    trans_correct_counts = [word_stats[word]['trans_correct'] for word in words]
    trans_incorrect_counts = [word_stats[word]['trans_incorrect'] for word in words]
    
    # Create subplots
    fig = make_subplots(rows=1, cols=2, subplot_titles=("Pronunciation", "Translation"))

    # Pronunciation subplot
    fig.add_trace(
        go.Bar(x=words, y=correct_counts, name='Correct Pronunciation'),
        row=1, col=1
    )
    fig.add_trace(
        go.Bar(x=words, y=incorrect_counts, name='Incorrect Pronunciation'),
        row=1, col=1
    )

    # Translation subplot
    fig.add_trace(
        go.Bar(x=words, y=trans_correct_counts, name='Correct Translation'),
        row=1, col=2
    )
    fig.add_trace(
        go.Bar(x=words, y=trans_incorrect_counts, name='Incorrect Translation'),
        row=1, col=2
    )

    # Update layout
    fig.update_layout(title_text="Performance Overview", barmode='group')
    
    # Save the figure
    file_path = os.path.join(plots_dir, 'run_plot.png')
    fig.write_image(file_path)
    print(f"Plot saved to {file_path}")
    fig.show()

if __name__ == "__main__":
    main()
