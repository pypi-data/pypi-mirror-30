from client import Client
from testSet import TestSet
import json
import time

client = Client()

testSet = {"testSet": [
    TestSet(stocks=["DNB"], fromTime="20180122", toTime="20180125", exchange="OSE").toJSON(),
    TestSet(stocks=["DNB", "AKER", "AFG"], fromTime="20180122", toTime="20180125", exchange="OSE").toJSON(),
]}
print("Testset: ", testSet);
"""testSet = {
    "testSet": [
        {
            "fromTime": "20180122",
            "toTime": "20180125",
            "tickers": ["DNB"],
            "exchange":"OSE"
        },
        {
            "fromTime": "20180122",
            "toTime": "20180125",
            "tickers": ["DNB", "AKER", "AFG"]
            "exchange":"OSE"
        }
    ]
}"""

print(testSet)
client.createTestSet(testSet)
client.startTestSet()

client.setSettings({
    "startingCapital": 100000,
    "resolution": 60
})

for i in range(0, 10):
    timewindows = client.requestTimeAdvance(3600)
    timewindow = timewindows[-1]
    try:
        print("Tick: ", timewindow.getTick("DNB", -1))
    except:
        pass

print("Wallet: ", client.wallet())
client.buy("DNB", 1000, 153.5, None, 0.05)
print("Wallet: ", client.wallet())

for i in range(0, 50):
    timewindows = client.requestTimeAdvance(3600)
    timewindow = timewindows[-1]
    try:
        print("Tick: ", timewindow.getTick("DNB", -1))
    except:
        pass
    print("Wallet: ", client.wallet())

print("Trying to sell DNB position")

status = client.sell("DNB", None, 153.5, 1, 0.05)
print(status)
time.sleep(1)
for i in range(0, 3600*50):
    timewindows = client.requestTimeAdvance(3600, True)
    print(timewindows)
    print(i, "Wallet: ", client.wallet())
print("Finished")



#for i in range(0, 58):
#    data = client.requestTimeAdvance(3600);
#    print("Data: ", data)
#    continue
#    window = data[0]
#    if len(window) > 1:
#        print(i, window[1])
#    else:
#        print(i, window[0])

#client = Client()
#client.setExchange("OSE")
#client.setDay("20180122")
#client.addStock("DNB")
#for i in range(0, 48):
#    print(i, client.requestTimeAdvance(3600))


