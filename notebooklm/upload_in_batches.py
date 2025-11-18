#!/usr/bin/env python3
"""Upload PDFs en lots de 50 avec fermeture/réouverture du navigateur"""
import sys
import shutil
import subprocess
from pathlib import Path
from notebooklm.utils import get_pdf_files

def main():
    if len(sys.argv) < 3:
        print("Usage: python upload_in_batches.py <folder> <notebook_url>")
        sys.exit(1)
    
    folder = Path(sys.argv[1])
    notebook_url = sys.argv[2]
    
    # Récupérer tous les PDFs
    pdfs = get_pdf_files(folder)
    print(f"📚 {len(pdfs)} PDFs trouvés")
    
    # Créer 3 dossiers de 50 PDFs max
    MAX_PER_LOT = 50
    num_lots = (len(pdfs) + MAX_PER_LOT - 1) // MAX_PER_LOT
    
    print(f"📦 Création de {num_lots} lot(s)")
    
    lots_folder = folder / "_lots"
    lots_folder.mkdir(exist_ok=True)
    
    for i in range(num_lots):
        lot_folder = lots_folder / f"lot{i+1}"
        lot_folder.mkdir(exist_ok=True)
        
        start = i * MAX_PER_LOT
        end = min((i + 1) * MAX_PER_LOT, len(pdfs))
        lot_pdfs = pdfs[start:end]
        
        # Copier les PDFs
        for pdf in lot_pdfs:
            shutil.copy2(pdf, lot_folder / pdf.name)
        
        print(f"   ✓ Lot {i+1} : {len(lot_pdfs)} PDFs")
    
    # Uploader chaque lot
    for i in range(num_lots):
        lot_folder = lots_folder / f"lot{i+1}"
        
        print(f"\n📤 Upload du lot {i+1}/{num_lots}...")
        
        cmd = [
            "python3", "notebooklm/upload_pdfs.py",
            "--folder", str(lot_folder),
            "--notebook-url", notebook_url
        ]
        
        result = subprocess.run(cmd, capture_output=False)
        
        if result.returncode != 0:
            print(f"❌ Erreur lors de l'upload du lot {i+1}")
            sys.exit(1)
        
        print(f"✅ Lot {i+1} uploadé")
    
    print("\n🎉 Tous les lots uploadés !")
    print(f"📓 {notebook_url}")

if __name__ == "__main__":
    main()
