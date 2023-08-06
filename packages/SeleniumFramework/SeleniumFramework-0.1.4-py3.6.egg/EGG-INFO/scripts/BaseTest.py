import unittest
import json
import os
from selenium import webdriver
from Action import Action


class BaseTest(unittest.TestCase):
    suite_data = object
    test_data = object
    execute_start_flow = False
    json_file = ""

    def __init__(self, test_name, json_file, suite_data):
        super(BaseTest, self).__init__(
            test_name)
        self.json_file = json_file
        self.suite_data = suite_data

    def load_data(self):
        with open(self.json_file) as json_data:
            json_text = json_data.read()
            return json.loads(json_text)

    def setUp(self):
        self.test_data = self.load_data()
        # chrome_options = webdriver.ChromeOptions()
        # if "RUN_HEADLESS" in os.environ:
        #    chrome_options.add_argument("--headless")
        #    chrome_options.add_argument('--disable-extensions')
        #    chrome_options.add_argument('--disable-gpu')
        #    chrome_options.add_argument('--no-sandbox')
        # else:
        #   chrome_options.add_argument('--disable-extensions')
        self.d = webdriver.Chrome()
        self.d.implicitly_wait(5)
        self.d.get("data:text/html;charset=utf-8,<div>executing test " + self.test_data["name"] + "...</div>")
        self.d.maximize_window()

    # def start(self):
    # self.start(self.suite_data["init_url"])

    def run_test(self):

        print('{ "name":"' + self.test_data["name"] + '"')

        if self.execute_start_flow:
            self.execute_flow(self.suite_data["started_flow"])

        result = False

        try:
            self.execute_flow(self.test_data["flow"])
            result = True
        except Exception as e:
            print(', "message":"' + str(e) + '"')
        finally:
            print(', "result":' + str(result).lower() + '},')

    def execute_flow(self, flow):
        action = Action(self.d)
        for step in flow:
            action.execute_step(step)
