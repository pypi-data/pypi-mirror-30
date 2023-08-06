from client import Client
from testSet import TestSet
import time


def single():
    client = Client()
    testSet = {"testSet": [
        TestSet(stocks=["DNB"], fromTime="20180122", toTime="20180125", exchange="OSE").toJSON(),
        TestSet(stocks=["DNB", "AKER", "AFG"], fromTime="20180122", toTime="20180125", exchange="OSE").toJSON(),
    ]}

    client.createTestSet(testSet)
    client.startTestSet()
    start_time = time.time()
    client.setSettings({
        "startingCapital": 100000,
        "resolution": 60
    })
    return time.time() - start_time

def multiple():
    clients = []
    n_clients = 10

    for i in range(n_clients):
        client = Client()
        testSet = {"testSet": [
            TestSet(stocks=["DNB"], fromTime="20180122", toTime="20180125", exchange="OSE").toJSON(),
            TestSet(stocks=["DNB", "AKER", "AFG"], fromTime="20180122", toTime="20180125", exchange="OSE").toJSON(),
        ]}

        client.createTestSet(testSet)
        client.startTestSet()
        clients.append(client)

    start_time = time.time()
    for i in range(n_clients):
        client = clients[i]
        client.setSettings({
            "startingCapital": 100000,
            "resolution": 60
        })
    for i in range(n_clients):
        client = clients[i]
        print(client.getSettings())
    return time.time() - start_time

print("Single time: ", single())
print("Multiple time: ", multiple())



