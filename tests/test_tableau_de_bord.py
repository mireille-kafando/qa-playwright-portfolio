"""Tableau de bord des accidents de la route (cas TC-T01 à TC-T06).

Oracle : le fichier donnees.json publié avec la page. Les indicateurs affichés doivent être
recalculables à partir de ses lignes, quels que soient les filtres. TC-T04 vérifie en plus que le SQL
affiché sous les graphiques est celui du dépôt du projet.
"""
import re

import pytest
from playwright.sync_api import Page, expect

from conftest import PROPRIETAIRE, verifier

pytestmark = pytest.mark.tableau
TABLEAU = "/accidents-quebec/"


@pytest.fixture
def donnees(page: Page, base_url: str):
    reponse = page.request.get(base_url + TABLEAU + "donnees.json")
    assert reponse.ok, reponse.status
    return reponse.json()


@pytest.fixture
def tableau(page: Page, base_url: str, erreurs_console):
    page.goto(base_url + TABLEAU)
    expect(page.locator("#k-total")).not_to_have_text("–")
    return page


def attendu(donnees, usager, region="tout"):
    bloc = donnees["resultats"]["q02_usagers_par_annee"][usager][region]
    lignes = [dict(zip(bloc["colonnes"], l)) for l in bloc["lignes"]]
    total = sum(l["accidents"] for l in lignes)
    graves = sum(l["mortels_ou_graves"] for l in lignes)
    return total, graves, lignes


def chiffre(texte):
    """« 30 455 » (espaces fines insécables) ou « 30,455 » -> 30455."""
    return int(re.sub(r"[^\d]", "", texte))


def test_tc_t01_chargement_sans_erreur(tableau, erreurs_console):
    expect(tableau.get_by_role("heading", level=1)).to_contain_text("Accidents de la route")
    expect(tableau.locator("#g-annees svg circle")).to_have_count(12)          # 2011 à 2022
    assert erreurs_console == []


def test_tc_t02_indicateurs_recalcules_depuis_les_donnees(tableau, donnees):
    total, graves, lignes = attendu(donnees, "pieton")
    assert chiffre(tableau.locator("#k-total").inner_text()) == total
    assert chiffre(tableau.locator("#k-2022").inner_text()) == lignes[-1]["accidents"]
    pct = round(100 * graves / total, 1)
    expect(tableau.locator("#k-mg")).to_have_text(f"{pct:.1f} %".replace(".", ","))


def test_tc_t03_filtres_usager_et_region(tableau, donnees):
    tableau.get_by_role("button", name="Cyclistes").click()
    tableau.get_by_label("Région administrative").select_option(label="Mauricie")
    total, _, _ = attendu(donnees, "velo", "4")
    expect(tableau.get_by_role("button", name="Cyclistes")).to_have_attribute("aria-pressed", "true")
    expect(tableau.locator("#k-total")).to_have_text(re.compile(r"\D*".join(str(total))))
    # la région choisie est mise en avant dans le graphique des régions
    expect(tableau.locator('#g-regions [data-item="4"] rect')).to_have_attribute("fill", "var(--accent)")


def test_tc_t04_sql_affiche_identique_au_depot(tableau, api_github):
    tableau.locator("#p-vitesse summary").click()
    affiche = tableau.locator("#sql-vitesse").inner_text()
    reponse = api_github.get(f"/repos/{PROPRIETAIRE}/accidents-routiers-quebec/contents/sql/requetes/q03_gravite_selon_vitesse.sql",
                             headers={"Accept": "application/vnd.github.raw"})
    if reponse.status == 403:
        verifier(reponse)
    assert reponse.ok, reponse.status
    assert affiche.strip() == reponse.text().strip()


def test_tc_t05_petits_effectifs_signales(tableau, donnees):
    """Une barre calculée sur moins de 30 accidents est pâle : son pourcentage est peu fiable."""
    tableau.get_by_role("button", name="Cyclistes").click()
    tableau.get_by_label("Région administrative").select_option(label="Mauricie")
    bloc = donnees["resultats"]["q03_gravite_selon_vitesse"]["velo"]["4"]
    for vitesse, n in ((l[0], l[1]) for l in bloc["lignes"]):
        barre = tableau.locator(f'#g-vitesse [data-item="{vitesse}"] rect')
        if n < 30:
            expect(barre).to_have_attribute("fill", "var(--bar-faible)")
        else:
            expect(barre).not_to_have_attribute("fill", "var(--bar-faible)")


def test_tc_t06_anglais_et_format_des_nombres(tableau, donnees):
    total, _, _ = attendu(donnees, "pieton")
    tableau.get_by_role("button", name="English").click()
    expect(tableau.locator("html")).to_have_attribute("lang", "en")
    expect(tableau.get_by_role("heading", level=1)).to_contain_text("Road accidents")
    expect(tableau.locator("#k-total")).to_have_text(f"{total:,}")
