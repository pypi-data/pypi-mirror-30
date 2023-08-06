import sys
import json
from BaseTest import BaseTest
import os
import unittest


class Suite:

    suite_data = object
    base_path = ''
    result = {}

    def load_data(self, json_file: str):
        with open(json_file) as json_data:
            json_text = json_data.read()
            return json.loads(json_text)

    def run_suite(self, json_file, verbose=1):

        self.base_path = os.path.dirname(os.path.abspath(json_file)) + "\\"
        self.suite_data = self.load_data(json_file)

        self.result["suite_name"] = self.suite_data["name"]
        self.result["start"] = "empezo a las 3:40"

        test_suite = unittest.TestSuite()

        self.result["tests"] = []

        result = False

        try:
            for test in self.suite_data["tests"]:
                test_suite.addTest(
                    BaseTest(
                        "run_test",
                        self.base_path + test["json_file"],
                        self.suite_data,
                        self.base_path,
                        self.result["tests"]
                    )
                )

                unittest.TextTestRunner(verbosity=2).run(test_suite)

                result = True
        except Exception as e:
            self.result["message"] = "{0}".format(e)

        finally:
            self.result["result"] = str(result).lower()

        self.result["end"] = "acabo a las 5:60"

        if verbose == 1:
            print(json.dumps(self.result))
        # with open('result.res', 'w') as outfile:
        #    json.dump(self.result, outfile)


if __name__ == "__main__":
    # print('Argument List:', str(sys.argv))
    Suite().run_suite(sys.argv[1], int(sys.argv[2]))

