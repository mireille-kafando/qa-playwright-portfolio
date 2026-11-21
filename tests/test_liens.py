"""Liens externes du portfolio et de la démo (cas TC-L01). Dépend du réseau : marqueur « liens »."""
import pytest
from playwright.sync_api import Page

pytestmark = pytest.mark.liens

# Codes acceptés en plus des 2xx/3xx : LinkedIn répond 999 aux robots ; 429 = limitation de débit.
TOLERES = {999, 429}


def liens_externes(page: Page, url: str):
    page.goto(url)
    return page.locator("a[href^='http']").evaluate_all("els => [...new Set(els.map(e => e.href))]")


@pytest.mark.parametrize("chemin", ["/", "/demo-pietons/"])
def test_tc_l01_liens_externes_valides(page: Page, base_url: str, chemin):
    morts = []
    for lien in liens_externes(page, base_url + chemin):
        reponse = page.request.get(lien, max_redirects=5, fail_on_status_code=False, timeout=20_000)
        if reponse.status >= 400 and reponse.status not in TOLERES:
            morts.append((lien, reponse.status))
    assert morts == []
