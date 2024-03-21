# Commands
For splittling a translated list in 25 word chunks and randomizing
```zsh
python split_sorted_into_25chunks.py data/25split/translations_g_sorted_2023-12-01.csv --randomize
```

For playing the list backwards
```zsh
python text_to_speech_prompt.py --backward
```

For playing doing stats based
```zsh
python text_to_speech_prompt.py --stats
```

The list will always be played randomly unless you use
```zsh
python text_to_speech_prompt.py --no-random
```
