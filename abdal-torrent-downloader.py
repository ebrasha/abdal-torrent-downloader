"""
**********************************************************************
* -------------------------------------------------------------------
* Project Name : Abdal Torrent Downloader
* File Name    : main.py
* Author       : Ebrahim Shafiei (EbraSha)
* Email        : Prof.Shafiei@Gmail.com
* Created On   : 2025-08-02 3:00:00
* Description  : Main entry point for a professional torrent downloader supporting both CLI and interactive modes, with advanced features and user-friendly interface.
* -------------------------------------------------------------------
*
* "Coding is an engaging and beloved hobby for me. I passionately and insatiably pursue knowledge in cybersecurity and programming."
* – Ebrahim Shafiei
*
**********************************************************************
"""
# -------------------------------------------------------------------
# Programmer       : Ebrahim Shafiei (EbraSha)
# Email            : Prof.Shafiei@Gmail.com
# -------------------------------------------------------------------

import libtorrent as lt
import time
import argparse
import os
import sys
from pathlib import Path
import readline
from prompt_toolkit import prompt
from prompt_toolkit.completion import WordCompleter, PathCompleter
from rich.console import Console
from rich.theme import Theme
from prompt_toolkit.styles import Style

prompt_style = Style.from_dict({
    "": "#ff00ff bold",  # Cyberpunk magenta for all prompts
})

# Cyberpunk color theme for rich
cyberpunk_theme = Theme({
    'prompt': 'bold magenta',
    'info': 'bold cyan',
    'success': 'bold bright_green',
    'error': 'bold bright_red',
    'progress': 'bold bright_yellow',
    'event': 'bold bright_blue',
    'banner': 'bold bright_magenta',
})
console = Console(theme=cyberpunk_theme)

STALL_TIMEOUT_DEFAULT = 1200  # 20 minutes

# Show program banner with ASCII art and programmer's name
def show_banner():
    console.print(r"""
 _______________________________________________________________
|                                                               |
,---,---,---,---,---,---,---,---,---,---,---,---,---,-------,   |
| ~ | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 0 | [ | ] | <-    |   |
|---'-,-'-,-'-,-'-,-'-,-'-,-'-,-'-,-'-,-'-,-'-,-'-,-'-,-----|   |
| ->| | " | , | . | A | B | D | A | L | ? | | | / | = |  \  |   |
|-----',--',--',--',--',--',--',--',--',--',--',--',--'-----|   |
| Caps | E | B | R | A | H | I | M | M | M | M | - |  Enter |   |
|------'-,-'-,-'-,-'-,-'-,-'-,-'-,-'-,-'-,-'-,-'-,-'--------|   |
|        | ; | S | H | A | F | I | E | I | - | , |          |   |
|------,-',--'--,'---'---'---'---'---'---'-,-'---',--,------|   |
| ctrl |  | alt |         EbraSha          | alt  |  | ctrl |   |
'------'  '-----'--------------------------'------'  '------'   |
|                                                               |
|   [bold bright_cyan]Abdal Torrent Downloader ver 11.3[/bold bright_cyan]                           |
|   [bright_magenta]Programmer: Ebrahim Shafiei (EbraSha)[/bright_magenta]                       |
|   [bright_magenta]GitHub: https://github.com/ebrasha[/bright_magenta]                          |
|   [bright_magenta]Email: Prof.Shafiei@Gmail.com[/bright_magenta]                               |
|_______________________________________________________________|
""", style="banner")

# Configure and return a libtorrent session with optional SOCKS5 proxy

def create_session(proxy_host=None, proxy_port=None):
    ses = lt.session()
    settings = {
        'user_agent': 'EbraShaTorrent/1.0',
        'listen_interfaces': '0.0.0.0:6881',
        'anonymous_mode': True,
        'enable_dht': True,
        'enable_lsd': True,
        'enable_upnp': True,
        'enable_natpmp': True
    }
    ses.apply_settings(settings)

    if proxy_host and proxy_port:
        proxy = lt.proxy_settings()
        proxy.type = lt.proxy_type_t.socks5
        proxy.hostname = proxy_host
        proxy.port = proxy_port
        proxy.proxy_peer_connections = True
        proxy.anonymous = True
        ses.set_proxy(proxy)

    return ses

# Start downloading a single magnet link

def download_magnet(ses, magnet_uri, save_path, stall_timeout: int = STALL_TIMEOUT_DEFAULT) -> bool:
    """Download a single magnet link with stall timeout. Returns True if successful, False if stalled."""
    params = {
        'save_path': save_path,
        'storage_mode': lt.storage_mode_t.storage_mode_sparse
    }
    handle = lt.add_magnet_uri(ses, magnet_uri, params)
    print(f"Fetching metadata for: {magnet_uri}")
    while not handle.has_metadata():
        time.sleep(1)
    print(f"Metadata received: {handle.name()}")

    last_progress = 0.0
    last_change = time.time()
    while not handle.is_seed():
        s = handle.status()
        if s.progress > last_progress:
            last_progress = s.progress
            last_change = time.time()
        elif time.time() - last_change > stall_timeout:
            print(f"\nStalled: No progress for {stall_timeout//60} minutes. Skipping {handle.name()}.")
            return False
        print(f"Downloading {handle.name()}: {s.progress * 100:.2f}% - {s.download_rate / 1000:.2f} kB/s ↓", end='\r')
        time.sleep(2)
    print(f"\nDownload completed: {handle.name()}")
    return True

# Start downloading from a .torrent file

def download_torrent_file(ses, torrent_path, save_path, stall_timeout: int = STALL_TIMEOUT_DEFAULT) -> bool:
    """Download a single .torrent file with stall timeout. Returns True if successful, False if stalled."""
    info = lt.torrent_info(torrent_path)
    params = {
        'ti': info,
        'save_path': save_path,
        'storage_mode': lt.storage_mode_t.storage_mode_sparse
    }
    handle = ses.add_torrent(params)
    print(f"Started: {info.name()}")

    last_progress = 0.0
    last_change = time.time()
    while not handle.is_seed():
        s = handle.status()
        if s.progress > last_progress:
            last_progress = s.progress
            last_change = time.time()
        elif time.time() - last_change > stall_timeout:
            print(f"\nStalled: No progress for {stall_timeout//60} minutes. Skipping {info.name()}.")
            return False
        print(f"Downloading {info.name()}: {s.progress * 100:.2f}% - {s.download_rate / 1000:.2f} kB/s ↓", end='\r')
        time.sleep(2)
    print(f"\nDownload completed: {info.name()}")
    return True

# Handle batch magnet downloads from a text file

def download_batch_magnets(ses, list_path, save_path, stall_timeout: int = STALL_TIMEOUT_DEFAULT):
    with open(list_path, 'r') as f:
        links = [line.strip() for line in f if line.strip().startswith("magnet:")]

    total = len(links)
    failed = []
    for idx, link in enumerate(links, start=1):
        print(f"[{idx}/{total}] Magnet: {link[:60]}...")
        success = download_magnet(ses, link, save_path, stall_timeout=stall_timeout)
        if not success:
            failed.append(link)
    if failed:
        print(f"\nFailed to download {len(failed)} magnet(s). See failed_magnets.txt.")
        with open(os.path.join(save_path, "failed_magnets.txt"), "w") as f:
            for link in failed:
                f.write(link + "\n")

# Handle batch torrent downloads from a directory

def download_batch_torrents(ses, dir_path, save_path, stall_timeout: int = STALL_TIMEOUT_DEFAULT):
    files = list(Path(dir_path).glob("*.torrent"))
    total = len(files)
    failed = []
    for idx, file in enumerate(files, start=1):
        print(f"[{idx}/{total}] File: {file.name}")
        success = download_torrent_file(ses, str(file), save_path, stall_timeout=stall_timeout)
        if not success:
            failed.append(str(file))
    if failed:
        print(f"\nFailed to download {len(failed)} torrent(s). See failed_torrents.txt.")
        with open(os.path.join(save_path, "failed_torrents.txt"), "w") as f:
            for file in failed:
                f.write(file + "\n")

# Main entry point

def interactive_mode():
    """Interactive mode for user input when no CLI arguments are provided, using prompt_toolkit and rich."""
    console.print("\n[Interactive Mode]", style="event")
    console.print("Select download type:", style="prompt")
    choices = ["Single Magnet Link", "Magnet List File", "Single .torrent File", "Directory of .torrent Files"]
    choice_completer = WordCompleter(["1", "2", "3", "4"])
    for i, c in enumerate(choices, 1):
        console.print(f"  {i}) {c}", style="info")
    choice = prompt("Enter choice (1-4): ", completer=choice_completer, style=prompt_style).strip()
    if choice not in {"1", "2", "3", "4"}:
        console.print("Invalid choice. Exiting.", style="error")
        sys.exit(1)

    # Use PathCompleter for directory paths
    path_completer = PathCompleter()
    out_path = prompt("Enter output directory: ", completer=path_completer, style=prompt_style).strip()
    out_path = os.path.abspath(out_path)
    os.makedirs(out_path, exist_ok=True)

    use_proxy = prompt("Use SOCKS5 proxy? (y/N): ", style=prompt_style).strip().lower() == 'y'
    proxy_host = proxy_port = None
    if use_proxy:
        proxy = prompt("Enter SOCKS5 proxy (ip:port): ", style=prompt_style).strip()
        try:
            proxy_host, proxy_port = proxy.split(":")
            proxy_port = int(proxy_port)
        except ValueError:
            console.print("Invalid SOCKS5 format. Use ip:port", style="error")
            sys.exit(1)

    try:
        stall_timeout = int(prompt(f"Enter stall timeout in minutes (default {STALL_TIMEOUT_DEFAULT//60}): ", style=prompt_style).strip() or STALL_TIMEOUT_DEFAULT//60) * 60
    except ValueError:
        stall_timeout = STALL_TIMEOUT_DEFAULT

    ses = create_session(proxy_host, proxy_port)

    if choice == "1":
        magnet = prompt("Enter magnet link: ", style=prompt_style).strip()
        if not magnet.startswith("magnet:"):
            console.print("Invalid magnet link.", style="error")
            sys.exit(1)
        download_magnet_rich(ses, magnet, out_path, stall_timeout=stall_timeout)
    elif choice == "2":
        list_path = prompt("Enter path to magnet list file: ", completer=path_completer, style=prompt_style).strip()
        download_batch_magnets_rich(ses, list_path, out_path, stall_timeout=stall_timeout)
    elif choice == "3":
        torrent_path = prompt("Enter path to .torrent file: ", completer=path_completer, style=prompt_style).strip()
        download_torrent_file_rich(ses, torrent_path, out_path, stall_timeout=stall_timeout)
    elif choice == "4":
        dir_path = prompt("Enter directory containing .torrent files: ", completer=path_completer, style=prompt_style).strip()
        download_batch_torrents_rich(ses, dir_path, out_path, stall_timeout=stall_timeout)

# Rich-enabled download functions for interactive mode
def download_magnet_rich(ses, magnet_uri, save_path, stall_timeout: int = STALL_TIMEOUT_DEFAULT) -> bool:
    params = {
        'save_path': save_path,
        'storage_mode': lt.storage_mode_t.storage_mode_sparse
    }
    handle = lt.add_magnet_uri(ses, magnet_uri, params)
    console.print(f"[info]Fetching metadata for:[/info] [progress]{magnet_uri}[/progress]")
    while not handle.has_metadata():
        time.sleep(1)
    console.print(f"[success]Metadata received:[/success] [event]{handle.name()}[/event]")

    last_progress = 0.0
    last_change = time.time()
    while not handle.is_seed():
        s = handle.status()
        if s.progress > last_progress:
            last_progress = s.progress
            last_change = time.time()
        elif time.time() - last_change > stall_timeout:
            console.print(f"\n[error]Stalled: No progress for {stall_timeout//60} minutes. Skipping {handle.name()}.[/error]")
            return False
        console.print(f"[progress]Downloading {handle.name()}: {s.progress * 100:.2f}% - {s.download_rate / 1000:.2f} kB/s ↓[/progress]", end='\r')
        time.sleep(2)
    console.print(f"\n[success]Download completed: {handle.name()}[/success]")
    return True

def download_torrent_file_rich(ses, torrent_path, save_path, stall_timeout: int = STALL_TIMEOUT_DEFAULT) -> bool:
    info = lt.torrent_info(torrent_path)
    params = {
        'ti': info,
        'save_path': save_path,
        'storage_mode': lt.storage_mode_t.storage_mode_sparse
    }
    handle = ses.add_torrent(params)
    console.print(f"[info]Started:[/info] [event]{info.name()}[/event]")

    last_progress = 0.0
    last_change = time.time()
    while not handle.is_seed():
        s = handle.status()
        if s.progress > last_progress:
            last_progress = s.progress
            last_change = time.time()
        elif time.time() - last_change > stall_timeout:
            console.print(f"\n[error]Stalled: No progress for {stall_timeout//60} minutes. Skipping {info.name()}.[/error]")
            return False
        console.print(f"[progress]Downloading {info.name()}: {s.progress * 100:.2f}% - {s.download_rate / 1000:.2f} kB/s ↓[/progress]", end='\r')
        time.sleep(2)
    console.print(f"\n[success]Download completed: {info.name()}[/success]")
    return True

def download_batch_magnets_rich(ses, list_path, save_path, stall_timeout: int = STALL_TIMEOUT_DEFAULT):
    with open(list_path, 'r') as f:
        links = [line.strip() for line in f if line.strip().startswith("magnet:")]

    total = len(links)
    failed = []
    for idx, link in enumerate(links, start=1):
        console.print(f"[event][{idx}/{total}] Magnet:[/event] [progress]{link[:60]}...[/progress]")
        success = download_magnet_rich(ses, link, save_path, stall_timeout=stall_timeout)
        if not success:
            failed.append(link)
    if failed:
        console.print(f"\n[error]Failed to download {len(failed)} magnet(s). See failed_magnets.txt.[/error]")
        with open(os.path.join(save_path, "failed_magnets.txt"), "w") as f:
            for link in failed:
                f.write(link + "\n")

def download_batch_torrents_rich(ses, dir_path, save_path, stall_timeout: int = STALL_TIMEOUT_DEFAULT):
    files = list(Path(dir_path).glob("*.torrent"))
    total = len(files)
    failed = []
    for idx, file in enumerate(files, start=1):
        console.print(f"[event][{idx}/{total}] File:[/event] [progress]{file.name}[/progress]")
        success = download_torrent_file_rich(ses, str(file), save_path, stall_timeout=stall_timeout)
        if not success:
            failed.append(str(file))
    if failed:
        console.print(f"\n[error]Failed to download {len(failed)} torrent(s). See failed_torrents.txt.[/error]")
        with open(os.path.join(save_path, "failed_torrents.txt"), "w") as f:
            for file in failed:
                f.write(file + "\n")


def print_cyberpunk_help():
    help_text = '''
[bold bright_magenta]+--------------------------------------------------------------------+
|                  [bright_cyan]ABDAL TORRENT DOWNLOADER ver 11.2[/bright_cyan]                  
|   [bright_magenta]Programmer: Ebrahim Shafiei (EbraSha)[/bright_magenta]               
|   [bright_magenta]GitHub: https://github.com/ebrasha[/bright_magenta]                  
|   [bright_magenta]Email: Prof.Shafiei@Gmail.com[/bright_magenta]                       
+--------------------------------------------------------------------+
| [bright_yellow]Arguments:[/bright_yellow]                                                     
|   [bold cyan]--magnet[/bold cyan]         [white]Download a single magnet link.[/white]                
|   [bold cyan]--magnet-list[/bold cyan]    [white]Download all magnet links from a text file.[/white]    
|   [bold cyan]--torrent[/bold cyan]        [white]Download a single .torrent file.[/white]               
|   [bold cyan]--torrent-dir[/bold cyan]    [white]Download all .torrent files from a directory.[/white]  
|   [bold cyan]--out[/bold cyan]            [white]Output path for downloads (required for CLI).[/white]  
|   [bold cyan]--socks5[/bold cyan]         [white]SOCKS5 proxy in ip:port format (optional).[/white]     
|   [bold cyan]--stall-timeout[/bold cyan]  [white]Stall timeout in [bold bright_yellow]MINUTES[/bold bright_yellow] (default: 20).[/white]      
|                   [bright_black]If no progress for this period, file is skipped.[/bright_black]          
+--------------------------------------------------------------------+
| [bright_yellow]Examples:[/bright_yellow]                                                      
|   [green]python main.py --magnet "magnet:?xt=urn:btih:..." --out ./downloads[/green]          
|   [green]python main.py --magnet-list magnets.txt --out ./downloads --stall-timeout 30[/green]
|   [green]python main.py --torrent-dir ./torrents --out ./downloads[/green]                    
+--------------------------------------------------------------------+
| [bold bright_magenta]Tip:[/bold bright_magenta] [white]Run without arguments for interactive cyberpunk mode![/white]         |
+--------------------------------------------------------------------+
'''
    console.print(help_text)
    sys.exit(0)

def main():
    show_banner()
    if '-h' in sys.argv or '--help' in sys.argv:
        print_cyberpunk_help()
    parser = argparse.ArgumentParser(
        description="",  # Help is now handled by rich
        formatter_class=argparse.RawDescriptionHelpFormatter,
        add_help=False
    )
    parser.add_argument("--magnet", help="Single magnet link")
    parser.add_argument("--magnet-list", help="Text file containing magnet links")
    parser.add_argument("--torrent", help="Single .torrent file path")
    parser.add_argument("--torrent-dir", help="Directory containing .torrent files")
    parser.add_argument("--out", help="Output path for downloads")
    parser.add_argument("--socks5", help="SOCKS5 proxy (ip:port)")
    parser.add_argument("--stall-timeout", type=int, default=STALL_TIMEOUT_DEFAULT//60, help="Stall timeout in MINUTES (default: 20). If no progress for this period, file is skipped.")
    args = parser.parse_args()

    # If no download source is provided, enter interactive mode
    if not any([args.magnet, args.magnet_list, args.torrent, args.torrent_dir]):
        interactive_mode()
        return

    if not args.out:
        print("Output path is required. Use --out or run in interactive mode.")
        sys.exit(1)

    out_path = os.path.abspath(args.out)
    os.makedirs(out_path, exist_ok=True)

    proxy_host = proxy_port = None
    if args.socks5:
        try:
            proxy_host, proxy_port = args.socks5.split(":")
            proxy_port = int(proxy_port)
        except ValueError:
            print("Invalid SOCKS5 format. Use ip:port")
            sys.exit(1)

    ses = create_session(proxy_host, proxy_port)
    stall_timeout = args.stall_timeout * 60

    if args.magnet:
        magnet = args.magnet.strip()
        if not magnet.startswith("magnet:"):
            print("Invalid magnet link.")
            sys.exit(1)
        download_magnet(ses, magnet, out_path, stall_timeout=stall_timeout)
    elif args.magnet_list:
        download_batch_magnets(ses, args.magnet_list, out_path, stall_timeout=stall_timeout)
    elif args.torrent:
        download_torrent_file(ses, args.torrent, out_path, stall_timeout=stall_timeout)
    elif args.torrent_dir:
        download_batch_torrents(ses, args.torrent_dir, out_path, stall_timeout=stall_timeout)
    else:
        print("No download source provided. Use --help for usage.")
        sys.exit(1)

if __name__ == "__main__":
    main()