"""Logique de conversion EPUB vers PDF via Calibre."""
import subprocess
from pathlib import Path
from typing import Optional


class CalibreConverter:
    """Convertisseur EPUB vers PDF utilisant Calibre CLI."""
    
    def __init__(self, calibre_path: str = "/Applications/calibre.app/Contents/MacOS/ebook-convert"):
        self.calibre_path = Path(calibre_path)
        self._check_calibre_installed()
    
    def _check_calibre_installed(self):
        """Vérifie que Calibre est installé."""
        if not self.calibre_path.exists():
            raise FileNotFoundError(
                f"Calibre n'est pas installé à {self.calibre_path}.\n"
                "Installez Calibre depuis : https://calibre-ebook.com/download_osx"
            )
    
    def convert(self, epub_path: Path, pdf_path: Optional[Path] = None) -> Path:
        """
        Convertit un fichier EPUB en PDF.
        
        Args:
            epub_path: Chemin du fichier EPUB source
            pdf_path: Chemin du fichier PDF destination (optionnel)
        
        Returns:
            Path: Chemin du fichier PDF créé
        
        Raises:
            FileNotFoundError: Si le fichier EPUB n'existe pas
            subprocess.CalledProcessError: Si la conversion échoue
        """
        if not epub_path.exists():
            raise FileNotFoundError(f"Fichier EPUB introuvable : {epub_path}")
        
        # Définir le chemin de sortie
        if pdf_path is None:
            pdf_path = epub_path.with_suffix('.pdf')
        
        # Options de conversion pour qualité optimale
        cmd = [
            str(self.calibre_path),
            str(epub_path),
            str(pdf_path),
            '--paper-size', 'a4',
            '--pdf-page-margin-bottom', '72',
            '--pdf-page-margin-top', '72',
            '--pdf-page-margin-left', '72',
            '--pdf-page-margin-right', '72',
        ]
        
        # Exécuter la conversion
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True
        )
        
        return pdf_path
