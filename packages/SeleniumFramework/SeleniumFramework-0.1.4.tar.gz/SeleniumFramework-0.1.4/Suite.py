import sys
import json
from BaseTest import BaseTest


class Suite:

    suite_data = object

    def load_data(self, json_file: str):
        with open(json_file) as json_data:
            json_text = json_data.read()
            return json.loads(json_text)

    def run_suite(self, json_file):
        import unittest
        self.suite_data = self.load_data(json_file)

        test_suite = unittest.TestSuite()

        print('{ "tests":[')
        for test in self.suite_data["tests"]:
            test_suite.addTest(BaseTest("run_test", test["json_file"], self.suite_data))

        unittest.TextTestRunner(verbosity=2).run(test_suite)

        print(']}')


if __name__ == "__main__":
    # print('Argument List:', str(sys.argv))
    Suite().run_suite(sys.argv[2])

