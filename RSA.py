
# RSA encryption and decryption implementation

def exgcd(a, b, x, y):
    """Extended Euclidean algorithm to find GCD and coefficients x, y."""
    if b == 0:
        x[0], y[0] = 1, 0
        return a
    ans = exgcd(b, a % b, x, y)
    temp = x[0]
    x[0] = y[0]
    y[0] = temp - (a // b) * y[0]
    return ans

def tocal(a, b):
    """Calculate the modular multiplicative inverse of a modulo b."""
    x, y = [0], [0]
    gcd = exgcd(a, b, x, y)
    if 1 % gcd != 0:
        return -1
    x[0] = x[0] * (1 // gcd)
    b = abs(b)
    ans = x[0] % b
    if ans <= 0:
        ans += b
    return ans

def main():
    print("Enter p, q (both prime numbers):")
    p, q = map(int, input().split())
    n = p * q
    n1 = (p - 1) * (q - 1)  # Euler's totient function
    print(f"Enter e (coprime with {n1} and 1 < e < {n1}):")
    e = int(input())
    
    d = tocal(e, n1)
    
    print("\n")
    print(f"{{ {e}, {n} }} is the public key")
    print(f"{{ {d}, {n} }} is the private key")
    
    print("\n")
    print(f"Enter plaintext (must be less than {n}):")
    before = int(input())
    
    print("\nCiphertext is:")
    after = pow(before, e, n)  # Efficient modular exponentiation
    print(after)
    
    print("Decrypted plaintext is:")
    real = pow(after, d, n)  # Efficient modular exponentiation
    print(real)
    
if __name__ == "__main__":
    main()