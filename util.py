def read_words(filename):
    """Reads a list of words from a file."""

    with open(filename) as reader:
        words = [line.strip() for line in reader]
    return words


from scipy.optimize import minimize

def make_f(a):
    def f(x, y):
        return a*x + y
    return f

