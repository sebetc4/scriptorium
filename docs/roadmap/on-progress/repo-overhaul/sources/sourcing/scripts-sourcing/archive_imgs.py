from PIL import Image
import os, hashlib, json

S = "/tmp/claude-1000/-code-claude-pdf-creator/1f74a2c5-71e5-418f-aefb-de48a4f56d00/scratchpad"
D = "/code/claude/pdf-creator/library/electronique/repair/electribe-2/sources/images"

# nom de destination -> (source, origine, légende, côté long max)
PLAN = {
    # --- la pièce maîtresse : le schéma reconstitué par mcv
    "mcv-schema-power.jpg":      (f"{S}/imgs/schema-WwbyM8Y.jpeg", "https://imgur.com/a/0C2Nj — album « electribe DP2 component » de mcv", "Schéma de la section Power reconstitué à la main par mcv depuis le PCB", 0),
    # --- le pont J4 documenté
    "j4-bridge-reference.png":   (f"{S}/bridge.png", "https://ancientcomputing.org/electribe-bridge.png", "Zone SW1 / J4 avec le pont matérialisé en rouge", 0),
    # --- galerie de réparation de mcv (album « Fixing electribe sampler »)
    "mcv-klm3315-power-area.jpg":(f"{S}/mcv/VjoMIRY.jpeg", "https://imgur.com/a/zEsqp", "KLM-3315 : bouton SW1, empreinte J4 et le bloc DT1–DT4 / R3–R6 / C29 / C30", 4200),
    "mcv-klm3314-top.jpg":       (f"{S}/mcv/t13vxMA.jpeg", "https://imgur.com/a/zEsqp", "KLM-3314 : AM1802B, Blackfin BF523, lecteur SD, régulateur ADP5052", 2600),
    "mcv-klm3314-hand.jpg":      (f"{S}/mcv/uCDwmjv.jpeg", "https://imgur.com/a/zEsqp", "KLM-3314 extraite", 2600),
    "mcv-klm3314-back.jpg":      (f"{S}/mcv/AZEavNe.jpeg", "https://imgur.com/a/zEsqp", "Face soudure de la KLM-3314", 2600),
    "mcv-klm3315-solder-1.jpg":  (f"{S}/mcv/HPNIDkL.jpeg", "https://imgur.com/a/zEsqp", "Face soudure de la KLM-3315, marquage « 3315 » visible", 2600),
    "mcv-klm3315-solder-2.jpg":  (f"{S}/mcv/bh5n40k.jpeg", "https://imgur.com/a/zEsqp", "Face soudure de la KLM-3315, autre cadrage", 2600),
    "mcv-klm3315-solder-3.jpg":  (f"{S}/mcv/WjQHUdR.jpeg", "https://imgur.com/a/zEsqp", "Face soudure de la KLM-3315, zone D44", 2600),
    "mcv-pads-front.jpg":        (f"{S}/mcv/6RddIfG.jpeg", "https://imgur.com/a/zEsqp", "Face composants de la KLM-3315 : contacts des pads", 2600),
    "mcv-pads-front-2.jpg":      (f"{S}/mcv/dPZEa0T.jpeg", "https://imgur.com/a/zEsqp", "Contacts des pads, autre angle", 2600),
    "mcv-pads-front-3.jpg":      (f"{S}/mcv/96kaAZa.jpeg", "https://imgur.com/a/zEsqp", "Contacts des pads, rasant", 2600),
    "mcv-board-in-case.jpg":     (f"{S}/mcv/byY97KA.jpeg", "https://imgur.com/a/zEsqp", "Carte principale avec l'écran, avant remontage", 2600),
    "mcv-rubber-pads.jpg":       (f"{S}/mcv/LoN2pTP.jpeg", "https://imgur.com/a/zEsqp", "Nappe caoutchouc des pads et boutons, déposée", 2600),
    "mcv-connectors.jpg":        (f"{S}/mcv/eS5Cmeu.jpeg", "https://imgur.com/a/zEsqp", "Zone connecteurs arrière de la carte principale", 2600),
    "mcv-bench.jpg":             (f"{S}/mcv/nqODgFI.jpeg", "https://imgur.com/a/zEsqp", "Le poste de travail de mcv, machine ouverte", 2600),
    "mcv-fixed.jpg":             (f"{S}/mcv/plzRT5g.jpeg", "https://imgur.com/a/zEsqp", "Machine réparée, écran allumé", 2600),
    # --- démontage cntrlchng, fil « Guts of a Virgin »
    "guts-klm3314-a.jpg":        (f"{S}/imgs/YYacgBC.jpg", "https://www.korgforums.com/forum/phpBB3/viewtopic.php?t=94641", "KLM-3314, vue d'ensemble (cntrlchng)", 2600),
    "guts-klm3314-b.jpg":        (f"{S}/imgs/mRJj8ws.jpg", "https://www.korgforums.com/forum/phpBB3/viewtopic.php?t=94641", "KLM-3314, circuits intégrés repérés (cntrlchng)", 2600),
    "guts-klm3314-c.jpg":        (f"{S}/imgs/GrgUuSh.jpg", "https://www.korgforums.com/forum/phpBB3/viewtopic.php?t=94641", "KLM-3314, alimentation et mémoires (cntrlchng)", 2600),
    "guts-klm3315-a.jpg":        (f"{S}/imgs/Sk3Px7Z.jpg", "https://www.korgforums.com/forum/phpBB3/viewtopic.php?t=94641", "KLM-3315, vue d'ensemble (cntrlchng)", 2600),
    "guts-klm3315-b.jpg":        (f"{S}/imgs/L1OXqNn.jpg", "https://www.korgforums.com/forum/phpBB3/viewtopic.php?t=94641", "KLM-3315, multiplexeurs et ampli-op (cntrlchng)", 2600),
    "guts-klm3315-c.jpg":        (f"{S}/imgs/n2pGVSM.jpg", "https://www.korgforums.com/forum/phpBB3/viewtopic.php?t=94641", "KLM-3315, détail (cntrlchng)", 2600),
    "guts-klm3315-d.jpg":        (f"{S}/imgs/bT7oKli.jpg", "https://www.korgforums.com/forum/phpBB3/viewtopic.php?t=94641", "KLM-3315, détail (cntrlchng)", 2600),
    "guts-klm3315-e.jpg":        (f"{S}/imgs/UfluvSr.jpg", "https://www.korgforums.com/forum/phpBB3/viewtopic.php?t=94641", "KLM-3315, détail (cntrlchng)", 2600),
    "guts-klm3315-f.jpg":        (f"{S}/imgs/okrpR9d.jpg", "https://www.korgforums.com/forum/phpBB3/viewtopic.php?t=94641", "KLM-3315, microcontrôleur Cortex-M3 (cntrlchng)", 2600),
    "guts-inside-a.jpg":         (f"{S}/imgs/8MayZ1J.jpg", "https://www.korgforums.com/forum/phpBB3/viewtopic.php?t=94641", "Intérieur de l'Electribe 2 ouverte (cntrlchng)", 2600),
    "guts-inside-b.jpg":         (f"{S}/imgs/9Loq21v.jpg", "https://www.korgforums.com/forum/phpBB3/viewtopic.php?t=94641", "Intérieur, autre vue (cntrlchng)", 2600),
    "guts-inside-c.jpg":         (f"{S}/imgs/FvrUOIc.jpg", "https://www.korgforums.com/forum/phpBB3/viewtopic.php?t=94641", "Intérieur, autre vue (cntrlchng)", 2600),
}

os.makedirs(D, exist_ok=True)
manifest = []
for name, (src, origin, caption, maxside) in sorted(PLAN.items()):
    if not os.path.exists(src):
        print("MANQUANT", src); continue
    sha_src = hashlib.sha256(open(src, "rb").read()).hexdigest()
    im = Image.open(src)
    w0, h0 = im.size
    dst = os.path.join(D, name)
    if maxside and max(w0, h0) > maxside:
        im.thumbnail((maxside, maxside), Image.LANCZOS)
    if name.endswith(".png"):
        im.save(dst, optimize=True)
    else:
        im.convert("RGB").save(dst, quality=88, optimize=True, progressive=True)
    manifest.append({
        "fichier": name, "origine": origin, "legende": caption,
        "dimensions_origine": [w0, h0], "dimensions_stockees": list(im.size),
        "sha256_original": sha_src, "octets": os.path.getsize(dst),
    })
    print(f"{name:32s} {w0}x{h0} -> {im.size[0]}x{im.size[1]}  {os.path.getsize(dst)//1024} Ko")

json.dump(manifest, open(os.path.join(D, "manifest.json"), "w"), indent=2, ensure_ascii=False)
print("\ntotal", sum(m["octets"] for m in manifest) // 1024 // 1024, "Mo /", len(manifest), "images")
