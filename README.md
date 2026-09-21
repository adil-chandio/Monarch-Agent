# Monarch

Faceless YouTube OS for **Arena Agent Mode**.

## Start

Clone branch `arena/01a0c2a6-monarch-agent`, then only:

```
monarch activate 💀
```

Agent asks 4 things: channel/niche, 16:9 or 9:16, short or long, language.  
Then: YT forensic + keywords → 10 ideas + TOP 1 → wait → script → wait → video (haan) → QC → thumbs → metadata. **You upload.**

Full law: `BOOT.md` · `AGENT.md` · `docs/WORKFLOW.md`

```
python -m monarch status
python -m monarch maths --seconds 60
```

## M3 script in Fountain

Write the script as a `.fountain` screenplay, gate it into numbered scenes:

```
monarch m3
monarch screen-script script.fountain --length short --board-out board.json
monarch script-fountain board.json --out approved.fountain
```

Words per clip come from the maths line, never from taste — no padding, no fake counts.
Full law: `docs/FOUNTAIN_M3.md`.
