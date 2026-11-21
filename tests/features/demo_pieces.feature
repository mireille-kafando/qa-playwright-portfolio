# language: fr
Fonctionnalité: Reconnaissance d'une pièce de monnaie dans le navigateur
  En tant que visiteur du portfolio
  Je veux envoyer une photo de pièce à la démo
  Afin de voir quelle valeur le modèle reconnaît, et avec quelle confiance

  Contexte:
    Étant donné que la démo des pièces est ouverte et que le modèle est chargé

  Scénario: Analyser une image
    Quand j'envoie l'image de référence
    Alors 4 probabilités s'affichent, dont la somme vaut 100 %
    Et le verdict nomme la classe la plus probable
    Et l'image analysée est décrite pour les lecteurs d'écran

  Plan du scénario: Refuser un fichier inutilisable
    Quand j'envoie <fichier>
    Alors le message « <message> » s'affiche
    Et aucun verdict n'est donné

    Exemples:
      | fichier                 | message                 |
      | un fichier texte        | n'est pas une image     |
      | un JPEG corrompu        | Impossible de lire      |
