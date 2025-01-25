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

# SQL script to insert users, accounts, and transactions
# SQL script to insert users, accounts, and transactions
import sqlite3

from website.rsa_encryption import RSA_encrypt

# Path to the SQLite database
db_path = "../instance/database.db"

sql_script = """
-- Insert 50 users
INSERT INTO user (email, password, first_name, last_name, honey_words)
VALUES
    {users};

-- Insert 50 accounts
INSERT INTO account (user_id, balance, currency, account_number)
VALUES
    {accounts};

-- Insert 50 transactions
INSERT INTO transaction (account_id_from, account_id_to, amount)
VALUES
    {transactions};
"""

# Generate test data
with open("public_key.txt", "r") as pub_file:
    n, e = map(int, pub_file.read().split())
users = [
    (f"user{i}@example.com", RSA_encrypt("password123", n, e), f"First{i}", f"Last{i}", "word1,word2,word3")
    for i in range(1, 51)
]
accounts = [
    (i, round(1000.0 * i, 2), "USD", f"ACCT{i:04d}")
    for i in range(1, 51)
]
transactions = [
    (i, i + 1 if i < 50 else 1, round(100.0 * i, 2))
    for i in range(1, 51)
]

# Format the data for SQL
formatted_users = ",\n    ".join([str(user) for user in users])
formatted_accounts = ",\n    ".join([str(account) for account in accounts])
formatted_transactions = ",\n    ".join([str(transaction) for transaction in transactions])

# Replace placeholders in the SQL script
sql_script = sql_script.format(
    users=formatted_users,
    accounts=formatted_accounts,
    transactions=formatted_transactions
)

def run_inserts():
    try:
        print("Inserting data into the database...")
        # Connect to the database and execute the script
        connection = sqlite3.connect(db_path)
        print("script is: " + sql_script)
        cursor = connection.cursor()
        cursor.executescript(sql_script)
        connection.commit()
        connection.close()
        return "Data inserted successfully!"
    except Exception as e:
        return f"An error occurred: {e}"

run_inserts()
