import pandas as pd
import os
import argparse
import random

def split_csv(file_path, target_dir, rows_per_file, randomize=False):
    # Ensure the target directory exists
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)

    # Read the CSV file
    df = pd.read_csv(file_path)

    # Randomize rows if requested
    if randomize:
        df = df.sample(frac=1).reset_index(drop=True)

    # Number of files needed
    num_files = -(-len(df) // rows_per_file)  # Ceiling division

    # Split and save each chunk
    for i in range(num_files):
        start_row = i * rows_per_file
        end_row = start_row + rows_per_file
        df_chunk = df.iloc[start_row:end_row]
        chunk_file_name = os.path.join(target_dir, f'list{i}.csv')
        df_chunk.to_csv(chunk_file_name, index=False)

def main():
    parser = argparse.ArgumentParser(description='Split a CSV file into smaller chunks.')
    parser.add_argument('file_path', type=str, help='Path to the CSV file')
    parser.add_argument('--randomize', action='store_true', help='Randomize the order of the rows before splitting')
    args = parser.parse_args()

    file_path = args.file_path
    target_dir = './data/25split/01-12-2023/randomorder'
    rows_per_file = 25

    split_csv(file_path, target_dir, rows_per_file, args.randomize)

if __name__ == "__main__":
    main()
