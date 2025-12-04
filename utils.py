import logging
import sys
from pathlib import Path

# Try to import colorama, fallback to dummy objects if missing
try:
    from colorama import Fore, Style, init
    init(autoreset=True)
except ImportError:
    class DummyColor:
        def __getattr__(self, name):
            return ""
    Fore = DummyColor()
    Style = DummyColor()
    def init(*args, **kwargs): pass

def setup_logging(log_file: Path):
    """Configure logging to file and console"""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )

def print_success(msg: str):
    print(f"{Fore.GREEN}✅ {msg}{Style.RESET_ALL}")

def print_warning(msg: str):
    print(f"{Fore.YELLOW}⚠️  {msg}{Style.RESET_ALL}")

def print_error(msg: str):
    print(f"{Fore.RED}❌ {msg}{Style.RESET_ALL}")

def print_info(msg: str):
    print(f"{Fore.CYAN}ℹ️  {msg}{Style.RESET_ALL}")

def clean_filename(filename: str) -> str:
    """Remove invalid characters from filenames"""
    return "".join(c for c in filename if c.isalnum() or c in (' ', '-', '_', '.', '(', ')')).strip()
