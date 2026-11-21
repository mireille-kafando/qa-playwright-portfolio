# Tests de bout en bout du portfolio et de ses démos d'apprentissage automatique

[![Tests de bout en bout](https://github.com/mireille-kafando/qa-playwright-portfolio/actions/workflows/tests-e2e.yml/badge.svg)](https://github.com/mireille-kafando/qa-playwright-portfolio/actions/workflows/tests-e2e.yml)

[English summary below](#english-summary)

Projet d'assurance qualité sur un système réel : mon [portfolio](https://mireille-kafando.github.io) et ses deux démos où un modèle s'exécute dans le navigateur, la [détection de piétons](https://mireille-kafando.github.io/demo-pietons/) (YOLOv8) et la [reconnaissance de pièces de monnaie](https://mireille-kafando.github.io/demo-pieces/) (VGG16). Le projet comprend un plan de test, une suite de tests automatisés avec **Playwright** et **pytest** (bout en bout, API et HTTP, scénarios **BDD** en Gherkin), une intégration continue qui teste aussi le site en production chaque jour, et des rapports de défauts suivis jusqu'à leur correction.

## En bref

| | |
|---|---|
| Plan de test | [`docs/plan_de_test.md`](docs/plan_de_test.md) : objectifs, périmètre, approche, 49 cas de test et 5 scénarios BDD, critères de sortie, risques |
| Tests automatisés | 54 tests (147 exécutions sur Chromium et Firefox) : parcours utilisateur, cas d'erreur, cohérence du modèle avec une référence Python, accessibilité, liens, API REST de GitHub, HTTP du site, scénarios BDD |
| Défauts | [`docs/defauts/`](docs/defauts/) : 13 rapports (1 bloquant, 3 majeurs, 7 mineurs, 2 cosmétiques) ; 11 corrigés et couverts par un test, 1 accepté comme limite connue, 1 ouvert |
| Exécution | [`docs/rapport_execution.md`](docs/rapport_execution.md) : toutes les exécutions réussies, et vérification que les tests de non-régression échouent sur l'ancienne version |
| Intégration continue | GitHub Actions : à chaque modification, chaque jour et à la demande ; rapports HTML, JUnit et traces publiés |

## Ce qui est testé

| Fichier | Cas | Contenu |
|---|---|---|
| [`tests/test_portfolio.py`](tests/test_portfolio.py) | TC-P01 à TC-P10 | Identité, bascule français/anglais et sa persistance, liens vers les projets et la démo, contenus clés, lien LinkedIn, erreurs JavaScript, mise en page de 375 à 1 440 pixels, aperçu de partage |
| [`tests/test_demo_pietons.py`](tests/test_demo_pietons.py) | TC-D01 à TC-D09 | Chargement du modèle et analyse automatique, effet du seuil de confiance, comparaison des modèles v1 et v2, envoi d'une image, fichier non image, image illisible, langue, erreurs JavaScript, exactitude de la description |
| [`tests/test_demo_pieces.py`](tests/test_demo_pieces.py) | TC-C01 à TC-C09 | Chargement du modèle, probabilités identiques à celles calculées en Python, cohérence de l'affichage (somme à 1, barres, pourcentages, verdict), fichier non image, image illisible, langue, description textuelle |
| [`tests/test_accessibilite.py`](tests/test_accessibilite.py) | TC-A01 à TC-A06 | Textes alternatifs, noms accessibles, hiérarchie des titres, langue du document (trois pages), description textuelle du résultat de la démo, nom accessible qui contient le texte visible (WCAG 2.5.3) |
| [`tests/test_liens.py`](tests/test_liens.py) | TC-L01 | Liens externes des trois pages |
| [`tests/test_api_github.py`](tests/test_api_github.py) | TC-API01 à TC-API07 | API REST de GitHub : les dépôts du portfolio existent et sont présentables, contrat de la réponse (schéma JSON), 404, auteure unique des commits, pagination et en-têtes |
| [`tests/test_http_site.py`](tests/test_http_site.py) | TC-H01 à TC-H05 | Site sans navigateur : statuts, type de contenu, redirection vers HTTPS, modèles servis (HEAD), cache conditionnel (ETag, 304) |
| [`tests/features/`](tests/features/) et `test_bdd_*.py` | 5 scénarios BDD | Gherkin en français : analyse d'une pièce, fichiers refusés (plan de scénario), parcours d'un recruteur, langue |

Choix de conception :
- **Sélecteurs :** les tests visent les rôles et les noms accessibles (`get_by_role`) plutôt que la structure CSS, comme le ferait un utilisateur.
- **Attentes :** elles sont explicites, jamais fixes ; le chargement du modèle (13 Mo) dispose d'un délai de 90 secondes.
- **Résultats du modèle :** ils sont vérifiés par des bornes, par exemple « au moins 3 piétons », car le redimensionnement des images varie légèrement d'un navigateur à l'autre.
- **Données de test :** elles sont produites pendant le test (fichier texte, JPEG corrompu, image d'exemple téléchargée), sauf l'image synthétique de la démo des pièces, versionnée dans `tests/donnees/`.
- **Oracle de référence :** pour la démo des pièces, les probabilités d'une image synthétique ont été calculées en Python avec le même modèle ONNX. Le navigateur doit retrouver ces valeurs à 0,001 près : ce test détecte toute erreur de prétraitement (taille, ordre des canaux, normalisation, format des données) ou d'ordre des classes.
- **Non-régression :** chaque défaut corrigé a son test, vérifié en le lançant sur la version d'avant la correction.
- **API et HTTP :** ces tests utilisent l'`APIRequestContext` de Playwright, sans navigateur. Ils sont rapides, ne tournent qu'une fois par exécution de la CI, et séparent un problème de serveur d'un problème d'affichage. Le contrat de l'API est vérifié par un schéma JSON.
- **BDD :** les scénarios sont écrits en français (`# language: fr`), dans des phrases qu'une personne non technique peut relire. Les étapes Python réutilisent les localisateurs et l'oracle des autres tests.
- **Défaut ouvert :** un test qui révèle un défaut non encore corrigé est marqué `xfail` (échec attendu) avec la référence du défaut, plutôt que supprimé ou ignoré.

## Lancer les tests

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python -m playwright install chromium firefox

pytest                                        # site en production, Chromium
pytest --browser firefox --headed             # Firefox, fenêtre visible
pytest -m "not liens"                         # sans les tests qui dépendent de sites tiers
pytest -m api                                 # tests d'API et HTTP seulement (quelques secondes)
pytest -m bdd -v                              # scénarios BDD, avec le nom de chaque scénario
GITHUB_TOKEN=… pytest -m api                  # avec un jeton : 5 000 requêtes par heure au lieu de 60
pytest --base-url http://127.0.0.1:8000       # copie locale du site (python -m http.server 8000)
pytest --html=rapport/rapport.html --self-contained-html
```

En cas d'échec, la capture d'écran et la trace Playwright sont enregistrées dans `test-results/`. La trace s'ouvre avec `playwright show-trace`.

## Organisation

```
tests/
├── conftest.py               Fixtures : erreurs de console, démos prêtes, données de test
├── donnees/                  Image synthétique et probabilités de référence (démo des pièces)
├── test_portfolio.py
├── test_demo_pietons.py
├── test_demo_pieces.py
├── test_accessibilite.py
├── test_liens.py
├── test_api_github.py        API REST de GitHub
├── test_http_site.py         HTTP du site, sans navigateur
├── features/                 Scénarios Gherkin (demo_pieces.feature, parcours_recruteur.feature)
└── test_bdd_*.py             Étapes des scénarios
docs/
├── plan_de_test.md
├── rapport_execution.md
└── defauts/                  DEF-001 à DEF-013
.github/workflows/tests-e2e.yml
pytest.ini                    Adresse du site testé, marqueurs, traces et captures en cas d'échec
```

## Compétences mises en œuvre

Planification de tests · tests de bout en bout (Playwright, pytest) · tests d'API REST et HTTP · validation de schéma JSON · BDD (Gherkin, pytest-bdd) · tests multinavigateurs · tests d'accessibilité · rapports de défauts et tests de non-régression · intégration continue (GitHub Actions) · surveillance d'un site en production

## Auteure

**Mireille Kafando** · [Portfolio](https://mireille-kafando.github.io) · [LinkedIn](https://www.linkedin.com/in/mireille-kafando-386b2a420/)

## Licence

MIT (voir [`LICENSE`](LICENSE)).

---

## English summary

A QA project on a real system: my portfolio site and its two in-browser ML demos, YOLOv8 pedestrian detection and VGG16 coin recognition.

- **Test plan** ([`docs/plan_de_test.md`](docs/plan_de_test.md)): objectives, scope, approach, 49 test cases and 5 BDD scenarios with priorities, exit criteria, risks.
- **Automated tests**:
  - 54 Playwright + pytest tests (147 runs on Chromium and Firefox);
  - coverage: user journeys, language switching, both ML demos (model loading, confidence threshold, model comparison, uploads, error cases), basic accessibility checks and external links;
  - API tests on the GitHub REST API (status, JSON-schema contract, 404, pagination, headers, single-author commit history) and HTTP tests of the site (redirects, HEAD, ETag caching), with Playwright's APIRequestContext;
  - BDD scenarios in French Gherkin (pytest-bdd), including a scenario outline;
  - test oracle: the coin demo must reproduce, within 0.001, the class probabilities computed in Python with the same ONNX model on a synthetic image;
  - selectors are role-based.
- **Defect reports** ([`docs/defauts/`](docs/defauts/)): 13 real defects (1 blocker, 3 major, 7 minor, 2 cosmetic), each with steps to reproduce and either the fix with a regression test or, for one model limitation, the decision to accept it with a warning; one is open and tracked by an expected-failure (`xfail`) test. The regression tests were confirmed to fail on the pre-fix version.
- **CI**: GitHub Actions runs the suite on every push, daily against production, and on demand, publishing HTML/JUnit reports and Playwright traces.
