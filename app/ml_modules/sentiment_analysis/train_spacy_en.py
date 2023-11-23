import numpy as np
import pandas as pd
import spacy
from spacy.cli import download
import random
import re
import pandas as pd
from spacy.pipeline.textcat import Config, single_label_cnn_config, single_label_bow_config, single_label_default_config
from spacy.training.example import Example
from spacy.util import minibatch
from sklearn.model_selection import train_test_split

spacy.prefer_gpu()
spacy.require_gpu()

data1 = pd.read_csv('datasets/data.csv')
data2 = pd.read_csv('datasets/data1/all-data.csv', encoding="windows_1258")
df = pd.concat([data1, data2], axis=0, ignore_index=True)

df["Sentence"]=df["Sentence"].str.lower() #We convert our texts to lowercase.
df["Sentence"]=df["Sentence"].str.replace("[^\w\s]","") #We remove punctuation marks from our texts.
#df["text"]=df["text"].str.replace("\d+","") #We are removing numbers from our texts.
df["Sentence"]=df["Sentence"].str.replace("\n","").replace("\r","") #We remove spaces in our texts.
df=df[df['Sentiment']!='neutral']

df, test = train_test_split(df, train_size=0.9, shuffle=True, stratify=df['Sentiment'])

train_texts = df['Sentence'].values
train_labels = [{'cats': {'positive': label == 'positive',
                          'negative': label == 'negative'}}
                for label in df['Sentiment']]

train_data = list(zip(train_texts, train_labels))
# Create an empty model
#nlp = spacy.load("en_core_web_trf")
nlp = spacy.blank('en')
config = Config().from_str(single_label_bow_config)
text_cat = nlp.add_pipe('textcat', config=config, last=True)
text_cat.add_label("positive")
text_cat.add_label("negative")
#text_cat.add_label("neutral")


random.seed(1)
spacy.util.fix_random_seed(1)
optimizer = nlp.begin_training()
last_loss = diff = 1000
losses = {}
epoch = 0
#hile diff >= 0.0001 and epoch < 300:
for epoch in range(60):
    random.shuffle(train_data)
    # Create the batch generator with batch size = 8
    batches = minibatch(train_data, size=8)
    # Iterate through minibatches
    for batch in batches:
        texts, annotations = zip(*batch)

        example = []
        # Update the model with iterating each text
        for i in range(len(texts)):
            doc = nlp.make_doc(texts[i])
            example.append(Example.from_dict(doc, annotations[i]))

            # Update the model
        nlp.update(example, drop=0.5, losses=losses)
    print(losses)
    epoch += 1
    diff = last_loss - losses['textcat']
    last_loss = losses['textcat']

nlp.to_disk('spacy_en')
