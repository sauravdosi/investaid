from flask import Flask, request
from configparser import ConfigParser
import spacy

app = Flask(__name__)


class SentimentFinder:
    def __init__(self):
        self._models = {}
        self.sentiment = None
        self.sentiment_score = None
        self.sentiment_scores = None
        self.cat_scores = None
        self.output = {}
        self.all_results = {}
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

    def load_models(self):
        self._spacy_config()
        self._models["spacy_en"] = spacy.load(self._spacy_en_path)
        self._models["spacy_trf"] = spacy.load(self._spacy_trf_path)

    def get_sentiment(self, statement, model="spacy_trf"):
        if model in self._models:
            doc = self._models[model](statement)
            sentiments = ['positive', 'negative', 'neutral']
            self.sentiment = max(sentiments, key=lambda s: doc.cats[s] if s in doc.cats else 0)
            self.sentiment_score = doc.cats.get(self.sentiment, 0)
            self.cat_scores = doc.cats
            self.output = {
                'sentiment': self.sentiment,
                'cat_score': self.sentiment_score,
                'cat_scores': self.cat_scores,
                'model': model
            }
            self.all_results[model] = self.output
        elif model == "all":
            for m in self._models:
                self.get_sentiment(statement, model=m)
            self.output = self.all_results


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
