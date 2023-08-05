import requests

class Client:
    def __init__(self):
        self.session = requests.session()
        return

    def addStock(self, ticker):
        self.session.get("http://localhost:8000/add/stock", params = {"ticker": ticker})

    def setExchange(self, exchange):
        self.session.get("http://localhost:8000/set/exchange", params = {"exchange": exchange})

    def requestTimeAdvance(self, duration):
        r = self.session.get("http://localhost:8000/requestTimeAdvance", params= {"duration": duration})
        return r.json()

    def setDay(self, day):
        r = self.session.get("http://localhost:8000/set/day", params = {"day": day})
        return r.status_code;

    def createTestSet(self, testSet):
        r = self.session.post("http://localhost:8000/create/testSet", json = testSet);
        return r.status_code;

    def startTestSet(self):
        r = self.session.get("http://localhost:8000/start/testSet");
        return r.status_code;
