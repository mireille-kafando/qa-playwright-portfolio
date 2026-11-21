"""Page d'accueil du portfolio (cas TC-P01 à TC-P09 du plan de test)."""
import re

import pytest
from playwright.sync_api import Page, expect

pytestmark = pytest.mark.portfolio


@pytest.fixture
def accueil(page: Page, base_url: str):
    page.goto(base_url + "/")
    return page


def test_tc_p01_titre_et_identite(accueil: Page):
    expect(accueil).to_have_title(re.compile("Mireille Kafando"))
    expect(accueil.locator("h1")).to_have_count(1)
    expect(accueil.locator("h1")).to_contain_text("Mireille Kafando")


def test_tc_p02_bascule_de_langue_et_persistance(accueil: Page):
    expect(accueil.locator("html")).to_have_attribute("lang", "fr")
    accueil.get_by_role("button", name=re.compile("English|switch language")).click()
    expect(accueil.locator("html")).to_have_attribute("lang", "en")
    expect(accueil.get_by_role("heading", name="Skills")).to_be_visible()
    accueil.reload()
    expect(accueil.locator("html")).to_have_attribute("lang", "en"), "la préférence de langue doit survivre au rechargement"
    accueil.get_by_role("button", name=re.compile("Français|switch language")).click()
    expect(accueil.get_by_role("heading", name="Compétences")).to_be_visible()


def test_tc_p03_chaque_projet_mene_a_son_depot(accueil: Page):
    depots = accueil.locator("a[href^='https://github.com/mireille-kafando/']")
    cibles = {re.sub(r"/(tree|blob)/.*", "", h) for h in depots.evaluate_all("els => els.map(e => e.href)")}
    attendus = {"software-defect-prediction-promise", "pedestrian-detection-adas",
                "coin-classification-cnn", "csharp-immutability-experiment-statistics"}
    assert attendus <= {c.rstrip("/").split("/")[-1] for c in cibles}


def test_tc_p04_lien_vers_la_demo(accueil: Page, base_url: str):
    lien = accueil.get_by_role("link", name=re.compile("Essayer la démo en ligne"))
    expect(lien).to_be_visible()
    lien.click()
    expect(accueil).to_have_url(base_url + "/demo-pietons/")


def test_tc_p05_resultat_adas_a_jour(accueil: Page):
    """Le score affiché est celui de la v2 ; l'ancien 0,685 de la v1 ne doit plus apparaître."""
    carte = accueil.locator("article", has_text="ADAS")
    expect(carte).to_contain_text("0,86")
    expect(accueil.locator("body")).not_to_contain_text("0,685")


def test_tc_p06_competences_alignees_sur_les_cv(accueil: Page):
    competences = accueil.locator("#competences")
    expect(competences).to_contain_text("Java, C# (notions)")
    expect(competences).to_contain_text("Langues")


def test_tc_p07_lien_linkedin_correct(accueil: Page):
    liens = accueil.locator("a[href*='linkedin.com']").evaluate_all("els => els.map(e => e.href)")
    assert liens, "aucun lien LinkedIn"
    assert all("/in/mireille-kafando-386b2a420" in l for l in liens), liens


def test_tc_p08_aucune_erreur_console(page: Page, base_url: str, erreurs_console):
    page.goto(base_url + "/")
    page.wait_for_load_state("networkidle")
    assert erreurs_console == []


@pytest.mark.parametrize("largeur,hauteur", [(375, 812), (768, 1024), (1440, 900)])
def test_tc_p09_pas_de_defilement_horizontal(page: Page, base_url: str, largeur, hauteur):
    page.set_viewport_size({"width": largeur, "height": hauteur})
    page.goto(base_url + "/")
    assert page.evaluate("document.documentElement.scrollWidth <= window.innerWidth")


@pytest.mark.parametrize("chemin", ["/", "/demo-pietons/"])
def test_tc_p10_metadonnees_de_partage(page: Page, base_url: str, chemin):
    """Image d'aperçu pour les partages (défaut DEF-007 sur la démo)."""
    page.goto(base_url + chemin)
    image = page.locator("meta[property='og:image']")
    expect(image).to_have_count(1)
    reponse = page.request.get(image.get_attribute("content").replace("https://mireille-kafando.github.io", base_url))
    assert reponse.ok and reponse.headers["content-type"].startswith("image/")
