import random
import sqlite3

# sqlite 3 connect & table CARD create
conn = sqlite3.connect('card.s3db')
cur = conn.cursor()
cur.execute("DROP TABLE IF EXISTS card;")
cur.execute('''CREATE TABlE card (id INTEGER, number TEXT, pin TEXT, balance INTEGER DEFAULT 0)''')
conn.commit()

balance = 0
id_db = 0


def card_database(card_number_db, pin_db, balance_db):
    global id_db
    id_db += 1
    cur.execute("INSERT INTO card VALUES (?, ?, ?, ?)", (id_db, card_number_db, pin_db, balance_db))
    conn.commit()


def luhn_alg(card_number_15_digits):
    card_num_list = []
    for y in str(card_number_15_digits):
        card_num_list.append(int(y))
    # print(card_num_list)

    for y in range(15):
        if y % 2 == 0:
            card_num_list[y] = card_num_list[y] * 2
    # print(card_num_list)

    for y in range(15):
        if card_num_list[y] > 9:
            card_num_list[y] -= 9
    # print(card_num_list)

    a = 0
    for y in card_num_list:
        a += y
    # print(a)

    if a % 10 == 0:
        last_digit = 0
    else:
        last_digit = (((a // 10) + 1) * 10) - a
    # print(last_digit)
    # print(str(card_number_15_digits) + str(last_digit))
    return str(card_number_15_digits) + str(last_digit)


def card_validity(card_number_16_dig):
    card_num_list = []
    for y in str(card_number_16_dig):
        card_num_list.append(str(y))

    if len(card_num_list) != 16:
        print('Such a card does not exist.')
        return False

    card_num_list.pop()

    a = ''
    card_number_15_dig = a.join(card_num_list)
    if str(card_number_16_dig) != str(luhn_alg(card_number_15_dig)):
        print('Probably you made a mistake in the card number. Please try again!')
        return False
    else:
        return True


while True:
    print('1. Create an account')
    print('2. Log into account')
    print('0. Exit')

    action = input()

    if action == '0':
        print()
        print('Bye!')
        quit()

    if action == '1':
        print()
        print('Your card has been created')
        print('Your card number:')
        card_number = int('400000' + str(random.random())[2:11])
        card_number = int(luhn_alg(card_number))
        print(card_number)

        print('Your card PIN:')
        card_pin = str(random.random())
        card_pin = card_pin[2:6]
        print(card_pin)
        print()

        card_database(str(card_number), card_pin, balance)

    if action == '2':
        print()
        print('Enter your card number:')
        inp_card_num = str(input())
        print('Enter your PIN:')
        inp_card_pin = str(input())

        cur.execute("SELECT number=:num FROM card", {'num': inp_card_num})
        check = cur.fetchall()
        i = 0
        for x in check:
            if x[0]:
                i += 1

        check_pin = False

        if i == 1:
            cur.execute("SELECT pin=:pin FROM card WHERE number=:num", {'num': inp_card_num, 'pin': inp_card_pin})
            check_pin = cur.fetchone()[0]

        if check_pin:
            print()
            print('You have successfully logged in!')

            while True:
                print()
                print('1. Balance')
                print('2. Add income')
                print('3. Do transfer')
                print('4. Close account')
                print('5. Log out')
                print('0. Exit')
                logged_action = input()
                print()
                if logged_action == '1':
                    cur.execute("SELECT balance FROM card WHERE number=:num", {'num': str(inp_card_num)})
                    balance = cur.fetchone()[0]
                    print(f'Balance: {balance}')

                elif logged_action == '2':
                    print('Enter income:')
                    income = int(input())
                    cur.execute("UPDATE card SET balance=balance+(?) WHERE number=(?)", (income, str(inp_card_num)))
                    conn.commit()
                    print('Income was added!')

                elif logged_action == '3':
                    print('Transfer')
                    print('Enter card number:')
                    transfer_to = input()

                    if str(transfer_to) == str(inp_card_num):
                        print("You can't transfer money to the same account!")

                    elif card_validity(transfer_to):
                        cur.execute("SELECT number=:num FROM card", {'num': transfer_to})
                        check = cur.fetchall()
                        i = 0
                        for x in check:
                            if x[0]:
                                i += 1
                        if i == 1:
                            print('Enter how much money you want to transfer:')
                            transfer_money = input()
                            cur.execute("SELECT balance FROM card WHERE number=:num", {'num': str(inp_card_num)})
                            current_balance = cur.fetchone()[0]
                            if (int(current_balance) - int(transfer_money)) < 0:
                                print('Not enough money!')
                            else:
                                cur.execute("UPDATE card SET balance=balance-(?) WHERE number=(?)", (transfer_money, str(inp_card_num)))
                                conn.commit()
                                cur.execute("UPDATE card SET balance=balance+(?) WHERE number=(?)", (transfer_money, str(transfer_to)))
                                conn.commit()
                                print('Success!')
                        else:
                            print('Such a card does not exist.')

                elif logged_action == '4':
                    cur.execute("DELETE FROM card WHERE number=:num", {'num': str(inp_card_num)})
                    conn.commit()
                    print('The account has been closed!')
                    print()
                    break
                elif logged_action == '5':
                    print('You have successfully logged out!')
                    print()
                    break
                if logged_action == '0':
                    print('Bye!')
                    quit()
        else:
            print()
            print('Wrong card number or PIN!')
            print()
