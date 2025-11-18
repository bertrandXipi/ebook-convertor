#!/usr/bin/env python3
"""
Script de conversion manuelle - traite tous les EPUBs du dossier Downloads
"""
import sys
from pathlib import Path

from converter import CalibreConverter
from watcher import EpubWatcher
from utils import setup_logger


def main():
    """Traite tous les EPUBs existants puis quitte."""
    logger = setup_logger()
    
    # Configuration
    downloads_path = Path.home() / "Downloads"
    delete_epub_after_conversion = False
    
    logger.info("=" * 60)
    logger.info("🚀 Conversion EPUB → PDF")
    logger.info("=" * 60)
    
    try:
        # Initialiser le convertisseur
        converter = CalibreConverter()
        logger.info("✓ Calibre détecté")
        
        # Créer le watcher (sans surveillance continue)
        watcher = EpubWatcher(
            watch_path=downloads_path,
            converter=converter,
            delete_epub=delete_epub_after_conversion,
            organize_by_date=True
        )
        
        # Traiter uniquement les fichiers existants
        watcher.process_existing_epubs()
        
        logger.info("\n✅ Traitement terminé !")
        logger.info("Appuyez sur Entrée pour fermer...")
        input()
    
    except FileNotFoundError as e:
        logger.error(f"✗ Erreur : {e}")
        logger.info("\nAppuyez sur Entrée pour fermer...")
        input()
        sys.exit(1)
    
    except Exception as e:
        logger.error(f"✗ Erreur inattendue : {e}")
        logger.info("\nAppuyez sur Entrée pour fermer...")
        input()
        sys.exit(1)


if __name__ == "__main__":
    main()
