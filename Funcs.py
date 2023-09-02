from pygame import mixer
from gtts import gTTS
import os
from time import sleep
from chess import SQUARES


def read_out(text, filename="temp.mp3", delete_audio_file=True, language="en", slow=False):
    """
    Reads out a piece of text using Google Translate's text-to-speech feature.

    An audio file will be created and then played, after which the function terminates.

    :param text: Text
    :param filename: Name of the audio file to be created
    :param delete_audio_file: Whether the audio file created is to be deleted after it is played
    :param language: THe language of the text
    :param slow: Whether the text should be read out slowly
    """
    audio = gTTS(text, lang=language, slow=slow)
    audio.save(filename)

    mixer.init()
    mixer.music.load(filename)
    mixer.music.play()

    seconds = 0
    while mixer.music.get_busy() == 1:
        sleep(0.25)
        seconds += 0.25

    mixer.quit()
    if delete_audio_file:
        os.remove(filename)


def num_pieces_by_color(board, color):
    """
    :param board: A board layout.
    :param color: A color (black or white).
    :return: The number of pieces of the given color in the given board.
    """
    return sum([board.color_at(i) == color for i in SQUARES])