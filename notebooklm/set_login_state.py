#!/usr/bin/env python3
"""
Script d'authentification pour NotebookLM.
Ouvre un navigateur et sauvegarde la session après connexion manuelle.
"""
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout

from config import NOTEBOOKLM_URL, STATE_FILE, TIMEOUT
from utils import setup_logger


def main():
    """Point d'entrée principal."""
    logger = setup_logger()
    
    logger.info("=" * 60)
    logger.info("🔐 Configuration de l'authentification NotebookLM")
    logger.info("=" * 60)
    logger.info("")
    
    try:
        with sync_playwright() as p:
            # Lancer le navigateur en mode visible
            logger.info("🌐 Ouverture du navigateur...")
            browser = p.chromium.launch(headless=False, slow_mo=100)
            context = browser.new_context()
            page = context.new_page()
            
            # Naviguer vers NotebookLM
            logger.info(f"📍 Navigation vers {NOTEBOOKLM_URL}...")
            page.goto(NOTEBOOKLM_URL, timeout=TIMEOUT)
            
            logger.info("")
            logger.info("👤 Veuillez vous connecter avec votre compte Google...")
            logger.info("⏳ En attente de la connexion...")
            logger.info("")
            
            # Attendre que l'utilisateur soit connecté
            # On détecte la connexion en attendant un élément spécifique de NotebookLM
            try:
                # Attendre le bouton "New notebook" ou un élément de l'interface principale
                page.wait_for_selector(
                    'button:has-text("New notebook"), [aria-label*="New notebook"]',
                    timeout=300000  # 5 minutes max
                )
                logger.info("✅ Connexion détectée !")
                
            except PlaywrightTimeout:
                logger.error("⏱️  Timeout : Connexion non détectée après 5 minutes")
                logger.info("💡 Assurez-vous de vous connecter dans le navigateur")
                browser.close()
                sys.exit(1)
            
            # Sauvegarder l'état de la session
            logger.info("💾 Sauvegarde de la session...")
            context.storage_state(path=str(STATE_FILE))
            
            logger.info("")
            logger.info("=" * 60)
            logger.info(f"✅ Session sauvegardée : {STATE_FILE}")
            logger.info("=" * 60)
            logger.info("")
            logger.info("🎉 Configuration terminée !")
            logger.info("Vous pouvez maintenant utiliser upload_pdfs.py")
            logger.info("")
            
            # Fermer le navigateur
            browser.close()
    
    except Exception as e:
        logger.error(f"❌ Erreur : {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
