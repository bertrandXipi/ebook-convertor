#!/usr/bin/env python3
"""
Auto-Convertisseur EPUB vers PDF
Surveille le dossier Downloads et convertit automatiquement les EPUBs en PDF.
"""
import sys
from pathlib import Path

from converter import CalibreConverter
from watcher import EpubWatcher
from utils import setup_logger


def main():
    """Point d'entrée principal."""
    logger = setup_logger()
    
    # Configuration
    downloads_path = Path.home() / "Downloads"
    delete_epub_after_conversion = False  # Changer à True pour supprimer les EPUBs
    
    logger.info("=" * 60)
    logger.info("🚀 Auto-Convertisseur EPUB → PDF")
    logger.info("=" * 60)
    
    try:
        # Initialiser le convertisseur
        converter = CalibreConverter()
        logger.info("✓ Calibre détecté")
        
        # Initialiser et démarrer le watcher
        watcher = EpubWatcher(
            watch_path=downloads_path,
            converter=converter,
            delete_epub=delete_epub_after_conversion,
            organize_by_date=True  # Organiser les fichiers par date
        )
        watcher.start()
    
    except FileNotFoundError as e:
        logger.error(f"✗ Erreur : {e}")
        sys.exit(1)
    
    except KeyboardInterrupt:
        logger.info("\n👋 Arrêt demandé par l'utilisateur")
        sys.exit(0)
    
    except Exception as e:
        logger.error(f"✗ Erreur inattendue : {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
