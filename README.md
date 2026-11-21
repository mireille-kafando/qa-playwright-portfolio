# Tests de bout en bout du portfolio et de la démo de détection de piétons

[![Tests de bout en bout](https://github.com/mireille-kafando/qa-playwright-portfolio/actions/workflows/tests-e2e.yml/badge.svg)](https://github.com/mireille-kafando/qa-playwright-portfolio/actions/workflows/tests-e2e.yml)

[English summary below](#english-summary)

Projet d'assurance qualité sur un système réel : mon [portfolio](https://mireille-kafando.github.io) et sa [démo de détection de piétons](https://mireille-kafando.github.io/demo-pietons/), où un modèle YOLOv8 s'exécute dans le navigateur. Le projet comprend un plan de test, une suite de tests automatisés avec **Playwright** et **pytest**, une intégration continue qui teste aussi le site en production chaque jour, et des rapports de défauts suivis jusqu'à leur correction.

## En bref

| | |
|---|---|
| Plan de test | [`docs/plan_de_test.md`](docs/plan_de_test.md) : objectifs, périmètre, approche, 25 cas de test, critères de sortie, risques |
| Tests automatisés | 33 tests (66 exécutions sur Chromium et Firefox) : parcours utilisateur, cas d'erreur, accessibilité, liens |
| Défauts | [`docs/defauts/`](docs/defauts/) : 7 rapports (1 bloquant, 1 majeur, 4 mineurs, 1 cosmétique), tous corrigés et couverts par un test |
| Exécution | [`docs/rapport_execution.md`](docs/rapport_execution.md) : 62 sur 62 réussis, et vérification que les tests de non-régression échouent sur l'ancienne version |
| Intégration continue | GitHub Actions : à chaque modification, chaque jour et à la demande ; rapports HTML, JUnit et traces publiés |

## Ce qui est testé

| Fichier | Cas | Contenu |
|---|---|---|
| [`tests/test_portfolio.py`](tests/test_portfolio.py) | TC-P01 à TC-P10 | Identité, bascule français/anglais et sa persistance, liens vers les projets et la démo, contenus clés, lien LinkedIn, erreurs JavaScript, mise en page de 375 à 1 440 pixels, aperçu de partage |
| [`tests/test_demo_pietons.py`](tests/test_demo_pietons.py) | TC-D01 à TC-D09 | Chargement du modèle et analyse automatique, effet du seuil de confiance, comparaison des modèles v1 et v2, envoi d'une image, fichier non image, image illisible, langue, erreurs JavaScript, exactitude de la description |
| [`tests/test_accessibilite.py`](tests/test_accessibilite.py) | TC-A01 à TC-A05 | Textes alternatifs, noms accessibles, hiérarchie des titres, langue du document, description textuelle du résultat de la démo |
| [`tests/test_liens.py`](tests/test_liens.py) | TC-L01 | Liens externes des deux pages |

Choix de conception :
- **Sélecteurs :** les tests visent les rôles et les noms accessibles (`get_by_role`) plutôt que la structure CSS, comme le ferait un utilisateur.
- **Attentes :** elles sont explicites, jamais fixes ; le chargement du modèle (13 Mo) dispose d'un délai de 90 secondes.
- **Résultats du modèle :** ils sont vérifiés par des bornes, par exemple « au moins 3 piétons », car le redimensionnement des images varie légèrement d'un navigateur à l'autre.
- **Données de test :** elles sont produites pendant le test (fichier texte, JPEG corrompu, image d'exemple téléchargée).
- **Non-régression :** chaque défaut corrigé a son test, vérifié en le lançant sur la version d'avant la correction.

## Lancer les tests

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python -m playwright install chromium firefox

pytest                                        # site en production, Chromium
pytest --browser firefox --headed             # Firefox, fenêtre visible
pytest -m "not liens"                         # sans les tests qui dépendent de sites tiers
pytest --base-url http://127.0.0.1:8000       # copie locale du site (python -m http.server 8000)
pytest --html=rapport/rapport.html --self-contained-html
```

En cas d'échec, la capture d'écran et la trace Playwright sont enregistrées dans `test-results/`. La trace s'ouvre avec `playwright show-trace`.

## Organisation

```
tests/
├── conftest.py               Fixtures : erreurs de console, démo prête, image d'exemple
├── test_portfolio.py
├── test_demo_pietons.py
├── test_accessibilite.py
└── test_liens.py
docs/
├── plan_de_test.md
├── rapport_execution.md
└── defauts/                  DEF-001 à DEF-007
.github/workflows/tests-e2e.yml
pytest.ini                    Adresse du site testé, marqueurs, traces et captures en cas d'échec
```

## Compétences mises en œuvre

Planification de tests · tests de bout en bout (Playwright, pytest) · tests multinavigateurs · tests d'accessibilité · rapports de défauts et tests de non-régression · intégration continue (GitHub Actions) · surveillance d'un site en production

## Auteure

**Mireille Kafando** · [Portfolio](https://mireille-kafando.github.io) · [LinkedIn](https://www.linkedin.com/in/mireille-kafando-386b2a420/)

## Licence

MIT (voir [`LICENSE`](LICENSE)).

---

## English summary

A QA project on a real system: my portfolio site and its in-browser YOLOv8 pedestrian detection demo.

- **Test plan** ([`docs/plan_de_test.md`](docs/plan_de_test.md)): objectives, scope, approach, 25 test cases with priorities, exit criteria, risks.
- **Automated tests**:
  - 33 Playwright + pytest tests (66 runs on Chromium and Firefox);
  - coverage: user journeys, language switching, the ML demo (model loading, confidence threshold, model comparison, uploads, error cases), basic accessibility checks and external links;
  - selectors are role-based.
- **Defect reports** ([`docs/defauts/`](docs/defauts/)): 7 real defects (1 blocker, 1 major, 4 minor, 1 cosmetic), each with steps to reproduce, the fixing commit and a regression test. The regression tests were confirmed to fail on the pre-fix version.
- **CI**: GitHub Actions runs the suite on every push, daily against production, and on demand, publishing HTML/JUnit reports and Playwright traces.
