# 👑 MONARCH MASTER PRODUCTION PROMPT — v2 (SAB SEEKHA HUA)

**Faceless YouTube Short Production Law — 100% Tested & Verified**
Source: operator-registered failure log from the live production session
(16 galteeyan, unki ASLI wajah, fix, aur hamesha-lagu rule). Yeh canon
hai — RENDER_LAWS.md render-QC ka jesta hai, yeh POORA pipeline chalta
hai. Dono canons sath chalte hain; jahan numbering takraye, dono apni
apni jagah sahi hain.

**REPO STANCE (standing order #1):** G7 ka layered-mixing architecture
aur Part 4 checklist KNOWLEDGE hain — in-repo Monarch previz/QC emit
karta hai, MP4 render/mix/player parked hai. `monarch audit` in laws
ke khilaf EXISTING artifacts ko report karta hai, kabhi nahi banata.
Upload INSAAN karega (HAAN gate).

----------------------------------------------------------------
## PART 1 — PIPELINE (ORDER HAMESHA YEH)

1. INTAKE: 4 sawal (channel/niche · 16:9 ya 9:16 · short ya long ·
   language) → STOP, jawab ka wait.
2. F0 FORENSIC: market research → 10 ideas → TOP 1 + wajah → operator
   pick kare (STOP).
3. M3 SCRIPT: Fountain format, maths line se words (60s class short =
   18 beats x 7 words exact). Operator bole "perfect" tab aage.
4. M5b RENDER: "haan" ke bina render NAHI (permission gate).
5. M5c QC: har checkpoint honest, fail = stop-fix-reverify.
6. M6/P3: thumbnails + title gate + listing + .srt captions.
7. UPLOAD: INSAAN karega — tum sirf pack do.

----------------------------------------------------------------
## PART 2 — REGISTERED FAILURES (KYA HUA · KYUN HUA · KYA FIX HUA · AB RULE)

### [G1] pip install fail — "Multiple top-level packages in flat-layout"
- Hua: repo mein monarch/ refs/ vendor/ top-level the; setuptools ne
  build refuse kiya.
- Wajah: pyproject flat-layout auto-discovery.
- Fix: PYTHONPATH shim (`#!/bin/sh` + `PYTHONPATH=<repo> python3 -m
  monarch "$@"` → /usr/local/bin/monarch).
- RULE: zero-dependency repo ko packaging se mat laro — direct
  source-run + PYTHONPATH. Out-of-tree helper scripts ko bhi hamesha
  PYTHONPATH do (ModuleNotFoundError se bacho).

### [G2] Sandbox har turn reset hota hai
- Hua (2 baar): ffmpeg gayab + render/work/ ke saare intermediates
  (segments, captioned video, sfx wavs) wipe — build beech mein fail.
- Wajah: sirf workspace sources persist hote hain; binaries, /tmp,
  generated intermediates NAHI.
- Fix: har build idempotent + self-contained (SFX/music builder ke
  andar regenerate; missing ho to khud bana le).
- RULE: (a) naye session mein `which ffmpeg` warna apt install;
  (b) builders intermediates khud regenerate karein; (c) big
  intermediates kaam khatam hote hi delete (workspace budget);
  (d) /tmp mein kuch permanent mat rakho.

### [G3] Image generation limit — 10 per turn
- Hua: 18 frames ek turn mein mangi → beech mein ruk gaya.
- RULE: pehle hi batch plan banao: turn A = 10 frames, turn B = 8
  frames + 2 thumbnails. Speech clips bhi max 10/turn — 9 VO clips
  + buffer hisaab pehle se.

### [G4] Fountain parser grammar
- Hua: roman-urdu lines lowercase likhi to parser ne unhe dialogue
  samjha; commas/dashes word-count se gir gaye; capitalization badli.
- Fix: parser ke tokenizer rules ke andar likho; count hamesha
  engine se validate (`screen-script` output har beat pe [n words]
  dikhata hai).
- RULE: line ka word count hamesha ENGINE ke tokenizer se check ho
  (`[A-Za-z0-9']+`), apne haath se nahi. Visual notes `:: ... ::
  spoken-line` format mein — visual words count NAHI hote.

### [G5] board.json ek LIST hai, dict nahi
- Hua: `b["maths"]` pe TypeError.
- RULE: kisi bhi generated JSON pe script likhne se pehle uska
  top-level shape dekho (json.load + type print).

### [G6] ffmpeg expression errors
- Hua #1: `if(lt(t,a) and gt(t,b))` → "Invalid argument" (ffmpeg
  expr mein `and`/`or` nahi hote). FIX: `between(t,a,b)`.
- Hua #2: ek input mein do sines `sine=...|sine=...` → invalid.
  FIX: `aevalsrc=0.6*sin(2*PI*98*t)+0.5*sin(2*PI*116.5*t):d=..`.
- RULE: lavfi syntax yaad rakho; naya expression likhne se pehle
  1-second chhota test chalao, phir bade graph mein lagao.

### [G7] ⚠️ SAB SE BADA: VO silently mix se nikal gaya (2 baar)
- Hua: 40-input single ffmpeg filtergraph → "Stream specifier
  'vobus'" / "matches no streams" errors; kaam-chalau workarounds
  ne audio banaya jisme VO inputs MISBIND the — final video mein
  VO ki jagah SFX booms the. Operator ne pakda: "voice over remove
  kardiya".
- Wajah (asli): (a) giant single graph + label reuse = ffmpeg 7.1.5
  parser instability/misbinding; (b) verification broadband
  `volumedetect` pe thi — clip-start ke BOOMS loud hote hain, is
  liye FALSE PASS mila; (c) ek hi window pe check kiya, multiple
  nahi; (d) input indices code mein add hote rahe, reference
  constants purane reh gaye (off-by-one) — pehla "start ka VO cut"
  bhi yehi tha (VO index 9 se start, 8 hona chahiye tha).
- FINAL FIX (yehi architecture hamesha):
  LAYERED MIXING — kabhi bhi >10 inputs per ffmpeg command nahi:
  1) vo_bus.wav     = 9 VO clips amix        (9 inputs)
  2) musd.wav       = music + vo_bus sidechain-duck (2 inputs)
  3) whoosh batches = 9 + 8                  (max 10 inputs)
  4) booms.wav      = 9 booms                (10 inputs)
  5) kit.wav        = subdrop+riser+shine    (3 inputs)
  6) L1 = vo_bus+musd · L2 = L1+whoosh+booms+kit (3 inputs)
  7) master = L2 → limiter → loudnorm -14 LUFS → fade
  8) MUX: video + master, sirf 2 inputs, `-c:v copy -c:a copy`

  CHECKPOINT GATES (fail-closed, har layer ke baad):
  - Speech-band level: `highpass=f=250,volumedetect` — VO window ka
    level RAW take ke level ke ±6dB ke andar ho.
  - MULTIPLE windows (pehla clip @0.0s + beech ka + aakhri clip).
  - BROADBAND volumedetect akela PROOF NAHI (booms dhoka dete hain)
    — sirf speech-band + raw-compare hi proof hai.
  - VO onset har window start pe ≤0.3s.

### [G8] VO ke leading breath-silence se 0.00s khamoshi
- Hua: naye takes mein shuru mein halki saans/khamoshi — pehla word
  der se aaya (retention law toota).
- FIX: har take pe
  `silenceremove=start_periods=1:start_silence=0.06:start_threshold=-45dB`
  + onset verification (clip 1 bhi 0.00s pe hi bole).
- RULE: hook mein pehli awaaz 0.3s ke andar — KOI excuse nahi.

### [G9] Fluffy script — 63.6s, filler lines
- Hua: "Camera on", "Kitabein seminars TED talks" jaise extra beats —
  pace slow, FOMO kam.
- FIX: har word test "kya ye line kaam karti hai?" → 51.6s tight.
- RULE: 60-class short ka final 50–56s range; filler word pe
  operator se poochh ke hi likhna.

### [G10] Voice quality — 3 dafa artist badla
- Hua: voice-00 formal/dramatic tha; accent/flow operator ko pasand
  nahi aaya (2 dafa complaint).
- FIX: voice BATTLE mein jeetwao — dono candidates ko SCRIPT KI
  ASLI LINE sunao (audition = preview); Pakistani Urdu ke liye
  language tag `ur` (hamesha `hi` nahi); use-case `conversational`
  (narration nahi) short-form VO ke liye.
- RULE: VO change = captions REBUILD + timelines REGENERATE + sab
  audio checkpoints dobara. Voice, captions, music — sab VO ke
  durations se derive hote hain, assumptions se nahi.

### [G11] Captions initially poor/absent
- FIX jo standard ban gaya: WORD-LEVEL KARAOKE captions:
  - timing REAL audio se (phrase char-weight + silencedetect ke
    real pauses pe snap; koi andaza nahi)
  - Anton font, auto-fit ≤980px, heavy black stroke + shadow
  - ACTIVE word amber (#FFC93C), baaki white; phrase-start pop-in
  - lower-third y≈1385 (1080x1920 safe zone)
  - har VO change pe captions.py dobara chalao
  - YouTube ke liye captions.srt bhi export (bonus reach)

### [G12] SFX bahut subtle + koi asli music nahi
- FIX jo standard ban gaya: SYNTHESIZED 3-ACT SCORE (royalty-free):
  - Act1 tension: Am drone + heartbeat pulse + clock ticks (FOMO)
    + mystery plucks
  - Flip point (VO ke "flip" window pe): 3s riser → sub-drop +
    heavy boom
  - Act2 dread: lower Dm drone + half-time heavy pulse
  - Act3 uplift: C-major drone + rising arpeggio + resolve chord
  - 17 whooshes har cut pe + 9 impact booms har clip start pe
  - Music VO ke neeche SIDECHAIN-DUCK (voice hamesha forward)
  - Master: -14 LUFS, TP -1.5, limiter, end-fade
- RULE: flip/uplift ki timing VO windows se aati hai — kad nahi.
  Music-only window ka bed level check karo (sunai deni chahiye,
  VO ke neeche dabni nahi chahiye).

### [G13] Editing grammar jo WORKING standard ban gaya
- 2–3s scene changes: clip ke andar hold >3.55s ho to mid-scene
  visual pivot (mirror variant + apna SFX) — video sabse pehle
  banti hai silent (shots → concat), phir caption overlay passes,
  phir audio mux.
- Har shot pe zoom motion (zoompan 1.0 → 1.10) — static frame kabhi
  nahi.
- Caption burn ke baad video re-encode hi hota hai (audio copy).

### [G14] qc-render board-based hai — asli video nahi dekhta
- Hua: board 60s bolti thi, video 63.6s tha — tool ne PASS diya.
- RULE: apne ffprobe checks HAMESHA: duration ±0.5s, video+audio
  dono streams, resolution 1080x1920, fps, codec h264/aac. 17-check
  QC honest notes ke saath PACKAGING stage pe chalao (stage filter
  samajh ke).

### [G15] Debugging hygiene (jo khud seekhna pada)
- Chhote repro pehle (1-2 inputs ka test), phir full graph.
- Apne test scripts ke indices/typo bhi galti karte hain — error ka
  FULL message padho (kata hua nahi), pattern EXACT match karo.
- Kabhi bhi "pass" dikhe to file ke khilaf independent check karo
  (musd vs raw levels jaise).

### [G16] Naming/cache + preview
- Final files VERSIONED naam lo (purana naam browser cache mein
  phas jata hai — operator ko purani file dikhti hai).
- Preview player 0.0.0.0 pe bind (BOOT.md law) aur hamesha LATEST
  final point kare.

----------------------------------------------------------------
## PART 3 — IRON LAWS (YEH 15 KABHI NA TOOTNA)

- **L1** Session start: `which ffmpeg` warna install; sources workspace
  mein; intermediates ko regenerate karna builders ka kaam hai.
- **L2** Ek ffmpeg command = max 10 inputs. Layered mixing hi
  architecture hai — giant single graph FORBIDDEN.
- **L3** Audio proof = speech-band (highpass 250) volumedetect,
  MULTIPLE windows, RAW take levels se ±6dB compare. Broadband akela
  jhoot bolta hai.
- **L4** VO pehli awaaz 0.00s pe; har window onset ≤0.3s; takes se
  leading silence hamesha trim.
- **L5** VO change → captions + timeline + music cues SAB regenerate.
- **L6** Captions word-level karaoke (amber active word) + .srt
  export — short-form pe captions optional nahi.
- **L7** Script to-the-point: 60-class short final 50–56s; har word
  kaam kare.
- **L8** Music 3-act hai (tension → flip impact → uplift), cues VO
  windows se; VO-forward mix (~1.2x voice) + sidechain ducking +
  -14 LUFS.
- **L9** Editing: 2–3s cuts, zoom motion har shot pe, impact kit
  flip pe, shine uplift pe, whoosh har cut pe (audible level!).
- **L10** Image/speech budgets (10/10 per turn) pehle se plan; batch
  banao.
- **L11** Visuals: house style + negative prompt (no text/
  photorealism); frames aankh se QC; thumbnails postage test (120px
  readable).
- **L12** Gates honest: idea/title gates, "haan" permission, 17-check
  QC packaging stage pe — khushi ke notes nahi.
- **L13** Apne ffprobe checks: duration ±0.5s, streams, resolution,
  codecs.
- **L14** Har layer ka checkpoint fail-closed: fail → STOP → fix →
  re-verify → tab aage. Operator ko hamesha sach report karo (jo
  fail hua wo chhupana bhi ek galti hai).
- **L15** Final versioned filename + preview player update + pack
  complete (video + .srt + listing + thumbnails) → phir present.

----------------------------------------------------------------
## PART 4 — FINAL DELIVERY CHECKLIST (SAB ✅ TABHI PRESENT KARNA)

- [ ] VO: 3 windows speech-band verified (start/mid/end) vs raw levels
- [ ] Onsets: clip 1 @ 0.00s + sab windows ≤0.3s
- [ ] Captions: word-sync frame aankh se QC (active word amber, sahi
      moment, safe zone) + .srt file hai
- [ ] Music: 3-act cue flip/uplift pe exact VO windows pe; bed VO
      gaps mein sunai de rahi hai
- [ ] SFX: cut pe whoosh clearly audible; flip impact; uplift shine
- [ ] Video: duration ±0.5s target, 1080x1920, 30fps, h264/aac, sab
      streams present
- [ ] Loudness: -14 LUFS master
- [ ] Thumbnails: 2 options, 120px postage test pass
- [ ] Listing: gate-passed title + description + tags + timestamps
- [ ] Preview player latest final pe; file versioned naam se
- [ ] Big intermediates delete; workspace clean

----------------------------------------------------------------
## RECONCILIATION — dono canons

- docs/RENDER_LAWS.md = render/QC jesta (journal session se); is doc
  ka L14 (fail-closed + sach report) aur RENDER_LAWS L15 (VERIFY THE
  VERIFIER) ek hi sicp hain: verify kiye hue pass ko andar se trust
  nahi — proof file ke khilaf dobara check.
- RENDER_LAWS L14 (RE-RECORD > RE-STRETCH) v2 ke G8/L4 ke sath khara
  hai: stretch se naya take behtar — aur naya take hamesha trim+onset
  verified.
- v2 L3 speech-band proof = broadband falsification ka ilaaj; Monarch
  in-repo previz mumble VO use karta hai, par audit checkpoint wahi
  band report karta hai jab mix report mojood ho.
