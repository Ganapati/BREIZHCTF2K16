from mifare import MIFARE, CardNotFoundError
import sqlite3
import sys
import time
import curses
import curses.textpad
import hashlib
import string

FLAG = "BZHCTF{NEW_TECH_SAME_VULNZ}"

class NFCError(Exception):
    pass

def read_card(mifare):
    try:
        data = mifare.read()
        if data == FLAG:
            raise Exception()
        (login, password) = data.split(":", 1)
        hash = password.rstrip(' \t\r\n\0')
        return (login.rstrip(' \t\r\n\0'), hash)
    except Exception, e:
        if e.__class__.__name__ != "CardNotFoundError":
            raise NFCError("Error reading data")

def main(con, mifare):
    message = ""
    try:
        (login, password) = read_card(mifare)
        login = login.replace("'", "\\'")
        m = hashlib.md5()
        m.update(password)
        password = m.digest()
        try:
            req = "SELECT flag from flag where login='"+login+"' and (password='"+password+"')"
            password = req
            cur.execute(req)
            data = cur.fetchone()
            message = "Sorry !"
        except:
            data = None

        if data is None:
            response = "Verification Failed"
            message = "Token : %s" % repr(password)
        else:
           data = data[-1]
           if data == "SUCCESS":
               response = "Welcome Admin !"
               message = "Congratz !"
               mifare.write(FLAG)
           else:
               response = data
        return (message, response)
    except TypeError:
        raise CardNotFoundError()
    except CardNotFoundError, e:
        if e.__class__.__name__ != "CardNotFoundError":
            raise NFCError("Error reading data")

if __name__ == "__main__":
    mifare = MIFARE()
    con = sqlite3.connect('chall.db')
    cur = con.cursor()
    screen = curses.initscr()

    while True:
        response = "Welcome To Super Secure Wireless Zone"
        message = "Waiting for card..."
        try:
            error = ""
            (message, response) = main(cur, mifare)
        except NFCError:
            response = "ERROR :"
            message = "INVALID CARD"
        except CardNotFoundError:
            pass
        except:
            pass

        screen.border(0)
        screen.addstr(12, 20, response)
        screen.addstr(14, 20, message)
        screen.refresh()
        screen.clear()
        time.sleep(0.2)

