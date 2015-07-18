import speech_recognition as sr
r = sr.Recognizer()
r.energy_threshold = 1000

print("Listening...")
with sr.Microphone() as source:             # use the default microphone as the audio source
    audio = r.listen(source)                # listen for the first phrase and extract it into audio data

print("Received: %3.1f" % (len(audio.data) / float(audio.rate)))
try:
    print("Recognized:\n\n\t" + r.recognize(audio))  # recognize speech using Google Speech Recognition
except LookupError:
    print("Error: could not understand audio.")      # speech is unintelligible
