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
import logging
from pathlib import Path
import readline
from prompt_toolkit import prompt
from prompt_toolkit.completion import WordCompleter, PathCompleter
from rich.console import Console
from rich.theme import Theme
from prompt_toolkit.styles import Style

# Setup logging
def setup_logging():
    """Setup logging configuration to write to a file next to the script."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    log_file = os.path.join(script_dir, "abdal-torrent-downloader.log")
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    return logging.getLogger(__name__)

logger = setup_logging()

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
    try:
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
|   [bold bright_cyan]Abdal Torrent Downloader ver 11.6[/bold bright_cyan]                           |
|   [bright_magenta]Programmer: Ebrahim Shafiei (EbraSha)[/bright_magenta]                       |
|   [bright_magenta]GitHub: https://github.com/ebrasha[/bright_magenta]                          |
|   [bright_magenta]Email: Prof.Shafiei@Gmail.com[/bright_magenta]                               |
|_______________________________________________________________|
""", style="banner")
        logger.info("Banner displayed successfully")
    except Exception as e:
        logger.error(f"Error displaying banner: {e}")
        print("Abdal Torrent Downloader - By Ebrahim Shafiei (EbraSha)")

# Configure and return a libtorrent session with optional SOCKS5 proxy
def create_session(proxy_host=None, proxy_port=None):
    try:
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
            logger.info(f"Proxy configured: {proxy_host}:{proxy_port}")

        logger.info("Libtorrent session created successfully")
        return ses
    except Exception as e:
        logger.error(f"Error creating libtorrent session: {e}")
        console.print(f"[error]Failed to create session: {e}[/error]")
        sys.exit(1)

# Start downloading a single magnet link
def download_magnet(ses, magnet_uri, save_path, stall_timeout: int = STALL_TIMEOUT_DEFAULT) -> bool:
    """Download a single magnet link with stall timeout. Returns True if successful, False if stalled."""
    try:
        params = lt.parse_magnet_uri(magnet_uri)
        params.save_path = save_path
        params.storage_mode = lt.storage_mode_t.storage_mode_sparse
        
        handle = ses.add_torrent(params)
        logger.info(f"Started magnet download: {magnet_uri[:50]}...")
        print(f"Fetching metadata for: {magnet_uri}")
        
        # Wait for metadata
        while not handle.status().has_metadata:
            time.sleep(1)
        print(f"Metadata received: {handle.name()}")
        logger.info(f"Metadata received for: {handle.name()}")

        last_progress = 0.0
        last_change = time.time()
        while not handle.status().is_seeding:
            try:
                s = handle.status()
                if s.progress > last_progress:
                    last_progress = s.progress
                    last_change = time.time()
                elif time.time() - last_change > stall_timeout:
                    logger.warning(f"Download stalled for {handle.name()}")
                    print(f"\nStalled: No progress for {stall_timeout//60} minutes. Skipping {handle.name()}.")
                    return False
                print(f"Downloading {handle.name()}: {s.progress * 100:.2f}% - {s.download_rate / 1000:.2f} kB/s ↓", end='\r')
                time.sleep(2)
            except Exception as e:
                logger.error(f"Error during download loop: {e}")
                return False
                
        print(f"\nDownload completed: {handle.name()}")
        logger.info(f"Download completed successfully: {handle.name()}")
        return True
    except Exception as e:
        logger.error(f"Error downloading magnet {magnet_uri[:50]}...: {e}")
        console.print(f"[error]Error downloading magnet: {e}[/error]")
        return False

# Start downloading from a .torrent file
def download_torrent_file(ses, torrent_path, save_path, stall_timeout: int = STALL_TIMEOUT_DEFAULT) -> bool:
    """Download a single .torrent file with stall timeout. Returns True if successful, False if stalled."""
    try:
        if not os.path.exists(torrent_path):
            logger.error(f"Torrent file not found: {torrent_path}")
            console.print(f"[error]Torrent file not found: {torrent_path}[/error]")
            return False
            
        info = lt.torrent_info(torrent_path)
        params = lt.add_torrent_params()
        params.ti = info
        params.save_path = save_path
        params.storage_mode = lt.storage_mode_t.storage_mode_sparse
        
        handle = ses.add_torrent(params)
        logger.info(f"Started torrent download: {info.name()}")
        print(f"Started: {info.name()}")

        last_progress = 0.0
        last_change = time.time()
        while not handle.status().is_seeding:
            try:
                s = handle.status()
                if s.progress > last_progress:
                    last_progress = s.progress
                    last_change = time.time()
                elif time.time() - last_change > stall_timeout:
                    logger.warning(f"Download stalled for {info.name()}")
                    print(f"\nStalled: No progress for {stall_timeout//60} minutes. Skipping {info.name()}.")
                    return False
                print(f"Downloading {info.name()}: {s.progress * 100:.2f}% - {s.download_rate / 1000:.2f} kB/s ↓", end='\r')
                time.sleep(2)
            except Exception as e:
                logger.error(f"Error during download loop: {e}")
                return False
                
        print(f"\nDownload completed: {info.name()}")
        logger.info(f"Download completed successfully: {info.name()}")
        return True
    except Exception as e:
        logger.error(f"Error downloading torrent {torrent_path}: {e}")
        console.print(f"[error]Error downloading torrent: {e}[/error]")
        return False

# Handle batch magnet downloads from a text file
def download_batch_magnets(ses, list_path, save_path, stall_timeout: int = STALL_TIMEOUT_DEFAULT):
    try:
        if not os.path.exists(list_path):
            logger.error(f"Magnet list file not found: {list_path}")
            console.print(f"[error]Magnet list file not found: {list_path}[/error]")
            return
            
        with open(list_path, 'r', encoding='utf-8') as f:
            links = [line.strip() for line in f if line.strip().startswith("magnet:")]

        if not links:
            logger.warning("No valid magnet links found in file")
            console.print("[warning]No valid magnet links found in file[/warning]")
            return

        total = len(links)
        failed = []
        logger.info(f"Starting batch download of {total} magnet links")
        
        for idx, link in enumerate(links, start=1):
            try:
                print(f"[{idx}/{total}] Magnet: {link[:60]}...")
                success = download_magnet(ses, link, save_path, stall_timeout=stall_timeout)
                if not success:
                    failed.append(link)
                    logger.warning(f"Failed to download magnet {idx}/{total}")
            except Exception as e:
                logger.error(f"Error processing magnet {idx}/{total}: {e}")
                failed.append(link)
                
        if failed:
            logger.warning(f"Failed to download {len(failed)} magnet(s)")
            print(f"\nFailed to download {len(failed)} magnet(s). See failed_magnets.txt.")
            try:
                with open(os.path.join(save_path, "failed_magnets.txt"), "w", encoding='utf-8') as f:
                    for link in failed:
                        f.write(link + "\n")
                logger.info("Failed magnets list saved to failed_magnets.txt")
            except Exception as e:
                logger.error(f"Error saving failed magnets list: {e}")
    except Exception as e:
        logger.error(f"Error in batch magnet download: {e}")
        console.print(f"[error]Error in batch magnet download: {e}[/error]")

# Handle batch torrent downloads from a directory
def download_batch_torrents(ses, dir_path, save_path, stall_timeout: int = STALL_TIMEOUT_DEFAULT):
    try:
        if not os.path.exists(dir_path):
            logger.error(f"Torrent directory not found: {dir_path}")
            console.print(f"[error]Torrent directory not found: {dir_path}[/error]")
            return
            
        files = list(Path(dir_path).glob("*.torrent"))
        
        if not files:
            logger.warning(f"No .torrent files found in directory: {dir_path}")
            console.print(f"[warning]No .torrent files found in directory: {dir_path}[/warning]")
            return

        total = len(files)
        failed = []
        logger.info(f"Starting batch download of {total} torrent files")
        
        for idx, file in enumerate(files, start=1):
            try:
                print(f"[{idx}/{total}] File: {file.name}")
                success = download_torrent_file(ses, str(file), save_path, stall_timeout=stall_timeout)
                if not success:
                    failed.append(str(file))
                    logger.warning(f"Failed to download torrent {idx}/{total}: {file.name}")
            except Exception as e:
                logger.error(f"Error processing torrent {idx}/{total}: {e}")
                failed.append(str(file))
                
        if failed:
            logger.warning(f"Failed to download {len(failed)} torrent(s)")
            print(f"\nFailed to download {len(failed)} torrent(s). See failed_torrents.txt.")
            try:
                with open(os.path.join(save_path, "failed_torrents.txt"), "w", encoding='utf-8') as f:
                    for file in failed:
                        f.write(file + "\n")
                logger.info("Failed torrents list saved to failed_torrents.txt")
            except Exception as e:
                logger.error(f"Error saving failed torrents list: {e}")
    except Exception as e:
        logger.error(f"Error in batch torrent download: {e}")
        console.print(f"[error]Error in batch torrent download: {e}[/error]")


# Main entry point

def interactive_mode():
    """Interactive mode for user input when no CLI arguments are provided, using prompt_toolkit and rich."""
    try:
        console.print("\n[Interactive Mode]", style="event")
        console.print("Select download type:", style="prompt")
        choices = ["Single Magnet Link", "Magnet List File", "Single .torrent File", "Directory of .torrent Files"]
        choice_completer = WordCompleter(["1", "2", "3", "4"])
        for i, c in enumerate(choices, 1):
            console.print(f"  {i}) {c}", style="info")
        choice = prompt("Enter choice (1-4): ", completer=choice_completer, style=prompt_style).strip()
        if choice not in {"1", "2", "3", "4"}:
            console.print("Invalid choice. Exiting.", style="error")
            logger.warning("Invalid choice selected in interactive mode")
            sys.exit(1)

        # Use PathCompleter for directory paths
        path_completer = PathCompleter()
        out_path = prompt("Enter output directory: ", completer=path_completer, style=prompt_style).strip()
        out_path = os.path.abspath(out_path)
        try:
            os.makedirs(out_path, exist_ok=True)
            logger.info(f"Output directory created/verified: {out_path}")
        except Exception as e:
            logger.error(f"Error creating output directory {out_path}: {e}")
            console.print(f"[error]Error creating output directory: {e}[/error]")
            sys.exit(1)

        use_proxy = prompt("Use SOCKS5 proxy? (y/N): ", style=prompt_style).strip().lower() == 'y'
        proxy_host = proxy_port = None
        if use_proxy:
            proxy = prompt("Enter SOCKS5 proxy (ip:port): ", style=prompt_style).strip()
            try:
                proxy_host, proxy_port = proxy.split(":")
                proxy_port = int(proxy_port)
                logger.info(f"Proxy configured: {proxy_host}:{proxy_port}")
            except ValueError:
                console.print("Invalid SOCKS5 format. Use ip:port", style="error")
                logger.error("Invalid SOCKS5 proxy format provided")
                sys.exit(1)

        try:
            stall_timeout = int(prompt(f"Enter stall timeout in minutes (default {STALL_TIMEOUT_DEFAULT//60}): ", style=prompt_style).strip() or STALL_TIMEOUT_DEFAULT//60) * 60
            logger.info(f"Stall timeout set to {stall_timeout//60} minutes")
        except ValueError:
            stall_timeout = STALL_TIMEOUT_DEFAULT
            logger.warning("Invalid stall timeout, using default")

        ses = create_session(proxy_host, proxy_port)

        if choice == "1":
            magnet = prompt("Enter magnet link: ", style=prompt_style).strip()
            if not magnet.startswith("magnet:"):
                console.print("Invalid magnet link.", style="error")
                logger.error("Invalid magnet link provided")
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
    except Exception as e:
        logger.error(f"Error in interactive mode: {e}")
        console.print(f"[error]Error in interactive mode: {e}[/error]")
        sys.exit(1)

# Rich-enabled download functions for interactive mode
def download_magnet_rich(ses, magnet_uri, save_path, stall_timeout: int = STALL_TIMEOUT_DEFAULT) -> bool:
    try:
        params = lt.parse_magnet_uri(magnet_uri)
        params.save_path = save_path
        params.storage_mode = lt.storage_mode_t.storage_mode_sparse
        
        handle = ses.add_torrent(params)
        logger.info(f"Started magnet download (rich): {magnet_uri[:50]}...")
        console.print(f"[info]Fetching metadata for:[/info] [progress]{magnet_uri}[/progress]")
        
        # Wait for metadata
        while not handle.status().has_metadata:
            time.sleep(1)
        console.print(f"[success]Metadata received:[/success] [event]{handle.name()}[/event]")
        logger.info(f"Metadata received for: {handle.name()}")

        last_progress = 0.0
        last_change = time.time()
        while not handle.status().is_seeding:
            try:
                s = handle.status()
                if s.progress > last_progress:
                    last_progress = s.progress
                    last_change = time.time()
                elif time.time() - last_change > stall_timeout:
                    logger.warning(f"Download stalled for {handle.name()}")
                    console.print(f"\n[error]Stalled: No progress for {stall_timeout//60} minutes. Skipping {handle.name()}.[/error]")
                    return False
                console.print(f"[progress]Downloading {handle.name()}: {s.progress * 100:.2f}% - {s.download_rate / 1000:.2f} kB/s ↓[/progress]", end='\r')
                time.sleep(2)
            except Exception as e:
                logger.error(f"Error during download loop (rich): {e}")
                return False
                
        console.print(f"\n[success]Download completed: {handle.name()}[/success]")
        logger.info(f"Download completed successfully: {handle.name()}")
        return True
    except Exception as e:
        logger.error(f"Error downloading magnet (rich) {magnet_uri[:50]}...: {e}")
        console.print(f"[error]Error downloading magnet: {e}[/error]")
        return False

def download_torrent_file_rich(ses, torrent_path, save_path, stall_timeout: int = STALL_TIMEOUT_DEFAULT) -> bool:
    try:
        if not os.path.exists(torrent_path):
            logger.error(f"Torrent file not found: {torrent_path}")
            console.print(f"[error]Torrent file not found: {torrent_path}[/error]")
            return False
            
        info = lt.torrent_info(torrent_path)
        params = lt.add_torrent_params()
        params.ti = info
        params.save_path = save_path
        params.storage_mode = lt.storage_mode_t.storage_mode_sparse
        
        handle = ses.add_torrent(params)
        logger.info(f"Started torrent download (rich): {info.name()}")
        console.print(f"[info]Started:[/info] [event]{info.name()}[/event]")

        last_progress = 0.0
        last_change = time.time()
        while not handle.status().is_seeding:
            try:
                s = handle.status()
                if s.progress > last_progress:
                    last_progress = s.progress
                    last_change = time.time()
                elif time.time() - last_change > stall_timeout:
                    logger.warning(f"Download stalled for {info.name()}")
                    console.print(f"\n[error]Stalled: No progress for {stall_timeout//60} minutes. Skipping {info.name()}.[/error]")
                    return False
                console.print(f"[progress]Downloading {info.name()}: {s.progress * 100:.2f}% - {s.download_rate / 1000:.2f} kB/s ↓[/progress]", end='\r')
                time.sleep(2)
            except Exception as e:
                logger.error(f"Error during download loop (rich): {e}")
                return False
                
        console.print(f"\n[success]Download completed: {info.name()}[/success]")
        logger.info(f"Download completed successfully: {info.name()}")
        return True
    except Exception as e:
        logger.error(f"Error downloading torrent (rich) {torrent_path}: {e}")
        console.print(f"[error]Error downloading torrent: {e}[/error]")
        return False

def download_batch_magnets_rich(ses, list_path, save_path, stall_timeout: int = STALL_TIMEOUT_DEFAULT):
    try:
        if not os.path.exists(list_path):
            logger.error(f"Magnet list file not found: {list_path}")
            console.print(f"[error]Magnet list file not found: {list_path}[/error]")
            return
            
        with open(list_path, 'r', encoding='utf-8') as f:
            links = [line.strip() for line in f if line.strip().startswith("magnet:")]

        if not links:
            logger.warning("No valid magnet links found in file")
            console.print("[warning]No valid magnet links found in file[/warning]")
            return

        total = len(links)
        failed = []
        logger.info(f"Starting batch download of {total} magnet links (rich)")
        
        for idx, link in enumerate(links, start=1):
            try:
                console.print(f"[event][{idx}/{total}] Magnet:[/event] [progress]{link[:60]}...[/progress]")
                success = download_magnet_rich(ses, link, save_path, stall_timeout=stall_timeout)
                if not success:
                    failed.append(link)
                    logger.warning(f"Failed to download magnet {idx}/{total}")
            except Exception as e:
                logger.error(f"Error processing magnet {idx}/{total}: {e}")
                failed.append(link)
                
        if failed:
            logger.warning(f"Failed to download {len(failed)} magnet(s)")
            console.print(f"\n[error]Failed to download {len(failed)} magnet(s). See failed_magnets.txt.[/error]")
            try:
                with open(os.path.join(save_path, "failed_magnets.txt"), "w", encoding='utf-8') as f:
                    for link in failed:
                        f.write(link + "\n")
                logger.info("Failed magnets list saved to failed_magnets.txt")
            except Exception as e:
                logger.error(f"Error saving failed magnets list: {e}")
    except Exception as e:
        logger.error(f"Error in batch magnet download (rich): {e}")
        console.print(f"[error]Error in batch magnet download: {e}[/error]")

def download_batch_torrents_rich(ses, dir_path, save_path, stall_timeout: int = STALL_TIMEOUT_DEFAULT):
    try:
        if not os.path.exists(dir_path):
            logger.error(f"Torrent directory not found: {dir_path}")
            console.print(f"[error]Torrent directory not found: {dir_path}[/error]")
            return
            
        files = list(Path(dir_path).glob("*.torrent"))
        
        if not files:
            logger.warning(f"No .torrent files found in directory: {dir_path}")
            console.print(f"[warning]No .torrent files found in directory: {dir_path}[/warning]")
            return

        total = len(files)
        failed = []
        logger.info(f"Starting batch download of {total} torrent files (rich)")
        
        for idx, file in enumerate(files, start=1):
            try:
                console.print(f"[event][{idx}/{total}] File:[/event] [progress]{file.name}[/progress]")
                success = download_torrent_file_rich(ses, str(file), save_path, stall_timeout=stall_timeout)
                if not success:
                    failed.append(str(file))
                    logger.warning(f"Failed to download torrent {idx}/{total}: {file.name}")
            except Exception as e:
                logger.error(f"Error processing torrent {idx}/{total}: {e}")
                failed.append(str(file))
                
        if failed:
            logger.warning(f"Failed to download {len(failed)} torrent(s)")
            console.print(f"\n[error]Failed to download {len(failed)} torrent(s). See failed_torrents.txt.[/error]")
            try:
                with open(os.path.join(save_path, "failed_torrents.txt"), "w", encoding='utf-8') as f:
                    for file in failed:
                        f.write(file + "\n")
                logger.info("Failed torrents list saved to failed_torrents.txt")
            except Exception as e:
                logger.error(f"Error saving failed torrents list: {e}")
    except Exception as e:
        logger.error(f"Error in batch torrent download (rich): {e}")
        console.print(f"[error]Error in batch torrent download: {e}[/error]")

def print_cyberpunk_help():
    try:
        help_text = '''
[bold bright_magenta]+--------------------------------------------------------------------+
|                  [bright_cyan]ABDAL TORRENT DOWNLOADER[/bright_cyan]                   |
|   [bright_magenta]Programmer: Ebrahim Shafiei (EbraSha)[/bright_magenta]               |
|   [bright_magenta]GitHub: https://github.com/ebrasha[/bright_magenta]                  |
|   [bright_magenta]Email: Prof.Shafiei@Gmail.com[/bright_magenta]                       |
+--------------------------------------------------------------------+
| [bright_yellow]Arguments:[/bright_yellow]                                                    |
|   [bold cyan]--magnet[/bold cyan]         [white]Download a single magnet link.[/white]                |
|   [bold cyan]--magnet-list[/bold cyan]    [white]Download all magnet links from a text file.[/white]   |
|   [bold cyan]--torrent[/bold cyan]        [white]Download a single .torrent file.[/white]              |
|   [bold cyan]--torrent-dir[/bold cyan]    [white]Download all .torrent files from a directory.[/white] |
|   [bold cyan]--out[/bold cyan]            [white]Output path for downloads (required for CLI).[/white] |
|   [bold cyan]--socks5[/bold cyan]         [white]SOCKS5 proxy in ip:port format (optional).[/white]    |
|   [bold cyan]--stall-timeout[/bold cyan]  [white]Stall timeout in [bold bright_yellow]MINUTES[/bold bright_yellow] (default: 20).[/white]      |
|                   [bright_black]If no progress for this period, file is skipped.[/bright_black]         |
+--------------------------------------------------------------------+
| [bright_yellow]Examples:[/bright_yellow]                                                     |
|   [green]python abdal-torrent-downloader.py --magnet "magnet:?xt=urn:btih:..." --out ./downloads[/green]         |
|   [green]python abdal-torrent-downloader.py --magnet-list magnets.txt --out ./downloads --stall-timeout 30[/green]|
|   [green]python abdal-torrent-downloader.py --torrent-dir ./torrents --out ./downloads[/green]                    |
+--------------------------------------------------------------------+
| [bold bright_magenta]Tip:[/bold bright_magenta] [white]Run without arguments for interactive cyberpunk mode![/white]         |
+--------------------------------------------------------------------+
'''
        console.print(help_text)
        logger.info("Help displayed successfully")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Error displaying help: {e}")
        print("Error displaying help. Use --help for basic help.")
        sys.exit(1)

def main():
    try:
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
            logger.info("No arguments provided, entering interactive mode")
            interactive_mode()
            return

        if not args.out:
            logger.error("Output path is required for CLI mode")
            print("Output path is required. Use --out or run in interactive mode.")
            sys.exit(1)

        out_path = os.path.abspath(args.out)
        try:
            os.makedirs(out_path, exist_ok=True)
            logger.info(f"Output directory created/verified: {out_path}")
        except Exception as e:
            logger.error(f"Error creating output directory {out_path}: {e}")
            console.print(f"[error]Error creating output directory: {e}[/error]")
            sys.exit(1)

        proxy_host = proxy_port = None
        if args.socks5:
            try:
                proxy_host, proxy_port = args.socks5.split(":")
                proxy_port = int(proxy_port)
                logger.info(f"Proxy configured: {proxy_host}:{proxy_port}")
            except ValueError:
                logger.error("Invalid SOCKS5 format provided")
                print("Invalid SOCKS5 format. Use ip:port")
                sys.exit(1)

        ses = create_session(proxy_host, proxy_port)
        stall_timeout = args.stall_timeout * 60
        logger.info(f"Stall timeout set to {stall_timeout//60} minutes")

        if args.magnet:
            magnet = args.magnet.strip()
            if not magnet.startswith("magnet:"):
                logger.error("Invalid magnet link provided")
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
            logger.warning("No download source provided")
            print("No download source provided. Use --help for usage.")
            sys.exit(1)
    except Exception as e:
        logger.error(f"Error in main function: {e}")
        console.print(f"[error]Unexpected error: {e}[/error]")
        sys.exit(1)

if __name__ == "__main__":
    main()