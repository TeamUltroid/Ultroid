from os import system
from time import sleep
from datetime import date

# clear screen
system("clear")

MANDATORY_REQS = [
    "https://github.com/New-dev0/Telethon/archive/Artifact.zip",
    "https://github.com/TeamUltroid/pyUltroid/archive/dev.zip",
#   "py-Ultroid==2022.2.10",
    "gitpython",
]

DISCLAIMER_TEXT = ""

COPYRIGHT = f"©️ TeamUltroid {date.year}"

ABOUT_TEXT = """
- ULTROID Termux Installation -
  The Main Aim of this script is to deploy Ultroid with basic requirements and save your phone resources.
"""

HEADER = """
╔╗ ╔╗╔╗  ╔╗            ╔╗
║║ ║║║║ ╔╝╚╗           ║║
║║ ║║║║ ╚╗╔╝╔═╗╔══╗╔╗╔═╝║
║║ ║║║║  ║║ ║╔╝║╔╗║╠╣║╔╗║
║╚═╝║║╚╗ ║╚╗║║ ║╚╝║║║║╚╝║
╚═══╝╚═╝ ╚═╝╚╝ ╚══╝╚╝╚══╝\n\n
"""


def ask_and_wait(text, header:bool=False):
    if header:
        text = with_header(text)
    print(text + "\nPress 'ANY Key' to Continue or 'Ctrl+C' to exit...\n")
    input("")


def with_header(text):
    return HEADER + "\n\n" + text

# ------------------------------------------------------------------------------------------ #

print(
    f"""
 _____________ 
 ▄▄   ▄▄ ▄▄▄     ▄▄▄▄▄▄▄ ▄▄▄▄▄▄   ▄▄▄▄▄▄▄ ▄▄▄ ▄▄▄▄▄▄  
█  █ █  █   █   █       █   ▄  █ █       █   █      █ 
█  █ █  █   █   █▄     ▄█  █ █ █ █   ▄   █   █  ▄    █
█  █▄█  █   █     █   █ █   █▄▄█▄█  █ █  █   █ █ █   █
█       █   █▄▄▄  █   █ █    ▄▄  █  █▄█  █   █ █▄█   █
█       █       █ █   █ █   █  █ █       █   █       █
█▄▄▄▄▄▄▄█▄▄▄▄▄▄▄█ █▄▄▄█ █▄▄▄█  █▄█▄▄▄▄▄▄▄█▄▄▄█▄▄▄▄▄▄█ 

{COPYRIGHT}
    """
)
sleep(2)
system("clear")

ask_and_wait(ABOUT_TEXT)
sleep(5)

print("Installing Mandatory requirements...")
all_ = "".join(f" {pip}" for pip in MANDATORY_REQS)
system(f"pip install{all_}")
