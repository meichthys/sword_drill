# Ignore these
import logging

# Loging Level can be any of these: ERROR, WARNING, INFO, DEBUG, NOTSET
# Error will log the least and NOTSET will log the most
LOGGING_LEVEL = logging.DEBUG

# Speech recognition settings
MIC_NUMBER = 0 # Can be 0 to n where n is the number of inputs recognized by the application
               # (The debug log will show the list of microphones recognized)
NON_SPEAKING_DURATION = 0.01 # seconds of non-speaking audio to keep on both sides of the recording (must be smaller than PAUSE_THRESHOLD)
PAUSE_THRESHOLD = 0.25 # seconds of non-speaking audio before a phrase is considered complete (must be larger than NON_SPEAKING_DURATION)

# Bible Version to use from the `Identifiers` listed here: https://bible-api.com/
TRANSLATION = "kjv"