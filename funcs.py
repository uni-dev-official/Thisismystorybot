def has_more_than_150_words(text, str) -> bool:
    # Split the text into words based on whitespace
    words = text.split()
    # Count the number of words
    return len(words) > 150