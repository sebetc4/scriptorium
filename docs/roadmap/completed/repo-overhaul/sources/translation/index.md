> **Archive, remplacée le 2026-09-16.** Ce qui est ici a été repris par la
> skill `translate` (`.claude/skills/translate/`) pour le découpage avec contexte,
> le contrôle des chiffres et de la terminologie et le recoupement entre deux
> moteurs, et par `docs/local-translation.md` pour les modèles visés. Leur mise
> en œuvre a son propre roadmap, `docs/roadmap/pending/local-translation/`. La
> correspondance point par point est dans les notes de la phase 7 du roadmap
> `repo-overhaul`. Ce fichier est conservé tel quel ; il n'est plus mis à jour.

Oui. Avec ta **RTX 5090 Laptop 24 Go**, je partirais sur une installation orientée **qualité maximale** plutôt que sur un LLM généraliste.

### Configuration que je recommande

**Modèle principal : MADLAD-400 10B-MT en Q8_0**

Le modèle officiel MADLAD-400 10B est un modèle de traduction basé sur T5, entraîné sur des centaines de langues et 250 milliards de tokens. Il existe aujourd'hui en GGUF **Q8_0 d'environ 11 Go**, avec une consommation GPU annoncée autour de **11,3 Go** lorsqu'il est entièrement déporté sur GPU. Ta 5090 24 Go a donc largement la marge nécessaire. ([Hugging Face][1])

Je privilégierais **Q8_0** plutôt que Q4/Q5/Q6 puisque tu as suffisamment de VRAM. Le but ici est de minimiser la perte liée à la quantification. Le dépôt propose également Q6_K, mais je ne vois pas de raison de descendre aussi bas dans ton cas. ([Hugging Face][2])

**Modèle de comparaison : NLLB-200 3.3B**

Je l'installerais également comme deuxième moteur. Le checkpoint officiel pèse environ **17,6 Go** et couvre 196 langues. Il reste une référence très sérieuse pour la traduction, même si Meta précise qu'il s'agit d'un modèle de recherche et qu'il n'est pas destiné notamment aux textes spécialisés ou à la traduction documentaire. ([Hugging Face][3])

### Pourquoi deux modèles ?

Pour de la traduction de haute qualité, je ne ferais pas simplement :

> texte → modèle → traduction

Je ferais plutôt :

**texte original → découpage intelligent → MADLAD-10B → contrôle NLLB → vérification terminologique → résultat final**

Et pour les documents longs, il faut conserver le contexte entre les paragraphes plutôt que d'envoyer chaque phrase indépendamment.

### Pour FR ↔ EN

MADLAD utilise des préfixes de langue et prend en charge les langues de son corpus multilingue. Le modèle officiel couvre plus de 400 langues. ([Hugging Face][4])

Pour ton application, je configurerais explicitement :

```text
Français → Anglais
Anglais → Français
```

avec une consigne très stricte du genre :

```text
Translate the following text from French to English.
Preserve:
- meaning
- terminology
- paragraph structure
- punctuation
- numbers
- proper names
- formatting

Do not summarize.
Do not add explanations.
Do not omit information.
```

### L'interface que je choisirais

Je **n'utiliserais pas Ollama comme première solution** pour ce cas précis.

Je partirais sur **llama.cpp + GGUF**, car des checkpoints MADLAD-400 10B Q8_0 existent déjà dans ce format et sont documentés pour llama.cpp. ([Hugging Face][5])

Cela te permet d'avoir un moteur entièrement local avec une API compatible et éventuellement une interface graphique par-dessus.

### Architecture idéale

```text
                 ┌──────────────────┐
                 │  Texte / fichier  │
                 └────────┬─────────┘
                          │
                    détection langue
                          │
                découpage en segments
                          │
                          ▼
               ┌─────────────────────┐
               │   MADLAD-400 10B   │
               │       Q8_0          │
               └──────────┬──────────┘
                          │
                    traduction
                          │
                          ▼
               ┌─────────────────────┐
               │ Contrôles qualité   │
               │ terminologie /      │
               │ chiffres / noms     │
               └──────────┬──────────┘
                          │
                          ▼
                 traduction finale
```

### Un point important

Je ne peux pas honnêtement affirmer que **MADLAD-10B est systématiquement meilleur que NLLB-3.3B pour anglais ↔ français** sur tous les textes. La fiche MADLAD indique elle-même que la qualité varie selon les langues et les domaines. ([Hugging Face][6])

Comme tu recherches **la meilleure qualité possible**, la bonne approche est donc de faire un **petit benchmark personnel FR↔EN** avec, par exemple, 20 passages représentatifs de ce que tu traduis réellement. On peut comparer MADLAD 10B Q8, MADLAD 7B Q8 et NLLB 3.3B, puis choisir sur des critères comme fidélité, naturel, terminologie et erreurs de sens.

**Ma configuration de départ serait donc : MADLAD-400 10B Q8_0 + llama.cpp + NLLB-200 3.3B comme second moteur de validation.**

Je peux te donner maintenant **la procédure complète d'installation sous Windows 11 pour ta RTX 5090 Laptop**, avec les commandes exactes et un petit script Python qui traduit des fichiers `.txt`, `.srt`, `.docx` ou `.md` entièrement hors ligne.

[1]: https://huggingface.co/google/madlad400-10b-mt?utm_source=chatgpt.com "google/madlad400-10b-mt · Hugging Face"
[2]: https://huggingface.co/thirteenbit/madlad400-10b-mt-gguf?utm_source=chatgpt.com "thirteenbit/madlad400-10b-mt-gguf · Hugging Face"
[3]: https://huggingface.co/facebook/nllb-200-3.3B?utm_source=chatgpt.com "facebook/nllb-200-3.3B · Hugging Face"
[4]: https://huggingface.co/google/madlad400-7b-mt/tree/main?utm_source=chatgpt.com "google/madlad400-7b-mt at main"
[5]: https://huggingface.co/NikolayKozloff/madlad400-10b-mt-Q8_0-GGUF?utm_source=chatgpt.com "NikolayKozloff/madlad400-10b-mt-Q8_0-GGUF · Hugging Face"
[6]: https://huggingface.co/google/madlad400-7b-mt?utm_source=chatgpt.com "google/madlad400-7b-mt · Hugging Face"
