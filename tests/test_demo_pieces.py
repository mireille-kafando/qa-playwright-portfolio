"""Démo de reconnaissance de pièces exécutée dans le navigateur (cas TC-C01 à TC-C09).

L'image de test est synthétique (un disque gris dessiné, pas une vraie pièce) : les photos du jeu ICDD
ne sont pas redistribuées. Elle sert d'« oracle » : ses probabilités ont été calculées en Python avec le
même modèle ONNX, et le navigateur doit retrouver les mêmes valeurs.
"""
import re

import pytest
from playwright.sync_api import Page, expect

from conftest import analyser

pytestmark = pytest.mark.pieces

CLASSES = ["rupee_1", "rupee_2", "rupee_5", "rupee_10"]


def test_tc_c01_chargement_du_modele(demo_pieces: Page, erreurs_console):
    expect(demo_pieces.locator("#status")).to_contain_text("Choisissez une photo")
    expect(demo_pieces.get_by_role("list", name="Probabilités par classe").get_by_role("listitem")).to_have_count(4)
    assert erreurs_console == []


def test_tc_c02_memes_probabilites_qu_en_python(demo_pieces: Page, reference_pieces):
    """Le prétraitement (taille, ordre des canaux, division par 255, format NHWC) est le même qu'en Python."""
    image, attendu = reference_pieces
    obtenu = analyser(demo_pieces, image)
    for classe in CLASSES:
        assert obtenu[classe] == pytest.approx(attendu[classe], abs=1e-3), classe


def test_tc_c03_probabilites_coherentes(demo_pieces: Page, reference_pieces):
    probs = analyser(demo_pieces, reference_pieces[0])
    assert sorted(probs) == sorted(CLASSES)
    assert sum(probs.values()) == pytest.approx(1, abs=1e-4)
    assert all(0 <= p <= 1 for p in probs.values())
    # La ligne mise en avant et le verdict désignent la classe la plus probable
    meilleure = max(probs, key=probs.get)
    expect(demo_pieces.locator("#rows li.top")).to_have_attribute("data-classe", meilleure)
    nom = demo_pieces.locator("#rows li.top span").first.inner_text()
    expect(demo_pieces.locator("#verdict")).to_contain_text(nom)


def test_tc_c04_barres_proportionnelles(demo_pieces: Page, reference_pieces):
    """Défaut DEF-008 : les barres restaient vides."""
    probs = analyser(demo_pieces, reference_pieces[0])
    for classe in CLASSES:
        ligne = demo_pieces.locator(f"#rows li[data-classe='{classe}']")
        piste = ligne.locator(".track").bounding_box()["width"]
        barre = ligne.locator(".fill").bounding_box()["width"]
        assert barre / piste == pytest.approx(probs[classe], abs=0.02), classe


def test_tc_c05_pourcentages_sur_une_ligne(demo_pieces: Page, reference_pieces):
    """Défaut DEF-009 : « 98,5 % » passait sur deux lignes."""
    analyser(demo_pieces, reference_pieces[0])
    nom = demo_pieces.locator("#rows li span").first.bounding_box()["height"]
    for pct in demo_pieces.locator("#rows .pct").all():
        expect(pct).to_have_text(re.compile(r"^\d{1,3},\d %$"))
        assert pct.bounding_box()["height"] <= nom * 1.2


def test_tc_c06_fichier_qui_n_est_pas_une_image(demo_pieces: Page, tmp_path):
    texte = tmp_path / "notes.txt"
    texte.write_text("pas une image")
    demo_pieces.locator("#file").set_input_files(texte)
    expect(demo_pieces.locator("#status")).to_contain_text("n'est pas une image")
    expect(demo_pieces.locator("#verdict")).to_have_text("–")


def test_tc_c07_image_illisible(demo_pieces: Page, tmp_path):
    corrompue = tmp_path / "corrompue.jpg"
    corrompue.write_bytes(b"\xff\xd8\xff\x00ceci n'est pas un JPEG")
    demo_pieces.locator("#file").set_input_files(corrompue)
    expect(demo_pieces.locator("#status")).to_contain_text("Impossible de lire")


def test_tc_c08_bascule_en_anglais(demo_pieces: Page, reference_pieces):
    analyser(demo_pieces, reference_pieces[0])
    demo_pieces.get_by_role("button", name="English").click()
    expect(demo_pieces.locator("html")).to_have_attribute("lang", "en")
    expect(demo_pieces.get_by_role("list", name="Probability per class")).to_contain_text("2 rupees")
    expect(demo_pieces.locator("#verdict")).to_have_text(re.compile(r"\(\d{1,3}\.\d %\)$"))


def test_tc_c09_resultat_decrit_en_texte(demo_pieces: Page, reference_pieces):
    """L'image analysée a un texte alternatif qui donne le résultat ; le verdict est annoncé (aria-live)."""
    analyser(demo_pieces, reference_pieces[0])
    expect(demo_pieces.get_by_role("img", name=re.compile("Photo analysée, reconnue comme"))).to_be_visible()
    expect(demo_pieces.locator("#verdict")).to_have_attribute("aria-live", "polite")
