"""Surveillance du système de fichiers pour détecter les nouveaux EPUBs."""
import time
import shutil
from datetime import datetime
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileCreatedEvent

from converter import CalibreConverter
from utils import setup_logger


class EpubHandler(FileSystemEventHandler):
    """Handler pour traiter les nouveaux fichiers EPUB."""
    
    def __init__(self, converter: CalibreConverter, delete_epub: bool = False, output_folder: Path = None):
        self.converter = converter
        self.delete_epub = delete_epub
        self.output_folder = output_folder
        self.logger = setup_logger()
        self.processing = set()  # Éviter les doublons
    
    def on_created(self, event):
        """Appelé quand un nouveau fichier est créé."""
        if event.is_directory:
            return
        
        if not isinstance(event, FileCreatedEvent):
            return
        
        file_path = Path(event.src_path)
        
        # Vérifier l'extension
        if file_path.suffix.lower() != '.epub':
            return
        
        # Éviter le traitement multiple
        if str(file_path) in self.processing:
            return
        
        self.processing.add(str(file_path))
        
        # Attendre que le fichier soit complètement écrit
        time.sleep(0.5)
        
        try:
            self._process_epub(file_path)
        finally:
            self.processing.discard(str(file_path))
    
    def _process_epub(self, epub_path: Path):
        """Traite un fichier EPUB détecté."""
        self.logger.info(f"📚 Détection de {epub_path.name}")
        
        try:
            # Conversion
            pdf_path = self.converter.convert(epub_path)
            self.logger.info(f"✓ Conversion réussie : {pdf_path.name}")
            
            # Déplacer les fichiers dans le dossier de sortie si spécifié
            if self.output_folder:
                # Déplacer le PDF
                new_pdf_path = self.output_folder / pdf_path.name
                shutil.move(str(pdf_path), str(new_pdf_path))
                
                # Déplacer l'EPUB (sauf si suppression demandée)
                if not self.delete_epub:
                    new_epub_path = self.output_folder / epub_path.name
                    shutil.move(str(epub_path), str(new_epub_path))
                    self.logger.info(f"📁 Fichiers déplacés vers : {self.output_folder.name}")
                else:
                    epub_path.unlink()
                    self.logger.info(f"📁 PDF déplacé vers : {self.output_folder.name}")
                    self.logger.info(f"🗑️  EPUB supprimé")
            else:
                # Suppression optionnelle de l'EPUB (mode sans dossier)
                if self.delete_epub:
                    epub_path.unlink()
                    self.logger.info(f"🗑️  EPUB supprimé : {epub_path.name}")
        
        except Exception as e:
            self.logger.error(f"✗ Erreur lors de la conversion de {epub_path.name} : {e}")


class EpubWatcher:
    """Surveille un dossier pour les nouveaux fichiers EPUB."""
    
    def __init__(self, watch_path: Path, converter: CalibreConverter, delete_epub: bool = False, organize_by_date: bool = True):
        self.watch_path = Path(watch_path)
        self.converter = converter
        self.delete_epub = delete_epub
        self.organize_by_date = organize_by_date
        self.output_folder = None
        self.logger = setup_logger()
        self.observer = None
    
    def _create_output_folder(self, first_epub: Path) -> Path:
        """Crée un dossier de sortie basé sur le premier fichier et la date."""
        # Nettoyer le nom du fichier (enlever extension et caractères spéciaux)
        base_name = first_epub.stem
        # Enlever les suffixes Z-Library
        base_name = base_name.replace(" (Z-Library)", "").strip()
        # Limiter la longueur et nettoyer
        base_name = base_name[:50].replace("/", "_").replace(":", "_")
        
        # Ajouter la date
        date_str = datetime.now().strftime("%Y-%m-%d")
        folder_name = f"{base_name}_{date_str}"
        
        # Créer le dossier
        output_path = self.watch_path / folder_name
        output_path.mkdir(exist_ok=True)
        
        return output_path
    
    def process_existing_epubs(self):
        """Traite les fichiers EPUB déjà présents dans le dossier."""
        epub_files = list(self.watch_path.glob("*.epub"))
        
        if not epub_files:
            self.logger.info("Aucun fichier EPUB existant à traiter")
            return
        
        self.logger.info(f"📚 {len(epub_files)} fichier(s) EPUB existant(s) détecté(s)")
        
        # Créer le dossier de sortie basé sur le premier fichier
        if self.organize_by_date:
            self.output_folder = self._create_output_folder(epub_files[0])
            self.logger.info(f"📁 Dossier de sortie : {self.output_folder.name}")
        
        event_handler = EpubHandler(self.converter, self.delete_epub, self.output_folder)
        for epub_file in epub_files:
            event_handler._process_epub(epub_file)
    
    def start(self):
        """Démarre la surveillance."""
        if not self.watch_path.exists():
            raise FileNotFoundError(f"Dossier introuvable : {self.watch_path}")
        
        self.logger.info(f"🔍 Surveillance démarrée : {self.watch_path}")
        
        # Traiter les fichiers existants
        self.process_existing_epubs()
        
        self.logger.info("\n👀 En attente de nouveaux fichiers EPUB...")
        self.logger.info("Appuyez sur Ctrl+C pour arrêter")
        
        event_handler = EpubHandler(self.converter, self.delete_epub, self.output_folder)
        self.observer = Observer()
        self.observer.schedule(event_handler, str(self.watch_path), recursive=False)
        self.observer.start()
        
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            self.stop()
    
    def stop(self):
        """Arrête la surveillance."""
        if self.observer:
            self.observer.stop()
            self.observer.join()
            self.logger.info("🛑 Surveillance arrêtée")
