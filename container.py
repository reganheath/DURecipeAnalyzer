import json

class Container(object):
    def __init__(self, id, name):
        self.id = id
        self.name = name
        self.producers = {}
        self.consumers = {}

    def max_input_reached(self):
        return len(self.producers) == 10

    def max_output_reached(self):
        return len(self.consumers) == 10

    def produce(self, name, id, item_amount):
        if self.max_input_reached():
            raise Exception("Cannot add producer, max input reached")
        producer = self.producers.get(name, None)
        if not producer:
            producer = {
                "name": name,
                "id": id,
                "items": []
            }
            self.producers[name] = producer
        producer['items'].append(item_amount)

    def consume(self, name, id, item_amount):
        if self.max_output_reached():
            raise Exception("Cannot add consumer, max output reached")
        consumer = self.consumers.get(name, None)
        if not consumer:
            consumer = {
                "name": name,
                "id": id,
                "items": []
            }
            self.consumers[name] = consumer
        consumer['items'].append(item_amount)

    def supply(self):
        if any(filter(lambda x: x['amount'] == -1, self.producers)):
            return -1
        return sum(map(lambda x: x['amount'], self.producers))

    def demand(self):
        return sum(map(lambda x: x['amount'], self.consumers))