"""Tests HTTP du site en ligne, sans navigateur (cas TC-H01 à TC-H05).

Ils vérifient ce que le navigateur ne montre pas : codes de statut, types de contenu, redirection vers
HTTPS, taille des modèles servis et mise en cache. Ils sont rapides et isolent un problème de serveur
d'un problème d'affichage.
"""
import pytest

pytestmark = pytest.mark.api

PAGES = ["/", "/demo-pietons/", "/demo-pieces/"]
MODELES = {"/demo-pietons/model/v2.onnx": (10e6, 16e6), "/demo-pieces/model/pieces_vgg16_int8.onnx": (12e6, 18e6)}


@pytest.mark.parametrize("chemin", PAGES)
def test_tc_h01_pages_servies_en_html(http_site, chemin):
    reponse = http_site.get(chemin)
    assert reponse.status == 200, reponse.status
    assert reponse.headers["content-type"].startswith("text/html")
    assert '<html lang="fr">' in reponse.text()


def test_tc_h02_page_inexistante(http_site):
    assert http_site.get("/cette-page-n-existe-pas/").status == 404


def test_tc_h03_http_redirige_vers_https(http_site, base_url):
    reponse = http_site.get(base_url.replace("https://", "http://") + "/", max_redirects=0)
    assert reponse.status == 301
    assert reponse.headers["location"].startswith("https://")


@pytest.mark.parametrize("chemin", MODELES)
def test_tc_h04_modeles_servis(http_site, chemin):
    """Requête HEAD : on lit la taille sans télécharger le modèle.

    « Accept-Encoding: identity » demande la taille réelle du fichier : sans lui, le serveur annonce la
    taille compressée (gzip), environ 40 % plus petite pour le modèle des pièces.
    """
    reponse = http_site.head(chemin, headers={"Accept-Encoding": "identity"})
    assert reponse.status == 200, reponse.status
    assert reponse.headers["content-type"] == "application/octet-stream"
    mini, maxi = MODELES[chemin]
    assert mini <= int(reponse.headers["content-length"]) <= maxi


def test_tc_h05_cache_conditionnel(http_site):
    """Un client qui renvoie l'ETag reçu obtient 304 : le modèle n'est pas retéléchargé."""
    chemin = "/demo-pieces/model/pieces_vgg16_int8.onnx"
    etag = http_site.head(chemin).headers["etag"]
    assert http_site.head(chemin, headers={"If-None-Match": etag}).status == 304
