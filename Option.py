from datetime import datetime

class Option :

    def __init__(self, K, mat, opt_type, style, isDiv = False, div = 0, date_div = None, calc_date = datetime.now() ) :
        self.strike = K
        self.opt_type = opt_type 
        self.style = style     
        self.mat = mat 
        self.isDiv = isDiv
        self.div = div
        self.date_div = date_div
        self.calc_date = calc_date

    def payoff(self, S):
        if self.opt_type == "call" :
            return max(S - self.strike, 0)
        elif self.opt_type == "put" :
            return max(self.strike - S, 0)
        else :
            raise ValueError("Type d'option non reconnu")
        