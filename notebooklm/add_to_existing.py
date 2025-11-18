#!/usr/bin/env python3
"""Ajoute des PDFs à un notebook existant"""
import sys
from pathlib import Path
from notebooklm.upload_pdfs import NotebookLMUploader

# URL du notebook
NOTEBOOK_URL = "https://notebooklm.google.com/notebook/4a694a29-fd85-42d7-a1a2-08fd1ef93826"

# Dossier des PDFs
PDF_FOLDER = Path.home() / "Downloads" / "Limage (Jacques Aumont) (1)_2025-11-18"

# Créer l'uploader
uploader = NotebookLMUploader(headless=False, limit=300)

# Récupérer tous les PDFs
from notebooklm.utils import get_pdf_files
all_pdfs = get_pdf_files(PDF_FOLDER)

# Prendre les 44 derniers
last_44 = all_pdfs[-44:]

print(f"📚 Upload de {len(last_44)} PDFs vers le notebook existant")
print(f"📓 {NOTEBOOK_URL}")
print()

# Démarrer le navigateur
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False, slow_mo=100)
    context = browser.new_context(storage_state=str(uploader.upload_logger.log_folder.parent / "state.json"))
    uploader.page = context.new_page()
    
    # Aller sur le notebook
    uploader.page.goto(NOTEBOOK_URL)
    uploader.page.wait_for_load_state("networkidle")
    
    # Upload les 44 PDFs
    uploader.upload_pdfs(last_44, "Collection Complète 2", NOTEBOOK_URL, is_first=False)
    
    print("\n✅ Terminé ! Vérifiez le notebook.")
    input("Appuyez sur Entrée pour fermer...")
    browser.close()
