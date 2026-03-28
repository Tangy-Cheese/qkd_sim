import numpy as np

def format_state(state:str)->str:
    """Format string of qubits into braket strings

    :param state: qubit string
    :return: bra-ket qubit string 
    """
    kets = ""
    for i in state:
        kets += f"|{i}> "

    return kets

def error_rate(keys:tuple[str,str])->float:
    """Compute qubit error rate between two keys

    :param keys: Tuple of the two compared keys
    :raises Exception: Checks if length of keys are the same
    :return: Qubit error rate
    """
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
    """Compute the binary entropy given the error_rate

    :param err_rate: Qubit error rate
    :return: Binary entropy
    """
    if err_rate == 0 or err_rate == 1:
        return 0
    
    Q = err_rate
    H = -Q*np.log2(Q) - (1-Q)*np.log2(1-Q)

    return H

def secure_key_rate(err_rate:float)->float:
    """Compute the secure key rate from the qubit error rate

    :param err_rate: Qubit error rate
    :return: Secure key rate
    """
    return 1 - 2*binary_entropy(err_rate)


def XOR(bitstr1:str, bitstr2:str)->str:
    """XOR operator applied onto two strings.
    XOR = a ⊕ b

    :param bitstr1: First bit string a
    :param bitstr2: Second bit string b
    :raises Exception: If the strings arent the same length XOR cannot be applied
    :return: XOR of two strings
    """
    if len(bitstr1) != len(bitstr2):
        raise Exception("Stoopid strings no same length")
   
    outcome = ""

    for bit1, bit2 in zip(bitstr1, bitstr2):
        if bit1 == bit2:
            outcome += "0" 

        else:
            outcome += "1"

    return outcome
