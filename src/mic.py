""" Contains parsing and recording functions """
import logging
import time

import requests
import speech_recognition as sr

import settings


# this is called from the background thread
def callback(recognizer, audio):
    """ This is called each time a chunk of speech is finished being recorded """
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
            logging.info(display_text)
        except:
            error = f"Failed to fetch {book.capitalize()} {chapter}:{verse} - Maybe it doesn't exist?"
            logging.error(error)
        index += 1 + additional_index

def start():
    """ Start recognizing speech """
    # Setup recognizer and change default settings.
    r = sr.Recognizer()
    # Change defaults using settings
    r.non_speaking_duration = settings.NON_SPEAKING_DURATION
    r.pause_threshold = settings.PAUSE_THRESHOLD
    m = sr.Microphone()
    with m as source:
        r.adjust_for_ambient_noise(source)  # we only need to calibrate once, before we start listening
    try:
    # start listening in the background (note that we don't have to do this inside a `with` statement)
    # stop_listening will be a function that when called will stop listening.
        stop_listening = r.listen_in_background(m, callback)
        while True: time.sleep(0.1)
    except Exception as e:
        logging.error(e)