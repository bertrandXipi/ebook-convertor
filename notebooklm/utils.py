"""Utilitaires pour logging et gestion des fichiers."""
import csv
import logging
from datetime import datetime
from pathlib import Path
from typing import List


def setup_logger(name: str = "notebooklm") -> logging.Logger:
    """Configure le logger pour l'application."""
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    
    # Handler console avec couleurs
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    
    # Format simple
    formatter = logging.Formatter('%(message)s')
    console_handler.setFormatter(formatter)
    
    # Éviter les doublons
    if not logger.handlers:
        logger.addHandler(console_handler)
    
    return logger


class UploadLogger:
    """Logger pour les uploads de PDFs."""
    
    def __init__(self, log_folder: Path):
        self.log_folder = Path(log_folder)
        self.log_folder.mkdir(exist_ok=True)
        
        # Créer un fichier de log avec timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        self.log_file = self.log_folder / f"upload_{timestamp}.csv"
        
        # Créer le fichier CSV avec headers
        with open(self.log_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([
                'timestamp',
                'notebook_title',
                'pdf_filename',
                'status',
                'error_message',
                'url'
            ])
    
    def log_upload(
        self,
        notebook_title: str,
        pdf_filename: str,
        status: str,
        error_message: str = "",
        url: str = ""
    ):
        """Log un upload de PDF."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        with open(self.log_file, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([
                timestamp,
                notebook_title,
                pdf_filename,
                status,
                error_message,
                url
            ])
    
    def get_log_path(self) -> str:
        """Retourne le chemin du fichier de log."""
        return str(self.log_file)


def get_pdf_files(folder: Path) -> List[Path]:
    """Récupère tous les fichiers PDF d'un dossier."""
    folder = Path(folder)
    if not folder.exists():
        raise FileNotFoundError(f"Dossier introuvable : {folder}")
    
    pdf_files = sorted(folder.glob("*.pdf"))
    return pdf_files


def format_file_size(size_bytes: int) -> str:
    """Formate une taille de fichier en format lisible."""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"


def print_progress_bar(current: int, total: int, prefix: str = "", length: int = 40):
    """Affiche une barre de progression."""
    percent = current / total
    filled = int(length * percent)
    bar = '█' * filled + '░' * (length - filled)
    print(f'\r{prefix} [{bar}] {current}/{total} ({percent*100:.0f}%)', end='', flush=True)
    
    if current == total:
        print()  # Nouvelle ligne à la fin
