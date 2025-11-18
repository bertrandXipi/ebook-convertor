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
        """Crée un nouveau notebook et retourne son URL (Version Robuste)."""
        self.logger.info(f"📚 Création du notebook '{title}'...")
        
        try:
            # 1. Cliquer sur "Nouveau notebook"
            self.page.wait_for_selector('.create-new-action-button-icon-container, button:has-text("New notebook")', state='visible', timeout=60000)
            time.sleep(2)
            self.page.click('.create-new-action-button-icon-container, button:has-text("New notebook")')
            
            # 2. Attendre la redirection et le chargement complet
            self.page.wait_for_url("**/notebook/**", timeout=TIMEOUT)
            
            # 3. Pause explicite pour laisser Angular charger le DOM (crucial pour NotebookLM)
            time.sleep(3)
            
            # 4. Gestion du titre
            try:
                title_selector = 'input[aria-label*="Title"], input[data-placeholder="Untitled notebook"], .notebook-title-input'
                self.page.wait_for_selector(title_selector, state='visible', timeout=10000)
                self.page.click(title_selector)
                self.page.keyboard.press("Control+A")
                self.page.keyboard.press("Backspace")
                self.page.fill(title_selector, title)
                self.page.keyboard.press("Enter")
            except Exception as e:
                self.logger.warning(f"⚠️  Attention: Titre peut-être non défini ({e})")
            
            self.logger.info(f"✓ Notebook créé : {self.page.url}")
            return self.page.url
        
        except Exception as e:
            raise Exception(f"Erreur lors de la création du notebook : {e}")
    
    def upload_pdfs(self, pdf_files: List[Path], notebook_title: str, notebook_url: str, is_first: bool = True):
        """Upload avec simulation 100% humaine (Mouvements souris + Clic maintenu)."""
        total = len(pdf_files)
        self.logger.info(f"📤 Upload de {total} PDF(s)...")
        
        try:
            file_paths = [str(pdf.absolute()) for pdf in pdf_files]
            
            # Si ce n'est pas le premier upload, cliquer sur "Ajouter des sources"
            if not is_first:
                self.logger.info("📂 Ouverture de la modale...")
                try:
                    add_btn = 'button:has-text("Ajouter des sources"), button:has-text("Add sources")'
                    self.page.click(add_btn, timeout=10000)
                    time.sleep(2)
                except Exception as e:
                    self.logger.warning(f"⚠️  Impossible d'ouvrir la modale : {e}")
            
            # 1. CIBLAGE : On utilise le sélecteur précis
            btn_selector = 'button[aria-label="Importer des sources depuis votre ordinateur"]'
            self.logger.info("⏳ Recherche du bouton...")
            
            # On attend qu'il soit stable dans le DOM
            self.page.wait_for_selector(btn_selector, state='visible', timeout=30000)
            
            # Pause "humaine" pour que l'interface soit calme
            time.sleep(2)
            
            # 2. APPROCHE SOURIS (HOVER)
            self.logger.info("🖱️  Approche de la souris...")
            button = self.page.locator(btn_selector).first
            
            # On déplace la souris physiquement sur l'élément
            button.hover()
            
            # Petite pause comme si l'humain vérifiait qu'il est au bon endroit
            time.sleep(0.5)
            
            # 3. CLIC HUMAIN ET INTERCEPTION
            self.logger.info("👆 Clic physique...")
            with self.page.expect_file_chooser() as fc_info:
                # click(delay=200) maintient le clic enfoncé 200ms (comme un vrai doigt)
                button.click(delay=200)
            
            # 4. ENVOI DES FICHIERS
            file_chooser = fc_info.value
            self.logger.info(f"📂 Fenêtre ouverte, sélection de {len(file_paths)} fichiers...")
            file_chooser.set_files(file_paths)
            
            # 5. ATTENTE DU TRAITEMENT (CRUCIAL)
            self.logger.info("⏳ Attente de la réaction de NotebookLM...")
            
            # On attend un peu que l'upload commence visuellement
            time.sleep(5)
            
            # On attend la fin du traitement
            self._wait_for_processing(total)
            
            # Vérification de sécurité : on attend encore un peu pour être sûr que Google sauvegarde
            time.sleep(3)
            
            # Logs
            for pdf in pdf_files:
                self.upload_logger.log_upload(
                    notebook_title=notebook_title,
                    pdf_filename=pdf.name,
                    status="success",
                    url=notebook_url
                )
            
            self.logger.info(f"✅ {total} PDF(s) uploadé(s) avec succès")
        
        except PlaywrightTimeout:
            self.logger.error("❌ Le bouton n'a pas réagi ou la fenêtre ne s'est pas ouverte.")
            self.page.screenshot(path="debug_human_click_fail.png")
            raise
        except Exception as e:
            self.logger.error(f"❌ Erreur : {e}")
            self.page.screenshot(path="debug_error.png")
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
                
                # Traiter les PDFs par batch de 50 max
                # SOLUTION FIABLE : 1 notebook par lot de 50
                MAX_PER_UPLOAD = 50
                created_notebooks = []
                
                # Diviser TOUS les PDFs en lots de 50
                total_lots = (len(pdf_files) + MAX_PER_UPLOAD - 1) // MAX_PER_UPLOAD
                
                for lot_idx in range(total_lots):
                    start_idx = lot_idx * MAX_PER_UPLOAD
                    end_idx = min((lot_idx + 1) * MAX_PER_UPLOAD, len(pdf_files))
                    lot = pdf_files[start_idx:end_idx]
                    
                    # Titre du notebook
                    if total_lots > 1:
                        notebook_title = f"{title} - Lot {lot_idx + 1}"
                    else:
                        notebook_title = title
                    
                    self.logger.info("")
                    self.logger.info(f"📤 Notebook {lot_idx + 1}/{total_lots} : {len(lot)} PDF(s)")
                    
                    # Créer un nouveau notebook pour chaque lot
                    notebook_url = self.create_notebook(notebook_title)
                    
                    # Upload le lot (toujours "premier upload" car nouveau notebook)
                    self.upload_pdfs(lot, notebook_title, notebook_url, is_first=True)
                    
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
                self.logger.info("")
                self.logger.info("⏳ Attente de 30 secondes pour que NotebookLM finisse...")
                time.sleep(30)
                
                self.logger.info("👋 Fermeture du navigateur...")
                browser.close()
        
        except Exception as e:
            self.logger.error(f"❌ Erreur : {e}")
            sys.exit(1)
    
    def run_add_to_existing(self, folder: Path, notebook_url: str):
        """Ajoute des PDFs à un notebook existant."""
        self.logger.info("=" * 60)
        self.logger.info(f"🚀 Ajout de PDFs à un notebook existant")
        self.logger.info("=" * 60)
        self.logger.info("")
        
        # Récupérer les PDFs
        self.logger.info(f"📁 Scan du dossier : {folder}")
        pdf_files = get_pdf_files(folder)
        
        if not pdf_files:
            self.logger.warning("⚠️  Aucun fichier PDF trouvé")
            sys.exit(0)
        
        total_size = sum(pdf.stat().st_size for pdf in pdf_files)
        self.logger.info(f"   → {len(pdf_files)} PDF(s) trouvé(s) ({format_file_size(total_size)})")
        self.logger.info("")
        
        try:
            with sync_playwright() as p:
                self.logger.info("✓ Session chargée depuis state.json")
                browser = p.chromium.launch(headless=self.headless, slow_mo=100)
                context = browser.new_context(storage_state=str(STATE_FILE))
                self.page = context.new_page()
                
                # Aller sur le notebook existant
                self.logger.info(f"🌐 Navigation vers le notebook...")
                self.page.goto(notebook_url, timeout=TIMEOUT)
                time.sleep(3)
                
                # Upload les PDFs
                self.upload_pdfs(pdf_files, "Notebook existant", notebook_url, is_first=False)
                
                self.logger.info("")
                self.logger.info("=" * 60)
                self.logger.info("✅ Upload terminé !")
                self.logger.info(f"📚 {len(pdf_files)} PDF(s) ajouté(s) au notebook")
                self.logger.info(f"📓 {notebook_url}")
                self.logger.info("=" * 60)
                self.logger.info("")
                self.logger.info("⏳ Attente de 30 secondes pour que NotebookLM finisse...")
                time.sleep(30)
                
                self.logger.info("👋 Fermeture du navigateur...")
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
        required=False,
        help="Titre du notebook (requis seulement pour nouveau notebook)"
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
    parser.add_argument(
        "--notebook-url",
        type=str,
        help="URL d'un notebook existant (pour ajouter des sources)"
    )
    
    args = parser.parse_args()
    
    # Créer l'uploader et lancer
    uploader = NotebookLMUploader(
        headless=args.headless,
        limit=args.limit
    )
    
    if args.notebook_url:
        # Ajouter à un notebook existant
        uploader.run_add_to_existing(
            folder=Path(args.folder),
            notebook_url=args.notebook_url
        )
    else:
        # Créer un nouveau notebook
        if not args.title:
            print("❌ --title est requis pour créer un nouveau notebook")
            sys.exit(1)
        uploader.run(
            folder=Path(args.folder),
            title=args.title
        )


if __name__ == "__main__":
    main()
