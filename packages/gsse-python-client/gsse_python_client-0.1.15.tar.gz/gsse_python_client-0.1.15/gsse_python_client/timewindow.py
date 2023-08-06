from gsse_python_client.series import Series
import numbers

class TimeWindows:
    def __init__(self, timewindows):
        self.timewindows = []
        for timewindow in timewindows:
            self.timewindows.append(TimeWindow(timewindow))

    def __getitem__(self, item):
        return self.timewindows[item]

    def __setitem__(self, key, value):
        self.timewindows[key] = value

    def __len__(self):
        return len(self.timewindows)

    def __iter__(self):
        for elem in self.timewindows:
            yield elem

class TimeWindow:
    def __init__(self, data):
        self.series = {}
        self.tickers = []
        for element in data:
            series = Series(element)
            self.series[series.ticker] = series
            self.tickers.append(series.ticker)

    def getTick(self, ticker, tickIndex):
        series = self.series[ticker]
        return series.getTick(tickIndex)

    def __getitem__(self, item):
        if isinstance(item, numbers.Number):
            return self.series[self.tickers[item]]
        return self.series[item]

    def __len__(self):
        return len(self.series)

