# 🛡️ CodeGuardian — Détection Intelligente des Bugs & Qualité Logicielle

**CodeGuardian** est une solution complète d'analyse de code combinant **l'analyse statique AST**, la **détection algorithmique de duplications**, la **prédiction des défauts logiciels par IA & métriques Git (churn/complexité)**, et des **suggestions interactives de remédiation assistées par IA** avec génération de correctifs (diffs).

Conçu selon les standards du génie logiciel moderne avec **FastAPI**, **React 18 / Tailwind CSS**, **CLI riche**, suite de tests automatisés et pipelines **CI/CD (GitHub Actions & GitLab CI)**.

---

## 🌟 Fonctionnalités Clés

### 🧠 1. Intelligence Artificielle & Génie Logiciel
- **Détection des bugs & code mal structuré** :
  - Parsing multi-langage par AST (Abstract Syntax Tree) Python et analyse heuristique/pattern JavaScript.
  - Détection des clauses `except:` nues, des arguments par défaut mutables (`def f(items=[])`), comparaisons non sécurisées (`== None`), structures cyclomatiques critiques, et "God methods".
- **Sécurité logicielle (DevSecOps)** :
  - Détection immédiate des secrets et clés d'API codés en dur (GitHub PAT, AWS keys, JWT, mots de passe) avec masquage automatique.
  - Identification des injections SQL (interpolation dynamique de chaînes f-string).
  - Détection des fonctions d'exécution arbitraire dangereuses (`eval()`, `exec()`, `os.system()`).
- **Identification des duplications & clones** :
  - Algorithme de fenêtre glissante par hachage Rabin-Karp détectant les clones exacts et quasi-identiques multi-fichiers, avec calcul du ratio de duplication global.
- **Suggestions de correction IA avec explications & diffs** :
  - Diagnostic complet de la cause racine technique.
  - Génération de code réparé prêt à l'emploi.
  - Vue **Unified Diff** intégrée avec coloration avant/après.
  - Liste de contrôle des bonnes pratiques logicielles.
  - Moteur IA hybride : supporte Gemini / OpenAI / Ollama ou moteur expert sémantique offline garanti sans dépendance externe.
- **Prédiction des fichiers les plus susceptibles de contenir des bugs (Hotspots)** :
  - Modèle prédictif fusionnant les métriques statiques (Complexité Cyclomatique de McCabe, Complexité Cognitive, Index de Maintenabilité SEI) et la dynamique Git (code churn, fréquence des commits, historique des commits de correctifs de bugs récents).
  - Score de risque (0 à 100%) et niveau de sévérité (`CRITICAL`, `HIGH`, `MEDIUM`, `LOW`).

### ⚙️ 2. Partie Génie Logiciel & Pipeline CI/CD
- **CLI Développeur (`codeguardian cli`)** :
  - Exécution en terminal avec tableaux Rich colorés et calcul du Health Score.
  - Codes de sortie conformes aux pipelines (`exit 1` en cas d'échec de la Quality Gate sur bugs critiques, `exit 0` en cas de succès).
  - Exportation directe des rapports en **Markdown**, **JSON** et **HTML**.
- **Historique & Traçabilité (SQLite / SQLAlchemy)** :
  - Persistance des projets, branches Git, commits, défauts et métriques de santé au fil du temps.
- **Intégration CI/CD clé en main** :
  - Workflow GitHub Actions prêt à l'emploi : `.github/workflows/codeguardian-ci.yml`.
  - Pipeline GitLab CI prêt à l'emploi : `.gitlab-ci.yml`.
  - Configuration de hooks Git locaux : `.pre-commit-config.yaml`.
- **Suite de tests automatisés (Pytest)** :
  - Couverture complète de l'analyseur AST, du détecteur de duplication, du prédicteur de risque et des endpoints de l'API.

---

## 🏛️ Architecture Technique

```
CodeGuardian/
├── backend/
│   ├── app/
│   │   ├── core/
│   │   │   ├── static_analyzer.py      # Moteur d'analyse statique AST & patterns
│   │   │   ├── complexity_metrics.py   # Complexité cyclomatique, cognitive, Halstead & MI
│   │   │   ├── duplication_detector.py # Détecteur de clones par rolling hash
│   │   │   ├── git_analyzer.py         # Churn Git, historique des commits et bugs
│   │   │   ├── bug_predictor.py        # Modèle de prédiction des hotspots
│   │   │   └── ai_engine.py            # Diagnostic IA, explications et génération de diffs
│   │   ├── routers/
│   │   │   ├── scans.py                # Déclenchement & détails des analyses
│   │   │   ├── ai.py                   # Endpoint de réparation interactive IA
│   │   │   ├── git_insights.py         # Métriques Git et points chauds
│   │   │   └── reports.py              # Export Markdown, JSON, HTML
│   │   ├── cli.py                      # CLI CodeGuardian pour terminal et CI/CD
│   │   ├── models.py                   # Modèles de données SQLAlchemy
│   │   ├── schemas.py                  # Schémas de validation Pydantic
│   │   └── main.py                     # Application FastAPI & montage statique
│   ├── tests/                          # Suite de tests unitaires et d'intégration
│   └── requirements.txt
├── frontend/                           # Dashboard moderne React 18, Vite & Tailwind CSS
│   ├── src/
│   │   ├── components/                 # Modales IA, Navbar, Métriques, Diff Viewer
│   │   ├── pages/                      # Dashboard, Défauts, Hotspots IA, Duplications, Historique
│   │   └── api/                        # Client API REST TypeScript
│   └── package.json
├── sample_project/                     # Projet témoin avec défauts réels pour démonstration
├── .github/workflows/codeguardian-ci.yml
├── .gitlab-ci.yml
└── .pre-commit-config.yaml
```

---

## 🚀 Démarrage Rapide

### 1. Prérequis
- Python 3.10+ (Python 3.12 recommandé)
- Node.js 18+ et npm

### 2. Démarrer l'Application Complète (Backend + Frontend Dashboard)

#### Option A : Démarrer le serveur unifié (FastAPI servant l'API + l'UI compilée)
```bash
# 1. Installer et activer le venv backend
cd backend
python -m venv .venv
# Sur Windows :
.venv\Scripts\activate
# Sur Linux / macOS :
# source .venv/bin/activate

pip install -r requirements.txt

# 2. Lancer le serveur unifié
python run_backend.py
```
Ouvrez votre navigateur sur **`http://localhost:8000`** pour accéder au Dashboard CodeGuardian complet !  
La documentation interactive de l'API FastAPI est accessible sur **`http://localhost:8000/docs`**.

#### Option B : Développement avec rechargement à chaud (Hot Reload)
```bash
# Terminal 1 - Backend FastAPI
cd backend
.venv\Scripts\activate
python run_backend.py

# Terminal 2 - Frontend Vite
cd frontend
npm run dev
```
Ouvrez **`http://localhost:5173`**.

---

## 💻 Utilisation de la Ligne de Commande (CLI)

CodeGuardian fournit une CLI intuitive pour analyser vos projets en local ou dans vos scripts d'automatisation :

```bash
# Lancer un scan sur le projet d'exemple avec arrêt automatique si des bugs critiques existent
python backend/app/cli.py scan sample_project --fail-on-critical --output rapport.md

# Analyser le projet courant
python backend/app/cli.py scan . --name "Scan Local"
```

### Options de la commande `scan` :
- `TARGET_PATH` : Répertoire cible à analyser (défaut : `.`).
- `--name` : Nom du projet associé dans la base de données.
- `--fail-on-critical` : Retourne le code d'erreur `1` si des bugs critiques sont détectés (idéal pour bloquer une PR en CI/CD).
- `--output [fichier]` : Sauvegarde le rapport au format `.md` ou `.json`.
- `--ai-fixes / --no-ai-fixes` : Active ou désactive la génération automatique de correctifs par IA.

---

## 🧪 Lancement des Tests Automatisés

Une suite complète de 10 tests unitaires et fonctionnels valide le bon fonctionnement de tous les modules :

```bash
cd backend
.venv\Scripts\activate
pytest tests -v
```

---

## 🛡️ Intégration CI/CD

### GitHub Actions
Le fichier `.github/workflows/codeguardian-ci.yml` s'exécute automatiquement sur chaque `push` et `pull_request` :
1. Exécute les tests unitaires via `pytest`.
2. Lance `CodeGuardian CLI` sur l'ensemble du dépôt avec `--fail-on-critical`.
3. Publie le rapport d'analyse en tant qu'artefact téléchargeable.

### Hook Git Pre-commit
Pour interdire les commits contenant des failles de sécurité ou des secrets en dur :
```bash
pip install pre-commit
pre-commit install
```

---

## 📁 Projet Démo Fourni (`sample_project/`)
Le dossier `sample_project/` contient des fichiers réalistes conçus pour valider toutes les capacités de CodeGuardian :
- `bad_auth.py` : Clé d'API GitHub en clair, clause `except:` vide, argument par défaut mutable `roles=[]`, injection SQL f-string.
- `complex_calculator.py` : Complexité cyclomatique extrême (CC = 37, Cognitive = 98) et plus de 5 paramètres.
- `payment_processor.py` et `refund_processor.py` : Bloc de code dupliqué pour tester le détecteur de clones.
- `frontend_helper.js` : Token hardcodé, comparaison souple `==`, utilisation de `eval()` non sécurisée.
