import math
from math import log, sqrt, exp
from scipy.stats import norm

def black_scholes(S0, K, T, r, sigma, type):
    if type == "call" :
        d1 = (math.log(S0 / K) + ( r + 0.5 * sigma ** 2 ) * T) / (sigma * math.sqrt(T))
        d2 = d1 - sigma * math.sqrt(T)
        return S0*norm.cdf(d1) - K*math.exp(-r * T)*norm.cdf(d2)
    else :
        d1 = (math.log(S0 / K) + ( r + 0.5 * sigma ** 2 ) * T) / (sigma * math.sqrt(T))
        d2 = d1 - sigma * math.sqrt(T)
        return K*math.exp(- r * T)*norm.cdf(- d2) - S0*norm.cdf(- d1)