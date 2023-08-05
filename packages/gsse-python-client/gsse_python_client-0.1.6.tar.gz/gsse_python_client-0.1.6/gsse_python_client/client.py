import requests

class Client:
    def __init__(self):
        self.session = requests.session()
        self.protocol = "http"
        self.host = "localhost"
        self.port = "8000"
        return

    def setHost(self, host):
        self.host = host

    def setPort(self, port):
        self.port = port

    def setProtocol(self, protocol):
        self.protocol = protocol

    def buildBaseUrl(self):
        return self.protocol + "://" + self.host + ":" + self.port

    def addStock(self, ticker):
        self.session.get(self.buildBaseUrl() + "/add/stock", params = {"ticker": ticker})

    def setExchange(self, exchange):
        self.session.get(self.buildBaseUrl() + "/set/exchange", params = {"exchange": exchange})

    def requestTimeAdvance(self, duration):
        r = self.session.get(self.buildBaseUrl() + "/requestTimeAdvance", params= {"duration": duration})
        return r.json()

    def setDay(self, day):
        r = self.session.get(self.buildBaseUrl() + "/set/day", params = {"day": day})
        return r.status_code

    def createTestSet(self, testSet):
        r = self.session.post(self.buildBaseUrl() + "/create/testSet", json = testSet)
        return r.status_code

    def startTestSet(self):
        r = self.session.get(self.buildBaseUrl() + "/start/testSet")
        return r.status_code
