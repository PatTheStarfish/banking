import random
import sqlite3

conn = sqlite3.connect("card.s3db")
cur = conn.cursor()
cur.execute("CREATE TABLE IF NOT EXISTS card ("
            "   id INTEGER,"
            "   number TEXT,"
            "   pin TEXT,"
            "   balance INTEGER DEFAULT 0"
            ");")
conn.commit()


class BankingSystem:

    def __init__(self):
        self.state = "start"
        self.current_user = None

    def print_menu(self):
        if self.state == "start":
            print("1. Create an account")
            print("2. Log into account")
            print("0. Exit")
        elif self.state == "account":
            print("1. Balance")
            print("2. Add income")
            print("3. Do transfer")
            print("4. Close account")
            print("5. Log out")
            print("0. Exit")
        else:
            print("Incorrect state")
            exit(-1)

    def create_account(self):
        cur.execute("SELECT * FROM card;")
        cards = cur.fetchall()
        customer_number = len(cards)
        card_number_raw = "400000" + str(customer_number).zfill(9)
        temp = [int(x) for x in card_number_raw]
        temp[::2] = [2 * x for x in temp[::2]]
        temp = [x - 9 if x > 9 else x for x in temp]
        checksum = 10 - (sum(temp) % 10)
        if checksum == 10:
            checksum = 0
        card_number = card_number_raw + str(checksum)
        card_pin = ""
        for _ in range(4):
            card_pin += str(random.randrange(10))
        cur.execute(f"INSERT INTO card (id, number, pin)"
                    f"VALUES ({len(cards)}, {card_number}, {card_pin});")
        conn.commit()
        print()
        print("Your card has been created")
        print("Your card number:")
        print(card_number)
        print("Your card PIN:")
        print(card_pin)
        print()
        self.start_menu()

    def authenticate_user(self):
        print("Enter your card number:")
        user_input = input()
        cur.execute(f"SELECT id, number, pin FROM card WHERE number = {user_input};")
        query = cur.fetchall()
        if query:
            if user_input == query[0][1]:
                self.current_user = query[0][0]
                print("Enter your PIN:")
                user_input = input()
                if user_input == query[0][2]:
                    self.state = "account"
                    print("You have successfully logged in!")
                    return True
                else:
                    print("Wrong card number or PIN!")
                    return False
            else:
                print("Enter your PIN:")
                input()
                print("Wrong card number or PIN!")
                return False
        else:
            print("Enter your PIN:")
            input()
            print("Wrong card number or PIN!")
            return False

    def print_balance(self):
        cur.execute(f"SELECT balance FROM card WHERE id = {self.current_user};")
        balance = cur.fetchall()
        print("Balance:", balance[0][0])

    def logout_user(self):
        self.state = "start"
        print("You have successfully logged out!")
        self.start_menu()

    def start_menu(self):
        self.print_menu()
        while True:
            user_input = int(input())
            if user_input == 0:
                self.exit_system()
            elif user_input == 1:
                self.create_account()
            elif user_input == 2:
                if self.authenticate_user():
                    self.state = "account"
                    self.account_menu()

    def account_menu(self):
        self.print_menu()
        while True:
            user_input = int(input())
            if user_input == 0:
                self.exit_system()
            elif user_input == 1:
                self.print_balance()
            elif user_input == 2:
                self.add_income()
            elif user_input == 3:
                self.do_transfer()
            elif user_input == 4:
                self.close_account()
            elif user_input == 5:
                self.logout_user()

    def add_income(self):
        print("Enter income:")
        user_input = int(input())
        cur.execute(f"SELECT * FROM card WHERE id = {self.current_user};")
        query = cur.fetchall()
        balance = query[0][3] + user_input
        cur.execute(f"DELETE FROM card WHERE id = {self.current_user};")
        cur.execute(f"INSERT INTO card "
                    f"VALUES ({query[0][0]},{query[0][1]},{query[0][2]},{balance});")
        conn.commit()
        print("Income was added!")
        self.account_menu()

    def close_account(self):
        cur.execute(f"DELETE FROM card WHERE id = {self.current_user};")
        conn.commit()
        print("The account has been closed!")
        self.state = "start"
        self.start_menu()

    def check_luhn(self, number):
        temp = [int(x) for x in number[:-1]]
        temp[::2] = [2 * x for x in temp[::2]]
        temp = [x - 9 if x > 9 else x for x in temp]
        checksum = 10 - (sum(temp) % 10)
        if checksum == 10:
            checksum = 0
        if int(number[-1]) == checksum:
            return True
        else:
            return False

    def do_transfer(self):
        print("Transfer")
        print("Enter card number:")
        user_input = input()
        cur.execute(f"SELECT * FROM card WHERE id = {self.current_user};")
        user_data = cur.fetchall()
        cur.execute(f"SELECT * FROM card;")
        query = cur.fetchall()
        if not self.check_luhn(user_input):
            print("Probably you made a mistake in the card number. Please try again!")
            self.account_menu()
        if user_input == user_data[0][1]:
            print("You can't transfer money to the same account!")
            self.account_menu()
        account_numbers = [x[1] for x in query]
        if user_input not in account_numbers:
            print("Such a card does not exist.")
            self.account_menu()
        recipient_number = user_input
        print(recipient_number)
        print("Enter how much money you want to transfer:")
        user_input = int(input())
        if user_data[0][3] < user_input:
            print("Not enough money!")
            self.account_menu()
        cur.execute(f"SELECT * FROM card WHERE number = {recipient_number}")
        recipient_data = cur.fetchall()
        user_balance = user_data[0][3] - user_input
        cur.execute(f"DELETE FROM card WHERE id = {self.current_user};")
        cur.execute(f"INSERT INTO card "
                    f"VALUES({user_data[0][0]}, {user_data[0][1]}, {user_data[0][2]}, {user_balance});")
        recipient_balance = recipient_data[0][3] + user_input
        cur.execute(f"DELETE FROM card WHERE id = {recipient_data[0][0]}")
        cur.execute(f"INSERT INTO card "
                    f"VALUES({recipient_data[0][0]}, {recipient_data[0][1]},"
                    f" {recipient_data[0][2]}, {recipient_balance});")
        conn.commit()
        print("Success!")
        self.account_menu()

    def exit_system(self):
        print("Bye!")
        exit(0)


bank = BankingSystem()
bank.start_menu()
