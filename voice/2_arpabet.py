import nltk.corpus

arpabet = nltk.corpus.cmudict.dict()
for word in ('petra', 'patrick', 'peter', 'pizza'):
    print(arpabet[word])
