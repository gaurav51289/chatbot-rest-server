from .Categorizer import Categorizer

categorizer = Categorizer('localhost', '5001')

def getCategories(question):
    return (categorizer.getCategories(question))['categories']



