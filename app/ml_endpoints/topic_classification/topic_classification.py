import ast
from transformers import pipeline
from configparser import ConfigParser
from flask import Flask, request

# classifier = pipeline("zero-shot-classification")
# sequence = "Company Xio takes down warehouses in India and US"
# candidate_labels = ["company growth", "user experience", "sales", "market position", "business expanse"]
#
# print(classifier(sequence, candidate_labels, multi_class=True))
#
# sequence = "The company's new product feels okay. Not good, not bad."
# candidate_labels = ["positive", "neutral", "negative"]
#
# print(classifier(sequence, candidate_labels, multi_class=False))

app = Flask("app")

class TopicClassification:
    def __init__(self, config_path="./config/topic_classification.ini"):
        self._config = ConfigParser()
        self._config.read([config_path])

        self._model_name = self._config.get("MODELS", "model_name")
        self._model = pipeline(self._model_name)

        self._news_classes = ast.literal_eval(self._config.get("NEWS", "news_classes"))
        self._news_multiclass_flag = ast.literal_eval(self._config.get("NEWS", "multiclass_flag"))
        self._news_output_dict = {label: 0 for label in self._news_classes}

        self._sentiment_classes = ast.literal_eval(self._config.get("SENTIMENT", "sentiment_classes"))
        self._sentiment_multiclass_flag = ast.literal_eval(self._config.get("SENTIMENT", "multiclass_flag"))
        self._sentiment_output_dict = {label: 0 for label in self._sentiment_classes}

        self._text = ""

        self._classifier = "all"

        self._custom_classes = []
        self._custom_multiclass_flag = False
        self._custom_output_dict = {}

        self._query = {}

        self._output = {"text": "",
                        "classifier": "prod",
                        "result": {"news": self._news_output_dict, "sentiment": self._sentiment_output_dict,
                                   "custom": {}}}

    @property
    def query(self):
        return self._query

    @query.setter
    def query(self, value):
        self._query = value
        self._text = self._query["text"]
        self._classifier = self._query["classifier"]
        self._custom_classes = self._query["custom_classes"]
        self._custom_multiclass_flag = self._query["custom_multiclass"]

    @property
    def classifier(self):
        return self._classifier

    @classifier.setter
    def classifier(self, value):
        self._classifier = value

    @property
    def output(self):
        self._execute_query()
        self._output = {"text": self._text,
                        "classifier": self._classifier,
                        "result": {"news": self._news_output_dict, "sentiment": self._sentiment_output_dict,
                                   "custom": self._custom_output_dict}}
        self._text = ""
        self._classifier = "prod"
        self._news_output_dict = {label: 0 for label in self._news_classes}
        self._sentiment_output_dict = {label: 0 for label in self._sentiment_classes}
        self._custom_output_dict = {}
        return self._output

    def _execute_query(self):
        if self._classifier == "prod":
            news_output = self._model(sequences=self._text, candidate_labels=self._news_classes,
                                      multi_class=self._news_multiclass_flag)
            print(news_output)
            self._news_output_dict = {key: news_output["scores"][i] for i, key in enumerate(news_output["labels"])}

            sentiment_output = self._model(sequences=self._text, candidate_labels=self._sentiment_classes,
                                      multi_class=self._sentiment_multiclass_flag)
            print(sentiment_output)
            self._sentiment_output_dict = {key: sentiment_output["scores"][i] for i, key in
                                           enumerate(sentiment_output["labels"])}

        if self._classifier == "news":
            news_output = self._model(sequences=self._text, candidate_labels=self._news_classes,
                                      multi_class=self._news_multiclass_flag)
            self._news_output_dict = {key: news_output["scores"][i] for i, key in enumerate(news_output["labels"])}

        if self._classifier == "sentiment":
            sentiment_output = self._model(sequences=self._text, candidate_labels=self._sentiment_classes,
                                           multi_class=self._sentiment_multiclass_flag)
            self._sentiment_output_dict = {key: sentiment_output["scores"][i] for i, key in
                                           enumerate(sentiment_output["labels"])}

        if self._classifier == "custom" and self._custom_classes:
            custom_output = self._model(sequences=self._text, candidate_labels=self._custom_classes,
                                      multi_class=self._custom_multiclass_flag)
            self._custom_output_dict = {key: custom_output["scores"][i] for i, key in
                                           enumerate(custom_output["labels"])}

        if self._classifier == "all":
            news_output = self._model(sequences=self._text, candidate_labels=self._news_classes,
                                      multi_class=self._news_multiclass_flag)
            self._news_output_dict = {key: news_output["scores"][i] for i, key in enumerate(news_output["labels"])}

            sentiment_output = self._model(sequences=self._text, candidate_labels=self._sentiment_classes,
                                           multi_class=self._sentiment_multiclass_flag)
            self._sentiment_output_dict = {key: sentiment_output["scores"][i] for i, key in
                                           enumerate(sentiment_output["labels"])}

            custom_output = self._model(sequences=self._text, candidate_labels=self._custom_classes,
                                        multi_class=self._custom_multiclass_flag)
            self._custom_output_dict = {key: custom_output["scores"][i] for i, key in
                                        enumerate(custom_output["labels"])}


topic_classification = TopicClassification()

@app.route("/get_response", methods=["POST"])
def get_response():
    query = request.json
    topic_classification.query = query["query"]
    # topic_classification.execute_query()
    return {"output": topic_classification.output}

if __name__ == "__main__":
    app.run(debug=False)