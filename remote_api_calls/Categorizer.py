import requests


class Categorizer:
    def __init__(self, host, port):
        self.categorizer_host = host + ':'
        self.categorizer_port = port
        self.categorizer_url = 'http://' + self.categorizer_host + self.categorizer_port

    def getCategories(self, question):
        end_point = '/categorize/'
        categorizer_url = self.categorizer_url + end_point

        data = {'question': question}

        response = requests.post(categorizer_url, data=data)

        return response.json()
