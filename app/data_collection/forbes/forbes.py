from configparser import ConfigParser
import pandas as pd
import requests
from bs4 import BeautifulSoup
from flask import Flask, request

app = Flask(__name__)


class ForbesArticles:
    def __init__(self):
        self._output = []
        self._tags = []
        self._query = "None"
        self._parsed_html = None
        self._session = requests.session()
        self._article_session = requests.session()
        self._article_counter = 0
        self._config = ConfigParser()
        self._config.read(["./config/forbes.ini"])
        self.__username = self._config.get("CREDENTIALS", "username")
        self.__password = self._config.get("CREDENTIALS", "password")
        self._chromedriver_path = self._config.get("RESOURCES", "chromedriver_path")
        self._csv_path = self._config.get("RESOURCES", "output_path")
        self._url = self._config.get("SERVICE", "url")

    @property
    def query(self):
        return self._query

    @query.setter
    def query(self, value):
        self._query = value

    @property
    def output(self):
        return self._output

    @property
    def tags(self):
        return self._tags

    def _get_tags(self):
        tag_list = list(self._parsed_html.find("body").find("ul", attrs={"class": "entity-lists__data"}).children)
        for li in tag_list:
            tag = []
            if li.find("a").find("div", attrs={"class": "entity-list__rank"}):
                tag.append(li.find("a").find("div", attrs={"class": "entity-list__rank"}).getText())
            if li.find("a").find("div", attrs={"class": "entity-list__title"}):
                tag.append(li.find("a").find("div", attrs={"class": "entity-list__title"}).getText())
            if tag:
                self._tags.append(" ".join(tag))

    def _get_article_body(self, link):
        if self._article_counter == 4:
            self._article_session.cookies.clear()
        response = self._article_session.get(link)
        parsed_html = BeautifulSoup(response.text, features="html.parser")
        try:
            paragraphs = parsed_html.find("body").find("div", attrs={"class": "article-body-container"}).find_all("p")
            article = []
            for p in paragraphs:
                if len(p.getText()):
                    article.append(p.getText())
            return " ".join(article[1:])
        except AttributeError:
            return ""

    def _get_articles(self):
        article_list = list(
            self._parsed_html.find("body").find("div",
                                                attrs={"class": "search-results__items"}
                                                ).find_all("article"))
        for article in article_list:
            if article:
                tmp = {
                    "date": article.find("div", attrs={"class": "stream-item__date"}).getText(),
                    "headline": article.find("a", attrs={"class": "stream-item__title"}).getText(),
                    "link": article.find("a", attrs={"class": "stream-item__title"}).attrs["href"]
                }
                tmp["article"] = self._get_article_body(tmp["link"])
                if len(tmp["article"]):
                    self._output.append(tmp)

    def execute_query(self):
        # self._driver.get(self._url.format(QUERY='+'.join(self._query.split(' '))))
        response = self._session.get(self._url.format(QUERY='+'.join(self._query.split(' '))))
        self._parsed_html = BeautifulSoup(response.text, features="html.parser")
        self._get_tags()
        self._get_articles()
        pd.DataFrame(self._output).to_csv(self._csv_path.format(COMPANY=self._query))


forbes_articles = ForbesArticles()


@app.route("/get_response", methods=["POST"])
def get_response():
    query = request.json
    forbes_articles.query = query["query"]
    forbes_articles.execute_query()
    return {"output": forbes_articles.output}


if __name__ == "__main__":
    app.run(debug=False)
    # forbes_articles.query = "tesla"
    # forbes_articles.execute_query()
