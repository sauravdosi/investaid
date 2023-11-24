import time
from selenium.webdriver.common.by import By
import undetected_chromedriver as uc
from configparser import ConfigParser
from flask import Flask, request
import progressbar
from itertools import cycle

app = Flask("app")

class ChatGPT:
    def __init__(self):
        self._tabs = []
        self._prompt = []
        self._output = ""
        self._driver = None
        self._config = ConfigParser()
        self._config.read(["./config/chatgpt.ini"])
        self.__username = self._config.get("CREDENTIALS", "username")
        self.__password = self._config.get("CREDENTIALS", "password")

        self._chromedriver_path = self._config.get("RESOURCES", "chromedriver_path")

        self._service_url = self._config.get("SERVICE", "url")

        self._login_button_id = self._config.get("WEB_IDENTIFIERS", "login_button")
        self._username_id = self._config.get("WEB_IDENTIFIERS", "username")
        self._username_continue_button_id = self._config.get("WEB_IDENTIFIERS", "username_continue_button")
        self._password_id = self._config.get("WEB_IDENTIFIERS", "password")
        self._password_continue_button_id = self._config.get("WEB_IDENTIFIERS", "password_continue_button")
        self._popup_id = self._config.get("WEB_IDENTIFIERS", "popup")
        self._prompt_id = self._config.get("WEB_IDENTIFIERS", "prompt")
        self._prompt_send_id = self._config.get("WEB_IDENTIFIERS", "prompt_send")
        self._output_id = self._config.get("WEB_IDENTIFIERS", "output")
        self._regenerate_id = self._config.get("WEB_IDENTIFIERS", "regenerate")
        self._new_tab_id = self._config.get("WEB_IDENTIFIERS", "new_tab")

        self._conversation_counter = {}
        self._first_query_flags = {}

        self._tab_count = int(self._config.get("SERVICE", "tab_count"))

        for i in range(self._tab_count):
            self._conversation_counter.update({f"tab{i}": 3})
            self._first_query_flags.update({f"tab{i}": True})

        self._tabs = [i for i in range(0, self._tab_count)]

        self._tab_queries = []
        self._window_queries = []
        self._output_dict = {}

    def _launch(self):
        print(f"Launching the {self.__class__.__name__} service...")
        self._driver = uc.Chrome(executable_path=self._chromedriver_path)
        self._driver.get(self._service_url)
        print("Launched!")

    def _new_tab(self):
        self._driver.switch_to.new_window('tab')

    def _switch_to_tab(self, tab_number:int):
        self._driver.switch_to.window(self._driver.window_handles[tab_number])

    def _launch_tabs(self):
        for i in range(1, self._tab_count):
            self._new_tab()
            self._driver.get(self._service_url)

    def _is_tab_free(self):
        try:
            self._driver.find_element(By.XPATH, "//button[@data-testid='send-button']")
            return True

        except Exception as e:
            return False

    def handle_multiple_queries(self):
        self._tab_queries = self._prompt
        self._tab_handler()

    def _tab_handler(self):

        for tab_number in cycle(self._tabs):
            self._switch_to_tab(tab_number)
            if self._is_tab_free():
                if not self._first_query_flags[f"tab{tab_number}"]:
                    output = self._driver.find_element(By.XPATH,
                                                       self._output_id.format(
                                                           self._conversation_counter[f"tab{tab_number}"]))
                    self._output_dict[self._tab_queries[0]] = output.text


                if not self._tab_queries:
                    break

                self._send_prompt(self._tab_queries[0])
                self._output_dict[self._tab_queries[0]] = ""
                self._tab_queries.pop(0)
                self._first_query_flags[f"tab{tab_number}"] = False


    def _windows_handler(self):
        pass


    def _login(self):
        print("Logging in...")
        login_button = self._driver.find_element(By.CSS_SELECTOR, self._login_button_id)
        login_button.click()
        time.sleep(1)
        username_field = self._driver.find_element(By.ID, self._username_id)
        username_field.send_keys(self.__username)
        username_continue_button = self._driver.find_element(By.NAME, self._username_continue_button_id)
        username_continue_button.click()

        password_field = self._driver.find_element(By.NAME, self._password_id)
        password_field.send_keys(self.__password)

        time.sleep(1)

        password_continue_button = self._driver.find_element(By.CLASS_NAME, self._password_continue_button_id)
        password_continue_button.click()
        print("We are in!")

        time.sleep(2)

        try:
            popup_button = self._driver.find_element(By.XPATH, self._popup_id)
            popup_button.click()
        except Exception as e:
            print(f"Handled exception {e}")
        print("Pop-up cleared, ready to generate!")

    @property
    def prompt(self):
        return self._prompt

    @prompt.setter
    def prompt(self, value):
        self._prompt = value

    @property
    def output(self):
        return self._output

    def _send_prompt(self, prompt):
        prompt_field = self._driver.find_element(By.ID, self._prompt_id)
        prompt_field.send_keys(prompt)
        prompt_send_button = self._driver.find_element(By.CSS_SELECTOR, self._prompt_send_id)
        prompt_send_button.click()

    def execute_query(self):
        self._send_prompt(self._prompt[0])

        wait_for_output = True

        # Create an indeterminate progress bar
        bar = progressbar.ProgressBar(max_value=progressbar.UnknownLength)

        # Check if the send button is available
        while wait_for_output:
            try:
                self._driver.find_element(By.XPATH, "//button[@data-testid='send-button']")
                print("\nOutput generated!")
                break
            except Exception as e:
                time.sleep(0.1)
                bar.update(bar.value + 1)

        output = self._driver.find_element(By.XPATH, self._output_id.format(self._conversation_counter["tab1"]))
        self._output = output.text

        self._conversation_counter["tab1"] += 2

    def deploy(self):
        self._launch()
        self._login()
        self._launch_tabs()

chatgpt = ChatGPT()
chatgpt.deploy()

@app.route("/get_response", methods=["POST"])
def get_response():
    prompt = request.form.getlist('prompt')
    chatgpt.prompt = prompt
    chatgpt.handle_multiple_queries()
    return {"output": chatgpt._output_dict}

if __name__ == "__main__":
    app.run(debug=False)
