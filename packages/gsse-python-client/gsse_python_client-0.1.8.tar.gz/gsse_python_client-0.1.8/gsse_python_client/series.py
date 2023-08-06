from tick import Tick

class Series:
    def __init__(self, data):
        self.ticker = data["ticker"]

        self.ticks = []
        for tick in data["ticks"]:
            self.ticks.append(Tick(tick))

    def getTick(self, tickIndex):
        return self.ticks[tickIndex]