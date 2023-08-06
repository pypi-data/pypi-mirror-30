from client import Client
import json
import time

client = Client()
client.setExchange("OSE")


testSet = {
    "testSet": [
        {
            "fromTime": "20180122",
            "toTime": "20180125",
            "tickers": ["DNB"]
        },
        {
            "fromTime": "20180122",
            "toTime": "20180125",
            "tickers": ["DNB", "AKER", "AFG"]
        }
    ]
}
print(testSet)
client.createTestSet(testSet)
client.startTestSet()
print("Settings: ", client.getSettings())
client.setSettings({
    "startingCapital": 1000
})
print("Settings: ", client.getSettings())

for i in range(0, 10):
    data = client.requestTimeAdvance(3600)
    print("Data: ", data)

print("Wallet: ", client.wallet())
client.buy("DNB", None, 153.5, 0.5, 0.05)
print("Wallet: ", client.wallet())

for i in range(0, 50):
    data = client.requestTimeAdvance(3600)
    print(data)
    print("Wallet: ", client.wallet())

print("Trying to sell DNB position")

status = client.sell("DNB", None, 153.5, 0.5, 0.05)
print(status)
time.sleep(5)
for i in range(0, 50):
    data = client.requestTimeAdvance(3600)
    print(data)
    print("Wallet: ", client.wallet())




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


