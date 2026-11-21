# language: fr
Fonctionnalité: Parcours d'un recruteur sur le portfolio
  En tant que recruteur
  Je veux trouver vite les projets de Mireille et les essayer
  Afin de juger ses compétences en quelques minutes

  Contexte:
    Étant donné que je suis sur la page d'accueil du portfolio

  Scénario: Essayer la démo d'un projet depuis sa carte
    Quand j'ouvre la démo de la carte « Classification de pièces de monnaie »
    Alors la démo des pièces s'affiche
    Et elle est prête à analyser une photo

  Scénario: Trouver le projet QA et son code
    Alors une carte présente le projet « Tests automatisés de ce portfolio (QA) »
    Et cette carte mène au dépôt « qa-playwright-portfolio »

  Plan du scénario: Lire le portfolio dans ma langue
    Quand je choisis la langue « <bouton> »
    Alors la page est en <code langue>
    Et la section des projets s'intitule « <titre> »

    Exemples:
      | bouton  | code langue | titre    |
      | English | en          | Projects |
