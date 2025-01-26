import random

import sympy

cod = {
    ' ': 0,
    'a': 1, 'b': 2, 'c': 3, 'd': 4, 'e': 5, 'f': 6, 'g': 7, 'h': 8, 'i': 9, 'j': 10,
    'k': 11, 'l': 12, 'm': 13, 'n': 14, 'o': 15, 'p': 16, 'q': 17, 'r': 18, 's': 19,
    't': 20, 'u': 21, 'v': 22, 'w': 23, 'x': 24, 'y': 25, 'z': 26,
    'A': 27, 'B': 28, 'C': 29, 'D': 30, 'E': 31, 'F': 32, 'G': 33, 'H': 34, 'I': 35,
    'J': 36, 'K': 37, 'L': 38, 'M': 39, 'N': 40, 'O': 41, 'P': 42, 'Q': 43, 'R': 44,
    'S': 45, 'T': 46, 'U': 47, 'V': 48, 'W': 49, 'X': 50, 'Y': 51, 'Z': 52,
    '0': 53, '1': 54, '2': 55, '3': 56, '4': 57, '5': 58, '6': 59, '7': 60, '8': 61, '9': 62,
    '!': 63, '@': 64, '#': 65, '$': 66, '%': 67, '^': 68, '&': 69, '*': 70, '(': 71, ')': 72,
    '-': 73, '_': 74, '=': 75, '+': 76, '[': 77, ']': 78, '{': 79, '}': 80, '|': 81,
    '\\': 82, ':': 83, ';': 84, '"': 85, '\'': 86, '<': 87, '>': 88, ',': 89, '.': 90,
    '?': 91, '/': 92
}

values = list(cod.values())
keys = list(cod.keys())
k = 2
l = 3


def generate_large_primes():
    while True:
        p = random.randint(1, 200)
        q = random.randint(1, 200)

        # Ensure that p and q are distinct
        while p == q or abs(p - q) > 100:
            q = random.randint(100, 900)

        # Make sure p and q are prime and that 27^k < n < 27^l
        if sympy.isprime(p) and sympy.isprime(q) and (27**k < p*q < 27**l):
            return p, q


def generate_keys(bit_length):
    # Generate two large distinct primes
    p, q = generate_large_primes()
    # Calculate n
    n = p * q
    # Calculate phi(n)
    phi = (p - 1) * (q - 1)
    # Calculate the encription key (used for the PUBLIC key)
    # Calculate e, 1 < e < phi(n) and gcd(e, phi(n))=1
    e = random.randint(2, phi - 1)
    while not sympy.isprime(e) or sympy.gcd(e, phi) != 1:
        e = random.randint(2, phi - 1)
    # Calculate the decription key (used for the PRIVATE key)
    # Calculate d, d = e^-1 mod phi(n)
    # mod_inverse is the function that calculate the modular inverse of a number
    d = sympy.mod_inverse(e, phi)
    print("p = ", p, "\nq = ", q, "\nn = ", n, "\ne = ", e, "\nd = ", d)
    KE = (n, e)  # Encription key = PUBLIC KEY
    KD = (n, d)  # Decription key = PRIVATE KEY
    return KE, KD


def RSA_encrypt(word, n, e):
    # The plain text is completed with spaces, if necessary
    for i in range(len(word) % k + 1):
        word += ' '
    # The text is separated in blocks of k letters
    blocksK = []
    i = 0
    w = ''
    for c in word:
        if i < k:
            w += c
            i += 1
        else:
            blocksK.append(w)
            i = 1
            w = c
    # print("Blocks K: ", blocksK)
    # We calculate the equivalent codes for the blocks
    # b = ?1 * 27 + ?2, where ?1?2 is the block of k letters
    newCodes = []
    for w in blocksK:
        b = 27 * cod[w[0]] + cod[w[1]]
        newCodes.append(b)
    # print("Equivalents: ", newCodes)
    # We encrypt the equivalent codes like so:
    # c = b^e mod n, where b is the equivalent code for the block of letters
    encryption = []
    for b in newCodes:
        c = (b ** e) % n
        encryption.append(c)
    # print("Encryption: ", encryption)
    # We find the equivalent letters for the encrypted codes
    # c = ?1 * 27^2 + ?2 * 27 + ?3 => ?1?2?3, blocks of l letters
    blocksL = []
    for c in encryption:
        new_cod = ''
        l1 = values.index(c // (27 * 27))
        c -= l1 * (27 * 27)
        l2 = values.index(c // 27)
        c -= l2 * 27
        l3 = c
        new_cod += keys[l1] + keys[l2] + keys[l3]
        blocksL.append(new_cod)
    # print("Blocks L:", blocksL)
    # We put together the blocks of l letters
    cyphertext = ''
    for c in blocksL:
        cyphertext += c
    # print("Cyphertext: ", cyphertext)
    return cyphertext


def RSA_decrypt(word, n, d):
    # The text is completed with spaces, if necessary
    for i in range(len(word) % k + 1):
        word += ' '
    # The text is separated in blocks of l letters
    blocksL = []
    i = 0
    w = ''
    for c in word:
        if i < l:
            w += c
            i += 1
        else:
            blocksL.append(w)
            i = 1
            w = c
    # print("Blocks L: ", blocksL)
    # We calculate the equivalent codes for the blocks
    # b = ?1 * 27^2 + ?2 * 27 + ?3, where ?1?2?3 is the block of l letters
    newCodes = []
    for w in blocksL:
        b = 27 * 27 * cod[w[0]] + 27 * cod[w[1]] + cod[w[2]]
        newCodes.append(b)
    # print("Equivalents: ", newCodes)
    # We decrypt the equivalent codes like so:
    # c = b^d mod n, where b is the equivalent code for the block of letters
    decryption = []
    for b in newCodes:
        c = b ** d % n
        decryption.append(c)
    # print("Decryption: ", decryption)
    # We find the equivalent letters for the decrypted codes
    # c = ?1 * 27 + ?2 => ?1?2, blocks of k letters
    blocksK = []
    for c in decryption:
        new_cod = ''
        l1 = values.index(c // 27)
        c -= l1 * 27
        l2 = c
        new_cod += keys[l1] + keys[l2]
        blocksK.append(new_cod)
    # print("Blocks K:", blocksK)
    # We put together the blocks of k letters
    plaintext = ''
    for c in blocksK:
        plaintext += c
    # print("Plain text: ", plaintext)
    return plaintext


def validate(word):
    allowed_chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*()-_=+[]{}|\\:;\"'<>,.?/ "
    return all(c in allowed_chars for c in word)

def get_public_key():
    with open("website/public_key.txt", "r") as pub_file:
        n, e = map(int, pub_file.read().split())
    return n, e
