# Run this script once to generate and save the keys.

# from rsa_encryption import generate_keys  # Assuming your RSA logic is in `rsa_encryption.py`
#
# def save_keys():
#     KE, KD = generate_keys(10)
#     with open("public_key.txt", "w") as pub_file:
#         pub_file.write(f"{KE[0]} {KE[1]}")  # Save n and e
#     with open("private_key.txt", "w") as priv_file:
#         priv_file.write(f"{KD[0]} {KD[1]}")  # Save n and d
#
# if __name__ == "__main__":
#     save_keys()