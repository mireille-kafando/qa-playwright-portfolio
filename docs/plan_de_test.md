# Plan de test : portfolio et démo de détection de piétons

| | |
|---|---|
| Système sous test | Portfolio [mireille-kafando.github.io](https://mireille-kafando.github.io) et démo [`/demo-pietons/`](https://mireille-kafando.github.io/demo-pietons/) |
| Version testée | Dépôt `mireille-kafando.github.io`, branche `main` (déploiement GitHub Pages) |
| Auteure | Mireille Kafando |
| Date | Novembre 2026 |

## 1. Objectifs

1. Vérifier que les parcours essentiels fonctionnent sur les navigateurs principaux : consulter le portfolio, changer de langue, ouvrir un projet, lancer la démo et analyser une image.
2. Détecter les régressions à chaque modification du site et chaque jour, sur le site en production.
3. Contrôler un socle d'accessibilité : textes alternatifs, noms accessibles, hiérarchie des titres, langue du document.
4. Garder la trace des défauts trouvés et vérifier, par un test de non-régression, que chaque défaut corrigé ne revient pas.

## 2. Périmètre

**Inclus :**
- page d'accueil : contenu clé, bascule français/anglais et sa persistance, liens vers les dépôts et la démo, mise en page de 375 à 1 440 pixels, métadonnées de partage ;
- démo : chargement du modèle ONNX, analyse automatique de l'image d'exemple, seuil de confiance, choix du modèle v1/v2, envoi d'une image, cas d'erreur (fichier non image, image illisible), bascule de langue ;
- accessibilité de base des deux pages ;
- validité des liens externes.

**Exclus :**
- **qualité du modèle de détection :** elle est mesurée dans le dépôt [pedestrian-detection-adas](https://github.com/mireille-kafando/pedestrian-detection-adas). Ici, on vérifie seulement que la démo produit des détections cohérentes ;
- **performances fines :** le temps d'inférence est affiché et contrôlé, mais pas mesuré par rapport à un objectif chiffré ;
- **audit d'accessibilité complet :** contrastes, navigation au clavier détaillée, lecteurs d'écran réels.

## 3. Approche

| Niveau | Outil | Contenu |
|---|---|---|
| Tests de bout en bout | Playwright (Python) avec pytest | Parcours utilisateur pilotés dans un vrai navigateur |
| Accessibilité | Requêtes sur le DOM et l'arbre d'accessibilité | Règles vérifiables automatiquement |
| Liens | Requêtes HTTP via Playwright | Codes de réponse des liens externes |
| Non-régression | Un test par défaut corrigé | Référencé dans le rapport de défaut |

- **Sélecteurs :** les tests privilégient les rôles et les noms accessibles (`get_by_role`), comme un utilisateur ou un lecteur d'écran, plutôt que la structure CSS.
- **Attentes :** elles sont explicites (`expect`) et jamais fixes ; le chargement du modèle (13 Mo) dispose d'un délai de 90 secondes.
- **Données de test :** l'image d'exemple de la démo, un fichier texte et un JPEG volontairement corrompu, générés pendant le test.

## 4. Environnements

| Environnement | Navigateurs | Déclenchement |
|---|---|---|
| Intégration continue (GitHub Actions, Ubuntu) | Chromium, Firefox | À chaque modification du dépôt de tests, chaque jour à 7 h 15 (heure de l'Est), et à la demande |
| Poste local | Chromium, Firefox, WebKit au choix | `pytest --browser …` ; `--base-url` pour tester une copie locale du site |

## 5. Cas de test

| ID | Fonction | Vérification | Priorité |
|---|---|---|---|
| TC-P01 | Accueil | Titre de la page et titre principal unique au nom de l'auteure | Haute |
| TC-P02 | Langue | La bascule français/anglais change la langue du document et les titres, et survit au rechargement | Haute |
| TC-P03 | Projets | Chaque projet mène à son dépôt GitHub | Haute |
| TC-P04 | Projets | Le lien « Essayer la démo en ligne » ouvre la démo | Haute |
| TC-P05 | Contenu | Le résultat ADAS affiché est celui de la v2 (0,86), l'ancien 0,685 n'apparaît plus | Moyenne |
| TC-P06 | Contenu | Compétences alignées sur les CV (Java, C# en notions) et ligne « Langues » présente | Moyenne |
| TC-P07 | Contenu | Tous les liens LinkedIn pointent vers le bon profil | Haute |
| TC-P08 | Robustesse | Aucune erreur JavaScript au chargement | Haute |
| TC-P09 | Mise en page | Pas de défilement horizontal à 375, 768 et 1 440 pixels | Moyenne |
| TC-P10 | Partage | Une image d'aperçu valide est déclarée sur chaque page | Basse |
| TC-D01 | Démo | L'image d'exemple est analysée au chargement avec la v2 : au moins 3 piétons, aucun cycliste, temps affiché | Haute |
| TC-D02 | Démo | Le nombre de détections décroît quand le seuil augmente (0,25 à 0,90) | Haute |
| TC-D03 | Démo | Le choix de la v1 relance l'analyse, puis le retour à la v2 | Moyenne |
| TC-D04 | Démo | Une image envoyée par l'utilisateur est analysée | Haute |
| TC-D05 | Erreurs | Un fichier qui n'est pas une image affiche un message | Moyenne |
| TC-D06 | Erreurs | Une image illisible affiche un message | Moyenne |
| TC-D07 | Langue | La démo bascule en anglais, séparateur décimal compris | Basse |
| TC-D08 | Robustesse | Aucune erreur JavaScript pendant le chargement et l'analyse | Haute |
| TC-D09 | Contenu | La description des données d'entraînement est exacte (75 images annotées, pas Cityscapes) | Haute |
| TC-A01 | Accessibilité | Toutes les images ont un texte alternatif | Moyenne |
| TC-A02 | Accessibilité | Champs, listes et boutons ont un nom accessible | Moyenne |
| TC-A03 | Accessibilité | Les niveaux de titres ne sautent pas de niveau | Basse |
| TC-A04 | Accessibilité | La langue du document est déclarée | Moyenne |
| TC-A05 | Accessibilité | Le résultat de la démo est décrit en texte, pas seulement dessiné | Moyenne |
| TC-L01 | Liens | Aucun lien externe en erreur (LinkedIn, qui répond 999 aux robots, est toléré) | Moyenne |

Les cas paramétrés sont exécutés sur chaque page ou chaque largeur concernée. Avec deux navigateurs, cela donne 66 exécutions.

## 6. Critères d'entrée et de sortie

- **Entrée :** le site est déployé et répond ; les dépendances de `requirements.txt` et les navigateurs Playwright sont installés.
- **Sortie :** tous les cas de priorité haute réussissent sur Chromium et Firefox ; tout échec est soit corrigé, soit consigné dans un rapport de défaut.

## 7. Gestion des défauts

Chaque défaut fait l'objet d'un rapport dans [`defauts/`](defauts/), avec :
- **identification :** son identifiant, sa gravité et sa priorité ;
- **reproduction :** l'environnement, les étapes, le résultat attendu et le résultat obtenu ;
- **suivi :** le correctif (commit) et le test de non-régression associé.

| Gravité | Définition |
|---|---|
| Bloquante | Une fonction principale est inutilisable, sans contournement |
| Majeure | Une fonction principale est dégradée, ou une information affichée est fausse |
| Mineure | Gêne limitée, ou non-conformité d'accessibilité avec contournement |
| Cosmétique | Présentation, sans effet sur l'usage |

## 8. Risques et limites

- **Tests réseau instables :** les tests de liens dépendent de sites tiers et peuvent échouer de façon intermittente (limitation de débit, blocage des robots). Ils sont isolés par le marqueur `liens`.
- **Écarts entre navigateurs :** le redimensionnement des images par le navigateur peut légèrement changer les scores de confiance. Les vérifications portent donc sur des bornes, comme « au moins 3 piétons », plutôt que sur des valeurs exactes.
- **Accessibilité partielle :** les règles automatisées ne remplacent pas un test avec un lecteur d'écran.
