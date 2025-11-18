# Requirements - Automatisation Upload PDFs NotebookLM

**Version:** 1.0  
**Date:** 18 novembre 2025  
**Auteur:** Henri @ Xipirons  
**Branche:** feature/notebooklm-automation

---

## 🎯 Objectif

Créer un script Python avec Playwright qui automatise l'upload en masse de fichiers PDF vers Google NotebookLM, en simulant le processus d'upload manuel que l'utilisateur effectue actuellement.

## 📋 Contexte

Actuellement, l'utilisateur télécharge des livres depuis Z-Library, les convertit en PDF (via le convertisseur EPUB), puis doit manuellement uploader ces PDFs vers NotebookLM pour créer des notebooks d'étude. Ce processus manuel est répétitif et chronophage.

## 🎯 Objectifs du Projet

1. **Automatiser l'authentification** à NotebookLM avec persistance de session
2. **Uploader en masse** des PDFs depuis un dossier local
3. **Gérer les limites** de NotebookLM (50 sources gratuit, 300 sources Plus)
4. **Créer automatiquement** plusieurs notebooks si nécessaire
5. **Logger les opérations** pour traçabilité et reprise sur erreur

---

## 📦 Fonctionnalités Requises

### 1. Authentification Persistante

**Script:** `set_login_state.py`

**Comportement:**
- Ouvre un navigateur Chromium en mode visible
- Navigue vers https://notebooklm.google.com
- Attend que l'utilisateur se connecte manuellement avec son compte Google
- Détecte automatiquement la connexion réussie
- Sauvegarde l'état de session (cookies, localStorage, sessionStorage) dans `state.json`
- Affiche un message de confirmation

**Critères d'acceptation:**
- ✅ Le fichier `state.json` est créé après connexion
- ✅ La session reste valide pendant au moins 7 jours
- ✅ Le script peut être relancé pour rafraîchir la session
- ✅ Gestion d'erreur si l'utilisateur ferme le navigateur sans se connecter

---

### 2. Upload Automatique de PDFs

**Script:** `upload_pdfs.py`

**Comportement:**
- Charge la session depuis `state.json`
- Navigue vers NotebookLM
- Crée un nouveau notebook
- Scanne le dossier spécifié pour trouver tous les fichiers PDF
- Upload tous les PDFs en une seule opération (multi-upload)
- Attend que NotebookLM traite tous les fichiers
- Nomme le notebook avec le titre fourni en paramètre
- Affiche la progression en temps réel dans le terminal

**Paramètres:**
```bash
python upload_pdfs.py --folder "./mes_pdfs" --title "Espagnol - Grammaire"
```

**Options supplémentaires:**
- `--headless` : Mode sans interface graphique (défaut: False)
- `--timeout` : Timeout en secondes pour le processing (défaut: 60)
- `--limit` : Nombre max de sources par notebook (défaut: 300)

**Critères d'acceptation:**
- ✅ Tous les PDFs du dossier sont uploadés
- ✅ Le notebook est créé avec le titre spécifié
- ✅ La progression est affichée (ex: "Uploading 3/10 PDFs...")
- ✅ Le script attend que tous les PDFs soient traités avant de terminer
- ✅ Un message de succès avec l'URL du notebook est affiché

---

### 3. Gestion des Limites NotebookLM

**Limites:**
- NotebookLM gratuit: **50 sources max** par notebook
- NotebookLM Plus: **300 sources max** par notebook

**Comportement:**
- Si le dossier contient plus de PDFs que la limite, créer automatiquement plusieurs notebooks
- Nommer les notebooks séquentiellement:
  - "Espagnol - Grammaire - Partie 1"
  - "Espagnol - Grammaire - Partie 2"
  - etc.
- Afficher un résumé à la fin:
  ```
  ✅ Upload terminé !
  📚 2 notebooks créés:
     - Espagnol - Grammaire - Partie 1 (300 PDFs)
     - Espagnol - Grammaire - Partie 2 (123 PDFs)
  ```

**Critères d'acceptation:**
- ✅ Détection automatique du nombre de notebooks nécessaires
- ✅ Création séquentielle des notebooks
- ✅ Répartition équilibrée des PDFs entre notebooks
- ✅ Logs détaillés pour chaque notebook créé

---

### 4. Configuration

**Fichier:** `config.py`

**Variables:**
```python
# Chemins
PDF_FOLDER = "./pdfs"           # Dossier source des PDFs
STATE_FILE = "state.json"       # Fichier de session
LOG_FOLDER = "./logs"           # Dossier des logs

# NotebookLM
NOTEBOOKLM_URL = "https://notebooklm.google.com"
DEFAULT_NOTEBOOK_TITLE = "Nouveau Notebook"

# Limites
MAX_SOURCES_FREE = 50           # Limite gratuite
MAX_SOURCES_PLUS = 300          # Limite Plus (Pro)
DEFAULT_LIMIT = 300             # Limite par défaut (utilisateur Pro)

# Playwright
HEADLESS = False                # Mode headless
TIMEOUT = 60000                 # Timeout en ms (60s)
SLOW_MO = 100                   # Ralentissement pour debug (ms)

# Upload
PROCESSING_TIMEOUT = 60         # Timeout par PDF (secondes)
DELAY_BETWEEN_ACTIONS = 2       # Délai entre actions (secondes)

# Contraintes PDF
MAX_PDF_SIZE_MB = 200           # Taille max par PDF
MAX_PDF_WORDS = 500000          # Nombre max de mots par PDF
```

**Critères d'acceptation:**
- ✅ Toutes les variables sont documentées
- ✅ Valeurs par défaut sensées
- ✅ Possibilité de surcharger via variables d'environnement

---

### 5. Gestion d'Erreurs et Logging

**Logs Terminal:**
```
🚀 NotebookLM PDF Uploader (Pro - 300 sources/notebook)
============================================================
✓ Session chargée depuis state.json
🌐 Navigation vers NotebookLM...
📚 Création du notebook "Espagnol - Grammaire"...
📁 Scan du dossier: ./mes_pdfs
   → 423 PDFs trouvés

⚠️  Limite de 300 sources détectée
   → 2 notebooks seront créés

📤 Upload Partie 1/2 (300 PDFs)...
   [████████████████████] 300/300 (100%)
   ✓ Tous les fichiers traités

📤 Upload Partie 2/2 (123 PDFs)...
   [████████████████████] 123/123 (100%)
   ✓ Tous les fichiers traités

✅ Upload terminé !
📚 2 notebooks créés avec succès
📊 Logs sauvegardés: logs/upload_2025-11-18_14-30-45.csv
```

**Fichier CSV de Log:**
```csv
timestamp,notebook_title,pdf_filename,status,error_message,url
2025-11-18 14:30:45,Espagnol - Partie 1,livre_01.pdf,success,,https://notebooklm.google.com/notebook/abc123
2025-11-18 14:31:12,Espagnol - Partie 1,livre_02.pdf,success,,https://notebooklm.google.com/notebook/abc123
2025-11-18 14:31:45,Espagnol - Partie 1,livre_03.pdf,failed,File too large,
```

**Gestion d'erreurs:**
- Try/except sur toutes les opérations critiques
- Messages d'erreur clairs et actionnables
- Possibilité de reprendre un upload interrompu (skip des PDFs déjà uploadés)
- Timeout configurable pour éviter les blocages infinis

**Critères d'acceptation:**
- ✅ Logs détaillés dans le terminal avec emojis et couleurs
- ✅ Fichier CSV créé avec horodatage
- ✅ Gestion des erreurs courantes (session expirée, PDF trop gros, timeout)
- ✅ Option `--resume` pour reprendre un upload interrompu

---

## 🛠️ Stack Technique

### Langage
- **Python 3.8+** (minimum requis pour Playwright)

### Dépendances Principales

**requirements.txt:**
```
playwright>=1.48.0
python-dotenv>=1.0.0
```

**Dépendances automatiques de Playwright:**
- pyee>=13,<14
- greenlet>=3.1.1,<4.0.0

### Navigateur
- **Chromium** (installé via `playwright install chromium`)

### Installation
```bash
# Créer environnement virtuel
python3 -m venv venv

# Activer (macOS/Linux)
source venv/bin/activate

# Installer dépendances
pip install -r requirements.txt

# Installer navigateur Chromium
playwright install chromium --with-deps
```

---

## 📁 Structure du Projet

```
ebook-convertor/                    # Projet existant
├── notebooklm/                     # Nouveau module
│   ├── __init__.py
│   ├── config.py                   # Configuration
│   ├── set_login_state.py          # Script d'authentification
│   ├── upload_pdfs.py              # Script principal
│   ├── utils.py                    # Utilitaires (logging, etc.)
│   ├── state.json                  # État de session (généré, gitignored)
│   ├── logs/                       # Dossier des logs
│   │   └── upload_*.csv
│   ├── requirements.txt            # Dépendances spécifiques
│   └── README.md                   # Documentation du module
├── converter.py                    # Existant
├── watcher.py                      # Existant
└── ...
```

---

## 🎯 Spécifications Playwright Critiques

### Sélecteurs à Utiliser

**Bouton "New notebook":**
```python
page.click('text=New notebook')
# ou
page.click('button:has-text("New notebook")')
```

**Input file pour upload:**
```python
file_input = page.locator('input[type="file"]')
file_input.set_input_files([path1, path2, path3, ...])
```

**Zone de titre du notebook:**
```python
page.fill('input[placeholder*="title"]', "Mon Titre")
# ou
page.fill('[aria-label*="title"]', "Mon Titre")
```

**Indicateurs de processing:**
```python
# Attendre que les sources apparaissent
page.wait_for_selector('.source-item', timeout=60000)

# Attendre que le processing soit terminé
page.wait_for_selector('.processing-indicator', state='hidden')
```

### Méthode d'Upload

**Approche 1: Multiple files via input (recommandée)**
```python
file_input = page.locator('input[type="file"]')
file_input.set_input_files([
    "/path/to/file1.pdf",
    "/path/to/file2.pdf",
    "/path/to/file3.pdf"
])
```

**Approche 2: Drag & Drop (si nécessaire)**
```python
# Utiliser dispatchEvent avec DataTransfer
page.evaluate("""
    const dataTransfer = new DataTransfer();
    // Ajouter les fichiers...
    element.dispatchEvent(new DragEvent('drop', { dataTransfer }));
""")
```

### Gestion de Session

```python
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    context = browser.new_context(storage_state="state.json")
    page = context.new_page()
    # ...
```

### Mode Headless

```python
# Pour debug (voir le navigateur)
browser = p.chromium.launch(headless=False, slow_mo=100)

# Pour production (invisible)
browser = p.chromium.launch(headless=True)
```

---

## ⚠️ Contraintes Techniques

### Timeouts
- **Timeout généreux** pour le processing des PDFs: 30-60 secondes par fichier volumineux
- **Délai entre actions**: 1-2 secondes pour éviter rate limiting
- **Timeout global**: Configurable, défaut 60 secondes

### Limites PDF
- **Taille max par PDF**: 200 MB
- **Nombre max de mots**: 500,000 mots par PDF
- **Formats supportés**: PDF uniquement (pour cette version)

### Limites NotebookLM
- **Gratuit**: 50 sources max par notebook
- **Plus**: 300 sources max par notebook
- **Rate limiting**: Respecter les délais entre requêtes

### Compatibilité
- **Python**: ≥ 3.8 requis
- **OS**: macOS, Linux, Windows
- **Navigateur**: Chromium (géré par Playwright)

---

## 🚀 Workflow d'Utilisation

### 1. Configuration Initiale (une seule fois)

```bash
cd notebooklm
python set_login_state.py
```

→ Navigateur s'ouvre, utilisateur se connecte, session sauvegardée

### 2. Upload de PDFs

```bash
python upload_pdfs.py --folder "../Downloads/Espagnol_2025-11-18" --title "Espagnol - Grammaire"
```

→ Tous les PDFs du dossier sont uploadés automatiquement

### 3. Upload avec Options

```bash
# Mode headless
python upload_pdfs.py --folder "./pdfs" --title "Maths" --headless

# Limite personnalisée (si besoin de limiter à moins de 300)
python upload_pdfs.py --folder "./pdfs" --title "Histoire" --limit 100

# Reprendre un upload interrompu
python upload_pdfs.py --folder "./pdfs" --title "Physique" --resume
```

---

## 🎁 Options Avancées (Nice to Have - V2)

### Phase 2 (Optionnel)
- [ ] Flag `--parallel` pour créer plusieurs notebooks simultanément
- [ ] Tri automatique des PDFs par thématique (basé sur noms de fichiers)
- [ ] Intégration avec `watchdog` pour auto-upload quand nouveaux PDFs arrivent
- [ ] Export des logs en JSON pour intégration N8N
- [ ] Support d'autres formats (EPUB, DOCX, TXT)
- [ ] Interface graphique simple (Tkinter)
- [ ] Notifications macOS à la fin de l'upload

---

## ✅ Critères de Succès

### Fonctionnels
- ✅ L'utilisateur peut uploader 100+ PDFs en un clic
- ✅ La session reste valide pendant au moins 7 jours
- ✅ Les notebooks sont créés automatiquement selon les limites
- ✅ Tous les PDFs sont uploadés avec succès (taux de succès > 95%)
- ✅ Les erreurs sont loggées et l'utilisateur peut reprendre

### Techniques
- ✅ Code Python propre et documenté
- ✅ Gestion d'erreurs robuste
- ✅ Logs détaillés et exploitables
- ✅ Performance acceptable (< 5 secondes par PDF)
- ✅ Compatible macOS (priorité), Linux, Windows

### UX
- ✅ Messages clairs et informatifs dans le terminal
- ✅ Progression visible en temps réel
- ✅ Pas d'intervention manuelle requise après lancement
- ✅ Documentation claire pour installation et utilisation

---

## 📚 Références

- [Playwright Python Documentation](https://playwright.dev/python/docs/intro)
- [NotebookLM Automation Example](https://github.com/DataNath/notebooklm_source_automation)
- [Automating NotebookLM with Python](https://oboe-violin-w3kd.squarespace.com/blogs/automating-link-uploads-to-notebooklm-using-python-and-playwright)
- [NotebookLM Upload Limits](https://elephas.app/blog/how-to-upload-more-files-notebooklm)
- [Playwright Python Package Guide](https://generalistprogrammer.com/tutorials/playwright-python-package-guide)

---

**Version:** 1.0  
**Statut:** Requirements validés  
**Prochaine étape:** Implémentation
