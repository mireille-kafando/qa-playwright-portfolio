"""Tests d'API : l'API REST de GitHub confirme ce que le portfolio affiche (cas TC-API01 à TC-API07).

Le portfolio renvoie vers des dépôts GitHub. Ces tests vérifient, sans navigateur, que chaque dépôt
existe, est public et présentable (description, licence, sujets), que la réponse de l'API respecte le
contrat attendu (schéma JSON), et que l'historique de chaque dépôt n'a qu'une auteure.
Ils utilisent l'APIRequestContext de Playwright : le même outil que pour les tests de bout en bout.
"""
import re

import pytest
from jsonschema import validate

from conftest import PROPRIETAIRE, verifier

pytestmark = pytest.mark.api

# Dépôts présentés sur le portfolio. TC-API01 vérifie que cette liste et les liens de la page concordent.
PROJETS = ["software-defect-prediction-promise", "pedestrian-detection-adas", "qa-playwright-portfolio",
           "accidents-routiers-quebec", "coin-classification-cnn", "csharp-immutability-experiment-statistics"]

# Contrat : les champs de la réponse sur lesquels les tests s'appuient, avec leur type.
SCHEMA_DEPOT = {
    "type": "object",
    "required": ["name", "full_name", "private", "archived", "html_url", "description", "license",
                 "topics", "default_branch", "pushed_at"],
    "properties": {
        "name": {"type": "string"},
        "full_name": {"type": "string", "pattern": f"^{PROPRIETAIRE}/"},
        "private": {"type": "boolean"},
        "archived": {"type": "boolean"},
        "html_url": {"type": "string", "pattern": "^https://github\\.com/"},
        "description": {"type": ["string", "null"]},
        "license": {"type": ["object", "null"], "properties": {"spdx_id": {"type": "string"}}},
        "topics": {"type": "array", "items": {"type": "string"}},
        "default_branch": {"type": "string"},
        "pushed_at": {"type": "string", "format": "date-time"},
    },
}


def test_tc_api01_le_portfolio_et_la_liste_des_projets_concordent(http_site):
    page = http_site.get("/")
    assert page.ok, page.status
    lies = set(re.findall(rf"https://github\.com/{PROPRIETAIRE}/([A-Za-z0-9._-]+)", page.text()))
    assert lies == set(PROJETS), f"liens de la page : {sorted(lies)}"


@pytest.mark.parametrize("nom", PROJETS)
def test_tc_api02_depot_public_et_actif(depots, nom):
    depot = verifier(depots(nom))
    assert depot["private"] is False and depot["archived"] is False
    assert depot["default_branch"] == "main"


@pytest.mark.parametrize("nom", PROJETS)
def test_tc_api03_reponse_conforme_au_schema(depots, nom):
    validate(instance=verifier(depots(nom)), schema=SCHEMA_DEPOT)


@pytest.mark.parametrize("nom", PROJETS)
def test_tc_api04_depot_presentable(depots, nom):
    """Ce qu'un recruteur voit en premier : une description, une licence, au moins 3 sujets (DEF-011)."""
    depot = verifier(depots(nom))
    assert (depot["description"] or "").strip(), "description vide"
    assert depot["license"] and depot["license"]["spdx_id"] not in ("", "NOASSERTION"), "pas de licence"
    assert len(depot["topics"]) >= 3, f"sujets : {depot['topics']}"


def test_tc_api05_depot_inexistant(api_github):
    reponse = api_github.get(f"/repos/{PROPRIETAIRE}/ce-depot-n-existe-pas")
    if reponse.status == 403 and reponse.headers.get("x-ratelimit-remaining") == "0":
        verifier(reponse)
    assert reponse.status == 404
    assert reponse.headers["content-type"].startswith("application/json")
    assert reponse.json()["message"] == "Not Found"


@pytest.mark.parametrize("nom", PROJETS)
def test_tc_api06_une_seule_auteure(api_github, nom):
    """Les 30 derniers commits sont de Mireille Kafando, sans co-auteur déclaré."""
    for c in verifier(api_github.get(f"/repos/{PROPRIETAIRE}/{nom}/commits", params={"per_page": 30})):
        resume = f"{c['sha'][:7]} {c['commit']['message'].splitlines()[0][:60]}"
        assert (c["author"] or {}).get("login") == PROPRIETAIRE, resume
        assert "co-authored-by" not in c["commit"]["message"].lower(), resume


def test_tc_api07_pagination_et_en_tetes(api_github):
    """per_page est respecté, l'en-tête Link donne la page suivante, la limite de débit est annoncée."""
    reponse = api_github.get(f"/repos/{PROPRIETAIRE}/mireille-kafando.github.io/commits", params={"per_page": 2})
    assert len(verifier(reponse)) == 2
    assert 'rel="next"' in reponse.headers.get("link", "")
    assert reponse.headers["x-github-api-version-selected"] == "2022-11-28"
    restant, limite = int(reponse.headers["x-ratelimit-remaining"]), int(reponse.headers["x-ratelimit-limit"])
    assert 0 <= restant <= limite
