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
    "enhancer==0.3.4",
    "telegraph"
]

OPT_PACKAGES = {
    "bs4":"Used for site-scrapping (used in commands like - .gadget and many more)",
    "yt-dlp": "Used for Youtuble Related Downloads...",
    "PIL": "Used for Image-Conversion related task. (size - approx 50mb ) (required for kang, convert and many more.)"
}

APT_PACKAGES = [
    "ffmpeg",
    "neofetch",
    "mediainfo"
]

DISCLAIMER_TEXT = ""

COPYRIGHT = f"©️ TeamUltroid {date.year}"

HEADER = """
╔╗ ╔╗╔╗  ╔╗            ╔╗
║║ ║║║║ ╔╝╚╗           ║║
║║ ║║║║ ╚╗╔╝╔═╗╔══╗╔╗╔═╝║
║║ ║║║║  ║║ ║╔╝║╔╗║╠╣║╔╗║
║╚═╝║║╚╗ ║╚╗║║ ║╚╝║║║║╚╝║
╚═══╝╚═╝ ╚═╝╚╝ ╚══╝╚╝╚══╝\n
"""

INFO_TEXT = """
# Important points to know.

1. This script will just install basic requirements because of which some command whose requirements are missing won't work. You can view all optional requirements in (./resources/startup/optional-requirements.txt)

2. You can install that requirement whenever you want with 'pip install' (a very basic python+bash knowledge is required.)

3. Some of the plugins are disabled for 'Termux Users' to save resources (by adding in EXCLUDE_OFFICIAL).
   - Read More - https://t.me/UltroidUpdates/36
   - Also, way to enable the disabled plugins is mentioned in that post.

   # Disabled Plugins Name
    -    autocorrect    -     compressor
    -    Gdrive         -     instagram
    -    nsfwfilter     -     glitch
    -    pdftools       -     writer
    -    youtube        -     megadl
    -    autopic        -     nightmode
    -    blacklist      -     forcesubscribe

4. You can't use 'VCBOT' on Termux.

5. You can't use 'MongoDB' on Termux (Android).

* Hope you are smart enought to understand.
* Enter 'A' to Continue, 'E' to Exit..\n
"""

def ask_and_wait(text, header:bool=False):
    if header:
        text = with_header(text)
    print(text + "\nPress 'ANY Key' to Continue or 'Ctrl+C' to exit...\n")
    input("")


def with_header(text):
    return HEADER + "\n\n" + text

def yes_no_apt():
    yes_no = input("").strip().lower()
    if yes_no in ["yes", "y"]:
        return True
    elif yes_no in ["no", "n"]:
        return False
    print("Invalid Input\nRe-Enter: ")
    return yes_no_apt()
                

def ask_process_info_text():
    strm = input("").lower().strip()
    if strm == "e":
        print("Exiting...")
        exit(0)
    elif strm == "a":
        pass
    else:
        print("Invalid Input")
        print("Enter 'A' to Continue or 'E' to exit...")
        ask_process_info_text()


def ask_process_apt_install():
    strm = input("")
    if strm == "e":
        print("Exiting...")
        exit(0)
    elif strm == "a":
        for apt in APT_PACKAGES:
            print(f"* Do you want to install '{apt}'? [Y/N] ")
            if yes_no_apt():
                print(f"Installing {apt}...")
                system(f"apt install {apt} -y")
            else:
                print("- Discarded {apt}.")
    elif strm == "i":
        names = " ".join(APT_PACKAGES)
        print("Installing all apt-packages...")
        system(f"apt install {names} -y")
    else:
        print("Invalid Input\n* Enter Again...")
        ask_process_apt_install()

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

- ULTROID Termux Installation -
  The Main Aim of this script is to deploy Ultroid with basic requirements and save your phone resources.


{COPYRIGHT}
    """
)
sleep(5)
system("clear")

print(with_header(INFO_TEXT))
ask_process_info_text()

system("clear")

print(with_header("Installing Mandatory requirements..."))
all_ = "".join(f" {pip}" for pip in MANDATORY_REQS)
system(f"pip install{all_}")

system("clear")
print(with_header("\n# Moving toward Installing Apt-Packages\n\n"))
print("---Enter---")
print(" - A = 'Ask Y/N for each'.")
print(" - I = 'Install all'")
print(" - S = 'Skip Apt installation.'")
print(" - E = Exit.\n")
ask_process_apt_install()

print("#EXTRA Features...\n")
print("* Do you want to get Ultroid Logs in Colors? [Y/N] ")
inp = input("").strip().lower()
if inp in ["yes", "y"]:
    print("*Spoking the Magical Mantras*")
    system("pip install coloredlogs")

print("\nYou are all Done! :party")
sleep(0.2)
print("Use 'bash startup' to try running Ultroid.")
sleep(0.5)
print("\nYou can head over to @UltroidSupport, if you get stucked somewhere.")
sleep(0.5)
print("\nMade with :love by @TeamUltroid...")
