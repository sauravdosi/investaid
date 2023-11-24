import datetime
import glob
import os
import time
from selenium.webdriver import Keys, ActionChains
from selenium.webdriver.common.by import By
import undetected_chromedriver as uc
from configparser import ConfigParser
from flask import Flask, request
from selenium.webdriver import ChromeOptions
import shutil

app = Flask("app")


class GoogleFinance:
    def __init__(self):
        self._query = ""
        self._output = ""
        self._driver = None
        self._config = ConfigParser()
        self._config.read(["./config/google_finance.ini"])
        self.__username = self._config.get("CREDENTIALS", "username")
        self.__password = self._config.get("CREDENTIALS", "password")

        self._chromedriver_path = self._config.get("RESOURCES", "chromedriver_path")

        self._service_url = self._config.get("SERVICE", "url")
        self._source_dir = self._config.get("SERVICE", "source_dir")
        self._destination_dir = self._config.get("SERVICE", "destination_dir")

        self._username_id = self._config.get("WEB_IDENTIFIERS", "username")
        self._password_id = self._config.get("WEB_IDENTIFIERS", "password")
        self._input_box_id = self._config.get("WEB_IDENTIFIERS", "input_box")
        self._cell_id = self._config.get("WEB_IDENTIFIERS", "cell")
        self._file_menu_id = self._config.get("WEB_IDENTIFIERS", "file_menu")
        self._download_option_id = self._config.get("WEB_IDENTIFIERS", "download_option")
        self._csv_option_id = self._config.get("WEB_IDENTIFIERS", "csv_option")
        self._sheet_title_id = self._config.get("WEB_IDENTIFIERS", "sheet_title")
        self._new_tab_id = self._config.get("WEB_IDENTIFIERS", "new_tab")

        self._company_name = ""
        self._parameter = ""
        self._start_date_str = ""
        self._end_date_str = ""
        self._interval = ""

    def _launch(self):
        print(f"Launching the {self.__class__.__name__} service...")
        self._driver = uc.Chrome(executable_path=self._chromedriver_path)
        self._driver.get(self._service_url)
        print("Launched!")

    def _new_tab(self):
        self._driver.execute_script(self._new_tab_id)

    def _switch_to_tab(self, tab_number:int):
        self._driver.switch_to.window(self._driver.window_handles[tab_number])

    def _tab_manager(self):
        pass

    def _login(self):
        print("Logging in...")
        username_field = self._driver.find_element(By.ID, self._username_id)
        username_field.send_keys(self.__username)
        time.sleep(1)
        username_field.send_keys(Keys.RETURN)
        time.sleep(2)
        password_field = self._driver.find_element(By.NAME, self._password_id)
        password_field.send_keys(self.__password)
        password_field.send_keys(Keys.RETURN)
        time.sleep(2)
        print("We are in!")

    @property
    def query(self):
        return self._query

    @query.setter
    def query(self, value):
        self._query = value
        self._company_name = self._query["company_name"]
        self._parameter = self._query["parameter"]
        self._start_date_str = self._query["start_date"]
        self._end_date_str = self._query["end_date"]
        self._interval = self._query["interval"]

    @property
    def output(self):
        return self._output

    def _write_sheet_name(self):
        self._sheet_name = "_".join([self._company_name, self._parameter, self._start_date_str[5:-1],
                                    self._end_date_str[5:-1], self._interval,
                                     str(datetime.datetime.now()).replace(" ", "_").replace(".", "_").replace(":", "_")
                                     ]).lower()
        self._sheet_name = self._sheet_name.replace(",", "_")
        sheet_name_button = self._driver.find_element(By.CLASS_NAME, self._sheet_title_id)
        sheet_name_button.click()
        sheet_name_button.send_keys(Keys.COMMAND + "A")
        sheet_name_button.send_keys(Keys.BACKSPACE)
        sheet_name_button.send_keys(self._sheet_name)

    def _download_csv(self):
        file_menu = self._driver.find_element(By.ID, self._file_menu_id)
        file_menu.click()
        download_option = self._driver.find_element(By.XPATH, self._download_option_id)
        download_option.click()
        csv_option = self._driver.find_element(By.XPATH, self._csv_option_id)
        csv_option.click()

    def _move_downloaded_file(self, extension=".csv"):
        search_path = f"{self._source_dir}/{self._sheet_name} - Sheet1{extension}"
        files = glob.glob(search_path)
        latest_file = max(files, key=os.path.getctime)
        shutil.move(f"{latest_file}", self._destination_dir)


    def execute_query(self):
        # start_date_str = "DATE(" + start_date.strftime("%Y,%m,%d") + ")"
        # end_date_str = "DATE(" + end_date.strftime("%Y,%m,%d") + ")"
        self._write_sheet_name()

        query = f'''=GOOGLEFINANCE("NASDAQ:{self._company_name}", "{self._parameter}", {self._start_date_str}, {self._end_date_str}, "{self._interval}")'''

        input_box = self._driver.find_element(By.CLASS_NAME, self._input_box_id)
        cell = input_box.find_element(By.ID, self._cell_id)
        cell.send_keys(query)
        time.sleep(2)
        cell.send_keys(Keys.ENTER)
        time.sleep(7)
        cell.send_keys(Keys.ARROW_UP)

        self._download_csv()
        time.sleep(3)
        self._move_downloaded_file()

    def deploy(self):
        self._launch()
        self._login()

google_finance = GoogleFinance()
google_finance.deploy()

@app.route("/get_response", methods=["POST"])
def get_response():
    query = request.json
    google_finance.query = query["query"]
    google_finance.execute_query()
    return {"output": google_finance.output}

if __name__ == "__main__":
    app.run(debug=False)
