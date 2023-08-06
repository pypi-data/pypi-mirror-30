import requests
import json


class Request:

    data = object

    def __init__(self, parsm_data):
        self.data = parsm_data

    def post(self):
        response = requests.post(
            self.data["endpoint"], headers=self.data["headers"], data=json.dumps(self.data["body"]))
        return response

    def get(self):
        response = requests.get(
            self.data["endpoint"], headers=self.data["headers"], params=self.data["body"])
        return response

    def put(self):
        response = requests.put(
            self.data["endpoint"], headers=self.data["headers"], data=json.dumps(self.data["body"]))
        return response

    def delete(self):
        response = requests.delete(
            self.data["endpoint"], headers=self.data["headers"], params=self.data["body"])
        return response
