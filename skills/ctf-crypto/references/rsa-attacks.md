# CTF Crypto - RSA Attacks

## Table of Contents
- [Small Public Exponent (Cube Root)](#small-public-exponent-cube-root)
- [Common Modulus Attack](#common-modulus-attack)
- [Wiener's Attack (Small Private Exponent)](#wieners-attack-small-private-exponent)
- [Pollard's p-1 Factorization](#pollards-p-1-factorization)
- [Hastad's Broadcast Attack](#hastads-broadcast-attack)
- [RSA with Consecutive Primes (Fermat Factorization)](#rsa-with-consecutive-primes-fermat-factorization)
- [Multi-Prime RSA](#multi-prime-rsa)
- [RSA with Restricted-Digit Primes (LACTF 2026)](#rsa-with-restricted-digit-primes-lactf-2026)
- [Coppersmith for Structured RSA Primes (LACTF 2026)](#coppersmith-for-structured-rsa-primes-lactf-2026)
- [Manger's RSA Padding Oracle Attack (Nullcon 2026)](#mangers-rsa-padding-oracle-attack-nullcon-2026)
- [Manger's Attack on RSA-OAEP via Timing Oracle (HTB Early Bird)](#mangers-attack-on-rsa-oaep-via-timing-oracle-htb-early-bird)
- [Polynomial Hash with Trivial Root (Pragyan 2026)](#polynomial-hash-with-trivial-root-pragyan-2026)
- [Polynomial CRT in GF(2)\[x\] (Nullcon 2026)](#polynomial-crt-in-gf2x-nullcon-2026)
- [Affine Cipher over Non-Prime Modulus (Nullcon 2026)](#affine-cipher-over-non-prime-modulus-nullcon-2026)
- [Hastad Broadcast Attack with Linear Padding -- Coppersmith (PlaidCTF 2017)](#hastad-broadcast-attack-with-linear-padding----coppersmith-plaidctf-2017)
- [Franklin-Reiter Related Message Attack on RSA e=3 (N1CTF 2018)](#franklin-reiter-related-message-attack-on-rsa-e3-n1ctf-2018)
- [Coppersmith Attack on Linearly-Related RSA Primes (ASIS CTF 2018)](#coppersmith-attack-on-linearly-related-rsa-primes-asis-ctf-2018)
- [rsa-attacks-2.md: RSA p=q Validation Bypass (BearCatCTF 2026)](./rsa-attacks-2.md#rsa-pq-validation-bypass-bearcatctf-2026)
- [rsa-attacks-2.md: RSA Cube Root CRT when gcd(e, phi) > 1 (BearCatCTF 2026)](./rsa-attacks-2.md#rsa-cube-root-crt-when-gcde-phi--1-bearcatctf-2026)
- [rsa-attacks-2.md: Factoring n from Multiple of phi(n) (BearCatCTF 2026)](./rsa-attacks-2.md#factoring-n-from-multiple-of-phin-bearcatctf-2026)
- [rsa-attacks-2.md: RSA Signature Forgery via Multiplicative Homomorphism (MMA CTF 2015)](./rsa-attacks-2.md#rsa-signature-forgery-via-multiplicative-homomorphism-mma-ctf-2015)
- [rsa-attacks-2.md: Weak RSA Key Generation via Base Representation (Sharif CTF 2016)](./rsa-attacks-2.md#weak-rsa-key-generation-via-base-representation-sharif-ctf-2016)
- [rsa-attacks-2.md: RSA with gcd(e, phi(n)) > 1 (CSAW 2015)](./rsa-attacks-2.md#rsa-with-gcde-phin--1-csaw-2015)
- [rsa-attacks-2.md: Batch GCD for Shared Prime Factoring (BSidesSF 2025)](./rsa-attacks-2.md#batch-gcd-for-shared-prime-factoring-bsidessf-2025)
- [rsa-attacks-2.md: RSA Partial Key Recovery from dp dq qinv (0CTF 2016)](./rsa-attacks-2.md#rsa-partial-key-recovery-from-dp-dq-qinv-0ctf-2016)
- [rsa-attacks-2.md: RSA-CRT Fault Attack / Bit-Flip Recovery (CSAW CTF 2016)](./rsa-attacks-2.md#rsa-crt-fault-attack--bit-flip-recovery-csaw-ctf-2016)
- [rsa-attacks-2.md: RSA Homomorphic Decryption Oracle Bypass (ECTF 2016)](./rsa-attacks-2.md#rsa-homomorphic-decryption-oracle-bypass-ectf-2016)
- [rsa-attacks-2.md: RSA with Small Prime Factors and CRT Decomposition (Hack The Vote 2016)](./rsa-attacks-2.md#rsa-with-small-prime-factors-and-crt-decomposition-hack-the-vote-2016)

---

## Small Public Exponent (Cube Root)

**Pattern:** Small `e` (typically 3) with small message. When `m^e < n`, the ciphertext is just `m^e` without modular reduction — take the integer eth root.

```python
import gmpy2

def small_e_attack(c, e):
    """Recover plaintext when m^e < n (no modular wrap)."""
    m, exact = gmpy2.iroot(c, e)
    if exact:
        return int(m)
    return None

# Usage
m = small_e_attack(c, e=3)
print(bytes.fromhex(hex(m)[2:]))
```

**When it fails:** If `m^e > n` (message padded or large), the modular reduction destroys the simple root. In that case, try Hastad's broadcast attack or Coppersmith's short-pad attack.

---

## Common Modulus Attack

**Pattern:** Same message encrypted with same `n` but two different public exponents `e1`, `e2` where `gcd(e1, e2) = 1`. Recover plaintext without factoring `n`.

```python
from math import gcd

def common_modulus_attack(c1, c2, e1, e2, n):
    """Recover plaintext from two encryptions with same n, coprime e1/e2."""
    # Extended GCD: find a, b such that a*e1 + b*e2 = 1
    def extended_gcd(a, b):
        if a == 0: return b, 0, 1
        g, x, y = extended_gcd(b % a, a)
        return g, y - (b // a) * x, x

    g, a, b = extended_gcd(e1, e2)
    assert g == 1, "e1 and e2 must be coprime"

    # m = c1^a * c2^b mod n
    # Handle negative exponent by using modular inverse
    if a < 0:
        c1 = pow(c1, -1, n)
        a = -a
    if b < 0:
        c2 = pow(c2, -1, n)
        b = -b
    m = (pow(c1, a, n) * pow(c2, b, n)) % n
    return m
```

**Key insight:** Two encryptions of the same message under the same modulus but different exponents leak the plaintext via Bezout's identity. No factoring required.

---

## Wiener's Attack (Small Private Exponent)

**Pattern:** Private exponent `d` is small (d < N^0.25). The continued fraction expansion of `e/n` reveals `d`.

```python
def wiener_attack(e, n):
    """Recover d when d < N^0.25 using continued fraction expansion of e/n."""
    def continued_fraction(num, den):
        cf = []
        while den:
            q, r = divmod(num, den)
            cf.append(q)
            num, den = den, r
        return cf

    def convergents(cf):
        convs = []
        h0, h1 = 0, 1
        k0, k1 = 1, 0
        for a in cf:
            h0, h1 = h1, a * h1 + h0
            k0, k1 = k1, a * k1 + k0
            convs.append((h1, k1))
        return convs

    cf = continued_fraction(e, n)
    for k, d in convergents(cf):
        if k == 0:
            continue
        # Check if d is valid: phi = (e*d - 1) / k must be integer
        if (e * d - 1) % k != 0:
            continue
        phi = (e * d - 1) // k
        # phi = (p-1)(q-1) = n - p - q + 1, so p+q = n - phi + 1
        s = n - phi + 1
        # p and q are roots of x^2 - s*x + n = 0
        discriminant = s * s - 4 * n
        if discriminant < 0:
            continue
        from math import isqrt
        t = isqrt(discriminant)
        if t * t == discriminant:
            return d
    return None

# Usage
d = wiener_attack(e, n)
m = pow(c, d, n)
```

**When to use:** Very large `e` (close to `n`) often indicates small `d`. Also try `owiener` Python package: `pip install owiener`.

---

## Pollard's p-1 Factorization

**Pattern:** One prime factor `p` has a smooth `p-1` (all prime factors of `p-1` are small). Compute `a^(B!) mod n`; GCD with `n` reveals `p`.

```python
from math import gcd

def pollard_p1(n, B=100000):
    """Factor n when p-1 is B-smooth for some prime factor p."""
    a = 2
    for j in range(2, B + 1):
        a = pow(a, j, n)
        d = gcd(a - 1, n)
        if 1 < d < n:
            return d, n // d
    return None

# Usage
result = pollard_p1(n)
if result:
    p, q = result
```

**Key insight:** By Fermat's little theorem, if `p-1` divides `B!`, then `a^(B!) ≡ 1 (mod p)`, so `gcd(a^(B!) - 1, n)` gives `p`. Increase `B` for larger smooth bounds. CTF primes generated with `getStrongPrime()` or similar are resistant.

---

## Hastad's Broadcast Attack

**Pattern:** Same plaintext `m` encrypted with `e` different public keys (all with exponent `e`, typically `e=3`). Use CRT to reconstruct `m^e`, then take the eth root.

```python
from functools import reduce

def hastad_broadcast(ciphertexts, moduli, e):
    """Recover m from e encryptions with the same exponent e."""
    assert len(ciphertexts) >= e and len(moduli) >= e

    # Chinese Remainder Theorem
    def crt(remainders, moduli):
        N = reduce(lambda a, b: a * b, moduli)
        result = 0
        for r, m in zip(remainders, moduli):
            Ni = N // m
            Mi = pow(Ni, -1, m)
            result += r * Ni * Mi
        return result % N

    # CRT gives m^e (mod N1*N2*...*Ne)
    # Since m < each Ni, m^e < N1*N2*...*Ne, so no modular reduction occurred
    me = crt(ciphertexts[:e], moduli[:e])

    import gmpy2
    m, exact = gmpy2.iroot(me, e)
    if exact:
        return int(m)
    return None

# Usage (e=3, three encryptions)
m = hastad_broadcast([c1, c2, c3], [n1, n2, n3], e=3)
print(bytes.fromhex(hex(m)[2:]))
```

**Key insight:** CRT reconstructs `m^e` exactly (no modular reduction) because `m < min(n_i)` and therefore `m^e < n_1 * n_2 * ... * n_e`. Taking the integer eth root recovers `m`.

---

## Hastad Broadcast Attack with Linear Padding -- Coppersmith (PlaidCTF 2017)

**Pattern:** Extension of Hastad's broadcast attack when each recipient applies a known linear transform `c_i = (a_i * m + b_i)^e mod n_i` before encryption.

```python
# Standard Hastad requires identical plaintext
# With linear padding: each ciphertext encrypts a_i*m + b_i
# Use CRT + Coppersmith's small_roots on the resulting polynomial

from sage.all import *
# Combine via CRT
N = prod(n_values)
T = [crt_coefficient(i, n_values) for i in range(e)]

P = PolynomialRing(Zmod(N), 'x')
x = P.gen()
poly = sum(T[i] * ((a[i]*x + b[i])**e - c[i]) for i in range(e))
poly = poly.monic()

# Coppersmith's method finds small root
roots = poly.small_roots(epsilon=1/30)
flag = int(roots[0])
```

**Key insight:** When the same message is encrypted with `e` different moduli but each applies a known affine transform `a_i * m + b_i`, CRT combines the congruences into a single polynomial of degree `e` over `Z/NZ`. Coppersmith's method recovers `m` as a small root, generalizing Hastad's attack beyond identical plaintexts.

**References:** PlaidCTF 2017

---

### Franklin-Reiter Related Message Attack on RSA e=3 (N1CTF 2018)

**Pattern:** When server encrypts `m+padding` where `padding = sha256(user_input)` and `e=3`, two ciphertexts with known padding difference allow polynomial GCD in `Zmod(n)` to recover `m`. (N1CTF 2018)

```python
# SageMath
def franklin_reiter(n, pad1, pad2, c1, c2):
    R.<X> = PolynomialRing(Zmod(n))
    f1 = (X + pad1)^3 - c1
    f2 = (X + pad2)^3 - c2
    return -gcd(f1, f2).coefficients()[0]
```

**Key insight:** With RSA e=3, if the same message `m` is encrypted with two known affine transformations (`m+pad1`, `m+pad2`), polynomial GCD over `Zmod(n)` recovers `m` directly. Works whenever the padding difference is known, even without knowing the full padding.

---

### Coppersmith Attack on Linearly-Related RSA Primes (ASIS CTF 2018)

**Pattern:** When RSA primes have a near-linear relation `q ~ 4p`, approximate `q` from `sqrt(4*n)`, then use Coppersmith's `small_roots` to find the error term. (ASIS CTF 2018)

```python
# SageMath
qbar = isqrt(4 * n)
R.<x> = PolynomialRing(Zmod(n))
f = x + qbar
roots = f.small_roots(X=2^200, beta=0.5)  # find small error term
q = qbar + int(roots[0])
p = n // q
```

**Key insight:** When `q ~ k*p` for known `k`, then `q ~ sqrt(k*n)`. The difference between `q` and this approximation is small enough for Coppersmith's method. This generalizes Fermat factorization to non-consecutive primes with known ratio.

---

## RSA with Consecutive Primes (Fermat Factorization)

**Pattern (Loopy Primes):** q = next_prime(p), making p ~ q ~ sqrt(N). Also known as Fermat factorization — works whenever `|p - q|` is small.

**Factorization:** Find first prime below sqrt(N):
```python
from sympy import nextprime, prevprime, isqrt

root = isqrt(n)
p = prevprime(root + 1)
while n % p != 0:
    p = prevprime(p)
q = n // p
```

**Multi-layer variant:** 1024 nested RSA encryptions, each with consecutive primes of increasing bit size. Decrypt in reverse order.

---

## Multi-Prime RSA

When N is product of many small primes (not just p*q):
```python
# Factor N (easier when many primes)
from sympy import factorint
factors = factorint(n)  # Returns {p1: e1, p2: e2, ...}

# Compute phi using all factors
phi = 1
for p, e in factors.items():
    phi *= (p - 1) * (p ** (e - 1))

d = pow(e, -1, phi)
plaintext = pow(ciphertext, d, n)
```

---

## RSA with Restricted-Digit Primes (LACTF 2026)

**Pattern (six-seven):** RSA primes p, q composed only of digits {6, 7}, ending in 7.

**Digit-by-digit factoring from LSB:**
```python
# At each step k, we know p mod 10^k -> compute q mod 10^k = n * p^{-1} mod 10^k
# Prune: only keep candidates where digit k of both p and q is in {6, 7}
candidates = [(6,), (7,)]  # p ends in 6 or 7
for k in range(1, num_digits):
    new_candidates = []
    for p_digits in candidates:
        for d in [6, 7]:
            p_val = sum(p_digits[i] * 10**i for i in range(len(p_digits))) + d * 10**k
            q_val = (n * pow(p_val, -1, 10**(k+1))) % 10**(k+1)
            q_digit_k = (q_val // 10**k) % 10
            if q_digit_k in {6, 7}:
                new_candidates.append(p_digits + (d,))
    candidates = new_candidates
```

**General lesson:** When prime digits are restricted to a small set, digit-by-digit recovery from LSB with modular arithmetic prunes exponentially. Works for any restricted character set.

---

## Coppersmith for Structured RSA Primes (LACTF 2026)

**Pattern (six-seven-again):** p = base + 10^k * x where base is fully known and x is small (x < N^0.25).

**Attack via SageMath:**
```python
# Construct f(x) such that f(x_secret) = 0 (mod p) and thus (mod N)
# p = base + 10^k * x -> x + base * (10^k)^{-1} = 0 (mod p)
R.<x> = PolynomialRing(Zmod(N))
f = x + (base * inverse_mod(10**k, N)) % N
roots = f.small_roots(X=2**70, beta=0.5)  # x < N^0.25
```

**When to use:** Whenever part of a prime is known and the unknown part is small enough for Coppersmith bounds (< N^{1/e} for degree-e polynomial, approximately N^0.25 for linear).

---

## Manger's RSA Padding Oracle Attack (Nullcon 2026)

**Pattern (TLS, Nullcon 2026):** RSA-encrypted key with threshold oracle. Phase 1: double f until `k*f >= threshold`. Phase 2: binary search. ~128 total queries for 64-bit key.

See [advanced-math.md](./advanced-math.md) for full implementation.

---

## Manger's Attack on RSA-OAEP via Timing Oracle (HTB Early Bird)

**Pattern:** Flask app implements RSA-OAEP with custom hash (PBKDF2, 2M iterations). Python's short-circuit `or` evaluation creates a timing oracle: if the first byte Y != 0, PBKDF2 is never called (~0.6s). If Y == 0, PBKDF2 runs (~2s).

**Vulnerable code pattern:**
```python
if Y != 0 or not self.H_verify(self.L, DB[:self.hLen]) or self.os2ip(PS) != 0:
    return {"ok": False, "error": "decryption error"}
```

**Oracle mapping:** Fast response → Y != 0 (decrypted message >= B). Slow response → Y == 0 (decrypted message < B = 2^(8*(k-1))).

**Calibration for network reliability:**
```python
def calibrate(n, e, k):
    B = pow(2, 8 * (k - 1))
    slow_times, fast_times = [], []
    for i in range(5):
        # Known-slow: encrypt values < B
        enc = pow(B - 1 - i*100, e, n).to_bytes(k, 'big')
        slow_times.append(measure(enc))
        # Known-fast: encrypt values > B
        enc = pow(B + 1 + i*100, e, n).to_bytes(k, 'big')
        fast_times.append(measure(enc))
    FAST_UPPER = max(fast_times) * 1.5
    SLOW_LOWER = min(slow_times) * 0.9
```

**Oracle with retry for ambiguous results:**
```python
def padding_oracle(c_int):
    while True:
        total = measure_response_time(c_int)
        if SLOW_LOWER < total < SLOW_UPPER:
            return True   # Y == 0 (below B)
        elif total < FAST_UPPER:
            return False  # Y != 0 (above B)
        # Ambiguous: retry
```

**Full 3-step Manger's attack (~1024 iterations for 1024-bit RSA):**
```python
# Step 1: Find f1 where f1 * m >= B
f1 = 2
while oracle((pow(f1, e, n) * c) % n):
    f1 *= 2

# Step 2: Find f2 where n <= f2 * m < n + B
f2 = (n + B) // B * f1 // 2
while not oracle((pow(f2, e, n) * c) % n):
    f2 += f1 // 2

# Step 3: Binary search narrowing m to exact value
mmin, mmax = ceil_div(n, f2), floor_div(n + B, f2)
while mmin < mmax:
    f = floor_div(2 * B, mmax - mmin)
    i = floor_div(f * mmin, n)
    f3 = ceil_div(i * n, mmin)
    if oracle((pow(f3, e, n) * c) % n):
        mmax = floor_div(i * n + B, f3)
    else:
        mmin = ceil_div(i * n + B, f3)
m = mmin
```

**Post-recovery OAEP decode:**
```python
from Crypto.Signature.pss import MGF1
maskedSeed = EM[1:hLen+1]
maskedDB = EM[hLen+1:]
seed = bytes(a ^ b for a, b in zip(maskedSeed, MGF1(maskedDB, hLen, HF)))
DB = bytes(a ^ b for a, b in zip(maskedDB, MGF1(seed, k - hLen - 1, HF)))
# DB[:hLen] should match lHash; rest is 0x00...0x01 || message
```

**Key insight:** Python's `or` short-circuits left-to-right. When expensive operations (PBKDF2, bcrypt, argon2) appear in chained conditions, the first condition becomes a timing oracle. RFC 8017 explicitly warns implementations must not let attackers distinguish error conditions — timing differences violate this.

**Detection:** RSA-OAEP with custom hash or slow KDF. Flask/Python backend. `/verify-token` or similar decryption endpoint returning generic errors. Timing differences between responses.

---

## Polynomial Hash with Trivial Root (Pragyan 2026)

**Pattern (!!Cand1esaNdCrypt0!!):** RSA signature scheme using polynomial hash `g(x,a,b) = x(x^2 + ax + b) mod P`.

**Vulnerability:** `g(0) = 0` for all parameters `a,b`. RSA signature of 0 is always 0 (`0^d mod n = 0`).

**Exploitation:** Craft message suffix so `bytes_to_long(prefix || suffix) = 0 (mod P)`:
```python
P = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF61  # 128-bit prime
# Compute required suffix value mod P
req = (-prefix_val * pow(256, suffix_len, P)) % P
# Brute-force partial bytes until all printable ASCII
while True:
    high = os.urandom(32).translate(printable_table)
    low_val = (req - int.from_bytes(high, 'big') * shift) % P
    low = low_val.to_bytes(16, 'big')
    if all(32 <= b <= 126 for b in low):
        suffix = high + low
        break
# Signature is simply 0
```

**General lesson:** Always check if hash function has trivial inputs (0, 1, -1). Factoring the polynomial often reveals these.

---

## Polynomial CRT in GF(2)[x] (Nullcon 2026)

**Pattern (Going in Circles, Nullcon 2026):** `r = flag mod f` where f is random GF(2) polynomial. Collect ~20 pairs, filter coprime, CRT combine.

See [advanced-math.md](./advanced-math.md) for GF(2)[x] polynomial arithmetic and CRT implementation.

---

## Affine Cipher over Non-Prime Modulus (Nullcon 2026)

**Pattern (Matrixfun, Nullcon 2026):** `c = A @ p + b (mod m)` with composite m. Chosen-plaintext difference attack. For composite modulus, solve via CRT in each prime factor field separately.

See [advanced-math.md](./advanced-math.md) for CRT approach and Gauss-Jordan implementation.

See also: [rsa-attacks-2.md](./rsa-attacks-2.md) for specialized RSA techniques (p=q bypass, cube root CRT, phi(n) multiple factoring, signature forgery, weak keygen, batch GCD, partial key recovery, CRT fault attack, homomorphic bypass).

---

## [来自实战] OvO — 超大e推导partial p + Coppersmith（长城杯决赛2024）

**技术模式**: e远大于n（e≈rr*n），说明e是由p/q/rr/kk构成的特殊形式；令rr=e//n，kk=rr-2，联立方程得p近似值，再用Coppersmith small_roots还原精确p。

**关键操作**:
1. 观察e的位数远超n：`rr = e // n`，`kk = rr - 2`
2. 原始关系式：`e = 65537 + kk*p + rr*(p+1)*(q+1) + 1`，展开为关于p的二次方程
3. sympy解方程得pbar（p的近似值，差约2^100以内）
4. SageMath Coppersmith：`f = x + pbar; x0 = f.small_roots(X=2^100, beta=0.4)[0]; p = x0 + pbar`
5. 得到精确p后：用真实e公式反算标准e=65537，RSA正常解密

**适用场景**: 遇到e位数接近或超过n时，先算rr=e//n判断是否为特殊构造；确认后列二次方程用sympy/numpy近似求解，再Coppersmith精化；beta=0.4表示p约为n^0.4大小

---

## [来自实战] hash — Python2.7内置hash逆推 + 乘法逆元（长城杯决赛2024）

**技术模式**: Python2.7的`hash(bytes)`是确定性64位线性变换（seed=0，乘1000003，模2^64），可通过乘法逆元逆向逐字节恢复7字节密钥，再SHA384 XOR解密flag。

**关键操作**:
1. Python2 hash算法：`x = (x * 1000003 ^ byte) & mask`，mask=(1<<64)-1，为可逆线性变换
2. 正向建表：预计算所有3字节前缀的hash值，存dict[hash3] = bytes3
3. 逆向：`ni = inverse(1000003, 1<<64)`，从已知hash值逐字节用`((r^b)*ni)&mask`反推
4. 爆破4层（各256）× 查表3层 = 恢复7字节key
5. Python2运行：`sha384(hexlify(key)).hexdigest()` → int ^ flag_int → long_to_bytes得明文

**适用场景**: 题目给出Python2 hash值作为密钥派生源时，直接用乘法逆元暴力反推；注意Python2 hash(str)在64位系统上是64位整数（不是32位）；最终输出需在Python2环境中运行

---

## [来自实战] CRYPTO01 — Boneh-Durfee攻击高位p/q已知 (网鼎杯2024青龙组)

**技术模式**: RSA N=p*q，已知p、q的高位部分（hint1=高位p，hint2=高位q）→ 用Boneh-Durfee格攻击恢复完整p/q。

**关键操作**:
1. 题目给出hint1（p的高若干位）、hint2（q的高若干位）
2. 使用Boneh-Durfee攻击脚本（基于LLL格基规约）：
   ```python
   delta = 299/1024  # 已知位数比例
   m = 7  # 格维度参数（根据题目调整）
   t = int((1-2*delta) * m)
   X = 2*floor(N^delta)
   # 构造多项式 f(x,y) = x*(hint2 + y) - N
   # 用LLL规约找小根
   ```
3. 恢复p、q后用`inverse(e, (p-1)*(q-1))`计算d → 解密flag
4. 工具：sagemath或现成Boneh-Durfee脚本（GitHub有多个实现）

**适用场景**: RSA题给出p/q部分高位 → Boneh-Durfee；已知位数≥N的0.292时攻击成功；delta参数=已知位/总位数

---

## [来自实战] CRYPTO02 — Pollard's rho分解大N (网鼎杯2024白虎组)

**技术模式**: RSA N较大但p-q差距适中 → Pollard's rho算法快速分解N。

**关键操作**:
1. N难以直接分解（如1024位），但p、q不是强素数
2. 用Pollard's rho：
   ```python
   from Crypto.Util.number import *
   def pollard_rho(n):
       x, y, d = 2, 2, 1
       f = lambda x: (x*x + 1) % n
       while d == 1:
           x = f(x)
           y = f(f(y))
           d = GCD(abs(x-y), n)
       return d
   p = pollard_rho(N)
   q = N // p
   ```
3. 分解后计算d → 解密

**适用场景**: N<2048位且题目无"strong primes"提示 → 先试Pollard's rho；比Fermat分解更通用；yafu工具内置此算法

---

## [来自实战] web03 — 近似等大素数p≈q分解SSH公钥 (网鼎杯2024朱雀组)

**技术模式**: SSH公钥对应RSA N=p*q，且p≈q（|p-q|很小如940）→ 从N开方附近搜索p。

**关键操作**:
1. 从wbStego隐写中提取SSH公钥（base64格式）
2. 解析公钥提取N、e（用`ssh-keygen -f key.pub -e -m pem`转PEM，再提取）
3. p≈q意味着`sqrt(N)`非常接近p：
   ```python
   from gmpy2 import isqrt
   s = isqrt(N)
   for i in range(1000000):  # 爆破范围
       p = s - i
       if N % p == 0:
           q = N // p
           break
   ```
4. 或用yafu的`factor(N)`直接分解（自动检测近素数）
5. 恢复私钥 → SSH登录

**适用场景**: SSH公钥题 + "close primes"提示 → 从sqrt(N)附近爆破；|p-q|<10^6时秒出；openssl生成弱密钥时可能出现此问题

---

## [来自实战] GCD杠上了 — 近似GCD格攻击恢复隐藏素数p (DASCTF)

**技术模式**: 四个样本 x_i = p*q_i + e_i（p是768bit隐藏素数，e_i是256bit小噪声），用LLL格攻击消去主项q_i，恢复差值 q_0*e_1 - q_1*e_0 等，再还原p。

**关键操作**:
1. 问题结构：x_i ≈ p*q_i（误差e_i < 2^256，而p*q≈2^1768）
2. 构造矩阵消去q_i主项：以x_0为基准，计算 q_0*x_i - q_i*x_0 = q_0*e_i - q_i*e_0（小量）
3. LLL矩阵（缩放以平衡格中向量大小）：
   ```python
   B = Matrix(ZZ, [
       [2^(rho+1), xs[1], xs[2], xs[3]],
       [0, -x0, 0, 0],
       [0, 0, -x0, 0],
       [0, 0, 0, -x0]
   ])
   L = B.LLL()
   ```
4. LLL规约后，某行首元素 = q_0 * 2^(rho+1)，提取得 q_0
5. 遍历 x_i // q_0 附近几个候选值作为p，验证p整除所有x_i（误差在[-2^255, 2^255]内）
6. 找到p后：`flag = "DASCTF{" + sha256(hex(p).encode()).hexdigest()[:32] + "}"`

**适用场景**: "多个x_i近似是p的倍数" = 近似GCD(Approximate GCD)问题；关键在于用LLL消主项后首元素直接给出q_0；噪声比rho/总长度<1/4时LLL有效；flag有时就是sha256(hex(p))

**适用场景**: 题目给出Python2 hash值作为密钥派生源时，直接用乘法逆元暴力反推；注意Python2 hash(str)在64位系统上是64位整数（不是32位）；最终输出需在Python2环境中运行
