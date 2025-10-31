""""
Container avec tous les paramètres qui seront utile au pricing
Cela nous permet d'éviter de rentrer manuellement tous les paramètres qui seront fixes a chaque fois

"""
class OptionPricingParam:
   
    def __init__(self, market, tree, option):
        self.market = market
        self.tree = tree
        self.option = option


    