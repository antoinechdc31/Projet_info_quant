# OptionPricingParam.py
class OptionPricingParam:
   
    def __init__(self, market, tree, option):
        self.market = market
        self.tree = tree
        self.option = option


















    """
    Conteneur minimal pour tout ce dont on a besoin pour pricer :
    - market (S0, r, sigma)
    - tree (N, dt)
    - option (K, mat, style, dividende éventuel)
    """