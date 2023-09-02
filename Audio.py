from pygame import mixer
from gtts import gTTS
import os
from time import sleep


def say(text, filename="temp.mp3", delete_audio_file=True, language="en", slow=False):
    # PART 2
    audio = gTTS(text, lang=language, slow=slow)
    audio.save(filename)

    # PART 3
    mixer.init()
    mixer.music.load(filename)
    mixer.music.play()

    # PART 4
    seconds = 0
    while mixer.music.get_busy() == 1:
        sleep(0.25)
        seconds += 0.25

    # PART 5
    mixer.quit()
    if delete_audio_file:
        os.remove(filename)