# RENDER LAWS — 15 Permanent Qanoon (Production-Forged)

Source: the "Log kya kahenge? 3 second test" production journal (v1→v7,
31 bugs, 2 rebuilds) — operator Adil Chandio + Monarch, 2026-09-24.
Every law below was paid for with a real bug. Bug badges reference the
journal's master table. L14/L15 added by the cross-session forensic audit
(same lessons, independently derived).

| # | Law | Badge |
|---|---|---|
| 01 | **VERIFY-FIRST** — automated proof before any deliverable: volumedetect windows, pixel classifiers, ffprobe. Kaan/aankh + instrument dono. | #12 #14 #26 |
| 02 | **REAL-FORMAT TESTING** — filter behavior ko ASLI pipeline ke pixel-format me test karo. RGB isolation pass + real YUV build = 8.5% olive. `darken` ka matlab format decide karta hai. | #25 |
| 03 | **TEMPLATE-PATCHING** — replace needle source ke ACTUAL form se match karo (f-string TEMPLATE), rendered VALUE se nahi. 0-replacements = galat needle. | #22 #24 |
| 04 | **OVERLAY BIRTH+DEATH** — har text/graphic `between(t,t0,t1)`. `gte` = FOREVER ON = stain. Aur: ek waqt = ek instance (linger tail 0.06s law). | #18 #29 |
| 05 | **COMPRESSED TIMELINE** — overlaps (xfade) ho to delays COMPRESSED (post-transition) starts se compute karo, grid values se nahi. | #11 |
| 06 | **RAM BUDGET** — inputs × nodes pehle gino. Archive-scale = multi-pass (crf15 master → split overlays). Empty-stderr SIGKILL = memory ka pehla shak. | #28 |
| 07 | **AI TIMING > MATH TIMING** — speech sync = asli audio timestamps (whisper/CPU-int8 proved). Act-block uniform math = robot rhythm. Monarch L1 ka render-side twin. | #19→v7 |
| 08 | **ACCENT = REGION TAG + AUDITION** — language tag ≠ accent. `ur-PK` for Desi audience; artist sun kar lock karo. | #09 |
| 09 | **STATELESS SANDBOX** — assets workspace me, power scripts (rebuild) me, repo lean (≤128MB cap). Artifact mat bachao, RECIPE bachao. | #13 #30 |
| 10 | **FIX CHECKLIST** — naye script me PURANE saare fixes port karo. S[18] do baar mara kyunki checklist nahi thi. | #16 #31 |
| 11 | **LIMITS = HONESTY** — caps (10 images/turn) pe reuse-map + honest log. Kabhi fake padding nahi. Too few = improve. | #04 |
| 12 | **OPERATOR = GROUND TRUTH** — har complaint → forensic root-cause. 3 sabse bade bugs (accent, silent audio, sync chaos) operator ke kaan/nein pakde. | #09 #11 #14 |
| 13 | **PROBE > ASSUME** — structures (list≠dict), filter vars (zoompan `on` not `t`), color spaces, cwd — run-time confirm. | #03 #10 #27 |
| 14 | **RE-RECORD > RE-STRETCH** — voice fit nahi hui to dobara record karo (voice-03 proved). Tempo stretch sirf aakhri ~5–8% ka temporary fix; 1.147× = JUGAAD tha, design nahi. | #07 #12 |
| 15 | **VERIFY THE VERIFIER** — QC instrument ki pehli test uski khud ki hoti hai. Olive-classifier me r≈g assumption fail hua; detector ko honestly rewrite kiya. Known-bad sample har naye detector ko do. | #26 |
