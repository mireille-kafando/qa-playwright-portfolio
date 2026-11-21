"""Scénarios Gherkin (BDD) de la démo des pièces : tests/features/demo_pieces.feature.

Les scénarios sont écrits en français, dans un langage qu'une personne non technique peut relire ;
chaque phrase est reliée ici à une étape Python. Les vérifications réutilisent les mêmes
localisateurs et la même image de référence que les tests TC-C.
"""
import pytest
from playwright.sync_api import Page, expect
from pytest_bdd import given, parsers, scenarios, then, when

from conftest import DEMO_PIECES, analyser

pytestmark = [pytest.mark.bdd, pytest.mark.pieces]

scenarios("features/demo_pieces.feature")

FICHIERS = {
    "un fichier texte": ("notes.txt", b"pas une image"),
    "un JPEG corrompu": ("corrompue.jpg", b"\xff\xd8\xff\x00ceci n'est pas un JPEG"),
}


@given("la démo des pièces est ouverte et que le modèle est chargé", target_fixture="demo")
def demo_ouverte(page: Page, base_url: str):
    page.goto(base_url + DEMO_PIECES)
    expect(page.get_by_role("button", name="Choisir une photo de pièce")).to_be_enabled(timeout=90_000)
    return page


@when("j'envoie l'image de référence", target_fixture="probabilites")
def envoyer_reference(demo: Page, reference_pieces):
    return analyser(demo, reference_pieces[0])


@when(parsers.re("j'envoie (?P<fichier>un fichier texte|un JPEG corrompu)"))
def envoyer_fichier(demo: Page, tmp_path, fichier):
    nom, contenu = FICHIERS[fichier]
    chemin = tmp_path / nom
    chemin.write_bytes(contenu)
    demo.locator("#file").set_input_files(chemin)


@then("4 probabilités s'affichent, dont la somme vaut 100 %")
def quatre_probabilites(demo: Page, probabilites):
    expect(demo.get_by_role("list", name="Probabilités par classe").get_by_role("listitem")).to_have_count(4)
    assert len(probabilites) == 4
    assert sum(probabilites.values()) == pytest.approx(1, abs=1e-4)


@then("le verdict nomme la classe la plus probable")
def verdict(demo: Page, probabilites):
    meilleure = max(probabilites, key=probabilites.get)
    expect(demo.locator("#rows li.top")).to_have_attribute("data-classe", meilleure)
    expect(demo.locator("#verdict")).to_contain_text(demo.locator("#rows li.top span").first.inner_text())


@then("l'image analysée est décrite pour les lecteurs d'écran")
def description_textuelle(demo: Page):
    expect(demo.locator("img[alt^='Photo analysée, reconnue comme']")).to_be_visible()


@then(parsers.parse("le message « {message} » s'affiche"))
def message_affiche(demo: Page, message):
    expect(demo.locator("#status")).to_contain_text(message)


@then("aucun verdict n'est donné")
def aucun_verdict(demo: Page):
    expect(demo.locator("#verdict")).to_have_text("–")
