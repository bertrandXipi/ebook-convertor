#!/usr/bin/env python3
"""
Workflow complet : Conversion EPUB→PDF + Upload NotebookLM
"""
import sys
import argparse
from pathlib import Path

# Import des modules existants
from converter import CalibreConverter
from watcher import EpubWatcher
from utils import setup_logger as setup_converter_logger

# Import du module NotebookLM
from notebooklm.upload_pdfs import NotebookLMUploader
from notebooklm.config import DEFAULT_LIMIT


def main():
    """Workflow complet."""
    parser = argparse.ArgumentParser(
        description="Workflow complet : EPUB→PDF + Upload NotebookLM"
    )
    parser.add_argument(
        "--folder",
        type=str,
        required=True,
        help="Dossier contenant les EPUBs à traiter"
    )
    parser.add_argument(
        "--title",
        type=str,
        required=True,
        help="Titre du notebook NotebookLM"
    )
    parser.add_argument(
        "--delete-epub",
        action="store_true",
        help="Supprimer les EPUBs après conversion"
    )
    parser.add_argument(
        "--headless",
        action="store_true",
        help="Mode headless pour NotebookLM"
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=DEFAULT_LIMIT,
        help=f"Limite de sources par notebook (défaut: {DEFAULT_LIMIT})"
    )
    
    args = parser.parse_args()
    folder = Path(args.folder)
    
    logger = setup_converter_logger()
    
    logger.info("=" * 70)
    logger.info("🚀 WORKFLOW COMPLET : EPUB → PDF → NotebookLM")
    logger.info("=" * 70)
    logger.info("")
    
    # ========================================
    # ÉTAPE 1 : Conversion EPUB → PDF
    # ========================================
    logger.info("📚 ÉTAPE 1/2 : Conversion EPUB → PDF")
    logger.info("-" * 70)
    
    try:
        # Initialiser le convertisseur
        converter = CalibreConverter()
        logger.info("✓ Calibre détecté")
        
        # Créer le watcher (sans surveillance continue)
        watcher = EpubWatcher(
            watch_path=folder,
            converter=converter,
            delete_epub=args.delete_epub,
            organize_by_date=True
        )
        
        # Traiter les EPUBs existants
        watcher.process_existing_epubs()
        
        # Récupérer le dossier de sortie créé
        output_folder = watcher.output_folder
        
        if not output_folder or not output_folder.exists():
            logger.error("❌ Aucun dossier de sortie créé (pas d'EPUBs trouvés ?)")
            sys.exit(1)
        
        logger.info("")
        logger.info(f"✅ Conversion terminée !")
        logger.info(f"📁 Dossier de sortie : {output_folder}")
        
        # Copier aussi les PDFs déjà présents dans le dossier source
        logger.info("")
        logger.info("📄 Récupération des PDFs existants...")
        import shutil
        from datetime import datetime
        
        existing_pdfs = list(folder.glob("*.pdf"))
        
        # Filtrer les PDFs du jour uniquement
        today = datetime.now().date()
        today_pdfs = [
            pdf for pdf in existing_pdfs
            if datetime.fromtimestamp(pdf.stat().st_mtime).date() == today
        ]
        
        if today_pdfs:
            logger.info(f"   → {len(today_pdfs)} PDF(s) du jour trouvé(s)")
            for pdf in today_pdfs:
                dest = output_folder / pdf.name
                if not dest.exists():  # Éviter les doublons
                    shutil.copy2(pdf, dest)
                    logger.info(f"   ✓ Copié : {pdf.name}")
        else:
            logger.info("   → Aucun PDF du jour trouvé")
        
        logger.info("")
        
    except FileNotFoundError as e:
        logger.error(f"❌ Erreur : {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"❌ Erreur lors de la conversion : {e}")
        sys.exit(1)
    
    # ========================================
    # ÉTAPE 2 : Upload vers NotebookLM
    # ========================================
    logger.info("")
    logger.info("📤 ÉTAPE 2/2 : Upload vers NotebookLM")
    logger.info("-" * 70)
    logger.info("")
    
    try:
        # Initialiser l'uploader NotebookLM
        uploader = NotebookLMUploader(
            headless=args.headless,
            limit=args.limit
        )
        
        # Lancer l'upload
        uploader.run(
            folder=output_folder,
            title=args.title
        )
        
    except Exception as e:
        logger.error(f"❌ Erreur lors de l'upload : {e}")
        sys.exit(1)
    
    # ========================================
    # FIN
    # ========================================
    logger.info("")
    logger.info("=" * 70)
    logger.info("🎉 WORKFLOW COMPLET TERMINÉ !")
    logger.info("=" * 70)
    logger.info("")
    logger.info(f"📁 Dossier traité : {output_folder}")
    logger.info(f"📚 Notebook créé sur NotebookLM")
    logger.info("")


if __name__ == "__main__":
    main()
