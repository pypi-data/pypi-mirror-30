class Tick:
    def __init__(self, data):
        self.ticker = data["ticker"]
        self.price = data["price"]
        self.quantity = data["quantity"]
        self.time = data["time"]

    def __str__(self):
        return "{ticker: " + str(self.ticker) + ", price: " + str(self.price) + ", quantity: " + str(self.quantity) + ", time: " + str(self.time) + "}"

    __repr__ = __str__

