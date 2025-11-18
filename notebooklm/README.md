# NotebookLM PDF Automation

Automatisation de l'upload en masse de fichiers PDF vers Google NotebookLM avec Playwright.

## 🎯 Fonctionnalités

- ✅ Authentification persistante (session sauvegardée)
- ✅ Upload en masse de PDFs
- ✅ Gestion automatique des limites (300 sources/notebook pour Pro)
- ✅ Création automatique de plusieurs notebooks si nécessaire
- ✅ Logs détaillés (terminal + CSV)
- ✅ Mode headless disponible

## 📋 Prérequis

- **Python** 3.8+
- **NotebookLM Pro** (300 sources/notebook)
- **Compte Google** avec accès à NotebookLM

## 🚀 Installation

### 1. Installer les dépendances

```bash
cd notebooklm
pip install -r requirements.txt
```

### 2. Installer Chromium

```bash
playwright install chromium --with-deps
```

## 💻 Utilisation

### 1. Configuration initiale (une seule fois)

Authentifiez-vous à NotebookLM :

```bash
python set_login_state.py
```

→ Un navigateur s'ouvre, connectez-vous avec votre compte Google  
→ La session est sauvegardée dans `state.json`

### 2. Upload de PDFs

```bash
python upload_pdfs.py --folder "../Downloads/Espagnol_2025-11-18" --title "Espagnol - Grammaire"
```

**Options disponibles :**

```bash
# Mode headless (sans interface graphique)
python upload_pdfs.py --folder "./pdfs" --title "Maths" --headless

# Limite personnalisée
python upload_pdfs.py --folder "./pdfs" --title "Histoire" --limit 100
```

## 📊 Exemple de sortie

```
🚀 NotebookLM PDF Uploader (Pro - 300 sources/notebook)
============================================================

✓ Session chargée depuis state.json
🌐 Navigation vers NotebookLM...
📁 Scan du dossier : ../Downloads/Espagnol_2025-11-18
   → 423 PDF(s) trouvé(s) (2.3 GB)

⚠️  Limite de 300 sources détectée
   → 2 notebook(s) seront créé(s)

📤 Upload Partie 1/2 (300 PDF(s))...
📚 Création du notebook 'Espagnol - Grammaire - Partie 1'...
✓ Notebook créé : https://notebooklm.google.com/notebook/abc123
📤 Upload de 300 PDF(s)...
⬆️  Upload en cours...
⏳ Traitement des fichiers par NotebookLM...
✅ 300 PDF(s) uploadé(s) avec succès

📤 Upload Partie 2/2 (123 PDF(s))...
📚 Création du notebook 'Espagnol - Grammaire - Partie 2'...
✓ Notebook créé : https://notebooklm.google.com/notebook/def456
📤 Upload de 123 PDF(s)...
⬆️  Upload en cours...
⏳ Traitement des fichiers par NotebookLM...
✅ 123 PDF(s) uploadé(s) avec succès

============================================================
✅ Upload terminé !
📚 2 notebook(s) créé(s) :
   - Espagnol - Grammaire - Partie 1 (300 PDF(s))
     https://notebooklm.google.com/notebook/abc123
   - Espagnol - Grammaire - Partie 2 (123 PDF(s))
     https://notebooklm.google.com/notebook/def456
📊 Logs sauvegardés : logs/upload_2025-11-18_14-30-45.csv
============================================================
```

## 📁 Structure

```
notebooklm/
├── __init__.py
├── config.py              # Configuration
├── set_login_state.py     # Script d'authentification
├── upload_pdfs.py         # Script principal
├── utils.py               # Utilitaires
├── requirements.txt       # Dépendances
├── state.json            # Session (généré, gitignored)
├── logs/                 # Logs CSV
└── README.md
```

## 🛠️ Configuration

Éditez `config.py` pour personnaliser :

```python
# Limites
DEFAULT_LIMIT = 300        # Limite par défaut (Pro)

# Playwright
HEADLESS = False           # Mode headless
TIMEOUT = 60000            # Timeout (ms)

# Upload
PROCESSING_TIMEOUT = 60    # Timeout par PDF (secondes)
DELAY_BETWEEN_ACTIONS = 2  # Délai entre actions (secondes)
```

Ou utilisez des variables d'environnement :

```bash
export HEADLESS=true
export TIMEOUT=90000
python upload_pdfs.py --folder "./pdfs" --title "Test"
```

## 🐛 Dépannage

### Session expirée

Si vous obtenez une erreur d'authentification :

```bash
python set_login_state.py
```

### Timeout lors de l'upload

Augmentez le timeout :

```bash
export PROCESSING_TIMEOUT=120
python upload_pdfs.py --folder "./pdfs" --title "Test"
```

### Sélecteurs invalides

Si l'interface de NotebookLM a changé, mettez à jour les sélecteurs dans `upload_pdfs.py`.

## 📝 Logs

Les logs sont sauvegardés dans `logs/upload_YYYY-MM-DD_HH-MM-SS.csv` :

```csv
timestamp,notebook_title,pdf_filename,status,error_message,url
2025-11-18 14:30:45,Espagnol - Partie 1,livre_01.pdf,success,,https://notebooklm.google.com/notebook/abc123
2025-11-18 14:31:12,Espagnol - Partie 1,livre_02.pdf,success,,https://notebooklm.google.com/notebook/abc123
```

## 🔮 Améliorations futures (V2)

- [ ] Option `--resume` pour reprendre un upload interrompu
- [ ] Upload parallèle de plusieurs notebooks
- [ ] Intégration avec watchdog pour auto-upload
- [ ] Export des logs en JSON
- [ ] Support d'autres formats (EPUB, DOCX)

## 📄 Licence

Projet personnel - Henri @ Xipirons

---

**Version** : 1.0.0  
**Date** : 18 novembre 2025
