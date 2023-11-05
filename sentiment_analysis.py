# import spacy
#
# nlp = spacy.load("en_core_web_trf")
# demo = nlp("I love this")
#
# print(demo)

from flair.data import Sentence
from flair.nn import Classifier
from configparser import ConfigParser
import re

# load the NER tagger
tagger = Classifier.load('sentiment')

config = ConfigParser()
config.read(["./emojis_mapping.ini"])

text = '''
Yahoo generated revenue primarily from digital advertising, including display and search advertising. Its sales performance was impacted by shifts in the online advertising landscape and competition from other digital platforms.
'''

# make a sentence
sentence = Sentence(text)

# run NER over sentence
tagger.predict(sentence)

# print the sentence with all annotations
print(sentence)
# print("I love this.😩")