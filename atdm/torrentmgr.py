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

import os.path
from colorama import Fore, Style, Back, init
from atdm import banner
from atdm import atdtools
from atdm import pubvars
from atdm import atdmenu
from torrentp import TorrentDownloader

# init for Colorama
init()


def torrent_files_storage_hndl():
    if not os.path.exists(pubvars.TORRENT_FILE_DIR):
        os.makedirs(pubvars.TORRENT_FILE_DIR)
    if not os.path.exists(pubvars.DOW_FILE_DIR):
        os.makedirs(pubvars.DOW_FILE_DIR)


def torrent_file_downloader():
    try:
        atdtools.clear()
        banner.banner_nit()
        current_working_directory = os.getcwd()
        total_file_counter = len(os.listdir(current_working_directory))
        counter = 0
        dic_torrent_file = {}
        if total_file_counter != 0:
            for file in os.listdir(current_working_directory):
                if file.endswith(".torrent"):
                    counter += 1
                    print(str(counter) + ". " + file)
                    dic_torrent_file[str(counter)] = file
        print(Fore.YELLOW + Style.DIM)
        torrent_file_name = input(f"Please Select The torrent file name: ")
        while torrent_file_name == "":
            torrent_file_name = input(f"Please Select The torrent file name: ")
        atdtools.clear()
        banner.banner_nit()
        print(Style.RESET_ALL)
        print(Fore.GREEN + Style.DIM)
        torrent_file = TorrentDownloader(dic_torrent_file[torrent_file_name], pubvars.DOW_FILE_DIR)
        torrent_file.start_download()
    except:
        print(Style.RESET_ALL)
        print(Fore.RED + Style.DIM)
        print("Check The Torrent File or Enter the correct file address!! ")
        print(Style.RESET_ALL)
        pass
    print(Style.RESET_ALL)


def torrent_multi_file_downloader():
    if not os.path.exists(pubvars.TORRENT_FILE_DIR):
        os.makedirs(pubvars.TORRENT_FILE_DIR)
    # Get all toorent files
    total_file_counter = len(os.listdir(pubvars.TORRENT_FILE_DIR))
    current_file_counter = 0
    if total_file_counter != 0:
        for file in os.listdir(pubvars.TORRENT_FILE_DIR):
            # check only text files
            if file.endswith('.torrent'):
                atdtools.clear()
                banner.banner_nit()
                print(Fore.YELLOW + Style.DIM + f"Fount file => " + file)
                print(Style.RESET_ALL)
                print(Fore.BLACK + Back.WHITE + Style.DIM)
                current_file_counter += 1
                print("Statistic: [ " + str(current_file_counter) + " / " + str(total_file_counter) + "  ]")
                print(Style.RESET_ALL)
                print(Fore.GREEN + Style.DIM)
                try:
                    torrent_file = TorrentDownloader(pubvars.TORRENT_FILE_DIR + "/" + file, pubvars.DOW_FILE_DIR)
                    torrent_file.start_download()
                except:
                    print(Style.RESET_ALL)
                    print(Fore.RED + Style.DIM)
                    print("Check The Torrent Files or Enter the correct file address!! ")
                    print(Style.RESET_ALL)
                    pass
                print(Style.RESET_ALL)
    else:
        print(Style.RESET_ALL)
        print(Fore.RED + Style.DIM)
        print("There is no torrent file in " + pubvars.TORRENT_FILE_DIR)
        print(Style.RESET_ALL)
        exit()


def torrent_multi_magnet_downloader():
    print(Fore.YELLOW + Style.DIM)
    torrent_magnet_link_file = input(f"Please Enter The file magnet link name: ")
    while torrent_magnet_link_file == "":
        torrent_magnet_link_file = input(f"Please Enter The file magnet link name: ")
    try:
        magnet_file_open = open(torrent_magnet_link_file, 'r')
        magnet_file_reader = magnet_file_open.readlines()
        total_file_counter = len(magnet_file_reader)
        current_file_counter = 0
        for mag_link in magnet_file_reader:
            atdtools.clear()
            banner.banner_nit()
            print(Fore.YELLOW + Style.DIM + f"Fount file => " + mag_link)
            print(Style.RESET_ALL)
            print(Fore.BLACK + Back.WHITE + Style.DIM)
            current_file_counter += 1
            print("Statistic: [ " + str(current_file_counter) + " / " + str(total_file_counter) + "  ]")
            print(Style.RESET_ALL)
            print(Fore.GREEN + Style.DIM)
            torrent_mag_link = TorrentDownloader(mag_link, pubvars.DOW_FILE_DIR)
            torrent_mag_link.start_download()
            print(Style.RESET_ALL)
    except:
        print(Style.RESET_ALL)
        print(Fore.RED + Style.DIM)
        print("Check The Magnet Links or Enter Enter the correct Magnet file address!! ")
        print(Style.RESET_ALL)
        pass


def torrent_magnet_downloader():
    print(Fore.YELLOW + Style.DIM)
    torrent_magnet_link = input(f"Please Enter The magnet link address: ")
    while torrent_magnet_link == "":
        torrent_magnet_link = input(f"Please Enter The magnet link address: ")
    atdtools.clear()
    banner.banner_nit()
    print(Style.RESET_ALL)
    print(Fore.GREEN + Style.DIM)
    try:
        torrent_mag_link = TorrentDownloader(torrent_magnet_link, pubvars.DOW_FILE_DIR)
        torrent_mag_link.start_download()
    except:
        print(Style.RESET_ALL)
        print(Fore.RED + Style.DIM)
        print("Check The Magnet Link !! ")
        print(Style.RESET_ALL)
        pass
    print(Style.RESET_ALL)
