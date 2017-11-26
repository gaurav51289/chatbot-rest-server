from .Categorizer import Categorizer
from .QA import QA

categorizer = Categorizer('localhost', '5001')
qa = QA('localhost', '5002')

def getCategories(question):
    return (categorizer.getCategories(question))['categories']

def getProbabilityOfCandidate(question, candidate):
    return qa.getProbabilityOfCandidate(question, candidate)

