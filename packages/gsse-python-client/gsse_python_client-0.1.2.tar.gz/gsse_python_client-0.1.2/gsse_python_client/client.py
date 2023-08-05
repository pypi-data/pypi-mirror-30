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
        r = self.session.get("http://localhost:8000/requestTimeAdvance", params={"duration": duration})
        return r.json()
