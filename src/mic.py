#!/usr/bin/env python3

import os
import queue
import sounddevice as sd
import vosk
import sys

import requests
from utils import str2int

def start():
    stream = queue.Queue()

    def callback(indata, frames, time, status):
        """This is called (from a separate thread) for each audio block."""
        if status:
            print(status, file=sys.stderr)
        stream.put(bytes(indata))

    try:
        model = load_model()
        # Use first device by default: soundfile expects an int, sounddevice provides a float:
        samplerate = int(sd.query_devices(0, 'input')['default_samplerate'])
        # Start Input
        with sd.RawInputStream(samplerate=samplerate, blocksize = 8000, device=0, dtype='int16',
                                channels=1, callback=callback):
            print('#' * 80)
            print('Press Ctrl+C to stop the recording')
            print('#' * 80)

            # Start speech recognition
            start_recognition(model, samplerate, stream)

    except KeyboardInterrupt:
        print('\nDone')

    except Exception as e:
        print(e)


def load_model():
    """Load required inputs for speech recognition"""
    model_name = "model"
    if not os.path.exists(model_name):
        print ("Please download a model for your language from https://alphacephei.com/vosk/models")
        print ("and unpack as 'model' in the current folder.")

    return vosk.Model(model_name)

def parse_stream(recognizer, stream):
    """Parse recognized text for Bible references
    ARGS:
        recognizer: the vosk recognizer
        stream: stream of recognized text
    """
    # Define book names (used as triggers to start looking for chapters/verses)
    books = ["genesis","exodus","leviticus","numbers","deuteronomy","joshua","judges","ruth","1 samuel","2 samuel","1 kings","2 kings","1 chronicles","2 chronicles","ezra","nehemiah","esther","job","psalms","proverbs","ecclesiastes","song of solomon","isaiah","jeremiah","lamentations","ezekiel","daniel","hosea","joel","amos","obadiah","jonah","micah","nahum","habakkuk","zephaniah","haggai","zechariah","malachi ","matthew","mark","luke","john","the acts","romans","1 corinthians","2 corinthians","galatians","ephesians","philippians","colossians","1 thessalonians","2 thessalonians","1 timothy","2 timothy","titus","philemon","hebrews","james","1 peter","2 peter","1 john","2 john","3 john","jude","revelation"]

    # If recording is still active, skip parsing
    if not recognizer.AcceptWaveform(stream.get()):
        return
    # If recording has finished a chunk, then parse
    raw = eval(recognizer.PartialResult())['partial'].split()
    recognizer.Result()
    # Filler words to be ignored durring parsing
    chapter_filler_words = ["chapter"]
    verse_filler_words = ["verse", "and"]
    # Cycle through words looking for book titles
    word_count = 0
    for word in raw:
        if ((word in books)
            or (word == "song")
            or (word == "first")
            or (word == "second")
            or (word == "third")
        ):
            # Consider the word to be a book title
            book = word
            # Default chapter to be 1 word after the book title
            chapter_index = 1
            # Handle Song of Solomon differently since it is three words
            if book == "song":
                # Make sure entire book title was parsed
                if not raw[word_count+1:word_count+3] == ["of", "solomon"]:
                    word_count += 1
                    continue
                book = "song of solomon"
                chapter_index = 3
            # Handle books with 'first'/'second'/'third' in title differently
            if book == "first" or book == "second" or book == "third":
                # Adjust Book Title
                if book == "first":
                    book = f"1 {raw[word_count+1]}"
                    # remove the book from the text to prevent book of John from also showing
                    raw.remove(raw[word_count+1])
                elif book == "second":
                    book = f"2 {raw[word_count+1]}"
                    # remove the book from the text to prevent book of John from also showing
                    raw.remove(raw[word_count+1])
                elif book == "third":
                    book = f"3 {raw[word_count+1]}"
                    # remove the book from the text to prevent book of John from also showing
                    raw.remove(raw[word_count+1])
                # Verify parsed book exists
                if not book in books:
                    word_count += 1
                    continue

            # Get amount of numbers after Book is mentioned
            chapter_filler_word_count = 0
            verse_filler_word_count = 0
            reference_items = 0
            number = 0
            while number < 4 + chapter_filler_word_count + verse_filler_word_count:
                try:
                    if raw[word_count+chapter_index+number] in chapter_filler_words:
                        chapter_filler_word_count += 1
                        number += 1
                        continue
                    elif raw[word_count+chapter_index+number] in verse_filler_words:
                        verse_filler_word_count += 1
                        number += 1
                        continue
                    else:
                        if str2int(raw[word_count+chapter_index+number].replace("for", "four").replace("to", "two").replace("fourty", "forty").replace("fourty", "forty")) != "":
                            reference_items += 1
                        number += 1
                except:
                    break
            # If only one number is referenced continue unless book has one chapter
            if reference_items == 1:
                # If book has only one chapter, then assume the number is a verse
                try:
                    if book in ["obadiah", "philemon", "jude", "2 john", "3 john"]:
                        chapter = 1
                        verse = str2int(raw[word_count+chapter_index].replace("for", "four").replace("to", "two").replace("fourty", "forty"))
                    else:
                        word_count += 1
                        continue
                except:
                    word_count += 1
                    continue
            # If two numbers are referenced, assume first is chapter and
            #   second is verse unless first is a multiple of 10, then continue
            elif reference_items == 2:
                try:
                    if raw[word_count+chapter_index+chapter_filler_word_count].endswith("ty") and verse_filler_word_count > 0:
                        chapter = str2int(raw[word_count+chapter_index+chapter_filler_word_count].replace("for", "four").replace("to", "two").replace("fourty", "forty"))
                        verse = str2int(raw[word_count+chapter_index+chapter_filler_word_count+1+verse_filler_word_count].replace("for", "four").replace("to", "two").replace("fourty", "forty"))
                    else:
                        chapter = str2int(raw[word_count+chapter_index+chapter_filler_word_count].replace("for", "four").replace("to", "two").replace("fourty", "forty"))
                        verse = str2int(raw[word_count+chapter_index+chapter_filler_word_count+1+verse_filler_word_count].replace("for", "four").replace("to", "two").replace("fourty", "forty"))
                except:
                    word_count += 1
                    continue
            elif reference_items == 3:
                try:
                    if raw[word_count+chapter_index+chapter_filler_word_count].endswith("ty") and chapter_filler_word_count > 0:
                        chapter = str2int(raw[word_count+chapter_index+chapter_filler_word_count].replace("for", "four").replace("to", "two").replace("fourty", "forty"))
                        verse = str2int(raw[word_count+chapter_index+chapter_filler_word_count+1+verse_filler_word_count].replace("for", "four").replace("to", "two").replace("fourty", "forty"))+str2int(raw[word_count+chapter_index+chapter_filler_word_count+1+verse_filler_word_count+1].replace("for", "four").replace("to", "two").replace("fourty", "forty"))
                    elif raw[word_count+chapter_index+chapter_filler_word_count].endswith("ty") and verse_filler_word_count == 0:
                        chapter = str2int(raw[word_count+chapter_index+chapter_filler_word_count].replace("for", "four").replace("to", "two").replace("fourty", "forty"))+str2int(raw[word_count+chapter_index+chapter_filler_word_count+1].replace("for", "four").replace("to", "two").replace("fourty", "forty"))
                        verse = str2int(raw[word_count+chapter_index+chapter_filler_word_count+1+verse_filler_word_count+1].replace("for", "four").replace("to", "two").replace("fourty", "forty"))
                    # elif verse_filler_word_count >= 0:
                    #     chapter = str2int(raw[word_count+chapter_index+chapter_filler_word_count].replace("for", "four").replace("to", "two").replace("fourty", "forty"))
                    #     verse = str2int(raw[word_count+chapter_index+chapter_filler_word_count+1+verse_filler_word_count].replace("for", "four").replace("to", "two").replace("fourty", "forty"))+str2int(raw[word_count+chapter_index+chapter_filler_word_count+1+verse_filler_word_count+1].replace("for", "four").replace("to", "two").replace("fourty", "forty"))
                    else:
                        chapter = str2int(raw[word_count+chapter_index+chapter_filler_word_count].replace("for", "four").replace("to", "two").replace("fourty", "forty"))+str2int(raw[word_count+chapter_index+chapter_filler_word_count+1].replace("for", "four").replace("to", "two").replace("fourty", "forty"))
                        verse = str2int(raw[word_count+chapter_index+chapter_filler_word_count+1+verse_filler_word_count+1].replace("for", "four").replace("to", "two").replace("fourty", "forty"))
                except:
                    word_count += 1
                    continue
            elif reference_items == 4:
                try:
                    chapter = str2int(raw[word_count+chapter_index+chapter_filler_word_count].replace("for", "four").replace("to", "two").replace("fourty", "forty"))+str2int(raw[word_count+chapter_index+chapter_filler_word_count+1].replace("for", "four").replace("to", "two").replace("fourty", "forty"))
                    verse = str2int(raw[word_count+chapter_index+chapter_filler_word_count+1+verse_filler_word_count].replace("for", "four").replace("to", "two").replace("fourty", "forty"))+str2int(raw[word_count+chapter_index+chapter_filler_word_count+1+verse_filler_word_count+1].replace("for", "four").replace("to", "two").replace("fourty", "forty"))
                except:
                    word_count += 1
                    continue
            else:
                word_count += 1
                continue
            if verse == "":
                api_url = f"https://bible-api.com/{book}+{chapter}"
            else:
                api_url = f"https://bible-api.com/{book}+{chapter}:{verse}"
            text = requests.get(api_url).json()["text"]
            print(f"{book.title()} {chapter}:{verse} \n {text}")
        word_count += 1

def start_recognition(model, samplerate, stream):
    """Start speech recognition
    ARGS:
        model: vosk speech recognition model
        samplerate: integer containing the sample rate
        stream: the audio stream
    """
    recognizer = vosk.KaldiRecognizer(model, samplerate)
    while True:
        parse_stream(recognizer, stream)