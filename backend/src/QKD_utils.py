import math
import numpy as np

def format_state(state:str)->str:
    kets = ""
    for i in state:
        kets += f"|{i}> "

    return kets

def error_rate(keys:tuple[str,str])->float:
    a_key = keys[0]
    b_key = keys[1]
    
    if len(a_key) != len(b_key):
        raise Exception("Keys need to be the same length.")
    
    if len(a_key) == 0:
        return 0.0
    
    errors = sum(1 for i, j in zip(a_key, b_key) if i != j)
    rate = errors/len(a_key)

    return rate

def binary_entropy(err_rate:float)->float: 

    if err_rate == 0 or err_rate == 1:
        return 0
    
    Q = err_rate
    H = -Q*np.log2(Q) - (1-Q)*np.log2(1-Q)

    return H

def secure_key_rate(err_rate:float)->float:
    
    return 1 - 2*binary_entropy(err_rate)