import requests


class QA:
    def __init__(self, host, port):
        self.qa_host = host + ':'
        self.qa_port = port
        self.qa_url = 'http://' + self.qa_host + self.qa_port

    def getProbabilityOfCandidate(self, question, candidate):
        end_point = '/qa/'
        qa_url = self.qa_url + end_point

        data = {
            'question': question,
            'candidate': candidate
        }

        response = requests.post(qa_url, data=data)

        return response.json()
