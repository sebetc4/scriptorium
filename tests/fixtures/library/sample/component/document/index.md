---
title: Composant d'essai
subtitle: Une fiche fictive, écrite pour la suite de tests et pour rien d'autre
eyebrow: Fiche d'essai
date: 2026-09-25
preset: report
lang: fr
theme: light
meta: {Version: "1.0"}
---

# Principe

Ce document n'existe que pour les tests. Il porte, en petit, tout ce qu'une
fiche de la bibliothèque contient : des chapitres, des schémas, un tableau trop
large pour une liseuse, un bloc de code et des encadrés. Son contenu décrit un
composant qui n'existe pas.

## Structure

Le composant d'essai est une pastille de deux millimètres reliée à deux
broches. Sa structure tient en une coupe.

![Vue en coupe du composant](assets/coupe.svg "Figure 1 — Vue en coupe"){: .diagram }

!!! important "À retenir"
    La pastille conduit dans un seul sens : c'est tout ce qu'il faut savoir
    pour la suite.

# Mise en œuvre

## Brochage

- :arrow-right: La broche A reçoit le courant.
- :arrow-right: La broche K le rend.

![Brochage du composant](assets/brochage.svg "Figure 2 — Brochage"){: .diagram }

## Caractéristiques

| Référence | Tension | Courant | Puissance | Boîtier | Température | Prix |
|---|---|---|---|---|---|---|
| CE-1 | 5 V | 100 mA | 0,5 W | TO-92 | 85 °C | 0,10 € |
| CE-2 | 12 V | 250 mA | 1 W | TO-220 | 125 °C | 0,35 € |
| CE-3 | 24 V | 500 mA | 2 W | TO-220 | 150 °C | 0,80 € |

!!! warning "Attention"
    Au-delà de la tension indiquée, le composant d'essai chauffe[^1].

[^1]: Dans la fiction de ce document, bien sûr.

# Dimensionnement

## Courbe

La courbe se lit de gauche à droite : le courant croît avec la tension.

![Courbe courant-tension](assets/courbe.svg "Figure 3 — Courant en fonction de la tension"){: .diagram }

## Montage

![Montage de référence](assets/montage.svg "Figure 4 — Montage de référence"){: .diagram }

La résistance se calcule ainsi :

```python
def resistance(tension, chute, courant):
    return (tension - chute) / courant
```
