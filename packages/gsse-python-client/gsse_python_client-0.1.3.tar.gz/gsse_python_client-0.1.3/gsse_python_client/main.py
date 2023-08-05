from client import Client

client = Client()
client.setExchange("OSE")
client.setDay("20180122")
client.addStock("DNB")
for i in range(0, 48):
    print(i, client.requestTimeAdvance(3600))


