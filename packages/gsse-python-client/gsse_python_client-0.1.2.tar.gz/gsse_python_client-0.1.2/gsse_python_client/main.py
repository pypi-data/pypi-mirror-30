from client import Client

client = Client()
client.setExchange("OSE")
client.addStock("DNB")
for i in range(0, 10):
    print(i, client.requestTimeAdvance(3600))


