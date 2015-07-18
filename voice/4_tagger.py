# nltk.download()
# 	tokenizers/punkt/english.pickle
# 	taggers/maxent_treebank_pos_tagger/english.pickle 

import nltk

# "Petra is not a spy."
# "Petra isn't a spy."
# "Peter was spying on us."
# "Pizza was spying on us."

text = nltk.word_tokenize("Peter is a spy.")
print(nltk.pos_tag(text))



# IMPROVEMENTS
#	- Identify nouns that are players in game.
#	- Tagging based on arpabet dictionary.
#	- Add probabilities to the possible tags.
