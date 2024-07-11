import random
from ecdsa import BRAINPOOLP512t1, SigningKey

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

# Parameters
n = 2  # Number of shares
k = 2  # Threshold number of shares needed to reconstruct the secret
secret_key = SigningKey.generate(curve=BRAINPOOLP512t1)
secret = secret_key.privkey.secret_multiplier  # The secret to be shared

# Generate shares
shares = generate_shares(n, k, secret)
print("Shares:")
for share in shares:
    print(f"Share {share[0]}: {share[1]}")

# Reconstruct the secret using any `k` shares
reconstructed_secret = reconstruct_secret(random.sample(shares, k))
print(f"OG secret: {secret}")
print(f"Reconstructed secret: {reconstructed_secret}")

# Verify that the reconstructed secret is the same as the original
print(f"Secret matches: {reconstructed_secret == secret}")
