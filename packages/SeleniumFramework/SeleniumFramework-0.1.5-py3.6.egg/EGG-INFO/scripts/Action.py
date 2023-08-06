from selenium.common.exceptions import NoSuchElementException
from MSDBConnect import MSDBConnect
from Request import Request
import time
import unittest
import json


class Action(unittest.TestCase):
    browser = None
    last_results = None
    base_path = ""

    def __init__(self, _browser, base_path):
        self.browser = _browser
        self.base_path = base_path

    def start(self, url):
        self.browser.get(url)
        self.browser.maximize_window()
        # self.browser.set_window_size(2048, 1536)

    def load_data(self, json_file):
        with open(self.base_path + json_file) as json_data:
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
        elif action == "focus":
            element.focus()
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
        elif action == 'maximize':
            self.browser.maximize_window()
        elif action == 'execute_on_db':
            db = MSDBConnect()
            db.connect(self.load_data(step["connect_info"]))
            self.last_results = db.execute(step["value"])
            db.disconnect()
        elif action == 'asert_on_db_result':
            self.assertEqual(self.last_results[int(step["row"])][int(step["column"])], step["value"])
        elif action == 'put':
            request = Request(self.load_data(step["params"]))
            response = request.put()
            self.last_results = response.text
        elif action == 'post':
            request = Request(self.load_data(step["params"]))
            response = request.post()
            self.last_results = response.text
        elif action == 'get':
            request = Request(self.load_data(step["params"]))
            response = request.get()
            self.last_results = response.text
        elif action == 'delete':
            request = Request(self.load_data(step["params"]))
            response = request.delete()
            self.last_results = response.text

    def white_on_document(self, value):
        self.browser.execute_script("document.write('" + value + "<br />');")
