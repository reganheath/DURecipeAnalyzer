# DURecipeAnalyzer
A simple python script to analyze Dual Universe recipes for industry design

## Usage
Run `python main.py --help` to see all supported commands.

### Commands
#### list (li, recipes, re)
The default command.  Lists all recipes, the tier, and industry required.

#### ingredients (in)
List all ingredients (those items used to create other items).

#### products (pr, prod)
List all final products (those items not used in subsequent recipes).

#### frequency (fr, freq)
List all items and their frequency of use in other recipes.

#### inputs / usage (us, use)
List all recipes using the specified ingredient.

#### consumers
List all consumers (industry) of the specified ingredient.

#### graph (gr)
WIP. Produce a Mermaid diagram (see https://github.com/mermaid-js/mermaid) which shows the tree of inputs to produce a specific recipe.

#### factory (fa)
WIP. Calculate the required industry units to produce all items listed in production.json (a dictionary of `item: count` keys).

##### todo
- Count consumers and determine container requirements

##### Known issue(s)
- Output includes recyclers when it gets all the Hydrogen/Oxygen it needs from Refiners

#### prices (price)
WIP. Provide scriptable hooks for collecting current market prices for each item so that future commands can be added to analyze benefits of selling ore and buying items vs investment in industry etc.
