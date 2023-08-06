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
    base_path = ""
    tests_info = None

    def __init__(self, test_name, json_file, suite_data, base_path, tests_info):
        super(BaseTest, self).__init__(
            test_name)
        self.json_file = json_file
        self.suite_data = suite_data
        self.base_path = base_path
        self.tests_info = tests_info
        self.info = {}

    def load_data(self):
        with open(self.json_file) as json_data:
            json_text = json_data.read()
            return json.loads(json_text)

    def setUp(self):
        self.test_data = self.load_data()
        self.info["test_name"] = self.test_data["name"]
        self.info["json_file"] = os.path.basename(self.json_file)

        self.info["start"] = "45:06"
        # self.tests_info.append({"df": "sd"})
        # chrome_options = webdriver.ChromeOptions()
        # if "RUN_HEADLESS" in os.environ:
        #    chrome_options.add_argument("--headless")
        #    chrome_options.add_argument('--disable-extensions')
        #    chrome_options.add_argument('--disable-gpu')
        #    chrome_options.add_argument('--no-sandbox')
        # else:
        #   chrome_options.add_argument('--disable-extensions')
        if "browser" in self.test_data:
            browser = self.test_data["browser"]
            if browser == "chrome":
                self.d = webdriver.Chrome()
            elif browser == "edge":
                self.d = webdriver.Edge()
            elif browser == "firefox":
                self.d = webdriver.Firefox(executable_path=os.path.dirname(os.path.abspath(__file__))
                                           + '\\geckodriver.exe')
        else:
            self.d = webdriver.Chrome()

        if "implicitly_wait" in self.test_data:
            self.d.implicitly_wait(int(self.test_data["implicitly_wait"]))
        else:
            self.d.implicitly_wait(3)

        self.d.get("data:text/html;charset=utf-8,<div>executing test " + self.test_data["name"] + "...</div>")
        self.d.maximize_window()

    def run_test(self):

        if self.execute_start_flow:
            self.execute_flow(self.suite_data["started_flow"])

        result = False

        try:
            self.execute_flow(self.test_data["flow"])
            result = True
        except Exception as e:
            self.info["message"] = str(e)
        finally:
            self.d.quit()
            self.info["result"] = str(result).lower()
            self.tests_info.append(self.info)

    def execute_flow(self, flow):
        action = Action(self.d, self.base_path)
        for step in flow:
            action.execute_step(step)
