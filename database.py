from tinydb import TinyDB, Query
from neural import NeuralNetwork
import json
db = TinyDB('db.json')
db.insert({'type': 'peach', 'count': 3})

for item in db:
    print(item)

Fruit = Query()
db.search(Fruit.type == 'peach')
db.search(Fruit.count > 5)

db.update({'count': 10}, Fruit.type == 'apple')


x = json.dumps(NeuralNetwork)
print(x)


# https://tinydb.readthedocs.io/en/latest/getting-started.html
