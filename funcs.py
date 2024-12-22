#bad words filter
import re

def load_bad_words(filename: str) -> list:
    with open(filename, "r") as f:
        return [line.strip() for line in f.readlines()]

BAD_WORDS = load_bad_words("bad_words.txt")

def contains_bad_words(text: str) -> bool:
    # Check if any bad word exists in the text (case insensitive)
    pattern = r'\b(' + '|'.join(re.escape(word) for word in BAD_WORDS) + r')\b'
    return bool(re.search(pattern, text, re.IGNORECASE))
