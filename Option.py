class Option :

    def __init__(self, K, mat, opt_type, style) :
        self.strike = K
        self.opt_type = opt_type 
        self.style = style     
        self.mat = mat

    def payoff(self, S):
        if self.opt_type == "call" :
            return max(S - self.strike, 0)
        elif self.opt_type == "put" :
            return max(self.K - S, 0)
        else :
            raise ValueError("Type d'option non reconnu")
        