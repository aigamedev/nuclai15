import sys

if 'win32' in sys.platform: 
	import win32com.client
	_voice = win32com.client.Dispatch("SAPI.SpVoice")
	say = _voice.Speak

if 'darwin' in sys.platform:
	import subprocess
	def say(phrase):
		subprocess.call(['/usr/bin/say', message]) # -v Zarvox
