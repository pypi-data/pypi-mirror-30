from series import Series

class TimeWindows:
    def __init__(self, timewindows):
        self.timewindows = []
        for timewindow in timewindows:
            self.timewindows.append(TimeWindow(timewindow))

    def __getitem__(self, item):
        return self.timewindows[item]

    def __setitem__(self, key, value):
        self.timewindows[key] = value

class TimeWindow:
    def __init__(self, data):
        self.series = {}
        for element in data:
            series = Series(element)
            self.series[series.ticker] = series

    def getTick(self, ticker, tickIndex):
        series = self.series[ticker]
        return series.getTick(tickIndex)

