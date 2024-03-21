import pandas as pd
import os
import plotly.graph_objects as go

def combine_stats_files(directory="stats/"):
    combined_stats = {}  # key: word, value: {'Correct': count, 'Incorrect': count}

    for file_name in os.listdir(directory):
        if file_name.startswith("flashcard_rich_stats_") and file_name.endswith(".csv"):
            file_path = os.path.join(directory, file_name)
            df = pd.read_csv(file_path)

            for index, row in df.iterrows():
                word = row['Word']
                if word not in combined_stats:
                    combined_stats[word] = {'Correct': 0, 'Incorrect': 0}
                combined_stats[word]['Correct'] += row['Correct']
                combined_stats[word]['Incorrect'] += row['Incorrect']

    return combined_stats

def plot_stats(stats):
    words = list(stats.keys())
    correct_counts = [stats[word]['Correct'] for word in words]
    incorrect_counts = [-stats[word]['Incorrect'] for word in words]  # Make the values negative for top-down bars

    fig = go.Figure()

    # Correct bars (bottom-up)
    fig.add_trace(go.Bar(
        name='Correct',
        x=words,
        y=correct_counts,
        marker_color='green',
        yaxis='y1'
    ))

    # Incorrect bars (top-down with opacity)
    fig.add_trace(go.Bar(
        name='Incorrect',
        x=words,
        y=incorrect_counts,
        marker_color='red',
        opacity=0.5,
        yaxis='y2'
    ))
    step = max(1, int(max(correct_counts) / 5))
    tickvals = [-val for val in range(0, int(max(correct_counts) * 1.5), step)]

    # fig.update_layout(
    #     barmode='relative',
    #     title="Flashcard Guesses",
    #     xaxis_title="Words",
    #     yaxis_title="Correct Count",
    #     yaxis2=dict(
    #         title="Incorrect Count",
    #         overlaying='y',
    #         side='right',
    #         showgrid=False,
    #         tickvals=tickvals,
    #         ticktext=[str(abs(val)) for val in tickvals]
    # ),
    # )
    # Calculate the absolute max value across both correct and incorrect counts
    # Calculate the absolute max value across both correct and incorrect counts
    absolute_max_correct = max(correct_counts)
    absolute_max_incorrect = abs(min(incorrect_counts))

    # Define the gap based on the larger of the two absolute max values
    gap = max(4, int(0.2 * max(absolute_max_correct, absolute_max_incorrect)))  # for instance, 20% of the larger absolute max value or 4, whichever is greater

    half_gap = gap / 2

    fig.update_layout(
        barmode='relative',
        title="Flashcard Guesses",
        xaxis_title="Words",
        yaxis_title="Correct Count",
        yaxis=dict(
            range=[0, absolute_max_correct + half_gap]
        ),
        yaxis2=dict(
            title="Incorrect Count",
            overlaying='y',
            side='right',
            showgrid=False,
            tickvals=tickvals,
            ticktext=[str(abs(val)) for val in tickvals],
            range=[-absolute_max_incorrect - half_gap, 0]  # set the negative range using the absolute_max_incorrect
        ),
    )




    


    


    fig.show()


def main():
    stats = combine_stats_files()
    plot_stats(stats)

if __name__ == "__main__":
    main()
