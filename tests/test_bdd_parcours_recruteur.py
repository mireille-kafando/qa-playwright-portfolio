"""Scénarios Gherkin (BDD) du parcours d'un recruteur : tests/features/parcours_recruteur.feature."""
import pytest
from playwright.sync_api import Page, expect
from pytest_bdd import given, parsers, scenarios, then, when

from conftest import DEMO_PIECES

pytestmark = [pytest.mark.bdd, pytest.mark.portfolio]

scenarios("features/parcours_recruteur.feature")


@given("je suis sur la page d'accueil du portfolio", target_fixture="accueil")
def page_accueil(page: Page, base_url: str):
    page.goto(base_url + "/")
    expect(page.locator("html")).to_have_attribute("lang", "fr")
    return page


@when(parsers.parse("j'ouvre la démo de la carte « {projet} »"))
def ouvrir_demo(accueil: Page, projet):
    accueil.locator("article", has_text=projet).get_by_role("link", name="Essayer la démo en ligne").click()


@then("la démo des pièces s'affiche")
def demo_affichee(accueil: Page, base_url: str):
    expect(accueil).to_have_url(base_url + DEMO_PIECES)
    expect(accueil.get_by_role("heading", level=1)).to_contain_text("pièces")


@then("elle est prête à analyser une photo")
def demo_prete(accueil: Page):
    expect(accueil.get_by_role("button", name="Choisir une photo de pièce")).to_be_enabled(timeout=90_000)


@then(parsers.parse("une carte présente le projet « {projet} »"), target_fixture="carte")
def carte_du_projet(accueil: Page, projet):
    carte = accueil.locator("article", has=accueil.get_by_role("heading", name=projet))
    expect(carte).to_be_visible()
    return carte


@then(parsers.parse("cette carte mène au dépôt « {depot} »"))
def lien_vers_le_depot(carte, depot):
    expect(carte.get_by_role("link", name="Voir le dépôt")).to_have_attribute(
        "href", f"https://github.com/mireille-kafando/{depot}")


@when(parsers.parse("je choisis la langue « {bouton} »"))
def choisir_langue(accueil: Page, bouton):
    accueil.get_by_role("button", name=bouton).click()


@then(parsers.parse("la page est en {code}"))
def langue_de_la_page(accueil: Page, code):
    expect(accueil.locator("html")).to_have_attribute("lang", code)


@then(parsers.parse("la section des projets s'intitule « {titre} »"))
def titre_des_projets(accueil: Page, titre):
    # Le titre visible : la version de l'autre langue est masquée (display:none), donc absente de l'arbre d'accessibilité
    expect(accueil.locator("#projets").get_by_role("heading", level=2)).to_have_accessible_name(titre)
