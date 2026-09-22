# Monarch

Faceless YouTube OS for **Arena Agent Mode**.  
**Created by Adil Chandio** | Contact: [workadilchandio@gmail.com](mailto:workadilchandio@gmail.com)

---

## 🔒 Security & Access Activation

Monarch Agent is protected with a private activation key. **The key is never stored in
this repository** — only its SHA-256 hash is — so cloning this repo does not reveal it.
You get the key directly from the boss
([workadilchandio@gmail.com](mailto:workadilchandio@gmail.com)).
If anyone clones or runs Monarch without activation, access is denied with:

> *"Me Monarch Agent muje Adil chandio ne banaya ha to apko mujhe access run Karne ke Liye key chaiye Yahan chat me key dalen Aage key NAHI ha to apko mere boss se milegi unka contact Gmail: workadilchandio@gmail.com"*

### How to Unlock / Activate:
```bash
# 1. Via CLI activation command:
monarch activate <your-key>

# 2. Or set environment variable:
export MONARCH_ACCESS_KEY="<your-key>"

# 3. Or pass inline with any command:
monarch --key <your-key> status
```

---

## Start

Clone the repo, activate with the key given to you, then:

```
monarch activate <your-key>
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
