from typing import Callable
#ici on défini une classe utilitaire qui implemente les formules de dérivées première et seconde 

class OneDimDerivative : 
    """
    Parametre de la classe :
    function : Callable[[object, float], float]
        Une fonction *f(param, x)* qui retourne le prix de l'option
        en fonction du paramètre x que l’on souhaite dériver. Callable nous ondique qu'on envoie en fonction

    other_parameters : object
        C'est un objet regroupant les éléments nécessaires pour pricer l’option
        (typiquement un `OptionPricingParam` contenant market, tree, option).

    Un float qui est le shift utilisé dans les formules de dérivations
    """

    def __init__(self,function : Callable[[object,float],float],other_parameters : object,shift : float ):
        self.f : Callable[[object,float],float]=function
        self.param : object = other_parameters
        self.shift : float = shift
    
    def first(self, x : float)-> float : 
        return (self.f(self.param , x + self.shift)-self.f(self.param , x - self.shift))/(2*self.shift)
    
    def second(self, x: float) -> float:
        return (self.f(self.param, x + self.shift) - 2*self.f(self.param, x) + self.f(self.param, x - self.shift)) / (self.shift ** 2)
    