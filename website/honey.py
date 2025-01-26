import random
import string

# Some common "leet speak" or visually similar substitutions
LEET_SUBSTITUTIONS = {
    'a': ['@', '4'],
    'e': ['3'],
    'i': ['1', '!'],
    'o': ['0'],
    's': ['5', '$'],
    'l': ['1', 'I'],
    't': ['7'],
    'g': ['9']
}


def random_case_swap(char):
    """
    Randomly flip the case of an alphabetic character.
    """
    if char.isalpha():
        return char.lower() if char.isupper() else char.upper()
    return char


def leet_substitution(char):
    """
    If the character has a known leet substitution, pick one at random.
    Otherwise, return it unchanged.
    """
    lower_char = char.lower()
    if lower_char in LEET_SUBSTITUTIONS:
        return random.choice(LEET_SUBSTITUTIONS[lower_char])
    return char


def random_insert(password):
    """
    Insert a random character somewhere in the password.
    """
    chars = string.ascii_letters + string.digits + "!@#$%^&*()_-+=<>?/{}[]"
    insert_char = random.choice(chars)
    pos = random.randint(0, len(password))
    return password[:pos] + insert_char + password[pos:]


def random_delete(password):
    """
    Delete one character from the password if it's not empty.
    """
    if not password:
        return password
    pos = random.randint(0, len(password) - 1)
    return password[:pos] + password[pos + 1:]


def small_typo_transform(password):
    """
    Apply one or two small changes (case swap, leet substitution, insertion, or deletion)
    to create a 'similar' password.
    """
    new_pwd = list(password)
    # Decide how many changes to make (1 or 2)
    changes_count = random.randint(1, 2)

    for _ in range(changes_count):
        # Pick a random type of change
        change_type = random.choice(["case", "leet", "insert", "delete"])

        if change_type == "case":
            if len(new_pwd) > 0:
                idx = random.randrange(len(new_pwd))
                new_pwd[idx] = random_case_swap(new_pwd[idx])

        elif change_type == "leet":
            if len(new_pwd) > 0:
                idx = random.randrange(len(new_pwd))
                new_pwd[idx] = leet_substitution(new_pwd[idx])

        elif change_type == "insert":
            # Rebuild as a string, then insert
            tmp_pwd = "".join(new_pwd)
            tmp_pwd = random_insert(tmp_pwd)
            new_pwd = list(tmp_pwd)

        elif change_type == "delete":
            # Rebuild as a string, then delete
            tmp_pwd = "".join(new_pwd)
            tmp_pwd = random_delete(tmp_pwd)
            new_pwd = list(tmp_pwd)

    return "".join(new_pwd)


def generate_honeywords(real_password, num_honeywords=5):
    """
    Generate a list containing the real password plus (num_honeywords - 1)
    'similar' decoys. Shuffle before returning.

    :param real_password: The actual password
    :param num_honeywords: How many total passwords to output (including real one)
    :return: A list of length num_honeywords with 1 real password + decoys
    """
    if num_honeywords < 1:
        raise ValueError("num_honeywords must be >= 1")

    honeywords = []

    # Generate decoys
    for _ in range(num_honeywords - 1):
        decoy = small_typo_transform(real_password)
        honeywords.append(decoy)

    random.shuffle(honeywords)

    return honeywords


# Quick demo
if __name__ == "__main__":
    real = "MyP@ssw0rd123"
    honey_list = generate_honeywords(real, num_honeywords=50)
    print("Honeywords:")
    for pw in honey_list:
        print(" ", pw)
