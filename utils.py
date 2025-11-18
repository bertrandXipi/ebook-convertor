"""Utilitaires pour logging et notifications."""
import logging
from datetime import datetime
from pathlib import Path


def setup_logger(name: str = "epub_converter") -> logging.Logger:
    """Configure le logger pour l'application."""
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    
    # Handler console
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    
    # Format
    formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(formatter)
    
    logger.addHandler(console_handler)
    return logger


def notify_macos(title: str, message: str):
    """Envoie une notification macOS (optionnel)."""
    try:
        import subprocess
        script = f'display notification "{message}" with title "{title}"'
        subprocess.run(['osascript', '-e', script], check=False)
    except Exception:
        pass  # Notifications optionnelles, ne pas bloquer si échec
