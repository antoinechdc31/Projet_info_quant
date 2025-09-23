import Tree
import Market
import math


class Node :

    def __init__(self, underlying, tree) :
        self.tree = tree
        self.underlying = underlying
        self.next = self.calcul_next()
        self.proba = self.calcul_proba()
        pass

    def calcul_next(self) :
        Smid = self.underlying * math.exp(self.tree.market.r * self.tree.dt)
        Sup = Smid * self.tree.alpha
        Sdown =  Smid/self.tree.alpha
        list_next = [Smid, Sup, Sdown]
        return list_next
    
    def forward(self) :
        esp = self.underlying * math.exp(self.tree.market.r * self.tree.dt)
        return esp
    
    def esp(self) :
        esp = self.next[0] * self.proba[0] + self.next[1] * self.proba[1] + self.next[2] * self.proba[2]
        return esp
    
    def variance(self) :
        var = (self.underlying**2) * math.exp(2*self.tree.market.r * self.tree.dt) * (math.exp(self.tree.market.sigma**2 *self.tree.dt) - 1) # =B16^2*EXP(2*Rate*DeltaT)*(EXP(Sigma^2*DeltaT)-1)
        return var

    def calcul_proba(self) :
        v = self.variance()
        alpha = self.tree.alpha
        numerateur = (self.next[0]**(-2))*( v + self.next[0]**2 ) - 1 - ( alpha + 1)*((self.next[0]**(-1))*self.next[0] - 1)
        den = (1 - alpha) * ((alpha**(-2)) - 1)
        Pdown = numerateur/den
        Pup = Pdown/alpha
        Pmid = ( 1 - (Pdown + Pup))
        return [Pmid, Pup, Pdown]
