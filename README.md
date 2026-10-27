# CodeGuardian — Détection Intelligente des Bugs & Qualité Logicielle

[![CodeGuardian Status](http://localhost:8000/api/reports/badge.svg)](http://localhost:8000)

**CodeGuardian** est une plateforme professionnelle d'analyse statique de code, de sécurité applicative (DevSecOps), d'audit des dépendances (SCA) et de prédiction de défauts logiciels assistée par intelligence artificielle.

Conçu pour s'intégrer harmonieusement dans les pipelines CI/CD modernes, CodeGuardian associe l'analyse syntaxique AST, la détection de clones par hachage algorithmique, l'analyse de l'historique Git (churn/complexité), la génération de correctifs avec diffs interactifs, et l'application automatique de correctifs en un clic avec sauvegarde de sécurité.

---

## Architecture et Fonctionnalités Clés

### 1. Analyse Statique & Détection des Vulnérabilités (AST Multi-langages)
- **Analyse AST Python & JavaScript/TypeScript** :
  - Détection des clauses `except:` nues capturant aveuglément les exceptions.
  - Détection des arguments par défaut mutables (`def fn(items=[])`).
  - Comparaisons non sécurisées (`== None` au lieu de `is None`, `==` au lieu de `===` en JS).
  - Détection des méthodes volumineuses ("God methods") et fonctions à forte arité.
- **Sécurité Applicative (SAST & Secrets Detection)** :
  - Détection immédiate des secrets et clés d'API codés en dur (GitHub PAT, AWS keys, JWT, mots de passe) avec masquage automatique.
  - Détection des injections SQL dynamiques (f-strings et concaténations dans les requêtes SQL).
  - Identification des fonctions d'exécution arbitraire dangereuses (`eval()`, `exec()`, `os.system()`).

### 2. Audit des Dépendances (Software Composition Analysis - SCA)
- **Scan des dépendances Python (`requirements.txt`) et Node.js (`package.json`)** :
  - Détection des versions vulnérables répertoriées avec identifiants CVE officiels et advisory advisory notes.
  - Interrogation en ligne de l'API PyPI Advisory / OSV avec base de données locale intégrée en cas d'environnement hors-ligne.
  - Recommandation immédiate de la version sécurisée minimale à installer.

### 3. Détection Algorithmique de Duplications
- **Algorithme Rabin-Karp à fenêtre glissante** :
  - Détection des clones de code exacts et quasi-identiques multi-fichiers.
  - Calcul du ratio de duplication global du projet et localisation exacte des fragments dupliqués.

### 4. Modèle Prédictif des Hotspots de Risque
- **Fusion Métriques Statiques & Dynamique Git** :
  - Calcul de la Complexité Cyclomatique de McCabe, Complexité Cognitive, et Index de Maintenabilité SEI.
  - Intégration de l'historique Git : volume de modifications (code churn), fréquence des commits, et récurrence des correctifs de bugs récents.
  - Attribution d'un score de risque unifié (0 à 100%) et classification par sévérité (`CRITICAL`, `HIGH`, `MEDIUM`, `LOW`).

### 5. Remédiation IA & Application de Correctifs en 1 Clic (Auto-Patch)
- **Moteur IA Hybride** : Support natif des modèles LLM (Gemini, OpenAI, Ollama) et moteur expert sémantique offline garanti sans dépendance externe.
- **Diff Unifié Interactif** : Comparateur de code avec coloration syntaxique avant/après.
- **Auto-Patch sécurisé** : Possibilité d'appliquer le correctif généré directement dans le fichier source sur disque en un clic, avec création systématique d'une copie de sauvegarde `.bak` et mise à jour de l'état du défaut en `RESOLVED`.

### 6. Mode Diff-Only pour Pull Requests
- Analyse ciblée uniquement sur les fichiers modifiés par rapport à une branche de référence (ex. `master` ou `main`), réduisant drastiquement le temps d'exécution en CI/CD.

### 7. Rapports & Badges Dynamiques
- **Badge de statut SVG dynamique** : Accessible via `/api/reports/badge.svg`, affichant le Health Score et le niveau de sévérité, intégrable directement dans les fichiers `README.md`.
- **Rapport d'audit imprimable** : Génération d'une page HTML stylisée pour impression PDF ou archivage exécutif (`/api/reports/export/html?scan_id=...`).
- **Export CLI multi-formats** : Exportation directe en Markdown et JSON.

---

## Arborescence du Projet

```
CodeGuardian/
├── backend/
│   ├── app/
│   │   ├── core/
│   │   │   ├── static_analyzer.py      # Moteur d'analyse statique AST & patterns
│   │   │   ├── complexity_metrics.py   # Complexité cyclomatique, cognitive & Index Maintenabilité
│   │   │   ├── duplication_detector.py # Détecteur de clones par hachage Rabin-Karp
│   │   │   ├── git_analyzer.py         # Churn Git, historique des commits et diffs PR
│   │   │   ├── bug_predictor.py        # Modèle empirique de prédiction des hotspots
│   │   │   ├── sca_scanner.py          # Scanner de vulnérabilités des dépendances (SCA)
│   │   │   └── ai_engine.py            # Diagnostic IA, explications et génération de diffs
│   │   ├── routers/
│   │   │   ├── scans.py                # Endpoints de déclenchement d'analyse (full & diff-only)
│   │   │   ├── ai.py                   # Endpoints de diagnostic et d'application de correctif
│   │   │   ├── git_insights.py         # Métriques Git et points chauds
│   │   │   └── reports.py              # Export Markdown, JSON, HTML imprimable et badge SVG
│   │   ├── cli.py                      # Interface en ligne de commande pour terminaux et CI/CD
│   │   ├── models.py                   # Modèles relationnels SQLAlchemy
│   │   ├── schemas.py                  # Schémas de validation Pydantic
│   │   └── main.py                     # Application FastAPI et point d'entrée API REST
│   ├── tests/                          # 14 tests automatisés pytest
│   ├── requirements.txt                # Dépendances Python
│   └── pytest.ini                      # Configuration pytest
├── frontend/                           # Application Single Page React 18, TypeScript, Tailwind CSS
│   ├── src/
│   │   ├── components/                 # Modale IA avec Auto-Patch, Diff Viewer, Canvas télémétrique
│   │   ├── pages/                      # Dashboard, Liste des défauts, Hotspots, Duplications, Historique
│   │   └── api/                        # Client API REST typé
│   ├── dist/                           # Fichiers de production compilés servis par FastAPI
│   └── package.json
├── sample_project/                     # Projet témoin pour démonstration et tests
├── Dockerfile                          # Image conteneurisée multi-stage de production
├── docker-compose.yml                  # Déploiement Docker en un clic
├── .github/workflows/codeguardian-ci.yml # Pipeline GitHub Actions
├── .gitlab-ci.yml                      # Pipeline GitLab CI
├── .pre-commit-config.yaml             # Hook local pre-commit
└── run.py                              # Script de démarrage unifié prêt à l'emploi
```

---

## Installation et Démarrage

### Option 1 : Démarrage Unifié (Recommandé)

```bash
# 1. Cloner ou naviguer dans le dossier du projet
cd CodeGuardian

# 2. Configurer l'environnement Python
cd backend
python -m venv .venv
# Sur Windows :
.venv\Scripts\activate
# Sur Linux / macOS :
source .venv/bin/activate

pip install -r requirements.txt

# 3. Lancer l'application unifiée
python run_backend.py
# ou depuis la racine :
python run.py
```

- **Dashboard Web** : [http://localhost:8000](http://localhost:8000)
- **Documentation API Swagger** : [http://localhost:8000/docs](http://localhost:8000/docs)
- **Badge de statut SVG** : [http://localhost:8000/api/reports/badge.svg](http://localhost:8000/api/reports/badge.svg)

---

### Option 2 : Déploiement avec Docker

Le projet intègre un `Dockerfile` optimisé multi-stage compilant le frontend et exécutant le backend FastAPI sous Linux :

```bash
# Construction et lancement avec Docker Compose
docker compose up -d --build

# Consulter les logs du service
docker compose logs -f

# Arrêter le conteneur
docker compose down
```

L'application est immédiatement accessible sur [http://localhost:8000](http://localhost:8000).

---

### Option 3 : Mode Développement (Hot Reload)

```bash
# Terminal 1 - Serveur Backend FastAPI
cd backend
.venv\Scripts\activate
python run_backend.py

# Terminal 2 - Serveur Frontend Vite
cd frontend
npm install
npm run dev
```

L'application de développement est disponible sur [http://localhost:5173](http://localhost:5173) avec proxy automatique vers le backend.

---

## Utilisation de l'Interface en Ligne de Commande (CLI)

CodeGuardian fournit une CLI complète adaptée aux développeurs et aux pipelines CI/CD :

```bash
# Analyse complète d'un répertoire avec arrêt bloquant en cas de sévérité critique
python backend/app/cli.py scan sample_project --fail-on-critical --output rapport.md

# Analyse incrémentale d'une Pull Request (fichiers modifiés uniquement)
python backend/app/cli.py scan . --diff-only --name "Scan PR #42"

# Analyse du projet courant sans génération de correctifs IA
python backend/app/cli.py scan . --no-ai-fixes
```

### Paramètres de la commande `scan` :
- `TARGET_PATH` : Répertoire cible à analyser (défaut : `.`).
- `--name` : Libellé du scan dans l'historique.
- `--fail-on-critical` : Retourne un code d'erreur `1` si des défauts critiques sont détectés (bloque le pipeline CI/CD).
- `--diff-only` : Restreint l'analyse aux fichiers modifiés par rapport au dernier commit ou branche de base.
- `--output [fichier]` : Sauvegarde le rapport sous format `.md`, `.json` ou `.html`.
- `--ai-fixes / --no-ai-fixes` : Active ou désactive la génération automatique de diagnostics IA.

---

## Suite de Tests Automatisés

Le projet intègre une suite de 14 tests unitaires et fonctionnels couvrant tous les sous-systèmes :

```bash
cd backend
.venv\Scripts\activate
pytest -v
```

### Couverture des tests :
- Analyse statique AST Python (clauses except nues, variables mutables, failles de sécurité).
- Détection des injections SQL et fuites de secrets/tokens.
- Calcul de la complexité cyclomatique et cognitive.
- Algorithme de hachage de détection de duplication de code.
- Scanner de dépendances SCA (advisories pip et npm).
- Modèle prédictif des fichiers à haut risque (Hotspots).
- Endpoints REST FastAPI (santé, scans, statistiques dashboard).
- Endpoint d'application automatique de correctifs avec création de fichier `.bak`.
- Génération dynamique de badges SVG.

---

## Intégration CI/CD

### Pipeline GitHub Actions
Le workflow `.github/workflows/codeguardian-ci.yml` s'exécute à chaque événement `push` ou `pull_request` :
1. Prépare l'environnement Python et installe les dépendances.
2. Exécute l'intégralité de la suite `pytest`.
3. Lance l'analyseur CodeGuardian avec `--fail-on-critical`.
4. Archive les rapports générés en artefacts de build.

### Pipeline GitLab CI
Le fichier `.gitlab-ci.yml` configure les étages `test` et `quality-gate` avec exportation des rapports compatibles avec les onglets de sécurité GitLab.

### Hook Pre-commit
Pour interdire les commits contenant des failles critiques ou des clés d'API hardcodées :
```bash
pip install pre-commit
pre-commit install
```
