# Auto-Convertisseur EPUB vers PDF

Application Python qui surveille automatiquement le dossier Téléchargements macOS et convertit instantanément les fichiers EPUB en PDF dès leur arrivée.

## 🎯 Fonctionnalités

- ✅ Surveillance en temps réel du dossier Downloads
- ✅ Conversion automatique EPUB → PDF via Calibre
- ✅ Logging détaillé dans le terminal
- ✅ Gestion des erreurs robuste
- ✅ Qualité de conversion professionnelle

## 📋 Prérequis

- **macOS** 10.15+ (Catalina ou supérieur)
- **Python** 3.8+
- **Calibre** installé dans `/Applications/`

## 🚀 Installation

### 1. Installer Calibre

Téléchargez et installez Calibre depuis : https://calibre-ebook.com/download_osx

### 2. Installer l'application

```bash
# Cloner ou télécharger le projet
cd epub-to-pdf-watcher

# Lancer le script d'installation
chmod +x install.sh
./install.sh
```

## 💻 Utilisation

### Démarrer la surveillance

```bash
source venv/bin/activate && python3 main.py
```

L'application surveille maintenant votre dossier `~/Downloads`. Chaque fichier `.epub` qui arrive sera automatiquement converti en PDF.

### Arrêter la surveillance

Appuyez sur `Ctrl+C` dans le terminal.

## ⚙️ Configuration

Éditez `main.py` pour personnaliser :

```python
# Dossier à surveiller (ligne 17)
downloads_path = Path.home() / "Downloads"

# Supprimer l'EPUB après conversion (ligne 18)
delete_epub_after_conversion = False  # Mettre True pour supprimer
```

## 📝 Exemple d'utilisation

```
🚀 Auto-Convertisseur EPUB → PDF
============================================================
✓ Calibre détecté
🔍 Surveillance démarrée : /Users/henri/Downloads
Appuyez sur Ctrl+C pour arrêter

📚 Détection de livre_01.epub
✓ Conversion réussie : livre_01.pdf

📚 Détection de livre_02.epub
✓ Conversion réussie : livre_02.pdf
```

## 🛠️ Dépannage

### Calibre non détecté

Si vous obtenez l'erreur "Calibre n'est pas installé" :
- Vérifiez que Calibre est dans `/Applications/calibre.app`
- Ou modifiez le chemin dans `converter.py` ligne 11

### Permissions

Si vous avez des erreurs de permissions :
```bash
# Donner les droits d'accès au dossier Downloads
# Préférences Système → Sécurité → Accès complet au disque
```

## 📦 Structure du projet

```
epub-to-pdf-watcher/
├── README.md           # Documentation
├── requirements.txt    # Dépendances Python
├── main.py            # Point d'entrée
├── watcher.py         # Surveillance du dossier
├── converter.py       # Conversion via Calibre
├── utils.py           # Logging et utilitaires
└── install.sh         # Installation automatique
```

## 🔮 Améliorations futures (V2.0)

- [ ] Fichier de configuration YAML
- [ ] Notifications macOS
- [ ] Logs persistants
- [ ] Lancement automatique au démarrage (launchd)
- [ ] Support d'autres formats (MOBI, AZW3)

## 📄 Licence

Projet personnel - Henri @ Xipirons

## 🤝 Support

Pour toute question ou problème, ouvrez une issue sur le dépôt.

---

**Version** : 1.0.0  
**Date** : 18 novembre 2025  
**Auteur** : Henri @ Xipirons
