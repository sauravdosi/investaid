from flask import Flask, request
from configparser import ConfigParser
import spacy

app = Flask(__name__)


class SentimentFinder:
    def __init__(self):
        self._models = {}
        self._sentiment = None
        self._sentiment_score = None
        self._sentiment_scores = None
        self._cat_scores = None
        self._output = {}
        self._all_results = {}
        self._config = ConfigParser()
        self._config.read(["./config/sentiment_analysis.ini"])
        self._gpu = self._config.get("CONFIG", "gpu")
        self._spacy_en_path = self._config.get("MODELS", "spacy_en_path")
        self._spacy_trf_path = self._config.get("MODELS", "spacy_trf_path")
        self.default_model = self._config.get("MODELS", "default_model")

    def _spacy_config(self):
        if self._gpu:
            spacy.prefer_gpu()
            spacy.require_gpu()

    @property
    def sentiment(self):
        return self._sentiment

    @property
    def sentiment_score(self):
        return self._sentiment_score

    @property
    def sentiment_scores(self):
        return self._sentiment_scores

    @property
    def cat_scores(self):
        return self._cat_scores

    @property
    def output(self):
        return self._output

    @property
    def all_results(self):
        return self._all_results

    def load_models(self):
        self._spacy_config()
        self._models["spacy_en"] = spacy.load(self._spacy_en_path)
        self._models["spacy_trf"] = spacy.load(self._spacy_trf_path)

    def get_sentiment(self, statement, model="spacy_trf"):
        if model in self._models:
            doc = self._models[model](statement)
            sentiments = ['positive', 'negative', 'neutral']
            self._sentiment = max(sentiments, key=lambda s: doc.cats[s] if s in doc.cats else 0)
            self._sentiment_score = doc.cats.get(self.sentiment, 0)
            self._cat_scores = doc.cats
            self._output = {
                'sentiment': self.sentiment,
                'cat_score': self.sentiment_score,
                'cat_scores': self.cat_scores,
                'model': model
            }
            self._all_results[model] = self.output
        elif model == "all":
            for m in self._models:
                self.get_sentiment(statement, model=m)
            self._output = self._all_results


sf = SentimentFinder()
sf.load_models()


@app.route('/get_sentiment', methods=['POST'])
def get_sentiment():
    data = request.form
    req_model = data.get("model", sf.default_model)
    sf.get_sentiment(data["text"], req_model)
    print(sf.output)
    return {"output": sf.output}


if __name__ == '__main__':
    app.run()
