#/usr/bin/python3
# Ultroid - UserBot
# Copyright (C) 2020 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# Please read the GNU Affero General Public License in <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.

# Standalone file for facilitating local deploys.

import os

a = """
  _    _ _ _             _     _ 
 | |  | | | |           (_)   | |
 | |  | | | |_ _ __ ___  _  __| |
 | |  | | | __| '__/ _ \| |/ _  |
 | |__| | | |_| | | (_) | | (_| |
  \____/|_|\__|_|  \___/|_|\__,_|
"""

def start():

    clear_screen()
    check_for_py()

    print(f"{a}\n\n")
    print("Welcome to Ultroid, lets start setting up!\n\n")
    print("Cloning the repository...\n\n")
    try:
        os.system('git clone https://github.com/TeamUltroid/Ultroid && cd Ultroid')
    except Exception as e:
        print(f"ERROR\n{str(e)}")
    print("\n\nDone")
    os.system("cd Ultroid")
    clear_screen()
    print(a)
    print("\n\nLet's start!\n")

    # generate session if needed.
    sessionisneeded = input("Do you want to generate a new session, or have an old session string? [generate/skip]")
    if sessionisneeded == "generate":
        gen_session()
    elif sessionisneeded == "skip":
        pass
    else:
        print("Please choose \"generate\" to generate a session string, or \"skip\" to pass on.\n\nPlease run the script again!")
        exit(0)

    # start bleck megik
    print("\n\nLets start entering the variables.\n\n")
    varrs = ['API_ID', 'API_HASH', 'SESSION', 'BOT_USERNAME', 'BOT_TOKEN', 'REDIS_URI', 'REDIS_PASSWORD', 'LOG_CHANNEL']
    all_done = "# Ultroid Environment Variables.\n# Do not delete this file.\n\n"
    for i in varrs:
        all_done += do_input(i)
    clear_screen()
    print(a)
    print("\n\nHere are the things you've entered.\nKindly check.")
    print(all_done)
    isitdone = input("\n\nIs it all correct? [y/n]")
    if isitdone == "y":
        f = open('Ultroid/.env', "w")
        f.write(all_done)
        f.close
    elif isitdone == "n":
        print("Oh, let's redo these then -_-")
        start()
    else:
        f = open('Ultroid/.env', "w")
        f.write(all_done)
        f.close
        pass
    clear_screen()
    print("\nCongrats. All done!\nTime to start the bot!")
    print("\nInstalling requirements... This might take a while...")
    os.system("cd Ultroid")
    os.system('pip3 install -r local-requirements.txt')
    clear_screen()
    print(a)
    print("\nStarting Ultroid...")
    os.system("python3 -m pyUltroid")

def do_input(var):
    val = input(f"Enter your {var}: ")
    to_write = f"{var}={val}\n"
    return to_write

def clear_screen():
    # clear screen
    if os.name == 'posix':
        _ = os.system('clear')
    else:
        # for windows platfrom
        _ = os.system('cls')

def check_for_py():
    print("Please make sure you have python installed. \nGet it from http://python.org/\n\n")
    try:
        ch = int(input("Enter Choice:\n1. Continue, python is installed.\n2. Exit and install python.\n"))
    except:
        print("Please run the script again, and enter the choice as a number!!")
        exit(0)
    if ch == 1:
        pass
    elif ch==2:
        print("Please install python and continue!")
        exit(0)
    else:
        print("Weren't you taught how to read? Enter a choice!!")
        return 

def gen_session():
    print("\nProcessing...")
    os.system("cd Ultroid && python3 resources/session/ssgen.py")
    return

start()
