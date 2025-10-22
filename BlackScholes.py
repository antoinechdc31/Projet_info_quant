import math
from math import log, sqrt, exp
from scipy.stats import norm

def black_scholes(S0, K, T, r, sigma, type): # classe de fct de test pour comparer avec black scholes
    d1 = (math.log(S0 / K) + ( r + 0.5 * sigma ** 2 ) * T) / (sigma * math.sqrt(T))
    d2 = d1 - sigma * math.sqrt(T)
    if type == "call" : # calcuol de la formule du call
        return S0 * norm.cdf(d1) - K * math.exp( - r * T)*norm.cdf(d2)
    else :
        return K * math.exp(- r * T) * norm.cdf(- d2) - S0 * norm.cdf( - d1)
    


def black_scholes_greeks(S0, K, T, r, sigma, type):
    """
    Calcule les Grecques analytiques du modèle Black-Scholes.
    Retourne : Delta, Gamma, Vega, Volga
    """
    d1 = (log(S0 / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * sqrt(T))
    d2 = d1 - sigma * sqrt(T)

    # Delta
    if type == "call":
        delta = norm.cdf(d1)
    elif type == "put":
        delta = norm.cdf(d1) - 1
    else:
        raise ValueError("Type d'option non reconnu")

    # Gamma (identique pour call/put)
    gamma = norm.pdf(d1) / (S0 * sigma * sqrt(T))

    # Vega (identique pour call/put)
    vega = S0 * norm.pdf(d1) * sqrt(T)

    # Volga (aussi appelée Vomma)
    volga = vega * d1 * d2 / sigma

    return delta, gamma, vega, volga