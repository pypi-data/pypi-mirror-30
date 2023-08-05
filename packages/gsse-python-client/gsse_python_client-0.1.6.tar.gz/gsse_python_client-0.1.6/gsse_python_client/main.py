from client import Client
import json

client = Client()
client.setExchange("OSE")


testSet = {
    "testSet": [
        {
            "fromTime": "20180122",
            "toTime": "20180123",
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
for i in range(0, 58):
    data = client.requestTimeAdvance(3600);
    window = data[0]
    if len(window) > 1:
        print(i, window[1])
    else:
        print(i, window[0])

#client = Client()
#client.setExchange("OSE")
#client.setDay("20180122")
#client.addStock("DNB")
#for i in range(0, 48):
#    print(i, client.requestTimeAdvance(3600))


