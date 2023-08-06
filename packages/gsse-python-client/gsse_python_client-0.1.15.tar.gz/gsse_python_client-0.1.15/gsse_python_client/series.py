from gsse_python_client.tick import Tick

class Series:
    def __init__(self, data):
        self.ticker = data["ticker"]

        self.ticks = []
        for tick in data["ticks"]:
            self.ticks.append(Tick(tick))

    def __getitem__(self, item):
        return self.ticks[item]

    def __len__(self):
        return len(self.ticks)