from typing import Callable

class OneDimDerivative : 
    def __init__(self,function : Callable[[object,float],float],other_parameters : object,shift : float = 1):
        self.f : Callable[[object,float],float]=function
        self.param : object = other_parameters
        self.shift : float = shift
    
    def first(self, x : float)-> float :
        return (self.f(self.param , x + self.shift)-self.f(self.param , x - self.shift))/(2*self.shift)
    
    def second(self, x: float) -> float:
        return (self.f(self.param, x + self.shift) - 2*self.f(self.param, x) + self.f(self.param, x - self.shift)) / (self.shift ** 2)
    
    