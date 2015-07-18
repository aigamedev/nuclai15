from nltk.chat.util import Chat, reflections

# A table of response pairs, where each pair consists of a regular expression,
# and a list of possible responses, with group-macros labelled as %1, %2.

pairs = (
  (r'You are (.*)',
  ( "Why do you think I am %1?",
    "Perhaps you would like me to be %1.",
    "Perhaps you're really talking about yourself?")),

  (r'You\'re (.*)',
  ( "Why do you say I am %1?",
    "Why do you think I am %1?",
    "Are we talking about you, or me?")),

  (r'(.*)\?',
  ( "Why do you ask that? It's suspicious.",
    "I think you know the answer better than I do.",
    "Why don't you tell me, dear Spy?")),

  (r'(.*) spy(.*)',
  ( "I think everyone looks suspicious.",
	"It's the same spies as last time...")),

  (r'quit',
  ( "That was a fun game!",
    "I think I'm done too.")),

  (r'(.*)',
  ( "This game is a bit difficult to follow.",
  	"Who do you think are the spies?",
  	)),
)


def main():
	print("OK, let's play a game of resistance!")
	chatbot = Chat(pairs, reflections)
	chatbot.converse()

if __name__ == "__main__":
	main()


# IMPROVEMENTS
#	- Integrate voice into loop:
#		http://www.nltk.org/_modules/nltk/chat/util.html#Chat.converse
#	- Match using phonemes and arpabet. 
#		http://www.nltk.org/_modules/nltk/chat/util.html#Chat.respond
