---
title: Guide de style
subtitle: La direction artistique commune à tous les PDF de la bibliothèque, et la manière de s'en écarter quand un document l'exige.
eyebrow: Référence
date: 2026-09-04
preset: report
theme: both
footer: Ma bibliothèque
meta:
  Version: "1.0"
---

## La chaîne de production

Un document est un dossier sous `library/`, dont `document/index.md` est l'entrée. Le contenu est
du Markdown ; la mise en forme vient entièrement de la cascade CSS du repo, donc
le contenu n'a jamais à porter de décision graphique.

![Chaîne de production](assets/chaine.svg "Figure 1 — De index.md au PDF"){: .diagram }

La profondeur sous `library/` est libre : les dossiers intermédiaires font office de
thèmes et se créent au besoin, sans registre à tenir à jour.

## La cascade

Huit niveaux, du plus général au plus spécifique. Chacun ne redéfinit que son
écart au précédent.

| Niveau | Fichier | Portée |
|---|---|---|
| 1 | `brand/tokens.css` | La DA — couleurs, typographie, format |
| 2 | `theme/base.css` | Typographie et éléments de contenu |
| 3 | `theme/code.css` | Surlignage du code, réduit aux rôles de la DA |
| 4 | `theme/page.css` | Page, en-têtes, couverture, sommaire |
| 5 | `theme/<preset>.css` | Registre du document |
| 6 | front-matter `page:` | Surcharges ponctuelles |
| 7 | `<doc>/theme.css` | Surcharge locale du document |
| 8 | front-matter `css:` | Feuilles additionnelles |

!!! important "Une seule source pour la marque"
    `brand/tokens.yaml` est le seul endroit où vivent les valeurs de marque. Sa
    section `palette` porte les rampes ; `colors` mappe les rôles dessus par
    référence, jamais par copie. `make brand` propage vers la feuille CSS des
    PDF **et** vers le profil de la skill `diagram-design`.

## Les diagrammes

Un diagramme s'écrit avec les mêmes rôles que le reste — `fill="var(--accent)"`,
`stroke="var(--rule)"` — jamais avec des valeurs. Le build l'inline dans la page
et résout ses variables contre la cascade du document : il suit donc la DA, et
la surcharge locale s'il y en a une, sans avoir à être régénéré.

La figure ci-dessus le démontre : son SVG ne contient aucune couleur.

## Les icônes

Le jeu **Lucide** est embarqué dans `brand/icons/` (2057 icônes, version
épinglée). Une icône s'écrit `:nom:` dans le texte, et prend un rôle de la DA
avec un suffixe : `:nom.accent:`, `:nom.alert:`, `:nom.danger:`, `:nom.muted:`,
`:nom.soft:`. Une entrée de liste qui commence par une icône voit sa puce
remplacée par celle-ci.

- :circle-check.accent: Ce qui est acquis
- :circle-dashed.muted: Ce qui reste à faire
- :arrow-right: Ce qui vient ensuite

Les encarts reçoivent l'icône **et la couleur** de leur type sans qu'on
l'écrive — :circle-alert.accent: pour `important`, :triangle-alert.alert: pour
`warning`, :octagon-alert.danger: pour `danger`, :info: pour `note`. En poser
une soi-même dans le titre désactive l'automatisme.

Comme pour les diagrammes, la couleur est résolue au build : WeasyPrint ne suit
ni `currentColor` ni `var()` à l'intérieur d'un SVG.

## Le registre typographique

Le corps est en `--font-body`, les titres en `--font-head`, le code et les
libellés techniques en `--font-mono`. L'échelle dérive d'une seule raison,
`--scale`, appliquée à `--size`.

> La couleur d'accent est éditoriale, pas signalétique : une à deux occurrences
> par page. Au-delà, elle cesse d'attirer l'œil.

Deux autres couleurs portent un sens, et elles seules : `alert` pour ce qui
coûte du temps ou fausse un résultat, `danger` pour ce qui détruit ou blesse.
Elles échappent au budget de l'accent — un risque réel se signale autant de fois
qu'il se présente — mais une alerte posée sur ce qui n'est pas risqué dévalue
toutes les autres.

!!! warning "Vigilance"
    Registre `alert`. L'erreur coûte du temps ou fausse une mesure.

!!! danger "Danger"
    Registre `danger`. L'erreur détruit le matériel ou blesse.

Ces deux rôles restent propres aux PDF : `diagram-design` tient à une seule
teinte accentuée, et un diagramme dit le risque par sa forme, pas par une
couleur qu'elle ne connaît pas.

Le texte courant est justifié avec césure automatique ; `orphans` et `widows`
sont fixés à trois lignes pour éviter les lignes esseulées en bas de page.

## S'écarter du thème

Un document qui a besoin d'un traitement particulier pose un `theme.css` dans
son `document/`, à côté de `index.md` — il est chargé après le preset et gagne donc l'arbitrage :

```css
/* library/finance/rapport-q3/document/theme.css */
:root { --accent: var(--link); }    /* un rôle, jamais une valeur */
.cover h1 { font-size: 48pt; }      /* couverture plus affirmée */
```

Pour un simple changement de format, le front-matter suffit :

```yaml
page:
  size: A5
  margin: 15mm
```
