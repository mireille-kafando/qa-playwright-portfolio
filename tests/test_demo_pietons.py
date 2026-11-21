"""Démo de détection de piétons exécutée dans le navigateur (cas TC-D01 à TC-D08)."""
import re

import pytest
from playwright.sync_api import Page, expect

from conftest import attendre_nouvelle_analyse, compteurs

pytestmark = pytest.mark.demo


def test_tc_d01_analyse_automatique_de_l_exemple(demo: Page):
    expect(demo.locator("#version")).to_have_value("v2")
    pietons, cyclistes = compteurs(demo)
    assert pietons >= 3, "la v2 détecte au moins 3 des 4 personnes de l'image d'exemple"
    assert cyclistes == 0
    expect(demo.locator("#timing")).to_have_text(re.compile(r"\d+ ms"))


def test_tc_d02_le_seuil_filtre_les_detections(demo: Page):
    totaux = []
    for seuil in ["0.25", "0.5", "0.7", "0.9"]:
        demo.locator("#conf").fill(seuil)
        expect(demo.locator("#confVal")).to_have_text(f"{float(seuil):.2f}".replace(".", ","))
        totaux.append(sum(compteurs(demo)))
    assert totaux == sorted(totaux, reverse=True), f"le nombre de détections doit décroître avec le seuil : {totaux}"
    assert totaux[-1] < totaux[0]


def test_tc_d03_comparaison_avec_la_v1(demo: Page):
    libelle = demo.locator("#canvas").get_attribute("aria-label")
    demo.locator("#version").select_option("v1")
    attendre_nouvelle_analyse(demo, libelle)
    expect(demo.locator("#canvas")).to_have_attribute("aria-label", re.compile("modèle v1"))
    demo.locator("#version").select_option("v2")
    expect(demo.locator("#canvas")).to_have_attribute("aria-label", re.compile("modèle v2"), timeout=90_000)


def test_tc_d04_envoi_d_une_image(demo: Page, image_exemple):
    # On efface la description du résultat précédent : elle ne réapparaît qu'après l'analyse de l'image envoyée.
    demo.locator("#canvas").evaluate("c => c.setAttribute('aria-label', '')")
    demo.locator("#file").set_input_files(image_exemple)
    attendre_nouvelle_analyse(demo, "")
    expect(demo.locator("#canvas")).to_have_attribute("aria-label", re.compile(r"\d+ piéton"))
    assert compteurs(demo)[0] >= 3


def test_tc_d05_fichier_qui_n_est_pas_une_image(demo: Page, tmp_path):
    """Défaut DEF-005 : un fichier non image était ignoré sans message."""
    texte = tmp_path / "notes.txt"
    texte.write_text("pas une image")
    demo.locator("#file").set_input_files(texte)
    expect(demo.locator("#status")).to_be_visible()
    expect(demo.locator("#status")).to_contain_text("n'est pas une image")


def test_tc_d06_image_illisible(demo: Page, tmp_path):
    corrompue = tmp_path / "corrompue.jpg"
    corrompue.write_bytes(b"\xff\xd8\xff\x00ceci n'est pas un JPEG")
    demo.locator("#file").set_input_files(corrompue)
    expect(demo.locator("#status")).to_contain_text("Impossible de lire")


def test_tc_d07_bascule_de_langue(demo: Page):
    demo.get_by_role("button", name="English").click()
    expect(demo.locator("html")).to_have_attribute("lang", "en")
    expect(demo.locator("#confVal")).to_have_text("0.25")
    expect(demo.get_by_role("heading", level=1, name="Pedestrian detection for driver assistance")).to_be_visible()
    demo.get_by_role("button", name="Français").click()
    expect(demo.locator("#confVal")).to_have_text("0,25")


def test_tc_d08_aucune_erreur_console(page: Page, base_url: str, erreurs_console):
    page.goto(base_url + "/demo-pietons/")
    expect(page.locator("#nPed")).not_to_have_text("–", timeout=90_000)
    assert erreurs_console == []


def test_tc_d09_description_des_donnees_exacte(page: Page, base_url: str):
    """Défaut DEF-003 : la démo affirmait un entraînement sur Cityscapes."""
    page.goto(base_url + "/demo-pietons/")
    expect(page.locator("main")).to_contain_text("75 images de rue annotées à la main")
    description = page.locator("meta[property='og:description']").get_attribute("content")
    assert "Cityscapes" not in description and "Cityscapes" not in page.locator("main").inner_text()
