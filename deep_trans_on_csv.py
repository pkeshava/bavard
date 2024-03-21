import pandas as pd
from deep_translator import GoogleTranslator

def add_translations(input_csv):
    # Read the input CSV without headers
    df = pd.read_csv(input_csv, header=None, names=['word', 'theme'])

    # Use the deep-translator library to get translations for the French words
    def translate_word(word):
        try:
            return GoogleTranslator(source='fr', target='en').translate(word)
        except Exception as e:
            print(f"Error translating {word}: {e}")
            return word

    df['translation'] = df['word'].apply(translate_word)

    # Save the CSV with all three columns
    df.to_csv("data/translated_with_theme.csv", index=False, header=False)

    # Save another CSV with just the French word and English translation
    df[['word', 'translation']].to_csv("data/translated_without_theme.csv", index=False, header=False)

    print("CSV files have been saved successfully!")

# Test the function
add_translations("/Users/pouyan/Documents/Obsidian Vault/français/resources/csv/master_vocab.csv")

