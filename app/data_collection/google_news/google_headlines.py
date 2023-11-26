from configparser import ConfigParser
import pandas as pd
import requests
from bs4 import BeautifulSoup
from flask import Flask, request
from selenium import webdriver
from selenium.common import NoSuchElementException, InvalidSelectorException
from selenium.webdriver.common.by import By

app = Flask(__name__)


class GoogleHeadlines:
    def __init__(self):
        self._output = []
        self._links = []
        self._query = None

        self._config = ConfigParser()
        self._config.read(["./config/google_news.ini"])
        self.__username = self._config.get("CREDENTIALS", "username")
        self.__password = self._config.get("CREDENTIALS", "password")
        self._chromedriver_path = self._config.get("RESOURCES", "chromedriver_path")
        self._csv_path = self._config.get("RESOURCES", "output_path")
        self._url = self._config.get("SERVICE", "url")
        self._page_number_links = self._config.get("WEB_IDENTIFIERS", "page_number_links")
        self._page_number_a = self._config.get("WEB_IDENTIFIERS", "page_number_a")
        self._headlines_containers = self._config.get("WEB_IDENTIFIERS", "headlines_containers")
        self._last_page_a = self._config.get("WEB_IDENTIFIERS", "last_page_a")
        self._date = self._config.get("WEB_IDENTIFIERS", "time")
        self._ancestor_a = self._config.get("WEB_IDENTIFIERS", "ancestor_a")

    @property
    def query(self):
        return self._query

    @query.setter
    def query(self, value):
        self._query = value

    @property
    def output(self):
        return self._output

    def _launch(self):
        print(f"Launching the {self.__class__.__name__} service...")
        self._driver = webdriver.Chrome()
        print("Launched!")

    @staticmethod
    def _time(time):
        if isinstance(time, int):
            return time
        diff = int(time.split(' ')[0])
        if "hours" in time or "hour" in time:
            diff = 1
        elif "mins" in time or "min" in time:
            diff = 1
        elif "weeks" in time or "week" in time:
            diff = diff * 7
        elif "months" in time or "month" in time:
            diff = diff * 30
        return diff

    @staticmethod
    def _process_link(link):
        r = requests.get(link)
        html = r.text
        parsed_html = BeautifulSoup(html, features="html.parser")
        title = parsed_html.find('title')
        return title.text.split('|')[0].split('-')[0]

    def _get_headlines(self):
        heading_divs = self._driver.find_elements(by=By.XPATH,
                                                  value=self._headlines_containers)
        for div in heading_divs:
            headline = div.text
            if len(headline):
                if '...' in div.text:
                    link = self._driver.find_element(by=By.XPATH,
                                                     value=self._ancestor_a.format(headline=div.text)).get_attribute(
                        'href')
                    headline = self._process_link(link)
                try:
                    time = self._driver.find_element(by=By.XPATH,
                                                     value=self._date.format(headline=div.text)).text
                except (InvalidSelectorException, NoSuchElementException):
                    time = self._output[-1]["days"]
                self._output.append({"headline": headline, "days": self._time(time)})

    def deploy(self):
        self._launch()

    def execute_query(self, ):
        self._driver.get(self._url.format(QUERY='+'.join(self._query.split(' '))))
        self._driver.implicitly_wait(3)
        self._get_headlines()
        last_page = self._driver.find_element(by=By.XPATH, value=self._last_page_a).get_attribute("aria-label")
        last_page = int(last_page.split(" ")[1])
        i = 2
        while i <= last_page:
            try:
                self._driver.find_element(by=By.XPATH,
                                          value=self._page_number_a.format(number=i)).click()
                i += 1
                if i != last_page:
                    last_page = self._driver.find_element(by=By.XPATH,
                                                          value=self._last_page_a).get_attribute("aria-label")
                    last_page = int(last_page.split(" ")[1])
                self._driver.implicitly_wait(5)
                self._get_headlines()
            except NoSuchElementException:
                continue
        pd.DataFrame(self._output).to_csv(self._csv_path.format(COMPANY=self._query))


google_headlines = GoogleHeadlines()
google_headlines.deploy()


@app.route("/get_response", methods=["POST"])
def get_response():
    query = request.json
    google_headlines.query = query["query"]
    google_headlines.execute_query()
    return {"output": google_headlines.output}


if __name__ == "__main__":
    app.run(debug=False)
