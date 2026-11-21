"""Vérifications d'accessibilité de base sur les pages du site (cas TC-A01 à TC-A06)."""
import pytest
from playwright.sync_api import Page, expect

pytestmark = pytest.mark.a11y
PAGES = ["/", "/demo-pietons/", "/demo-pieces/"]


@pytest.mark.parametrize("chemin", PAGES)
def test_tc_a01_images_avec_texte_alternatif(page: Page, base_url: str, chemin):
    page.goto(base_url + chemin)
    sans_alt = page.locator("img:not([alt])").evaluate_all("els => els.map(e => e.src)")
    assert sans_alt == []


@pytest.mark.parametrize("chemin", PAGES)
def test_tc_a02_champs_et_boutons_nommes(page: Page, base_url: str, chemin):
    page.goto(base_url + chemin)
    anonymes = page.evaluate("""() => [...document.querySelectorAll('input:not([type=hidden]):not([hidden]), select, textarea, button')]
        .filter(e => !(e.labels && e.labels.length) && !e.getAttribute('aria-label') && !e.innerText.trim())
        .map(e => e.outerHTML.slice(0, 80))""")
    assert anonymes == []


@pytest.mark.parametrize("chemin", PAGES)
def test_tc_a03_hierarchie_des_titres(page: Page, base_url: str, chemin):
    """Défaut DEF-006 : les titres passaient de H2 à H4 dans la section Compétences."""
    page.goto(base_url + chemin)
    niveaux = page.locator("h1, h2, h3, h4, h5, h6").evaluate_all("els => els.map(e => +e.tagName[1])")
    assert niveaux and niveaux[0] == 1
    sauts = [(a, b) for a, b in zip(niveaux, niveaux[1:]) if b > a + 1]
    assert sauts == [], f"niveau de titre sauté : {sauts}"


@pytest.mark.parametrize("chemin", PAGES)
def test_tc_a04_langue_du_document(page: Page, base_url: str, chemin):
    page.goto(base_url + chemin)
    expect(page.locator("html")).to_have_attribute("lang", "fr")


def test_tc_a05_resultat_de_la_demo_decrit_en_texte(page: Page, base_url: str):
    """Défaut DEF-004 : le résultat n'était qu'un dessin dans un canvas, sans alternative textuelle."""
    page.goto(base_url + "/demo-pietons/")
    expect(page.locator("#nPed")).not_to_have_text("–", timeout=90_000)
    canvas = page.locator("#canvas")
    expect(canvas).to_have_attribute("role", "img")
    nombre = page.locator("#nPed").inner_text()
    expect(canvas).to_have_attribute("aria-label", f"Image analysée : {nombre} piéton(s) et 0 cycliste(s) ou motard(s) détectés, modèle v2, seuil 0,25")


@pytest.mark.parametrize("chemin", PAGES)
def test_tc_a06_nom_accessible_contient_le_texte_visible(page: Page, base_url: str, chemin):
    """WCAG 2.5.3 (Label in Name) : un bouton se commande à la voix par le texte qu'on voit.

    Défaut DEF-013 : le bouton « English » s'appelait « Changer de langue / switch language ».
    """
    page.goto(base_url + chemin)
    ecarts = page.evaluate("""() => [...document.querySelectorAll('button[aria-label], a[aria-label]')]
        .filter(e => e.innerText.trim() && !e.getAttribute('aria-label').toLowerCase().includes(e.innerText.trim().toLowerCase()))
        .map(e => `${e.innerText.trim()} → ${e.getAttribute('aria-label')}`)""")
    assert ecarts == []
