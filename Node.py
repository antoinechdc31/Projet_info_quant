import Tree
import Market
import math

class Node :

    def __init__(self, underlying, tree, level = 0, up = None, down = None, div = 0) :
        self.tree = tree
        self.underlying = underlying
        self.level = level
        self.up = up
        self.down = down
        self.next = self.calcul_next(div)
        self.Nup = None
        self.Ndown = None
        self.Nmid = None
        self.proba = self.calcul_proba(div)
        pass

    def create_brick(self, trunc, direction = "up", div = 0, is_div = False) :
        if not is_div :
            Smid, Sup, Sdown = self.next
        else :

            Smid, Sup, Sdown = self.calcul_next(div, is_div)
            self.next = [Smid, Sup, Sdown]

        if trunc :
            self.Nmid = Node(Smid, self.tree, self.level, None, None, div)
            self.Nup = Node(Sup, self.tree, self.level + 1, None, self.Nmid, div)
            self.Ndown = Node(Sdown, self.tree, self.level - 1, self.Nmid, None, div)
            self.Nmid.up = self.Nup
            self.Nmid.down = self.Ndown
        elif direction == "up" and self.down is not None:
            self.Ndown = self.down.Nmid
            self.Nmid = self.down.Nup
            self.Nup = Node(Sup, self.tree, self.level + 1, down = self.Nmid, div = div)
            self.Nmid.up = self.Nup
            return
        # Si on construit en venant du haut
        elif direction == "down" and self.up is not None:
            self.Nup = self.up.Nmid
            self.Nmid = self.up.Ndown
            self.Ndown = Node(Sdown, self.tree, self.level - 1, up=self.Nmid, div = div)
            self.Nmid.down = self.Ndown
            return

        pass

    def calcul_next(self, div = 0, is_div = False) :

        if not is_div :

            Smid = self.underlying * (math.exp(self.tree.market.r * self.tree.dt)) - div
            Sup = Smid * self.tree.alpha
            Sdown =  Smid/self.tree.alpha
            list_next = [Smid, Sup, Sdown]

        else :
            alpha = self.tree.alpha
            r = self.tree.market.r
            dt = self.tree.dt

            if self.level == 0 :
                Smid = self.underlying * math.exp(r * dt) - div
                self.tree.Smid_tronc = Smid  # mémoriser

            elif self.tree.Smid_tronc is not None :

                Smid = self.tree.Smid_tronc * (alpha ** self.level)

            else :
                raise ValueError
            
            Sup = Smid * alpha
            Sdown = Smid / alpha

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

    def calcul_proba(self, div = 0) :
        v = self.variance()
        alpha = self.tree.alpha

        if div == 0 :

            numerateur = (self.next[0]**(-2))*( v + self.next[0]**2 ) - 1 - ( alpha + 1)*((self.next[0]**(-1))*self.next[0] - 1)
            den = (1 - alpha) * ((alpha**(-2)) - 1)
            Pdown = numerateur/den
            Pup = Pdown/alpha
            Pmid = ( 1 - (Pdown + Pup))

        else :
            
            Smid = self.next[0]
            numerateur = (Smid**(-2)) * (v + Smid**2) - 1 - (alpha + 1) * ((Smid**(-1)) * Smid - 1)
            den = (1 - alpha) * (alpha**(-2) - 1)
            Pdown = numerateur / den

            # Formule
            Pup = ((Smid**(-1)) * Smid - 1 - (alpha**(-1) - 1) * Pdown) / (alpha - 1)

            # Pmid
            Pmid = 1 - (Pdown + Pup)

        return [Pmid, Pup, Pdown]
