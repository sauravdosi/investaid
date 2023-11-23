import ast
import time
from selenium.webdriver import Keys, ActionChains
from selenium.webdriver.common.by import By
import undetected_chromedriver as uc
from configparser import ConfigParser
import progressbar
from flask import Flask, request
from datetime import date

app = Flask("app")


class GoogleFinance:
    def __init__(self):
        # self._tabs = []
        self._query = ""
        self._output = ""
        self._driver = None
        self._config = ConfigParser()
        self._config.read(["./config/google_finance.ini"])
        self.__username = self._config.get("CREDENTIALS", "username")
        self.__password = self._config.get("CREDENTIALS", "password")

        self._chromedriver_path = self._config.get("RESOURCES", "chromedriver_path")

        self._service_url = self._config.get("SERVICE", "url")

        self._username_id = self._config.get("WEB_IDENTIFIERS", "username")
        self._password_id = self._config.get("WEB_IDENTIFIERS", "password")
        self._input_box_id = self._config.get("WEB_IDENTIFIERS", "input_box")
        self._cell_id = self._config.get("WEB_IDENTIFIERS", "cell")
        self._file_menu = self._config.get("WEB_IDENTIFIERS", "file_menu")
        self._new_tab_id = self._config.get("WEB_IDENTIFIERS", "new_tab")

        self._company_name = ""
        self._parameter = ""
        self._start_date_str = ""
        self._end_date_str = ""
        self._interval = ""

        # self._conversation_counter = {"tab1": 3}

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
        # login_button.click()
        password_field = self._driver.find_element(By.NAME, self._password_id)
        password_field.send_keys(self.__password)
        password_field.send_keys(Keys.RETURN)
        time.sleep(2)

        # username_field = self._driver.find_element(By.ID, self._username_id)
        # username_field.send_keys(self.__username)
        # username_continue_button = self._driver.find_element(By.NAME, self._username_continue_button_id)
        # username_continue_button.click()
        #
        # password_field = self._driver.find_element(By.NAME, self._password_id)
        # password_field.send_keys(self.__password)
        #
        # time.sleep(1)
        #
        # password_continue_button = self._driver.find_element(By.CLASS_NAME, self._password_continue_button_id)
        # password_continue_button.click()
        print("We are in!")

        # time.sleep(2)
        #
        # try:
        #     popup_button = self._driver.find_element(By.XPATH, self._popup_id)
        #     popup_button.click()
        # except Exception as e:
        #     print(f"Handled exception {e}")
        # print("Pop-up cleared, ready to generate!")

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
        self._sheet_name = "_".join([self._company_name, self._parameter, self._start_date_str[5:-2],
                                    self._end_date_str[5:-2], self._interval]).lower()
        sheet_name_button = self._driver.find_element((By.CLASS_NAME, 'docs-title-input'))
        sheet_name_button.click()
        sheet_name_button.send_keys(self._sheet_name)

    def _download_csv(self):
        file_menu = self._driver.find_element(By.ID, self._file_menu)
        file_menu.click()
        # menu_locator = self._driver.find_element(By.CLASS_NAME, 'goog-menu')
        download_option = self._driver.find_element(By.XPATH, "//span[@aria-label='Download d']")
        download_option.click()
        csv_option = self._driver.find_element(By.XPATH, "//span[@aria-label='Comma Separated Values (.csv) c']")
        csv_option.click()
        # time.sleep(2)

    def execute_query(self):
        # start_date_str = "DATE(" + start_date.strftime("%Y,%m,%d") + ")"
        # end_date_str = "DATE(" + end_date.strftime("%Y,%m,%d") + ")"
        self._write_sheet_name()

        query = f'''=GOOGLEFINANCE("NASDAQ:{self._company_name}", 
        "{self._parameter}", {self._start_date_str}, {self._end_date_str}, "{self._interval}")'''

        input_box = self._driver.find_element(By.CLASS_NAME, self._input_box_id)
        cell = input_box.find_element(By.ID, self._cell_id)
        cell.send_keys(query)
        cell.send_keys(Keys.ENTER)
        time.sleep(3)

        self._download_csv()
        # prompt_field = self._driver.find_element(By.ID, self._prompt_id)
        # prompt_field.send_keys(self._prompt)
        # prompt_send_button = self._driver.find_element(By.CSS_SELECTOR, self._prompt_send_id)
        # prompt_send_button.click()

        # wait_for_output = True

        # Create an indeterminate progress bar
        # bar = progressbar.ProgressBar(max_value=progressbar.UnknownLength)

        # Check if the send button is available
        # while wait_for_output:
        #     try:
        #         self._driver.find_element(By.XPATH, "//button[@data-testid='send-button']")
        #         print("\nOutput generated!")
        #         break
        #     except Exception as e:
        #         time.sleep(0.1)
        #         bar.update(bar.value + 1)
        #
        # output = self._driver.find_element(By.XPATH, self._output_id.format(self._conversation_counter["tab1"]))
        # self._output = output.text
        #
        # self._conversation_counter["tab1"] += 2

    def deploy(self):
        self._launch()
        self._login()
        # self._download_csv()

google_finance = GoogleFinance()
google_finance.deploy()

@app.route("/get_response", methods=["POST"])
def get_response():
    query = request.json
    print(query)
    google_finance.query = query["query"]
    google_finance.execute_query()
    return {"output": google_finance.output}

if __name__ == "__main__":
    app.run(debug=False)

# driver = uc.Chrome(executable_path="/Users/sauravdosi/Documents/MSCS at UTD/Fall 2023/investaid/resources/chromedriver")
# driver.get("https://docs.google.com/spreadsheets/create")
#
#
# email_input = driver.find_element(By.ID, 'identifierId')
#
# # Perform actions on the input element
# email_input.send_keys('scotchmixtapesofficial@gmail.com')
# # time.sleep(1)
# email_input.send_keys(Keys.RETURN)
# time.sleep(2)
#
# password_field = driver.find_element(By.NAME, "Passwd")
# password_field.send_keys("AIisfuture@1116")
# password_field.send_keys(Keys.RETURN)
#
# time.sleep(2)
#
# input_box = driver.find_element(By.CLASS_NAME, "input-box")
#
# # Within the "input-box" div, find the nested div element by its ID "waffle-rich-text-editor"
# cell = input_box.find_element(By.ID, "waffle-rich-text-editor")
#
# # Click on the rich text editor div element to focus on it
# # cell.click()
# # cell.click()
# cell.send_keys(f'''=GOOGLEFINANCE("NASDAQ:GOOG", "price", DATE(2014,1,1), DATE(2014,12,31), "DAILY")''')
# cell.send_keys(Keys.ENTER)
# time.sleep(5)
#
# file_menu = driver.find_element(By.ID, "docs-file-menu")
# file_menu.click()
# time.sleep(2)



#
# app = Flask("app")

