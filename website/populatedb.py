import json
import random
import sqlite3
from datetime import datetime
from faker import Faker

from rsa_encryption import RSA_encrypt
from honeywords import generate_honeywords

# Setup for Faker to generate user data
fake = Faker()

# SQLite database file (adjust to your database connection details if using a different DB)
DB_PATH = "../instance/database.db"


def get_public_key():
    with open("public_key.txt", "r") as pub_file:
        n, e = map(int, pub_file.read().split())
    return n, e

def generate_account_number():
    """Generate a 10-digit account number prefixed by 'ROBTRL'."""
    return f"ROBTRL{random.randint(1000000000, 9999999999)}"


def generate_honey_words(real_password):
    return generate_honeywords(real_password, num_honeywords=50)


def populate_database():
    # Connect to the database
    connection = sqlite3.connect(DB_PATH)
    cursor = connection.cursor()

    try:
        # Add 50 users and corresponding account
        print("Adding users and account...")
        users = []
        account = []
        encrypted_password = RSA_encrypt("password123", *get_public_key())
        for _ in range(50):
            email = fake.email()
            first_name = fake.first_name()
            last_name = fake.last_name()
            password = "password123"
            honey_words = json.dumps(generate_honey_words(password))
            date_created = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # Insert user into the users table
            cursor.execute(
                """
                INSERT INTO user (email, first_name, last_name, password, date_created, honey_words)
                VALUES ( ?, ?, ?, ?, ?, ?);
                """,
                (email, first_name, last_name, encrypted_password, date_created, honey_words)
            )
            user_id = cursor.lastrowid

            account_number = generate_account_number()
            balance = round(random.uniform(500, 10000), 2)
            currency = "EUR"

            cursor.execute(
                "INSERT INTO account (account_number, balance, currency, user_id) VALUES (?, ?, ?, ?);",
                (account_number, balance, currency, user_id)
            )
            account_id = cursor.lastrowid

            users.append(user_id)
            account.append(account_id)

        # Commit users and account
        connection.commit()
        print(f"Added {len(users)} users and account successfully.")

        # Add 100 random transactions
        print("Adding random transactions...")
        for _ in range(100):
            # Pick random account for the transaction
            from_account = random.choice(account)
            to_account = random.choice(account)

            # Ensure sender and receiver account are not the same
            while from_account == to_account:
                to_account = random.choice(account)

            # Determine the transaction amount
            cursor.execute("SELECT balance FROM account WHERE id = ?;", (from_account,))
            from_account_balance = cursor.fetchone()[0]
            amount = round(random.uniform(10, min(from_account_balance, 500)), 2)  # Max transaction is 500
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # Update account balances
            cursor.execute("UPDATE account SET balance = balance - ? WHERE id = ?;", (amount, from_account))
            cursor.execute("UPDATE account SET balance = balance + ? WHERE id = ?;", (amount, to_account))

            # Insert the transaction into the transaction table
            cursor.execute("""
                INSERT INTO transactions (account_id_from, account_id_to, amount, timestamp)
                VALUES (?, ?, ?, ?);
            """, (from_account, to_account, amount, timestamp))

        # Commit the transactions
        connection.commit()
        print("Added 100 random transactions successfully.")
        print("Database population complete!")

    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
        connection.rollback()  # Rollback changes on error
    finally:
        connection.close()  # Ensure database connection is closed


if __name__ == "__main__":
    print("Populating database...")
    populate_database()
