import requests
import json

from timewindow import TimeWindows

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

    def requestTimeAdvance(self, duration, returnRawJSON=False):
        r = self.session.get(self.buildBaseUrl() + "/requestTimeAdvance", params= {"duration": duration})
        json = r.json()
        if returnRawJSON:
            return json
        return TimeWindows(json)

    def setDay(self, day):
        r = self.session.get(self.buildBaseUrl() + "/set/day", params = {"day": day})
        return r.status_code

    def createTestSet(self, testSet):
        r = self.session.post(self.buildBaseUrl() + "/create/testSet", json = testSet)
        return r.status_code

    def wallet(self):
        r = self.session.get(self.buildBaseUrl() + "/wallet")
        return r.json()

    def buy(self, ticker, amount, price, walletPercentage, priceLeeway):
        r = self.session.get(self.buildBaseUrl() + "/buy", params = {"ticker": ticker, "amount": amount, "pricePerStock": price, "walletPercentage": walletPercentage, "priceLeeway": priceLeeway})
        return r.text

    def sell(self, ticker, amount, price, stockPercentage, priceLeeway):
        r = self.session.get(self.buildBaseUrl() + "/sell", params = {"ticker": ticker, "amount": amount, "pricePerStock": price, "stockPercentage": stockPercentage, "priceLeeway": priceLeeway})
        return r.status_code

    def getSettings(self):
        r = self.session.get(self.buildBaseUrl() + "/get/settings")
        return r.json()

    def setSettings(self, settings):
        print("Settings", settings)
        r = self.session.get(self.buildBaseUrl() + "/set/settings", params = {"settings": json.dumps(settings)})
        return r.json()



    def startTestSet(self):
        r = self.session.get(self.buildBaseUrl() + "/start/testSet")
        return r.status_code
