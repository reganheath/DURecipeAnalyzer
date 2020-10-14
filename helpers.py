import calendar
import time

ids = {}
lastid = 0

def nextid():
    global lastid
    lastid = lastid + 1
    return str(lastid)

def getid(name):
    global ids
    id = ids.get(name)
    if not id:
        id = nextid()
        ids[name] = id
    return id

def filter_dict(d0, args):
    d = d0
    if args.match:
        d = dict(filter(lambda k: k[0].find(args.match) != -1, d0.items()))
    if args.tier:
        d = dict(filter(lambda k:  k[1].tier >= args.tier, d0.items()))
    return d

def now_timestamp():
    return calendar.timegm(time.gmtime())

def output_text(args, text = ""):
    if args.csv:
        return
    print(text)

def output_list(args, list):
    for item in list:
        if args.csv:
            print(item)
        else:
            print(f"  {item}")

def output_data(args, headers, data):
    n = len(headers)
    width = [0] * n

    # Max header width
    for i in range(n):
        width[i] = max(width[i], len(str(headers[i])))

    count = 0

    if args.csv:
        # Output csv
        for i in range(n):
            print(headers[i], end="," if i < n-1 else "\n")
        for item in data:
            count += 1
            for i in range(n):
                print(item[i], end="," if i < n-1 else "\n")
    else:
        items = list(data)
        # Max item width
        for item in items:
            for i in range(n):
                width[i] = max(width[i], len(str(item[i])))
        # Output in columns
        for i in range(n):
            print("{0: <{width}}".format(headers[i], width=width[i]), end=" " if i < n-1 else "\n")
        for item in items:
            count += 1
            for i in range(n):
                print("{0: <{width}}".format(item[i], width=width[i]), end=" " if i < n-1 else "\n")
    
    return count

class Input(object):
    def __init__(self, item, type, amount, rps):
        self.item = item
        self.amount = amount
        self.type = type
        self.rps = rps

    def __repr__(self):
        return f"{self.item} ({self.amount}) {self.rps}"
    def __str__(self):
        return f"{self.item} ({self.amount}) {self.rps}"

class Output(object):
    def __init__(self, item, type, amount, time, machine):
        self.item = item
        self.amount = amount
        self.time = time
        self.type = type
        self.machine = machine
        self.machine_count = 1
    
    def rps(self):
        return (float(self.amount) / float(self.time)) * self.machine_count

    def __repr__(self):
        return f"{self.item} ({self.amount}) [{self.time}s] {self.rps()}"
    def __str__(self):
        return f"{self.item} ({self.amount}) [{self.time}s] {self.rps()}"

    def add_machine(self):
        self.machine_count += 1
