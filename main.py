import sys
import argparse

from analyzer import RecipeAnalyzer

def create_parser():
    parser = argparse.ArgumentParser(formatter_class=lambda prog: argparse.HelpFormatter(prog, max_help_position=27), description='''
Anaylyse Dual Universe recipes.

Reads recipes from recipes.json.
If containers.json is provided, when graphing, will include container as source for items.
If resources.json is provided, will consider only recipes reachable from listed base resources (unless --all is given).''')
    parser.add_argument('-a', '--all', action='store_true', help='Ignore resources.json (consider all recipes)')
    parser.add_argument('--csv', action='store_true', help='Output in CSV form') # WIP csv should apply to all commands (only applies in factory)
    
    subparsers = parser.add_subparsers(title='commands', metavar="<command>")
    list = subparsers.add_parser("list", aliases=['li','recipes','re'], help='List recipes')
    list.add_argument('-t', '--tier', type=int, help='Filter by tier')
    list.add_argument('-m', '--match', help='Filter by name substring match')
    list.set_defaults(func=lambda args: RecipeAnalyzer(consider_all=args.all).list_recipes(args))

    ingredients = subparsers.add_parser("ingredients", aliases=['in'], help='List ingredients')
    ingredients.add_argument('-t', '--tier', type=int, help='Filter by tier')
    ingredients.add_argument('-m', '--match', help='Filter by name substring match')
    ingredients.set_defaults(func=lambda args: RecipeAnalyzer(consider_all=args.all).list_ingredients(args))

    products = subparsers.add_parser("products", aliases=['pr', 'prod'], help='List final products')
    products.add_argument('-t', '--tier', type=int, help='Filter by tier')
    products.add_argument('-m', '--match', help='Filter by name substring match')
    products.set_defaults(func=lambda args: RecipeAnalyzer(consider_all=args.all).list_products(args))

    freq = subparsers.add_parser("frequency", aliases=['fr', 'freq'], help='List ingredient frequency')
    freq.add_argument('-t', '--tier', type=int, help='Filter by tier')
    freq.add_argument('-m', '--match', help='Filter by name substring match')
    freq.set_defaults(func=lambda args: RecipeAnalyzer(consider_all=args.all).ingredient_frequency(args))

    inputs = subparsers.add_parser("inputs", aliases=['us', 'use'], help='List recipes using <ingredient>')
    inputs.add_argument('-t', '--tier', type=int, help='Filter by tier')
    inputs.add_argument('-m', '--match', help='Filter by name substring match')
    inputs.set_defaults(func=lambda args: RecipeAnalyzer(consider_all=args.all).list_inputs(args))

    usage = subparsers.add_parser("usage", aliases=['us', 'use'], help='List recipes using <ingredient>')
    usage.add_argument("ingredient", help="The ingredient name")
    usage.add_argument('-i', '--industry', help='Filter/combine by industry')
    usage.set_defaults(func=lambda args: RecipeAnalyzer(consider_all=args.all).ingredient_usage(args))

    consumers = subparsers.add_parser("consumers", aliases=['co', 'cons'], help='List consumers of <ingredient> by industry')
    consumers.add_argument("ingredient", help="The ingredient name")
    consumers.set_defaults(func=lambda args: RecipeAnalyzer(consider_all=args.all).show_consumers(args))
    
    graph = subparsers.add_parser("graph", aliases=['gr'], help='Graph <recipe>')
    graph.add_argument("recipe", help="The recipe name")
    graph.set_defaults(func=lambda args: RecipeAnalyzer(consider_all=args.all).graph(args))
    
    factory = subparsers.add_parser("factory", aliases=['fa'], help='Design factory')
    factory.add_argument('-t', '--tier', type=int, help='Filter by tier')
    factory.add_argument('-m', '--match', help='Filter by name substring match')
    factory.set_defaults(func=lambda args: RecipeAnalyzer(consider_all=args.all).factory(args))

    prices = subparsers.add_parser("prices", aliases=['price'], help='Update prices')
    prices.add_argument('-n', '--next', action='store_true', help='Get next item for price update')
    prices.add_argument('-i', '--item', type=str, help='The item name')
    prices.add_argument('-b', '--buy', type=int, help='Set buy price')
    prices.add_argument('-s', '--sell', type=int, help='Set sell price')
    prices.set_defaults(func=lambda args: RecipeAnalyzer(consider_all=args.all).update_prices(args))
    
    return parser

def default_command(args):
    setattr(args,'match',None)
    setattr(args,'tier',None)
    RecipeAnalyzer(consider_all=args.all).list_recipes(args)

def main():
    parser = create_parser()
    args = parser.parse_args(sys.argv[1:])
    if not hasattr(args, 'func'):
        default_command(args)
    else:
        args.func(args)
    return
    
if __name__ == "__main__":
    main()
