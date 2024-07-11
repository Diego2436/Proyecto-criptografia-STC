""" Imports API """
import random
from ecdsa import BRAINPOOLP512t1, SigningKey
from flask_bcrypt import Bcrypt
from functools import wraps
import jwt
import base64
from bson.objectid import ObjectId
import os
from time import sleep
import hashlib
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
""" End Imports """

# Secret Sharing
def save_to_pem(folder_path, name, data):
    file_path = os.path.join(folder_path, name + ".pem")
    with open(file_path, "wb") as f:
        f.write(data)

def generate_coefficients(k, secret):
    """Generate a list of `k` coefficients for the polynomial, with the secret as the constant term."""
    coeffs = [secret] + [random.randint(1, BRAINPOOLP512t1.order) for _ in range(k - 1)]
    return coeffs

def evaluate_polynomial(coeffs, x):
    """Evaluate the polynomial at a given x value."""
    result = 0
    for i, coeff in enumerate(coeffs):
        result += coeff * (x ** i)
    return result % BRAINPOOLP512t1.order

def generate_shares(n, k, secret):
    """Generate `n` shares for a `k`-threshold scheme."""
    coeffs = generate_coefficients(k, secret)
    shares = [(i, evaluate_polynomial(coeffs, i)) for i in range(1, n + 1)]
    return shares

def reconstruct_secret(shares):
    """Reconstruct the secret from shares using Lagrange interpolation."""
    def lagrange_interpolate(x, x_s, y_s, p):
        total = 0
        n = len(x_s)
        for i in range(n):
            xi, yi = x_s[i], y_s[i]
            li = 1
            for j in range(n):
                if i != j:
                    xj = x_s[j]
                    li *= (x - xj) * pow(xi - xj, -1, p)
                    li %= p
            total += yi * li
            total %= p
        return total

    x_s, y_s = zip(*shares)
    secret = lagrange_interpolate(0, x_s, y_s, BRAINPOOLP512t1.order)
    return secret
# End Secret Sharing

# Bcrypt
bcrypt = Bcrypt()

def hash_password(password):
    return bcrypt.generate_password_hash(password).decode('utf-8')

def check_password(hashed_password, password):
    return bcrypt.check_password_hash(hashed_password, password)
# End Bcrypt
