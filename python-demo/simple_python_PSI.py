"""
This file has a less efficient but extremely simple version of the PSI system. It is missing all communication protocols, client-server setup, or speed fixes. It is meant to be a simple example of how PSI works.
"""


# Importing required libraries
import hashlib
import pickle
import numpy as np

MODULUS = 10**9+7 
MODULUS = 97

def commutative_encryption_simple(x, key):
    """
    A simple commutative encryption function using modular exponentiation. This is not secure, and should be made modulus and work only with ints, but it is simple.
    """
    return pow(x, key, MODULUS)

def hash_function_any(x):
    """
    A hash function that can handle arbitrary Python objects.
    """
    # Serialize the input using pickle
    serialized_x = pickle.dumps(x)

    # Create a hash of the serialized input
    hash_object = hashlib.sha256(serialized_x)
    
    # Return the hexadecimal representation of the hash
    return int(hash_object.hexdigest(), 16)


def approximate_intersection(set1, set2, threshold):
    """
    Find the approximate intersection of two sets.

    Args:
        set1 (set): The first set of numbers.
        set2 (set): The second set of numbers.
        threshold (float): The maximum absolute difference to consider numbers as equal.

    Returns:
        set: The set of numbers present in both input sets within the threshold.
    """
    intersection = set()

    for num1 in set1:
        for num2 in set2:
            if abs(num1 - num2) <= threshold:
                intersection.add((num1, num2))

    return intersection

def find_PSI(A,B, hash_function = hash_function_any, commutative_encryption = commutative_encryption_simple, key_a=None, key_b=None):

    # Hash each element of A and B
    A_hashed = {hash_function(x) for x in A}
    B_hashed = {hash_function(x) for x in B}

    # Generate secret keys
    if key_a is None:
        key_a = np.random.randint(1, 100)
    if key_b is None:
        key_b = np.random.randint(1, 100)

    # Encrypt each set
    A_encrypted = {commutative_encryption(x, key_a) for x in A_hashed}
    B_encrypted = {commutative_encryption(x, key_b) for x in B_hashed}

    # Send B_encrypted to A and vice versa, then A encrypts B_encrypted and B encrypts A_encrypted
    B_encrypted_double = {commutative_encryption(x, key_a) for x in A_encrypted}
    A_encrypted_double = {commutative_encryption(x, key_b) for x in B_encrypted}

    # Decrypt the received data
    B_decrypted = {commutative_encryption(x, pow(key_b, MODULUS - 2, MODULUS)) for x in A_encrypted_double}
    A_decrypted = {commutative_encryption(x, pow(key_a, MODULUS - 2, MODULUS)) for x in B_encrypted_double}

    # Now both A and B can compute the intersection
    # We could use the & operator on the sets but sometimes in simple python we get floating errors, so we use an approximate solution.
    intersection_A = approximate_intersection(A_decrypted, A_encrypted, 0.0001)
    intersection_B = approximate_intersection(B_decrypted, B_encrypted, 0.0001)

    assert len(intersection_A) == len(intersection_B), "The intersection is not the same for both parties"

    return len(intersection_A)



# Main
if __name__ == "__main__":
    # Initialize sets and secret keys
    A = {1, 2, 3}
    B = {2, 3, 4}

    find_PSI(A,B)


   