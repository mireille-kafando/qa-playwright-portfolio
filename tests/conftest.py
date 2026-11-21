"""Fixtures communes : collecte des erreurs de la console, pages de démo prêtes, données de test."""
import json
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
