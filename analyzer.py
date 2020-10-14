import json
import time
from collections import defaultdict

#from container import Container
from recipe import load_recipes, save_recipes
from helpers import filter_dict, nextid, getid, Input, Output, now_timestamp

class RecipeAnalyzer(object):
    def __init__(self, consider_all=False):
        self.consider_all = consider_all
        
        consider_all = self.load_resources()
        self.machines = []
        self.load_recipes()
        self.load_produce()
        
        self.containers_by_item = defaultdict(lambda: [])
        self.containers_by_type = defaultdict(lambda: [])
        self.added = {}
        # self.units = defaultdict(lambda: 0)

        self.requirements = {}
        self.production = {}

    def is_viable(self, recipe):
        if self.consider_all == True:
            return True
        if recipe.name in self.resources:
            return True
        if len(recipe.input) == 0:
            return False
        for ingredient in recipe.input:
            if self.is_viable(self.recipes[ingredient]) == False:
                return False
        return True

    def load_recipes(self):
        self.recipes = load_recipes('recipes.json')
        if self.consider_all == False:
            self.recipes = dict(filter(lambda r: self.is_viable(r[1]), self.recipes.items()))

        ingredients = set()
        machines = set()
        for _, recipe in self.recipes.items():
            if len(recipe.input) > 0:
                ingredients = ingredients.union(set(recipe.input))
            machine = recipe.industry_unit()
            if machine:
                machines.add(machine)

        self.machines = sorted(machines)
        self.ingredients = dict(filter(lambda r: r[0] in ingredients, self.recipes.items()))
        self.products = dict(filter(lambda r: r[0] not in ingredients, self.recipes.items()))

    def load_containers(self):
        try:
            with open('containers.json') as f:
                data = json.load(f)
                for c in data:
                    product = self.recipes[c['name']]
                    container = self.select_output_container(product)
                    for item in c['contents']:
                        container.produce("containers.json", getid("containers.json"), {
                            "item": item,
                            "amount": -1, # infinite
                            "time": 0     # instant
                        })
        except FileNotFoundError:
            pass
    
    def load_resources(self):
        try:
            with open('resources.json') as f:
                self.resources = json.load(f)
        except FileNotFoundError:
            self.consider_all = True

    def load_produce(self):
        self.produce = None
        try:
            with open('production.json') as f:
                self.produce = json.load(f)
        except FileNotFoundError:
            pass

    def list_items(self, all_items, type, args):
        items = filter_dict(all_items, args)
        keys = list(items.keys())
        keys.sort()
        
        count = 0
        print(f"  {type:<42} {'Tier':<4} {'Industry':<30}")
        for key in keys:
            item = items[key]
            machine = item.industry_unit("NA")
            print(f"  {item.name:<42} {item.tier:<4} {machine:<30}")
            count += 1
        
        print(f"{count} {type}s")

    def list_recipes(self, args):
        self.list_items(self.recipes, "Recipe", args)

    def list_ingredients(self, args):
        self.list_items(self.ingredients, "Ingredients", args)

    def list_products(self, args):
        self.list_items(self.products, "Products", args)

    def ingredient_frequency(self, args):
        freq = defaultdict(lambda: 0)
        for _,recipe in self.recipes.items():
            for ingredient in recipe.input:
                freq[ingredient] += 1

        data = list(filter(lambda e: e[1] > 1, [(k, v) for k, v in freq.items()]))
        data.sort(key=lambda x: x[1])
       
        print("Ingredient frequency (>1):")
        print(f"  {'Freq':<4} {'Product':<42} {'Tier':<4} {'Industry':<30}")
        for k, v in data:
            recipe = self.recipes[k]
            if args.tier and recipe.tier < args.tier:
                continue
            machine = recipe.industry_unit()
            print(f"  {v:<4} {k:<42} {recipe.tier:<4} {machine:<30}")

    def list_inputs(self, args):
        for machine in self.machines:
            ingredients = set()
            for _, recipe in filter(lambda r: r[1].industry_unit() == machine, self.recipes.items()):
                if args.tier and recipe.tier > args.tier:
                    continue
                for ingredient in recipe.input:
                    ingredients.add(ingredient)
            print(f"Ingredients required by {machine} = {len(ingredients)}:")
            for ingredient in sorted(ingredients):
                print(f"  {ingredient}")
            print()

    def ingredient_usage(self, args):
        count = 0
        print(f"{args.ingredient} used in:")
        print(f"  {'Recipe':<42} {'Tier':<4} {'Industry':<30}")
        for _, recipe in self.recipes.items():
            if args.ingredient not in recipe.input:
                continue
            machine = recipe.industry_unit()
            if args.industry and machine.find(args.industry) == -1:
                continue
            print(f"  {recipe.name:<42} {recipe.tier:<4} {machine:<30}")
            count += 1
        print(f"{count} recipes")

    def show_consumers(self, args):
        inputs = defaultdict(lambda: 0)
        for _, recipe in self.recipes.items():
            if args.ingredient not in recipe.input:
                continue
            machine = recipe.industry_unit()
            if machine.startswith('Assembly'):
                continue
            inputs[machine] += 1

        if len(inputs) == 0:
            print(f"Ingredient {args.ingredient} not found")
            return

        data = []
        for k, v in filter(lambda elem: elem[1] > 0, inputs.items()):
            data.append((k,v))
        data.sort(key=lambda x: x[1])

        count = 0
        print(f"{args.ingredient} as input for:")
        print(f"  {'Recipes':<7} {'Industry':<30}")
        for k, v in data:
            print(f"  {v:<7} {k:<30}")
            count += v

        print(f"{count} recipes (+assemblies)")

    def update_prices(self, args):
        if args.next:
            items = sorted(self.recipes.values(), key=lambda r: r.price_updated())
            print(items[0].name)
        else:
            print(f"Setting {args.item} buy {args.buy} and sell {args.sell}")
            recipe = self.recipes[args.item]
            recipe.set_prices(args.buy, args.sell)
            save_recipes('recipes.json', self.recipes)

    def graph_step(self, output):
        self.added[output] = 1
        if output in self.containers_by_item:
            container = self.containers_by_item[output]
            print(f"    {getid(container['name'])}({container['name']}) --> {getid(output)}[{output}]")
            return

        recipe = self.recipes[output]
        machine = recipe.industry_unit()
        if not machine:
            return

        machineid = nextid()
        for ingredient in recipe.input:
            print(f"    {getid(ingredient)}[{ingredient}] --> {machineid}{{{machine}}}")
        print(f"    {machineid}{{{machine}}} --> {getid(output)}[{output} <{recipe.outputQuantity}>]")
        for byproduct in recipe.byproducts:
            print(f"    {machineid}{{{machine}}} --> {getid(byproduct)}[{byproduct} <{recipe.byproducts[byproduct]}>]")
        for ingredient in filter(lambda x: x not in self.added, recipe.input):
            self.graph_step(ingredient)

    def graph(self, args):
        self.load_containers()
        print("graph TD")
        self.graph_step(args.recipe)

    def produce_item(self, item_name):
        item = self.recipes[item_name]
        if item.name in self.production:
            output = self.production[item.name]
            output.amount += item.outputQuantity
        else:
            output = Output(item.name, item.type, item.outputQuantity, item.time, item.industry_unit())
            self.production[item.name] = output

    def total_production(self, product):
        if len(product.input) == 0:
            return
        self.produce_item(product.name)
        for byproduct in product.byproducts:
            self.produce_item(byproduct)
        for ingredient in product.input:
            self.total_production(self.recipes[ingredient])

    def total_requirements(self, product):
        for ingredient in product.input:
            rps = float(product.input[ingredient])/float(product.time)
            if ingredient in self.requirements:
                input = self.requirements[ingredient]
                input.amount += product.input[ingredient]
                input.rps += rps
            else:
                input = Input(ingredient, self.recipes[ingredient].type, product.input[ingredient], rps)
                self.requirements[ingredient] = input
        for ingredient in product.input:
            self.total_requirements(self.recipes[ingredient])

    def factory(self, args):
        for item, count in self.produce.items():
            product = self.products[item]
            for i in range(count):
                self.total_requirements(product)
                self.total_production(product)
        for item in self.requirements:
            required = self.requirements[item]
            if item not in self.production:
                continue
            production = self.production[item]
            while required.rps > production.rps():
                production.add_machine()

        industry = defaultdict(lambda: 0)
        for _, product in self.production.items():
            industry[product.machine] += product.machine_count
        if args.csv: # WIP csv should apply to all commands
            print("Count,Machine,Item")
            for machine, count in industry.items():
                print(f"{count},{machine}")
                for _, product in self.production.items():
                    if product.machine != machine:
                        continue
                    print(f"{product.machine_count},,{product.item}")
        else:
            print(f"Factory to produce {len(self.produce)} items:")
            for machine, count in industry.items():
                print(f"  {count:<3} {machine:<30}")
                for _, product in self.production.items():
                    if product.machine != machine:
                        continue
                    print(f"    {product.machine_count} {product.item}")

    #
    # Old code which attempted to design a factory layout complete with containers etc
    #

    # def select_container(self, item, filter_func, container_name=None):
    #     for container in filter(filter_func, self.containers_by_item[item.name]):
    #         return container
    #     for container in filter(filter_func, self.containers_by_type[item.type]):
    #         return container
    #     if not container_name:
    #         container_name = f"{item.type} {len(self.containers_by_type[item.type]) + 1}"
    #     print(f"creating {container_name}")
    #     container = Container(getid(container_name), container_name)
    #     self.containers_by_item[item.name].append(container)
    #     self.containers_by_type[item.type].append(container)
    #     return container

    # def select_output_container(self, item, container_name=None):
    #     container = self.select_container(item, lambda c: not c.max_input_reached(), container_name=container_name)
    #     return container

    # def select_input_container(self, item):
    #     container = self.select_container(item, lambda c: not c.max_output_reached())
    #     return container

    # def factory_stage(self, product):
    #     if product.name in self.added:
    #         return
    #     self.added[product.name] = 1
    #     machine = product.industry_unit()
    #     if not machine:
    #         return
    #     machine_n = self.units[machine]
    #     self.units[machine] = machine_n + 1
    #     machine_name = f"{machine} {machine_n}"
    #     print(f"creating output for {product}")
    #     container = self.select_output_container(product, container_name="OUT")
    #     container.produce(machine_name, getid(machine_name), { "item": product.name, "amount": product.outputQuantity, "time": product.time })
    #     for ingredient in product.input:
    #         recipe = self.recipes[ingredient]
    #         print(f"creating input for {ingredient}")
    #         container = self.select_input_container(recipe)
    #         container.consume(machine_name, getid(machine_name), { "item": ingredient, "amount": product.input[ingredient] })
    #         self.factory_stage(self.recipes[ingredient])

    # def redistribute(self, containers):
    #     if len(containers) < 2:
    #         return containers
    #     all_recipes = []

    #     for container in containers:
    #         for _, consumer in container.consumers.items():
    #             all_recipes.append([x['item'] for x in consumer['items']])
    #     all_recipes.sort(key=lambda x: len(x), reverse=True)
    #     print(all_recipes)
    #     output = {}
    #     for recipe in all_recipes:
    #         rec = None
    #         for item in recipe:
    #             rec = output.get(item, None)
    #             if rec:
    #                 break
    #         if not rec:
    #             rec = { "items": recipe, "count": 1 }
    #         else:
    #             rec['count'] += 1
    #         for item in recipe:
    #             output[item] = rec
    #     print(output)
    #     print()

    #     # for container in containers:
    #     #     print(f"container {container.name} outputs:")
    #     #     for _, consumer in container.consumers.items():
    #     #         print("..",', '.join(map(lambda x: x['item'], consumer['items'])))
    #     #         rec = None
    #     #         print(len(outputs))
    #     #         for item in filter(lambda x: x['item'] in outputs, consumer['items']):
    #     #             if not rec:
    #     #                 rec = outputs[item['item']]
    #     #                 print("*rec",rec)
    #     #             else:
    #     #                 ex = outputs[item['item']]
    #     #                 print("*ex",ex)
    #     #                 rec['items'] = rec['items'] + ex['items']
    #     #                 rec['count'] = rec['count'] + ex['count']
    #     #                 outputs[item['item']] = rec
    #     #         if not rec:
    #     #             rec = { "items": list(map(lambda x: x['item'], consumer['items'])), "count": 1}
    #     #             print("*new",rec)
    #     #         for item in consumer['items']:
    #     #             outputs[item['item']] = rec

    #     #     print("Freq")
    #     #     for _, output in outputs.items():
    #     #         print(f"{output['count']}", ', '.join(output['items']))

    #     return containers

    # def factory(self, args):
    #     self.load_containers()
    #     print("graph TD")
    #     for _, product in filter(lambda x: x[1]['name'] in self.produce, self.products.items()):
    #         self.factory_stage(product)
    #     for _, containers in self.containers_by_type.items():
    #         containers = self.redistribute(containers)
    #         # for container in containers:
    #         #     print(f"container {container.name} inputs:")
    #         #     for _, producer in container.producers.items():
    #         #         for item in producer['items']:
    #         #             print(f"..{item['item']}")
    #         #     print(f"container {container.name} outputs:")
    #         #     for _, consumer in container.consumers.items():
    #         #         print("..",', '.join(map(lambda x: x['item'], consumer['items'])))
    #             # for _, producer in container.producers.items():
    #             #     for item in producer['items']:
    #             #         print(f"    {producer['id']}{{{producer['name']}}} -->|{item['item']}| {container.id}({container.name})")
    #             # for _, consumer in container.consumers.items():
    #             #     for item in consumer['items']:
    #             #         print(f"    {container.id}({container.name}) -->|{item['item']}| {consumer['id']}{{{consumer['name']}}}")

        # todo place final products in out container
        # graph container tree

