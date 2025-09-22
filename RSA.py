def sign(message, private_key):
    """用私钥对明文数字直接签名。"""
    return pow(message, private_key[0], private_key[1])

def verify(message, signature, public_key):
    """用公钥验证签名。返回True/False。"""
    v = pow(signature, public_key[0], public_key[1])
    return message % public_key[1] == v
def gcd(a, b):
    """Calculate the Greatest Common Divisor using Euclidean algorithm."""
    while b != 0:
        a, b = b, a % b
    return a

def lcm(a, b):
    """Calculate the Least Common Multiple."""
    return a * b // gcd(a, b)

def exgcd(a, b):
    """Extended Euclidean algorithm to find GCD and coefficients x, y."""
    if b == 0:
        return a, 1, 0
    else:
        g, x1, y1 = exgcd(b, a % b)
        x = y1
        y = x1 - (a // b) * y1
        return g, x, y

def modinv(a, m):
    """Calculate the modular multiplicative inverse of a modulo m."""
    g, x, y = exgcd(a, m)
    if g != 1:
        return None  # No modular inverse
    else:
        return x % m
def is_prime(n):
    """Check if n is a prime number (simple trial division)."""
    if n <= 1:
        return False
    if n <= 3:
        return True
    if n % 2 == 0 or n % 3 == 0:
        return False
    i = 5
    while i * i <= n:
        if n % i == 0 or n % (i + 2) == 0:
            return False
        i += 6
    return True

def generate_keys(p, q, e):
    n = p * q
    phi_n = (p - 1) * (q - 1)
    if gcd(e, phi_n) != 1:
        raise ValueError(f"e={e} 与 φ(n)={phi_n} 不互质")
    d = modinv(e, phi_n)
    if d is None:
        raise ValueError("无法求出 e 关于 φ(n) 的模逆元")
    return (e, n), (d, n)

def encrypt(plaintext, public_key):
    e, n = public_key
    if plaintext >= n:
        raise ValueError("明文必须小于 n")
    return pow(plaintext, e, n)

def decrypt(ciphertext, private_key):
    d, n = private_key
    return pow(ciphertext, d, n)


def main():
    try:
        print("请输入两个素数 p, q（用空格分隔）:")
        p, q = map(int, input().split())
        if not (is_prime(p) and is_prime(q)):
            print("输入的 p 或 q 不是素数！")
            return
        n = p * q
        phi_n = (p - 1) * (q - 1)
        print(f"请输入 e（1 < e < {phi_n}，且与 {phi_n} 互质）:")
        e = int(input())
        if not (1 < e < phi_n):
            print("e 不在有效范围内！")
            return
        if gcd(e, phi_n) != 1:
            print(f"e={e} 与 φ(n)={phi_n} 不互质！")
            return
        public_key, private_key = generate_keys(p, q, e)
        print(f"\n公钥: {public_key}")
        print(f"私钥: {private_key}")
        print(f"\n请输入明文（数字，且小于 {n}）:")
        before = int(input())
        after = encrypt(before, public_key)
        print(f"\n密文为: {after}")
        real = decrypt(after, private_key)
        print(f"解密后明文为: {real}")

        # 数字签名演示
        print("\n--- 数字签名演示 ---")
        print(f"对明文 {before} 进行签名...")
        signature = sign(before, private_key)
        print(f"签名值: {signature}")
        print("验证签名...")
        if verify(before, signature, public_key):
            print("签名验证通过！")
        else:
            print("签名验证失败！")
    except Exception as ex:
        print(f"发生错误: {ex}")

if __name__ == "__main__":
    main()