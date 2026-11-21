"""Fixtures communes : collecte des erreurs de la console, pages de démo prêtes, données de test."""
import json
import os
from pathlib import Path

import pytest
from playwright.sync_api import Page, expect

DEMO = "/demo-pietons/"


@pytest.fixture
def erreurs_console(page: Page):
    """Liste des erreurs JavaScript et des messages d'erreur de la console pendant le test."""
    erreurs = []
    page.on("console", lambda m: erreurs.append(m.text) if m.type == "error" else None)
    page.on("pageerror", lambda e: erreurs.append(str(e)))
    return erreurs


@pytest.fixture
def demo(page: Page, base_url: str):
    """Ouvre la démo et attend la fin de la première analyse (image d'exemple, modèle v2)."""
    page.goto(base_url + DEMO)
    # Le compteur affiche « – » tant qu'aucune image n'a été analysée ; le modèle (13 Mo) peut être long à charger.
    expect(page.locator("#nPed")).not_to_have_text("–", timeout=90_000)
    return page


@pytest.fixture
def image_exemple(page: Page, base_url: str, tmp_path):
    """Copie locale de l'image d'exemple de la démo, pour les tests d'envoi de fichier."""
    reponse = page.request.get(base_url + DEMO + "exemples/bus.jpg")
    assert reponse.ok, reponse.status
    chemin = tmp_path / "bus.jpg"
    chemin.write_bytes(reponse.body())
    return chemin


def attendre_nouvelle_analyse(page: Page, ancien_libelle: str):
    """Attend que la description textuelle du résultat change, signe qu'une nouvelle analyse est affichée."""
    page.wait_for_function(
        "ancien => document.getElementById('canvas').getAttribute('aria-label') !== ancien",
        arg=ancien_libelle, timeout=90_000,
    )


def compteurs(page: Page):
    return int(page.locator("#nPed").inner_text()), int(page.locator("#nRider").inner_text())


# --- Démo de reconnaissance de pièces (TC-C) ---
DEMO_PIECES = "/demo-pieces/"
DONNEES = Path(__file__).parent / "donnees"


@pytest.fixture
def demo_pieces(page: Page, base_url: str):
    """Ouvre la démo des pièces et attend que le modèle (15 Mo) soit chargé."""
    page.goto(base_url + DEMO_PIECES)
    expect(page.get_by_role("button", name="Choisir une photo de pièce")).to_be_enabled(timeout=90_000)
    return page


def analyser(page: Page, chemin):
    """Envoie une image et attend les nouvelles probabilités."""
    page.evaluate("window.__probabilites = undefined")
    page.locator("#file").set_input_files(chemin)
    page.wait_for_function("window.__probabilites !== undefined", timeout=60_000)
    return page.evaluate("window.__probabilites")


@pytest.fixture
def reference_pieces():
    """Image synthétique et probabilités calculées en Python (onnxruntime) avec le même modèle."""
    ref = json.loads((DONNEES / "reference_piece_synthetique.json").read_text())
    return DONNEES / ref["image"], ref["probabilites"]


# --- Tests d'API et HTTP (TC-API, TC-H) : pas de navigateur, seulement des requêtes ---
PROPRIETAIRE = "mireille-kafando"


@pytest.fixture(scope="session")
def api_github(playwright):
    """Client de l'API REST de GitHub (APIRequestContext de Playwright).

    Sans jeton, GitHub limite à 60 requêtes par heure ; dans la CI, le jeton GITHUB_TOKEN du workflow
    relève cette limite. Le jeton n'apparaît jamais dans les rapports.
    """
    entetes = {"Accept": "application/vnd.github+json", "X-GitHub-Api-Version": "2022-11-28"}
    if os.environ.get("GITHUB_TOKEN"):
        entetes["Authorization"] = f"Bearer {os.environ['GITHUB_TOKEN']}"
    contexte = playwright.request.new_context(base_url="https://api.github.com", extra_http_headers=entetes)
    yield contexte
    contexte.dispose()


@pytest.fixture(scope="session")
def http_site(playwright, base_url):
    """Client HTTP du site en ligne, sans navigateur."""
    contexte = playwright.request.new_context(base_url=base_url)
    yield contexte
    contexte.dispose()


def verifier(reponse):
    """Échoue avec un message clair si l'API refuse la requête, au lieu d'une erreur obscure plus loin."""
    if reponse.status == 403 and reponse.headers.get("x-ratelimit-remaining") == "0":
        pytest.fail("Limite de débit de l'API GitHub atteinte : définir GITHUB_TOKEN (60 requêtes par heure sans jeton)")
    assert reponse.ok, f"{reponse.url} : HTTP {reponse.status}"
    return reponse.json()


@pytest.fixture(scope="session")
def depots(api_github):
    """Réponses de l'API pour chaque dépôt, mises en cache le temps de la session (moins de requêtes)."""
    cache = {}

    def lire(nom):
        if nom not in cache:
            cache[nom] = api_github.get(f"/repos/{PROPRIETAIRE}/{nom}")
        return cache[nom]
    return lire


@pytest.fixture(autouse=True)
def api_sur_chromium_seulement(request):
    """Les tests d'API et HTTP ne dépendent pas du navigateur : une seule exécution, dans la tâche Chromium."""
    navigateurs = request.config.getoption("--browser") or ["chromium"]
    if request.node.get_closest_marker("api") and "chromium" not in navigateurs:
        pytest.skip("test sans navigateur : exécuté dans la tâche Chromium")
