Dependencies
============

Install underlying system modules::

  * Windows http://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio
  * Linux ``sudo apt-get install python3-pyaudio`` or ``python-pyaudio`` 
  * OSX http://people.csail.mit.edu/hubert/pyaudio/#downloads

Python packages that are required::

  > pip install nltk speech_recognition


Models & Corpora
----------------

You need a few datasets for the natural language examples to work:

  * corpora/cmudict
  * tokenizers/punkt
  * taggers/maxent_treebank_pos_tagger

Just run the NLTK downloader as follows, and it will prompt you for instructions:

  C:\Users\alexjc\Development\speech>python

  Python 2.7.6 (default, Nov 10 2013, 19:24:18) [MSC v.1500 32 bit (Intel)] on win32
  Type "help", "copyright", "credits" or "license" for more information.
  >>> import nltk
  >>> nltk.download()
  NLTK Downloader
  ---------------------------------------------------------------------------
      d) Download   l) List    u) Update   c) Config   h) Help   q) Quit
  ---------------------------------------------------------------------------
  Downloader> d
  
  Download which package (l=list; x=cancel)?
    Identifier> cmudict
      Downloading package cmudict to
          C:\Users\alexjc\AppData\Roaming\nltk_data...
        Unzipping corpora\cmudict.zip.
  
  ---------------------------------------------------------------------------
      d) Download   l) List    u) Update   c) Config   h) Help   q) Quit
  ---------------------------------------------------------------------------
  Downloader> q
