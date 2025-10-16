#Module Greek qui contient les fonction utilitaires
from copy import deepcopy
from OptionPricingParam import OptionPricingParam
from OneDimDerivative import OneDimDerivative
from Tree import Tree

#Fonctions de prix 1D (pour dériver par rapport à une variable)
def _PriceTreeBackward_S0(param: OptionPricingParam, S0: float) -> float:
    market = deepcopy(param.market)
    option = deepcopy(param.option)
    market.S0 = S0
    t = Tree(market, N=param.tree.N, delta_t=param.tree.dt)
    return t.price_option_recursive(option)

# Fonctions principales de calcul des grecs
def OptionDeltaTreeBackward(market, tree, option, h_S=0.05):
    param = OptionPricingParam(market, tree, option)
    return OneDimDerivative(_PriceTreeBackward_S0, param, shift=h_S).first(market.S0)


def OptionGammaTreeBackward(market, tree, option, h_S=0.05):
    param = OptionPricingParam(market, tree, option)
    return OneDimDerivative(_PriceTreeBackward_S0, param, shift=h_S).second(market.S0)

 