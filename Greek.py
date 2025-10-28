from copy import deepcopy
from OptionPricingParam import OptionPricingParam
from OneDimDerivative import OneDimDerivative
from Tree import Tree

# --- Prix selon S0 ---
def _PriceTreeRecurs_S0(param: OptionPricingParam, S0: float) -> float:
    market = deepcopy(param.market)
    option = deepcopy(param.option)
    market.S0 = S0
    t2 = Tree(market, N=param.tree.N, delta_t=param.tree.dt)
    t2.tree_construction2(option)
    return t2.price_option_recursive(option)

# --- Prix selon sigma ---
def _PriceTreeRecurs_sigma(param: OptionPricingParam, sigma: float) -> float:
    market = deepcopy(param.market)
    option = deepcopy(param.option)
    market.sigma = sigma
    t3 = Tree(market, N=param.tree.N, delta_t=param.tree.dt)
    t3.tree_construction2(option)
    return t3.price_option_recursive(option)

# --- Grecs ---
def OptionDeltaTreeRecurs(market, tree, option, h_S=0.01):
    param = OptionPricingParam(market, tree, option)
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