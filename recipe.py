import json
import os
from helpers import now_timestamp

class Recipe(object):
    def __init__(self, name, d):
        self.__dict__ = {**{'name': name, "prices": {}}, **d}

    def to_dict(self):
        d = dict(self.__dict__)
        del d['name']
        if self.prices == {}:
            del d['prices']
        return d
    
    def industry_unit(self, default=None):
        return next(filter(lambda x: x != 'Nanopack', self.industries), default)

    def set_prices(self, buy, sell):
        self.prices['updated'] = now_timestamp()
        self.prices['buy'] = buy
        self.prices['sell'] = sell

    def get_price(self, which):
        if not self.prices:
            return None
        return self.prices[which]

    def buy_price(self):
        return self.get_price('buy')

    def sell_price(self):
        return self.get_price('sell')

    def price_updated(self):
        return int(self.get_price('updated') or 0)

def load_recipes(file):
    with open(file) as f:
        data = json.load(f)
        return dict(map(lambda x: (x[0], Recipe(x[0], x[1])), data.items()))

def save_recipes(file, recipes):
    with open(file) as f:
        data = json.load(f)
    for n, r in recipes.items():
        data[n] = r.to_dict()
    name, _ = os.path.splitext(file)
    with open(name + '.new', 'w') as f:
            f.write(json.dumps(data, indent=2))
    os.remove(file)
    os.rename(name + '.new', file)