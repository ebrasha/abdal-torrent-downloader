"""
 # Project Name: Abdal Torrent Downloader
 # Programmer: Ebrahim Shafiei
 # Programmer WebSite: https://hackers.zone/
 # Programmer Email: Prof.Shafiei@Gmail.com
 # License : MIT
 # Current Date : 2023-02-04
 # Current Time : 6:03 AM
 # File Description: for banner
"""
import os.path
from colorama import Fore, Style, Back, init

# init for Colorama
init()


banner = """

░█▀▀█ █▀▀▄ █▀▀▄ █▀▀█ █░░   ▀▀█▀▀ █▀▀█ █▀▀█ █▀▀█ █▀▀ █▀▀▄ ▀▀█▀▀ 
▒█▄▄█ █▀▀▄ █░░█ █▄▄█ █░░   ░▒█░░ █░░█ █▄▄▀ █▄▄▀ █▀▀ █░░█ ░░█░░ 
▒█░▒█ ▀▀▀░ ▀▀▀░ ▀░░▀ ▀▀▀   ░▒█░░ ▀▀▀▀ ▀░▀▀ ▀░▀▀ ▀▀▀ ▀░░▀ ░░▀░░

▒█▀▀▄ █▀▀█ █░░░█ █▀▀▄ █░░ █▀▀█ █▀▀█ █▀▀▄ █▀▀ █▀▀█ 
▒█░▒█ █░░█ █▄█▄█ █░░█ █░░ █░░█ █▄▄█ █░░█ █▀▀ █▄▄▀ 
▒█▄▄▀ ▀▀▀▀ ░▀░▀░ ▀░░▀ ▀▀▀ ▀▀▀▀ ▀░░▀ ▀▀▀░ ▀▀▀ ▀░▀▀
===============================================================
Welcome to Abdal Torrent Downloader 10.0.0
Programmer : Ebrahim Shafiei (EbraSha)
Mail: Prof.Shafiei@gmail.com
Github: https://github.com/ebrasha
"""


def banner_nit():
    print(Fore.GREEN + Style.DIM + f'{banner}')
    print(Style.RESET_ALL)
