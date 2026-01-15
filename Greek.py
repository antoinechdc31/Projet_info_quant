from copy import deepcopy
from OptionPricingParam import OptionPricingParam
from OneDimDerivative import OneDimDerivative
from Tree import Tree

# Prix selon S0
def _PriceTreeRecurs_S0(param: OptionPricingParam, S0: float) -> float: #c'est cette fonction qui sera ensuite passé en argument de OneDimDerivative
    
    # On duplique le marché et l'option pour éviter de modifier les objets originaux
    # (important car OneDimDerivative va recalculer plusieurs fois avec différents S0)
    market = deepcopy(param.market)
    option = deepcopy(param.option)

    # On remplace S0 par la nouvelle valeur passée en argument
    market.S0 = S0

    # On reconstruit un arbre identique à celui utilisé pour le pricing initial
    # (même N, même pas de temps Δt)
    t2 = Tree(market, N=param.tree.N, delta_t=param.tree.dt)
    t2.tree_construction2(option)
    return t2.price_option_recursive(option)

# On refait exactement pareil en prenant sigma comme paramètre cette fois
def _PriceTreeRecurs_sigma(param: OptionPricingParam, sigma: float) -> float:
    market = deepcopy(param.market)
    option = deepcopy(param.option)
    market.sigma = sigma
    t3 = Tree(market, N=param.tree.N, delta_t=param.tree.dt)
    t3.tree_construction2(option)
    return t3.price_option_recursive(option)

# --- Grecs ---
def OptionDeltaTreeRecurs(market, tree, option, h_S=0.01):

    # On emballe market, tree et option dans un conteneur (ObjectPricingParam) afin de pouvoir les passer facilement à la fonction f(S0)
    param = OptionPricingParam(market, tree, option)

    # On construit un objet OneDimDerivative :
    #   - _PriceTreeRecurs_S0 est la fonction de pricing en fonction de S0
    #   - param contient tous les paramètres nécessaires au pricing
    #   - shift = h_S correspond au pas de dérivation
    # Puis on appelle .firsr(market.S0) pour calculer la dérivée première.
    return OneDimDerivative(_PriceTreeRecurs_S0, param, shift=h_S).first(market.S0)

def OptionGammaTreeRecurs(market, tree, option, h_S=0.01):
    param = OptionPricingParam(market, tree, option)
    return OneDimDerivative(_PriceTreeRecurs_S0, param, shift=h_S).second(market.S0)

def OptionVegaTreeRecurs(market, tree, option, h_sigma=0.5):
    param = OptionPricingParam(market, tree, option)
    return OneDimDerivative(_PriceTreeRecurs_sigma, param, shift=h_sigma).first(market.sigma)

def OptionVommaTreeRecurs(market, tree, option, h_sigma=0.001):
    param = OptionPricingParam(market, tree, option)
    return OneDimDerivative(_PriceTreeRecurs_sigma, param, shift=h_sigma).second(market.sigma)