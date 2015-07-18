import difflib
import nltk.corpus

arpabet = nltk.corpus.cmudict.dict()


def similarity(A, B):
    """Crude measure of how similar two words sounds."""
    total = 0.0
    for a, b in zip(A[0], B[0]):
        s = difflib.SequenceMatcher(None, a, b)
        print(a, b, s.ratio())
        total += s.ratio()
    return total / len(A[0])


for word in ('patrick', 'peter', 'pizza'):
    print(similarity(arpabet['petra'], arpabet[word]))


# IMPROVEMENTS
#   - Support for words of different length.
#   - Missing or additional phonemes.
#   - Manually edited similarity metrics.
#   - Learning similarity from examples.
