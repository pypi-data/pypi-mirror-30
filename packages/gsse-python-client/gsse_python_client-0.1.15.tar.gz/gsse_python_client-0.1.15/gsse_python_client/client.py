import requests
from requests_futures.sessions import FuturesSession
import json

from gsse_python_client.timewindow import TimeWindows


class Client:
    def __init__(self):
        self.session = requests.session()
        self.session = FuturesSession()
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
        future = self.session.get(self.buildBaseUrl() + "/add/stock", params = {"ticker": ticker})
        r = future.result()

    def setExchange(self, exchange):
        future = self.session.get(self.buildBaseUrl() + "/set/exchange", params = {"exchange": exchange})
        r = future.result()

    def requestTimeAdvance(self, duration, returnRawJSON=False):
        future = self.session.get(self.buildBaseUrl() + "/requestTimeAdvance", params= {"duration": duration})
        r = future.result()
        json = r.json()
        if returnRawJSON:
            return json, r.status_code
        return TimeWindows(json), r.status_code

    def setDay(self, day):
        future = self.session.get(self.buildBaseUrl() + "/set/day", params = {"day": day})
        r = future.result()
        return r.status_code

    def createTestSet(self, testSet):
        future = self.session.post(self.buildBaseUrl() + "/create/testSet", json = testSet)
        r = future.result()
        return r.status_code

    def wallet(self):
        future = self.session.get(self.buildBaseUrl() + "/wallet")
        r = future.result()
        return r.json(), r.status_code

    def buy(self, ticker, amount, price, walletPercentage, priceLeeway):
        future = self.session.get(self.buildBaseUrl() + "/buy", params = {"ticker": ticker, "amount": amount, "pricePerStock": price, "walletPercentage": walletPercentage, "priceLeeway": priceLeeway})
        r = future.result()
        return r.text, r.status_code

    def sell(self, ticker, amount, price, stockPercentage, priceLeeway):
        future = self.session.get(self.buildBaseUrl() + "/sell", params = {"ticker": ticker, "amount": amount, "pricePerStock": price, "stockPercentage": stockPercentage, "priceLeeway": priceLeeway})
        r = future.result()
        return r.status_code

    def getSettings(self):
        future = self.session.get(self.buildBaseUrl() + "/get/settings")
        r = future.result()
        return r.json(), r.status_code

    def setSettings(self, settings):
        future = self.session.get(self.buildBaseUrl() + "/set/settings", params = {"settings": json.dumps(settings)})
        r = future.result()
        return r.json(), r.status_code

    def startTestSet(self):
        future = self.session.get(self.buildBaseUrl() + "/start/testSet")
        r = future.result()
        return r.status_code, r.status_code
