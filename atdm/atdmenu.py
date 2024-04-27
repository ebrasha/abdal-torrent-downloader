"""
 # Project Name: Abdal Torrent Downloader
 # Programmer: Ebrahim Shafiei
 # Programmer WebSite: https://hackers.zone/
 # Programmer Email: Prof.Shafiei@Gmail.com
 # License : MIT
 # Current Date : 2023-02-07
 # Current Time : 5:53 AM
 # File Description: no description
"""
from colorama import Fore, Style, Back, init
from atdm import banner
from atdm import atdtools
from atdm import torrentmgr

# init for Colorama
init()


class MainATD:
    def __init__(self):
        atdtools.clear()
        torrentmgr.torrent_files_storage_hndl()
        banner.banner_nit()
        print(Fore.MAGENTA + Style.DIM)
        print(f"1. Download Torrent With Single File")
        print(f"2. Download Torrent With Multi File")
        print(f"3. Download Torrent With Single Magnet Link")
        print(f"4. Download Torrent With Multi Magnet Link")
        print(f"5. Exit")
        print(Style.RESET_ALL)

    def main_menu(self):
        get_opt = input()
        if get_opt == "1":
            torrentmgr.torrent_file_downloader()
        elif get_opt == "2":
            torrentmgr.torrent_multi_file_downloader()
        elif get_opt == "3":
            torrentmgr.torrent_magnet_downloader()
        elif get_opt == "4":
            torrentmgr.torrent_multi_magnet_downloader()
        elif get_opt == "5":
            exit()
        else:
            print(Fore.RED + f"Wrong Option Selected")
            print(Style.RESET_ALL)
