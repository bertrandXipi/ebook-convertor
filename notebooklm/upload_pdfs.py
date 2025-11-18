#!/usr/bin/env python3
"""
Script d'upload automatique de PDFs vers NotebookLM.
"""
import argparse
import sys
import time
from pathlib import Path
from typing import List
from playwright.sync_api import sync_playwright, Page, TimeoutError as PlaywrightTimeout

from config import (
    NOTEBOOKLM_URL, STATE_FILE, DEFAULT_LIMIT, HEADLESS,
    TIMEOUT, DELAY_BETWEEN_ACTIONS, PROCESSING_TIMEOUT, LOG_FOLDER
)
from utils import (
    setup_logger, UploadLogger, get_pdf_files,
    format_file_size, print_progress_bar
)


class NotebookLMUploader:
    """Gestionnaire d'upload pour NotebookLM."""
    
    def __init__(self, headless: bool = HEADLESS, limit: int = DEFAULT_LIMIT):
        self.headless = headless
        self.limit = limit
        self.logger = setup_logger()
        self.upload_logger = UploadLogger(LOG_FOLDER)
        self.page = None
    
    def create_notebook(self, title: str) -> str:
        """Crée un nouveau notebook et retourne son URL."""
        self.logger.info(f"📚 Création du notebook '{title}'...")
        
        try:
            # Cliquer sur "New notebook"
            self.page.click('button:has-text("New notebook")', timeout=TIMEOUT)
            time.sleep(DELAY_BETWEEN_ACTIONS)
            
            # Attendre que le notebook soit créé
            self.page.wait_for_url("**/notebook/**", timeout=TIMEOUT)
            notebook_url = self.page.url
            
            # Définir le titre
            try:
                title_input = self.page.locator('input[placeholder*="title"], [aria-label*="title"]').first
                title_input.fill(title)
                time.sleep(1)
            except Exception as e:
                self.logger.warning(f"⚠️  Impossible de définir le titre : {e}")
            
            self.logger.info(f"✓ Notebook créé : {notebook_url}")
            return notebook_url
        
        except Exception as e:
            raise Exception(f"Erreur lors de la création du notebook : {e}")
    
    def upload_pdfs(self, pdf_files: List[Path], notebook_title: str, notebook_url: str):
        """Upload une liste de PDFs vers le notebook."""
        total = len(pdf_files)
        self.logger.info(f"📤 Upload de {total} PDF(s)...")
        self.logger.info("")
        
        try:
            # Trouver l'input file
            file_input = self.page.locator('input[type="file"]').first
            
            # Convertir les paths en strings
            file_paths = [str(pdf.absolute()) for pdf in pdf_files]
            
            # Upload tous les fichiers en une fois
            self.logger.info("⬆️  Upload en cours...")
            file_input.set_input_files(file_paths)
            
            # Attendre un peu pour que l'upload démarre
            time.sleep(DELAY_BETWEEN_ACTIONS)
            
            # Attendre que tous les fichiers soient traités
            self.logger.info("⏳ Traitement des fichiers par NotebookLM...")
            self._wait_for_processing(total)
            
            # Logger tous les uploads comme réussis
            for pdf in pdf_files:
                self.upload_logger.log_upload(
                    notebook_title=notebook_title,
                    pdf_filename=pdf.name,
                    status="success",
                    url=notebook_url
                )
            
            self.logger.info("")
            self.logger.info(f"✅ {total} PDF(s) uploadé(s) avec succès")
        
        except Exception as e:
            self.logger.error(f"❌ Erreur lors de l'upload : {e}")
            # Logger les échecs
            for pdf in pdf_files:
                self.upload_logger.log_upload(
                    notebook_title=notebook_title,
                    pdf_filename=pdf.name,
                    status="failed",
                    error_message=str(e),
                    url=notebook_url
                )
            raise
    
    def _wait_for_processing(self, expected_count: int):
        """Attend que tous les fichiers soient traités."""
        max_wait = expected_count * PROCESSING_TIMEOUT
        start_time = time.time()
        
        while time.time() - start_time < max_wait:
            try:
                # Vérifier si des indicateurs de processing sont présents
                # Adapter selon l'interface réelle de NotebookLM
                processing = self.page.locator('[aria-label*="processing"], [aria-label*="uploading"]').count()
                
                if processing == 0:
                    # Attendre un peu plus pour être sûr
                    time.sleep(3)
                    return
                
                time.sleep(2)
            
            except Exception:
                # Si on ne peut pas détecter le processing, attendre un temps fixe
                time.sleep(5)
                return
        
        self.logger.warning(f"⚠️  Timeout atteint ({max_wait}s), mais les fichiers sont peut-être traités")
    
    def run(self, folder: Path, title: str):
        """Exécute l'upload complet."""
        self.logger.info("=" * 60)
        self.logger.info(f"🚀 NotebookLM PDF Uploader (Pro - {self.limit} sources/notebook)")
        self.logger.info("=" * 60)
        self.logger.info("")
        
        # Vérifier que state.json existe
        if not STATE_FILE.exists():
            self.logger.error("❌ Fichier state.json introuvable")
            self.logger.info("💡 Lancez d'abord : python set_login_state.py")
            sys.exit(1)
        
        # Récupérer les PDFs
        self.logger.info(f"📁 Scan du dossier : {folder}")
        pdf_files = get_pdf_files(folder)
        
        if not pdf_files:
            self.logger.warning("⚠️  Aucun fichier PDF trouvé")
            sys.exit(0)
        
        total_size = sum(pdf.stat().st_size for pdf in pdf_files)
        self.logger.info(f"   → {len(pdf_files)} PDF(s) trouvé(s) ({format_file_size(total_size)})")
        self.logger.info("")
        
        # Calculer le nombre de notebooks nécessaires
        num_notebooks = (len(pdf_files) + self.limit - 1) // self.limit
        
        if num_notebooks > 1:
            self.logger.info(f"⚠️  Limite de {self.limit} sources détectée")
            self.logger.info(f"   → {num_notebooks} notebook(s) seront créé(s)")
            self.logger.info("")
        
        try:
            with sync_playwright() as p:
                # Lancer le navigateur avec la session sauvegardée
                self.logger.info("✓ Session chargée depuis state.json")
                browser = p.chromium.launch(headless=self.headless, slow_mo=100)
                context = browser.new_context(storage_state=str(STATE_FILE))
                self.page = context.new_page()
                
                # Naviguer vers NotebookLM
                self.logger.info("🌐 Navigation vers NotebookLM...")
                self.page.goto(NOTEBOOKLM_URL, timeout=TIMEOUT)
                time.sleep(DELAY_BETWEEN_ACTIONS)
                
                # Traiter les PDFs par batch
                created_notebooks = []
                
                for i in range(num_notebooks):
                    start_idx = i * self.limit
                    end_idx = min((i + 1) * self.limit, len(pdf_files))
                    batch = pdf_files[start_idx:end_idx]
                    
                    # Titre du notebook
                    if num_notebooks > 1:
                        notebook_title = f"{title} - Partie {i + 1}"
                    else:
                        notebook_title = title
                    
                    self.logger.info("")
                    self.logger.info(f"📤 Upload Partie {i + 1}/{num_notebooks} ({len(batch)} PDF(s))...")
                    
                    # Créer le notebook
                    notebook_url = self.create_notebook(notebook_title)
                    
                    # Upload les PDFs
                    self.upload_pdfs(batch, notebook_title, notebook_url)
                    
                    created_notebooks.append({
                        'title': notebook_title,
                        'count': len(batch),
                        'url': notebook_url
                    })
                    
                    # Si ce n'est pas le dernier, retourner à l'accueil
                    if i < num_notebooks - 1:
                        self.page.goto(NOTEBOOKLM_URL, timeout=TIMEOUT)
                        time.sleep(DELAY_BETWEEN_ACTIONS)
                
                # Résumé final
                self.logger.info("")
                self.logger.info("=" * 60)
                self.logger.info("✅ Upload terminé !")
                self.logger.info(f"📚 {len(created_notebooks)} notebook(s) créé(s) :")
                for nb in created_notebooks:
                    self.logger.info(f"   - {nb['title']} ({nb['count']} PDF(s))")
                    self.logger.info(f"     {nb['url']}")
                self.logger.info(f"📊 Logs sauvegardés : {self.upload_logger.get_log_path()}")
                self.logger.info("=" * 60)
                
                browser.close()
        
        except Exception as e:
            self.logger.error(f"❌ Erreur : {e}")
            sys.exit(1)


def main():
    """Point d'entrée principal."""
    parser = argparse.ArgumentParser(
        description="Upload automatique de PDFs vers NotebookLM"
    )
    parser.add_argument(
        "--folder",
        type=str,
        required=True,
        help="Dossier contenant les PDFs à uploader"
    )
    parser.add_argument(
        "--title",
        type=str,
        required=True,
        help="Titre du notebook"
    )
    parser.add_argument(
        "--headless",
        action="store_true",
        help="Mode headless (sans interface graphique)"
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=DEFAULT_LIMIT,
        help=f"Nombre max de sources par notebook (défaut: {DEFAULT_LIMIT})"
    )
    
    args = parser.parse_args()
    
    # Créer l'uploader et lancer
    uploader = NotebookLMUploader(
        headless=args.headless,
        limit=args.limit
    )
    uploader.run(
        folder=Path(args.folder),
        title=args.title
    )


if __name__ == "__main__":
    main()
