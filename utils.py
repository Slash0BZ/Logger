import requests
import json


class CogCompLoggerClient:
    def __init__(self, demo_name, base_url="http://127.0.0.1:5000"):
        self.demo_name = demo_name
        self.base_url = base_url
        if self.base_url.endswith("/"):
            self.url = self.base_url + "log"
        else:
            self.url = self.base_url + "/log"

    def log(self, content=""):
        params = {
            'entry_name': self.demo_name,
            'content': content
        }
        result = requests.post(url=self.url, params=params).json()
        if result['result'] == 'SUCCESS':
            return True
        return False

    def log_dict(self, d=None):
        if d is None:
            return self.log()
        else:
            return self.log(content=json.dumps(d))


if __name__ == "__main__":
    client = CogCompLoggerClient("zoe")
    for i in range(0, 100):
        client.log(str(i))
