
class TestSet:
    def __init__(self, stocks=[], fromTime="", toTime=""):
        self.tickers = stocks
        self.fromTime = fromTime
        self.toTime = toTime

    def addStock(self, ticker):
        self.tickers.append(ticker)

    def removeStock(self, ticker):
        self.tickers.remove(ticker)

    def getStocks(self):
        return self.tickers

    def setFromTime(self, fromTime):
        self.fromTime = fromTime

    def setToTime(self, toTime):
        self.toTime = toTime

    def getFromTime(self):
        return self.fromTime

    def getToTime(self):
        return self.toTime

    def toJSON(self):
        obj = {}
        obj["tickers"] = self.getStocks()
        obj["fromTime"] = self.getFromTime()
        obj["toTime"] = self.getToTime()
        return obj


