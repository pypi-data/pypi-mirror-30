from selenium.common.exceptions import NoSuchElementException
from MSDBConnect import MSDBConnect
import time
import unittest
import json


class Action(unittest.TestCase):
    browser = None
    last_query_results = None

    def __init__(self, _browser):
        self.browser = _browser

    def start(self, url):
        self.browser.get(url)
        self.browser.maximize_window()
        # self.browser.set_window_size(2048, 1536)

    def load_data(self, json_file):
        with open(json_file) as json_data:
            json_text = json_data.read()
            return json.loads(json_text)

    def execute_step(self, step):

        if "selector" in step:
            try:
                element = self.browser.find_element_by_xpath(step["selector"])
            except NoSuchElementException:
                raise Exception("No such elemen in step ref: " + step["selector"])

        action = 'none'
        if "action" in step:
            action = step["action"]
        if action == "click":
            element.click()
        elif action == "set":
            element.send_keys(step["value"])
        elif action == 'wait':
            time.sleep(int(step["value"]))
        elif action == 'assert':
            self.assertEqual(element.text, step["value"])
        elif action == 'assert_contains':
            self.assertTrue(element.text.find(step["value"]) != -1)
        elif action == 'start':
            self.start(step["value"])
        elif action == 'script':
            self.browser.execute_script(step["value"], element)
        elif action == 'navigate':
            self.browser.get(step["value"])
        elif action == 'execute_on_db':
            db = MSDBConnect()
            db.connect(self.load_data(step["connect_info"]))
            self.last_query_results = db.execute(step["value"])
            db.disconnect()
        elif action == 'asert_on_db_result':
            self.assertEqual(self.last_query_results[int(step["row"])][int(step["column"])], step["value"])
