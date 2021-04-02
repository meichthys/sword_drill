
import logging

import requests
import speech_recognition as sr
from threading import Thread

from PyQt5.QtWidgets import QMainWindow, QApplication

from gui.main_window import Ui_MainWindow
from app import settings


class MainWindow(QMainWindow, Ui_MainWindow):
    """ Main GUI window of application """
    def __init__(self):
        super(MainWindow, self).__init__()
        logging.debug("Setting up GUI...")
        self.setupUi(self)
        logging.debug("Setting up background listener...")
        t1 = Thread(target=self.start)
        t1.start()

    # this is called from the background thread
    def callback(self, recognizer, audio):
        """ This is called each time a chunk of speech is finished being recorded """
        logging.debug("Audio chunk sent for processing...")
        # Set book titles
        books = ["Genesis","Exodus","Leviticus","Numbers","Deuteronomy","Joshua","Judges","Ruth","1 Samuel","2 Samuel","1 Kings","2 Kings","1 Chronicles","2 Chronicles","Ezra","Nehemiah","Esther","Job","Psalms","Proverbs","Ecclesiastes","Song of Solomon","Isaiah","Jeremiah","Lamentations","Ezekiel","Daniel","Hosea","Joel","Amos","Obadiah","Jonah","Micah","Nahum","Habakkuk","Zephaniah","Haggai","Zechariah","Malachi","Matthew","Mark","Luke","John","Acts","Romans","1 Corinthians","2 Corinthians","Galatians","Ephesians","Philippians","Colossians","1 Thessalonians","2 Thessalonians","1 Timothy","2 Timothy","Titus","Philemon","Hebrews","James","1 Peter","2 Peter","1 John","2 John","3 John","Jude","Revelation"]
        # Get speech as list of words
        try:
            # For testing purposes, we're just using the default API key
            # to use another API key, use `r.recognize_google(audio, key="GOOGLE_SPEECH_RECOGNITION_API_KEY")`
            raw = recognizer.recognize_google(audio)
            logging.debug(f"Raw recognized text: {raw}")
            # Replace filler words
            speech = raw.replace(
                ":", " ").replace(
                "chapter", "").replace(
                "verse", "").replace(
                "and", "").split()

        except sr.UnknownValueError:
            logging.debug("No audio recognized")
            return
        except sr.RequestError as e:
            logging.error("Could not request results from speech recognition api; {0}".format(e))
            return
        # Parse references
        index = 0
        for word in speech:
            additional_index = 0
            # Get full book name if starts with number
            if word in ["1st", "2nd", "3rd"]:
                index += 1
                if word == "1st":
                    word = f"1 {speech[index]}"
                    additional_index = 1
                elif word == "2nd":
                    word = f"2 {speech[index]}"
                    additional_index = 1
                elif word == "3rd":
                    word = f"3 {speech[index]}"
                    additional_index = 1
            # Get full book name for Song of Solomon since it's multiple words long
            if word.lower() == "song":
                index += 2
                word = "Song of Solomon"
            # Make sure book name exist sin book list
            if not word in books:
                index += 1
                continue

            # Parse reference
            try:
                book = word
                chapter = speech[index + 1]
                if len(speech) >= index + 3:
                    verse = speech[index + 2]
                else:
                    verse = ""
                if not chapter.isdigit() and not verse.isdigit():
                    logging.debug(f"Parsed Chapter ({chapter}) and verse ({verse}) are not both digits")
                    index += 1
                    continue
                elif chapter.isdigit() and not verse.isdigit() and (
                    book in ["Obadiah", "Philemon", "Jude", "2 John", "3 John"]
                ):
                    verse = chapter
                    chapter = 1

            except IndexError:
                logging.debug(f"Could not parse reference from: {speech[index:]}")
                index += 1
                continue

            try:
                api_url = f"https://bible-api.com/{book}+{chapter}:{verse}?translation={settings.TRANSLATION}"
                logging.debug(f"Fetching url: {api_url}")
                text = requests.get(api_url).json()["text"]
                display_text = f"{book.title()} {chapter}:{verse} \n {text}"
                self.ui_label.setText(display_text)
                logging.info(display_text)
            except:
                error = f"Failed to fetch {book.capitalize()} {chapter}:{verse} - Maybe it doesn't exist?"
                logging.error(error)
            index += 1 + additional_index

    def start(self):
        """ Start recognizing speech """
        # Setup recognizer and change default settings.
        r = sr.Recognizer()
        # Change defaults using settings
        r.non_speaking_duration = settings.NON_SPEAKING_DURATION
        r.pause_threshold = settings.PAUSE_THRESHOLD
        m = sr.Microphone(device_index=settings.MIC_NUMBER)
        logging.info(f"Recognized microphones: {m.list_microphone_names()}")
        logging.info(f"Using microphone: {m.list_microphone_names()[settings.MIC_NUMBER]}")
        with m as source:
            logging.debug("Adjusting for ambient noise...")
            r.adjust_for_ambient_noise(source)  # we only need to calibrate once, before we start listening
        try:
        # start listening in the background (note that we don't have to do this inside a `with` statement)
        # stop_listening will be a function that when called will stop listening.
            self.stop_listening = r.listen_in_background(m, self.callback)
        except Exception as e:
            logging.error(e)
