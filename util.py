def read_words(filename):
    """Reads a list of words from a file."""

    with open(filename) as reader:
        words = [line.strip() for line in reader]
    return words
