"""Configuration pour l'automatisation NotebookLM."""
import os
from pathlib import Path

# Chemins
BASE_DIR = Path(__file__).parent
PDF_FOLDER = BASE_DIR / "pdfs"
STATE_FILE = BASE_DIR / "state.json"
LOG_FOLDER = BASE_DIR / "logs"

# NotebookLM
NOTEBOOKLM_URL = "https://notebooklm.google.com"
DEFAULT_NOTEBOOK_TITLE = "Nouveau Notebook"

# Limites
MAX_SOURCES_FREE = 50           # Limite gratuite
MAX_SOURCES_PLUS = 300          # Limite Plus (Pro)
DEFAULT_LIMIT = 300             # Limite par défaut (utilisateur Pro)

# Playwright
HEADLESS = os.getenv("HEADLESS", "false").lower() == "true"
TIMEOUT = int(os.getenv("TIMEOUT", "60000"))  # 60 secondes en ms
SLOW_MO = int(os.getenv("SLOW_MO", "100"))    # Ralentissement pour debug

# Upload
PROCESSING_TIMEOUT = int(os.getenv("PROCESSING_TIMEOUT", "60"))  # Secondes par PDF
DELAY_BETWEEN_ACTIONS = float(os.getenv("DELAY_BETWEEN_ACTIONS", "2"))  # Secondes

# Contraintes PDF
MAX_PDF_SIZE_MB = 200           # Taille max par PDF
MAX_PDF_WORDS = 500000          # Nombre max de mots par PDF

# Créer les dossiers nécessaires
LOG_FOLDER.mkdir(exist_ok=True)
PDF_FOLDER.mkdir(exist_ok=True)
