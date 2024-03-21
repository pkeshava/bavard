#%%
import pandas as pd
from datetime import datetime
date=datetime.today().strftime('%Y-%m-%d')
def organize_csv(filename):
    # Read the CSV into a DataFrame
    df = pd.read_csv(filename, header=None, names=["Col1", "Col2", "Word1", "Word2"])

    # Check where English is and swap columns if needed
    for idx, row in df.iterrows():
        if row["Col1"] == "French":
            # Swap the headers
            df.at[idx, "Col1"], df.at[idx, "Col2"] = df.at[idx, "Col2"], df.at[idx, "Col1"]
            
            # Swap the words
            df.at[idx, "Word1"], df.at[idx, "Word2"] = df.at[idx, "Word2"], df.at[idx, "Word1"]

    # Drop the original header columns now that we've ensured English and French are aligned correctly
    df = df.drop(columns=["Col1", "Col2"])

    # Rename columns for clarity
    df.columns = ["English", "French"]

    return df

# Test
filename = "data/translations_g_"+date+".csv"
df = organize_csv(filename)
print(df.head())

# %%
# save_to_csv.py

def save_sorted_csv(filename, output_filename):
    df = organize_csv(filename)
    df.to_csv(output_filename, index=False)

save_sorted_csv('data/translations_g_'+date+'.csv', 'data/translations_g_sorted_'+date+'.csv')


# %%
