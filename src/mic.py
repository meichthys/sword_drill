#!/usr/bin/env python3

import argparse
import os
import queue
import sounddevice as sd
import vosk
import sys

import requests
from utils import str2int

def start():
    q = queue.Queue()

    def int_or_str(text):
        """Helper function for argument parsing."""
        try:
            return int(text)
        except ValueError:
            return text

    def callback(indata, frames, time, status):
        """This is called (from a separate thread) for each audio block."""
        if status:
            print(status, file=sys.stderr)
        q.put(bytes(indata))

    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument(
        '-l', '--list-devices', action='store_true',
        help='show list of audio devices and exit')
    args, remaining = parser.parse_known_args()
    if args.list_devices:
        print(sd.query_devices())
        parser.exit(0)
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        parents=[parser])
    parser.add_argument(
        '-f', '--filename', type=str, metavar='FILENAME',
        help='audio file to store recording to')
    parser.add_argument(
        '-m', '--model', type=str, metavar='MODEL_PATH',
        help='Path to the model')
    parser.add_argument(
        '-d', '--device', type=int_or_str,
        help='input device (numeric ID or substring)')
    parser.add_argument(
        '-r', '--samplerate', type=int, help='sampling rate')
    args = parser.parse_args(remaining)

    try:
        if args.model is None:
            args.model = "model"
        if not os.path.exists(args.model):
            print ("Please download a model for your language from https://alphacephei.com/vosk/models")
            print ("and unpack as 'model' in the current folder.")
            parser.exit(0)
        if args.samplerate is None:
            device_info = sd.query_devices(args.device, 'input')
            # soundfile expects an int, sounddevice provides a float:
            args.samplerate = int(device_info['default_samplerate'])

        model = vosk.Model(args.model)

        if args.filename:
            dump_fn = open(args.filename, "wb")
        else:
            dump_fn = None
        with sd.RawInputStream(samplerate=args.samplerate, blocksize = 8000, device=args.device, dtype='int16',
                                channels=1, callback=callback):
                print('#' * 80)
                print('Press Ctrl+C to stop the recording')
                print('#' * 80)

                books = ["genesis","exodus","leviticus","numbers","deuteronomy","joshua","judges","ruth","1 samuel","2 samuel","1 kings","2 kings","1 chronicles","2 chronicles","ezra","nehemiah","esther","job","psalms","proverbs","ecclesiastes","song of solomon","isaiah","jeremiah","lamentations","ezekiel","daniel","hosea","joel","amos","obadiah","jonah","micah","nahum","habakkuk","zephaniah","haggai","zechariah","malachi ","matthew","mark","luke","john","the acts","romans","1 corinthians","2 corinthians","galatians","ephesians","philippians","colossians","1 thessalonians","2 thessalonians","1 timothy","2 timothy","titus","philemon","hebrews","james","1 peter","2 peter","1 john","2 john","3 john","jude","revelation"]
                rec = vosk.KaldiRecognizer(model, args.samplerate)
                while True:
                    data = q.get()
                    # Get recognized audio
                    if rec.AcceptWaveform(data):
                        latest = rec.PartialResult()
                        rec.Result()
                        # Parse partial text into a list of words and remove references to 'chapter' and 'verse'
                        current = eval(latest)["partial"].replace("chapter ", "").replace("verse ", "").replace("number ", "").split()
                        # Cycle through words looking for book titles
                        word_count = 0
                        for word in current:
                            # Default chapter to be 1 word after the book title
                            chapter_index = 1
                            # Default verse to be 2 words after the book title
                            verse_index = 2
                            if ((word in books)
                                or (word == "song")
                                or (word == "first")
                                or (word == "second")
                                or (word == "third")
                            ):
                                # Consider the word to be a book title
                                book = word
                                # Handle Song of Solomon differently since it is three words
                                if book == "song":
                                    # Make sure entire book title was parsed
                                    if not current[word_count+1:word_count+3] == ["of", "solomon"]:
                                        continue
                                    book = "song of solomon"
                                    chapter_index = 3
                                    verse_index = 4
                                # Handle books with 'first'/'second'/'third' in title differently
                                if book == "first" or book == "second" or book == "third":
                                    # Adjust Chapter/Verse index
                                    chapter_index = 2
                                    verse_index = 3
                                    # Adjust Book Title
                                    if book == "first":
                                        book = f"1 {current[word_count+1]}"
                                    elif book == "second":
                                        book = f"2 {current[word_count+1]}"
                                    elif book == "third":
                                        book = f"3 {current[word_count+1]}"
                                    # Verify parsed book exists
                                    if not book in books:
                                        continue
                                # Get chapter & verse numbers
                                try:
                                    chapter = str2int(current[word_count + chapter_index].replace("for", "four").replace("to", "two"))
                                except:
                                    chapter = ""
                                try:
                                    verse = str2int(current[word_count + verse_index].replace("for", "four").replace("to", "two"))
                                except:
                                    verse = ""
                                if chapter == "":
                                    continue
                                # Show entire chapter if no verse is given
                                if verse == "":
                                    api_url = f"https://bible-api.com/{book}+{chapter}"
                                else:
                                    api_url = f"https://bible-api.com/{book}+{chapter}:{verse}"
                                text = requests.get(api_url).json()["text"]
                                print(f"{book.title()} {chapter}:{verse} \n {text}")
                            word_count += 1

                    if dump_fn is not None:
                        dump_fn.write(data)

    except KeyboardInterrupt:
        print('\nDone')
        parser.exit(0)
    except Exception as e:
        parser.exit(type(e).__name__ + ': ' + str(e))
