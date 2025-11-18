#!/usr/bin/env python3
"""
Script d'authentification pour NotebookLM.
Ouvre un navigateur et attend que tu te connectes manuellement (avec passkey/empreinte).
"""
import sys
import time
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
            browser = p.chromium.launch(
                headless=False,
                slow_mo=100,
                args=[
                    '--disable-blink-features=AutomationControlled',
                ]
            )
            
            # Créer un contexte avec user agent réaliste
            context = browser.new_context(
                user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                viewport={'width': 1920, 'height': 1080}
            )
            
            page = context.new_page()
            
            # Masquer l'automatisation
            page.add_init_script("""
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                });
            """)
            
            # Naviguer vers NotebookLM
            logger.info(f"📍 Navigation vers {NOTEBOOKLM_URL}...")
            page.goto(NOTEBOOKLM_URL, timeout=TIMEOUT)
            time.sleep(2)
            
            logger.info("")
            logger.info("👤 Veuillez vous connecter avec votre compte Google...")
            logger.info("   → Utilisez votre empreinte digitale (Touch ID)")
            logger.info("   → Ou scannez le QR code avec votre téléphone")
            logger.info("")
            logger.info("⏳ En attente de la connexion...")
            logger.info("   (Timeout: 5 minutes)")
            logger.info("")
            
            # Attendre que l'utilisateur soit connecté
            # On détecte la connexion en attendant un élément spécifique de NotebookLM
            try:
                # Attendre le bouton "New notebook" ou l'interface principale
                # Nouveau sélecteur pour l'interface mise à jour
                page.wait_for_selector(
                    '.create-new-action-button-icon, mat-icon:has-text("add"), button:has-text("New notebook")',
                    timeout=300000  # 5 minutes max
                )
                logger.info("✅ Connexion détectée !")
                
            except PlaywrightTimeout:
                logger.error("⏱️  Timeout : Connexion non détectée après 5 minutes")
                logger.info("💡 Assurez-vous de vous connecter dans le navigateur")
                browser.close()
                sys.exit(1)
            
            # Attendre un peu pour que tout se stabilise
            logger.info("⏳ Stabilisation de la session...")
            time.sleep(5)
            
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
            time.sleep(2)
            browser.close()
    
    except Exception as e:
        logger.error(f"❌ Erreur : {e}")
        logger.info("")
        logger.info("💡 Conseils :")
        logger.info("   - Assurez-vous d'être connecté à NotebookLM")
        logger.info("   - Attendez que l'interface principale soit chargée")
        logger.info("   - Relancez le script si nécessaire")
        sys.exit(1)


if __name__ == "__main__":
    main()
