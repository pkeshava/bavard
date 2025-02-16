#%% 
import pandas as pd
#from rich.pretty import pprint
#from rich.console import Console
import glob
 
# %%

def combine_csv_stats():
    #console=Console()
    csv_files = glob.glob('stats/*.csv')

    dfs=[]
    for file in csv_files:
        df=pd.read_csv(file)
        dfs.append(df)
    combined_df = pd.concat(dfs, ignore_index=True)
    excluded_words = ['English', 'French']
    combined_df = combined_df[~combined_df['Word'].isin(excluded_words)]

    # Step 4: Group by the 'Word' column and sum the other columns
    final_df = combined_df.groupby('Word', as_index=False).sum()
    #console.print(final_df.head(5))
    return final_df

combined_stats_df = combine_csv_stats()

#%%
def order_by_stats(csv_file):
    combined_stats_df = combine_csv_stats()
    words2024_df = pd.read_csv(csv_file)
    words2024_df['French'] = words2024_df['French'].str.strip()

    merged_df = pd.merge(words2024_df, combined_stats_df[['Word', 'Trans Correct']], left_on='French', right_on='Word', how='left')


    merged_df.drop('Word', axis=1, inplace=True)
    merged_df['Trans Correct'].fillna(-1, inplace=True)  # Words not attempted are given -1 to sort them at the top

    ordered_df = merged_df.sort_values(by=['Trans Correct', 'French'], ascending=[True, True])

    ordered_df.reset_index(drop=True, inplace=True)
    ordered_df_no_trans = ordered_df.drop('Trans Correct', axis=1)

    #print(ordered_df)
    return ordered_df, ordered_df_no_trans
# %%
import plotly.express as px

# Step 1: Modified combine_csv_stats function
def combine_csv_stats_2(directory):
    csv_files = glob.glob(f"{directory}/*.csv")
    dfs = []
    for file in csv_files:
        df = pd.read_csv(file)
        dfs.append(df)
    combined_df = pd.concat(dfs, ignore_index=True)
    # Exclude specific words
    combined_df = combined_df[~combined_df['Word'].isin(['English', 'French'])]
    final_df = combined_df.groupby('Word', as_index=False).sum()
    return final_df

def reorder_based_on_performance(words_csv, stats_df):
    words_df = pd.read_csv(words_csv)
    words_df['French'] = words_df['French'].str.strip()  # Cleaning whitespace
    # Merge to find matching words and calculate net performance
    words_df['English'] = words_df['English'].str.strip()  # Cleaning whitespace
    # Merge to find matching words and calculate net performance
    merged_df = pd.merge(words_df, stats_df, how='left', left_on='French', right_on='Word')
    # Sorting - words not in combined_df have NaN and will be at the top
    merged_df['Net_Performance'] = merged_df['Trans Correct'] - merged_df['Trans Incorrect']
    reordered_df = merged_df.sort_values(by=['Net_Performance', 'Trans Correct'], ascending=[True, True]).reset_index(drop=True)
    return reordered_df[['English', 'French']]

# Step 3: Plotting Function
def plot_performance(stats_df):
    stats_df['Net_Performance'] = stats_df['Trans Correct'] - stats_df['Trans Incorrect']
    fig = px.scatter(stats_df, x='Word', y='Net_Performance',
                     color='Net_Performance',
                     title="French Word vs. Net Performance",
                     labels={"Word": "French Word", "Net_Performance": "Net Performance"})
    fig.write_html('plots/performance.html', auto_open=True)

# Example usage
directory_path = './stats'
combined_stats_df = combine_csv_stats_2(directory_path)

words2024_path = '/Users/pouyan/Documents/Obsidian Vault/français/resources/csv/words_2024.csv'
reordered_df = reorder_based_on_performance(words2024_path, combined_stats_df)
print(reordered_df)

def plot_bubble_performance(stats_df, filename='bubble_plot.html'):
    # Calculate total attempts for size
    stats_df['Total_Attempts'] = stats_df['Trans Correct'] + stats_df['Trans Incorrect']
    stats_df['Net_Performance'] = stats_df['Trans Correct'] - stats_df['Trans Incorrect']
    
    fig = px.scatter(stats_df, 
                     x='Word', 
                     y='Net_Performance',
                     size='Total_Attempts',  # Bubble size represents total attempts
                     color='Net_Performance',  # Color represents net performance
                     title="French Word vs. Net Performance (Bubble Plot)",
                     labels={"Word": "French Word", "Net_Performance": "Net Performance", "Total_Attempts": "Total Attempts"})
    
    # Save and automatically open the plot
    fig.write_html(filename, auto_open=True)

def plot_heatmap_performance(stats_df, filename='heatmap_plot.html'):
    # Assuming 'stats_df' is pre-processed to include relevant categories for heatmap plotting
    # This is a placeholder for the actual heatmap plotting code
    stats_df['Net_Performance'] = stats_df['Trans Correct'] - stats_df['Trans Incorrect']
    fig = px.density_heatmap(stats_df, x='Word', y='Net_Performance',
                             nbinsx=20,  # Adjust based on dataset size
                             title="Heatmap of French Words vs. Net Performance",
                             labels={"Word": "French Word", "Net_Performance": "Net Performance"})
    # Save and automatically open the plot
    fig.write_html(filename, auto_open=True)

def plot_sorted_bubble_performance(stats_df, filename='adjusted_bubble_plot.html'):
    # Calculate total attempts for size and net performance
    stats_df['Total_Attempts'] = stats_df['Trans Correct'] + stats_df['Trans Incorrect']
    stats_df['Net_Performance'] = stats_df['Trans Correct'] - stats_df['Trans Incorrect']
    
    # Sort by Net Performance
    sorted_stats_df = stats_df.sort_values(by='Net_Performance', ascending=False).reset_index(drop=True)
    
    # Creating a new column 'Word_Index' to use as x-axis for sorted words
    sorted_stats_df['Word_Index'] = range(1, len(sorted_stats_df) + 1)
    
    fig = px.scatter(sorted_stats_df, 
                     x='Word_Index', 
                     y='Net_Performance',
                     size='Total_Attempts',  # Bubble size represents total attempts
                     color='Net_Performance',  # Color represents net performance
                     hover_name='Word',  # Show word name on hover
                     title="French Word vs. Net Performance (Adjusted Bubble Plot)",
                     labels={"Word_Index": "French Word Index", "Net_Performance": "Net Performance", "Total_Attempts": "Total Attempts"},
                     #width=1200,  # Increase figure width
                     #height=600
                     )  # Adjust figure height as needed
    
    # Rotate x-axis labels and adjust font size
    fig.update_xaxes(tickangle=45, tickfont=dict(size=10))

    # Adjusting the x-axis tick labels to show the word instead of index
    fig.update_xaxes(tickvals=sorted_stats_df['Word_Index'][::5], ticktext=sorted_stats_df['Word'][::5])  # Show every 5th label to reduce clutter

    # Save and automatically open the plot
    fig.write_html(filename, auto_open=True)


# Plotting the performance
#plot_performance(combined_stats_df)
#plot_heatmap_performance(combined_stats_df, 'plots/heatmap_plot.html')

#plot_bubble_performance(combined_stats_df, 'plots/bubble_plot.html')
#plot_sorted_bubble_performance(combined_stats_df, 'plots/sorted_bubble_plot.html')

# %%


