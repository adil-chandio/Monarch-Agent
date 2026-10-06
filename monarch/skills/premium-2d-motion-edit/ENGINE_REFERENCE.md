# Premium 2D Motion Edit Engine — Style B technical reference

**Additive reference.** Style B is a sibling of Style A, not a replacement.
Nothing here changes Style A's files, prompts, or steps. This document defines
production requirements; it does not claim that Monarch already has a complete
renderer or audio-mix CLI for this engine. Verify the active project's actual
files before running a build command.

## 0. Style router

```text
if brief explicitly asks for character animation, walk cycle, gestures,
   consistent character, exact VO sync, frame-perfect timing, or no AI drift:
    choose Style B
elif brief asks for photoreal/illustrated scenes, many locations, fast, or cheap:
    choose Style A
else:
    choose Style A   # cheaper; escalate only when the brief demands it
```

- **Style A (existing, untouched):** make still images → compile → zoom,
  transitions, captions → export.
- **Style B (new):** draw every frame in Python + Pillow at **1080×1920**, then
  encode. No still-image assets. Use for deterministic character animation,
  repeatable house style, and exact picture/VO timing.

## 1. Premium is subtraction

The client rejected the denser version. Keep these laws:

1. Exactly **one motion-graphic cluster per scene**.
2. At most **three colours on screen**: paper, ink, one chapter accent.
3. Exactly **one transition type for the whole film**.
4. Character colours never change; only the world is chapter-themed.
5. If an element has no named job, delete it.

Restraint, a consistent grid, and continuous quiet motion read as premium;
density and neon do not.

## 2. Evidence loop

Use this order after each logical change:

```text
patch → assert the token changed → re-render → inspect the image → continue
```

- After every string replacement, assert that a token from the new text exists.
- After every logical change, render a probe and view it. Text diffs alone are
  not evidence that pixels changed correctly.
- For scene checks, build one **6×2 contact sheet** spanning all scenes. For
  character checks, build one **8-pose strip**. View both before proceeding.
- A stale helper call, wrong parameter name, or runtime-only geometry bug must
  be caught by rendering, not assumed away from a successful patch.

## 3. Forensics — measure the encoded deliverable

Run these checks on **every delivered file**. Do not substitute visual
impression for decoded measurements.

### 3.1 Video telemetry

Decode a small greyscale stream, then compute per-frame mean luma `luma` and
mean absolute frame difference `d`; `jerk = abs(diff(d))`:

```bash
ffmpeg -i out.mp4 -vf scale=216:384 -f rawvideo -pix_fmt gray /tmp/g.raw
```

```python
# a: decoded uint8 array, shape (frames, 384, 216)
a = np.memmap('/tmp/g.raw', dtype=np.uint8, mode='r').reshape(-1, 384, 216)
luma = a.mean(axis=(1, 2))
d = np.abs(a[1:].astype(np.int16) - a[:-1].astype(np.int16)).mean(axis=(1, 2))
jerk = np.abs(np.diff(d))
```

| Metric | Detects | Healthy target |
|---|---|---:|
| p10 of `d`, per scene | frozen portion of a scene | > 0.20 |
| global minimum `d` | dead frame | > 0.05 |
| runs of `d < 0.40` | retention-killing dead zones | none > ~0.5 s |
| p95 of `jerk`, per scene | snapping / unsettled reveals | < 2.0 |
| count of `abs(diff(luma)) > 8` | strobing | 0 |
| minimum `luma` | dark flash | within ~25 of mean |
| transition-energy peak vs cut frame | picture/audio misalignment | peak on cut, 0-frame offset |

Report the sampling, frame count, per-scene windows, and units alongside each
result; do not silently compare different scales or window sizes.

### 3.2 Audio telemetry

Use isolated PCM stems when comparing sources. For stereo `x`:

```python
L, R = x[:, 0], x[:, 1]
M = (L + R) / 2
S = (L - R) / 2
corr = np.corrcoef(L, R)[0, 1]
width = rms(S) / rms(M)
short_term_LUFS = -0.691 + 10 * log10(mean(M[w] ** 2))  # 400 ms window, 100 ms hop
band_share = abs(rfft) ** 2 summed per octave band / total
```

| Metric | Healthy target |
|---|---:|
| L/R correlation | 0.55–0.80 |
| side/mid energy | > 0.25 |
| 120–500 Hz share | < 58% |
| 1–4 kHz share | > 7% |
| 4–8 kHz share | > 10% |
| short-term minimum vs mean | within 9 LU |
| loudness range | < 16 LU |
| onset density | > 2 / s |
| largest onset gap | < 1.5 s |
| integrated loudness | −12 to −11 LUFS |
| true peak | ≤ −0.5 dBFS |
| VO vs bed during speech (separate stems) | +9 to +11 dB |

**Measurement trap:** never estimate VO/bed balance from the summed mix.
Transition impacts inside phrase gaps can make a sum-based comparison report a
misleading value. Render and meter the VO chain and bed as separate stems.

### 3.3 Design telemetry

Convert sRGB channels to linear light, then use WCAG relative luminance:

```python
def relative_luminance(c):  # sRGB -> linear; 0.2126 R + 0.7152 G + 0.0722 B
    ...
def contrast(a, b):
    return (max(La, Lb) + 0.05) / (min(La, Lb) + 0.05)
```

- Every accent/background pair: **≥ 4.5:1**.
- Every text-on-fill pair, including CTA text: **≥ 4.5:1**.
- Measure every text baseline against the platform safe area.

## 4. Platform grid, contrast, and transitions

### 4.1 Safe area

For a 1080×1920 short, all content must remain in **`y ∈ [180, 1500]`**.
The upper and lower regions are reserved for platform UI, even when the editor
preview looks clear.

```text
0–180       DEAD — platform chrome
142–210     progress hairline + “01 / 06  CHAPTER”
300–520     headline, max two lines
560–1060    exactly one graphic cluster
1060–1298   stage; ground line GY = 1298
1340–1408   payoff; PAY_Y = 1374
1430–1476   caption; CAP_Y = 1452
1500–1920   DEAD — platform chrome
```

The supplied grid lists the chapter hairline at y=142–210, which conflicts
with the stricter hard safe-area floor of y=180. Treat y=142–179 as dead: keep
all visible pixels of the hairline and label at y≥180 (move the header down
within 180–210 if necessary). The hard safe-area law wins over the example
position. When compressing the rest of the grid, scale the character too (×0.84
in the supplied fit) and re-anchor props positioned from the former ground line.
Re-audit all scenes after any character scale or layout change.

### 4.2 Accent contrast

The original light-background accents failed 4.5:1 on cream `(248,244,233)`;
white type on the original gold CTA was only 2.39:1. Use a dark text/accent set
on light backgrounds and a separate brighter set for dark panels:

```python
ACC = [
    (178, 44, 32), (28, 82, 190), (86, 54, 194),
    (166, 74, 14), (14, 112, 80), (146, 100, 12),
]
ACC_HI = [tuple(min(255, int(c * 1.34 + 22)) for c in a) for a in ACC]
```

Reference contrast against cream for `ACC`: **5.84 / 6.37 / 7.07 / 5.30 /
5.54 / 4.72**. White on the dark gold CTA: **5.18:1**. Recompute for actual
backgrounds and text; never assume a set passes on a changed paper colour.

### 4.3 One restrained transition

A full-bleed saturated panel caused large luma crashes (e.g. 222 → 92 → 227)
and visible flashes. Tint the paper; keep only a narrow saturated leading edge:

```python
tint = 0.18 * accent + 0.82 * paper   # body; luma stays near paper
glow = 0.40 * accent + 0.60 * paper  # feather
```

Layer the moving edge bottom-to-top:

```text
H*0.044 .. H       tint
H*0.026 .. 0.044   glow
H*0.007 .. 0.026   full accent, thin leading band
H*0.000 .. 0.007   INK hairline, crisp edge
```

- Centre the transition on cut `c`: `c − TDUR/2` to `c + TDUR/2`; the
  full-cover frame lands exactly on the cut/beat and VO start.
- Freeze the outgoing scene while progress `p < 0.5`.
- Use `TDUR = 0.46 s`; use `TLAG ≈ 0.050 s` where measured picture peaks
  precede the audio hit by 1–2 frames.
- Reference improvement: luma swing −131 → −13 and large luma jumps 49 → 0.
  Confirm the edge still reads hard, luma remains near paper, and no decoded
  frame has `abs(Δluma) > 8`.

## 5. Character system — depth, not a flat puppet

### 5.1 Body coordinates and projection

Body-space origin is hip centre: `x` screen-right, `y` down, `z` toward camera.
Resolve each limb segment from frontal abduction and sagittal swing:

```python
def _dirv(abd, swing):
    a, w = radians(abd), radians(swing)
    return (cos(w) * sin(a), cos(w) * cos(a), sin(w))
```

Use a long lens, so depth reads without distortion:

```python
F = 4.2 * s                 # focal length in body-height units
k = F / (F - z)             # per-joint scale
screen = (ox + x * k, oy + y * k)
```

Multiply limb radii by the same `k`. A hand reaching toward the lens should
grow about 8%, not stay the same size.

### 5.2 Joints, sorting, and aerial perspective

- Elbows flex **forward only**: `forearm_swing = arm_swing + max(0, elbow_flex)`.
- Knees flex **backward only**: `shin_swing = thigh_swing - max(0, knee_flex)`.
- Sort the groups left arm, right arm, left leg, right leg, torso, head by `z`.
  Within each group: draw all silhouettes expanded in outline colour, then all
  fills, avoiding seams at elbows/knees. Composite groups in depth order.
- Shade by depth: `k = 1 + 0.26 * (z / s)`; multiply RGB by `k` and clamp.
  Behind is darker; foreground is lifted.

### 5.3 Three-quarter view

Apply global yaw before projection so sagittal motion reads as horizontal
travel instead of invisible overlapping/scissoring:

| Action | yaw |
|---|---:|
| idle | 14° |
| walk | 27° |
| think | 20° |
| sit_type | 18° |
| shake | 23° |
| point | ±16° |
| dance | ±10° |
| present | 4° |

Shift eyes by `sin(yaw) * 0.34`. Do not exaggerate it; `1.05` made a lazy-eye
look.

### 5.4 Pose biomechanics and channels

- **Idle / contrapposto:** weight on one leg lifts that hip; pelvis sways over
  support; shoulders counter-tilt; spine forms a shallow S; unloaded knee is
  soft; drift weight over a ~6.8 s cycle. Arms retain a ~13° carrying angle.
- **Walk / two-beat gait:** legs swing ±27° in the sagittal plane; pelvis
  `+7.5*sin(phase)`; shoulders counter-rotate `−7.5*sin(phase)`; arms swing
  opposite their own leg. Knee flex: `7 + 52*max(0, sin(q + 2.0))**1.6`
  degrees. Body bob: `_bob = 0.020*abs(cos(phase)) - 0.008`.
- **Think:** hand to chin, opposite arm folded beneath to support the elbow.
- **Shake:** reach out of frame toward the other person, using depth.
- **Type / sit_type:** forearms come toward the camera.
- **Dance:** hips lead; shoulders follow with `sin(ph - 0.6)`.
- **Shrug:** raised shoulders, elbows pinned to ribs, palms up.

Pose channels: `yaw, lean, twist, pelvis, tilt, sway, sh_up, head, head_t,
 al/ar (arm abduction), az_l/az_r (arm swing), el/er (elbow in-plane),
 ef_l/ef_r (elbow flexion), ll/lr, lz_l/lz_r, kl/kr, hl/hr (hand shape),
 _bob, _br, _hv`.

Use plain world angles: 0 = down; positive = screen `+x`; write left/right
explicitly. A shared `±1` side multiplier cannot express asymmetric walk poses.
Never feed one rig's pose dictionary to another rig.

### 5.5 Foot direction and grounding

For the signed toe direction `T`, the heel is always behind it:

```python
heel = fx - T * 0.44  # correct: opposite the signed toe direction
```

Do not mix `abs(T)` with a signed multiplier in the same foot shape. Use the
full heel-back → heel-top → instep → toe-top → toe-front → toe-ground →
heel-ground profile; roll around the ankle by
`clamp(shin_sagittal_angle * 0.62, -26°, +26°)`.

For grounding, project both ankles and soles inside the renderer, find the
lower sole, then shift the figure until it touches the ground line. A flat-rig
analytic `foot_drop()` is not sufficient under perspective. Regression-test
`foot_drop == 0.0` for every standing pose.

### 5.6 Craft details

| Symptom | Required treatment |
|---|---|
| Hand becomes a black blob | hand fill `(41,36,31)`; crease `(132,122,112)` at `0.58·ow` |
| Finger circles weld into a mitten | one scalloped/notched polygon; thumb is a separate capsule |
| Fingers vanish or clip thighs | hand size `0.040·s` |
| Shoulder or knee shows a step | deltoid cap at shoulder; patella disc at knee |
| Head is bolted to collar | tapered capsule from shoulder centre to head base |
| Cuff reads as chest paint | draw it inside that arm's depth group, perpendicular to its forearm |
| Shirt is a flat silhouette | shirt hem; knee crease above 14° flex; inner-elbow wrinkles above 35° |
| Face looks plastic | seven warm ellipses at 6% alpha across lower skull |
| Figure floats | soft blob plus tighter, darker hard-contact core under soles |

### 5.7 Rendering implementation laws

- Grow the outline by stroking the closed perimeter at `2*ow` with curved
  joins, then fill. Per-shape dilation is not a substitute.
- For capsules, compute one `atan2` angle and sweep each end cap by π; never mix
  angle bases between cap points.
- Clip shading to an eroded mask, not raw alpha:
  `alpha.blur(ow*1.15).point(v > 248) × alpha`. Draw face details after
  shading so eyes and mouth stay dark.
- `ImageChops.offset` wraps. Use only when the figure cannot touch the tile
  edge, and re-multiply every shifted layer by its mask.

### 5.8 Pure secondary motion

All motion must be a pure function of absolute time so independent render shards
are identical at their seam:

```python
def phys(fn, t, **kw):
    p, pl, pm = fn(t), fn(t - 0.070), fn(t - 0.035)
    out = dict(p)
    for k in ('el', 'er', 'kl', 'kr'):
        out[k] = pl[k]                         # limb lag: 70 ms
    out['head'] = 0.55*p['head'] + 0.45*pm['head']
    out['_hv'] = (pm['head'] + pm['lean']) - (p['head'] + p['lean'])
    out['_br'] = sin(t * 2.05)                 # breathing ~0.33 Hz
    return out
```

`_br` changes torso width by `1 + 0.020*_br`. `_hv` swings hair tips, clamped
to ±`0.42·rx`, with roots fixed. No hidden mutable state, random stepping, or
frame-index accumulation.

## 6. Motion graphics and editing

### 6.1 Continuous, restrained movement

Nothing revealed should become perfectly still. Apply deterministic
phase-offset float to every revealed prop group:

```python
def fl(t, i=0, a=5.0, w=1.0):
    return sin(t*(0.78*w) + i*1.37)*a + sin(t*(1.23*w) + i*0.61)*a*0.42
```

Use on checklist rows, calendar blocks, sample cards, tick rows, and similar
revealed groups. A prior scene's frame-difference p10 improved from 0.06 to
0.22–0.47 with micro-float; remeasure on the active film.

### 6.2 Sub-pixel camera

Never quantize an animated zoom into an integer crop (`int(W*z)`); that can
produce byte-identical frames. Resample the full canvas using float offsets:

```python
iz = 1.0 / z
ox = (W - W*iz) * 0.5 + drift_x
oy = (H - H*iz) * 0.5 + drift_y
frame = frame.transform((W, H), Image.AFFINE,
                        (iz, 0, ox, 0, iz, oy), Image.BICUBIC)
```

Use two incommensurate sine drifts. Validate that frames keep moving and no
animated value stalls after integer conversion.

### 6.3 Camera and reveal discipline

- Per-scene push amplitudes: `(.026, .034, .020, .038, .028, .042)`; alternate
  direction by scene parity.
- Arrival settle: `exp(-lt*6.4) * sin(lt*16.5) * 0.0052`.
- **Never use camera shake.**
- Use `e_back(x, s=1.12)` (overshoot reduced from `s=1.5`):
  `1 + (s+1)*(x-1)**3 + s*(x-1)**2`, with clamped `x`.
- Word stagger: 0.30 (not 0.45); word ramp: 0.72 (not 0.55).
- Rise easing uses `e_out(p, 2.2)`, not `e_out(p, 3.2)`.
- Reveals settle rather than snap; remeasure per-scene p95 jerk (<2.0).
  Reference worst-scene jerk improved 4.13 → 1.62.

### 6.4 Type and emphasis

Extrude larger display type toward the light; captions get no extrusion:

```python
def _ext_col(col):
    if sum(col) < 220:
        return (201, 193, 177)             # warm emboss under near-black ink
    return tuple(int(c * 0.50) for c in col)

ex = int(sz / 15) if sz >= 68 else 0
for k in range(ex, 0, -1):
    draw.text((cx + k*0.54, y + dy + k*0.64), word,
              font=f, fill=ext_colour)
draw.text((cx, y + dy), word, font=f, fill=face_colour)
```

Ink needs a light emboss; a dark extrusion under near-black ink disappears.
The highlighted keyword lands 8.5% oversized then settles to 100%, including
its extrusion:

```python
k = 1.0 + 0.085 * (1 - e_out(word_progress, 2.0))
font = F(int(sz * k), weight)
```

The integer font-size call is a raster-resolution example, not permission for a
frame to stall. If adjacent frames quantize to the same glyph size, draw a fixed
high-resolution glyph layer and apply the animated `k` through a floating-point
transform before downsampling; verify adjacent frames are not byte-identical.

### 6.5 CTA and particles

- CTA sheen: diagonal soft-white sweep on a 1.6 s cycle; 11 feathered strokes,
  each ≤18% alpha, slanted ~13° off vertical. Check the text/fill contrast too.
- Celebration particles: 26 pieces, three shapes (rect/ribbon/disc), accent +
  ink only. Tumble each in 3D with
  `squash = abs(cos(t*rate + i))`, height × `(0.34 + 0.66*squash)`; fast
  pieces get a low-alpha speed streak. Do not use a rainbow.
- Recheck collisions after every scale/layout change; vertical-grid discipline
  prevents systemic text/character overlaps.

## 7. Audio design and mix

### 7.1 Width belongs in the bed; keep VO centred

A centred mono VO can swamp a carefully panned bed. Widen the **bed stem before
the sum**, and keep the voice centred:

```python
M_ = (mix[0] + mix[1]) * 0.5
S_ = (mix[0] - mix[1]) * 0.5
S_ = bandpass(S_, 150, 16000) * 3.30
mix = [M_ + S_, M_ - S_]
```

Reference result: correlation 0.9941 → 0.7547; side/mid 0.054 → 0.374.
Measure the actual result; do not promise those numbers for another source.

### 7.2 Spectrum and speech clarity

Reference starting spectrum was mud-heavy: 120–500 Hz 66.75%, 1–4 kHz
5.76%, and 8–16 kHz 0.60%. Reference improvements:

- Bus low-pass 8.2 kHz → 14.5 kHz; add `bandpass(6500, 17000) * 0.95`
  air on the sum.
- VO EQ: −4.2 dB @ 250 Hz (Q 1.0), −1.6 dB @ 430 Hz, +3.6 dB @
  3100 Hz, +2.8 dB shelf @ 7400 Hz.
- Final sum: +3.4 dB shelf @ 9000 Hz.
- Target reference shifts: 120–500 Hz 66.8% → 57.7%; 4–8 kHz 8.3% → 10.7%.
  Still check the actual spectrum; 1–4 kHz target is >7%.

### 7.3 Keep the mix alive without pumping

- Sidechain: ratio 5:1 (not 18:1), threshold 0.024 (not 0.014), release
  260 ms (not 360 ms).
- Bed 0.60 (not 0.40); VO 1.92 (not 2.15).
- Place 12 pad swells on **measured** holes, not guessed ones. Reference
  swell: 146.8 / 220 / 293.7 / 440 / 587.3 Hz plus a 1.004 detune layer;
  `sin(π·t/T)^1.6` envelope; 2.6 s; bandpass 70–2600 Hz; right channel
  rolled 331 samples for width.
- Reference improvement: holes 12 → 4; short-term minimum −32.4 → −27.3 LUFS;
  loudness range 20.9 → 15.2 LU. Report the active render's actual numbers.

### 7.4 Cue bus and ledger

- Dual bus: music stays dry; cues use the plate. Never send the chord bed to
  the cue reverb.
- `silk()` cue plate: 12 prime-spaced taps from 0.0131 to 0.4523 s, gains
  0.50 → 0.030, alternating 62/38 pan, 220 Hz–5.2 kHz, 34% wet.
- Percussive attacks ≥8 ms (pop 9 ms, tap 8 ms, thud 10 ms).
- Soft knee: `tanh(x*1.05) * 0.74`.
- Six-event cut stack: riser `c−0.84`, whoosh-in `c−0.16` (pan −0.55),
  thud and sub at `c`, chime `c+0.03`, whoosh-out `c+0.20` (pan +0.55).
- One chord per chapter; sub pulse every second beat; noise room floor ≈−42 dB.
- Keep an event ledger CSV (`t,tag,gain,pan`) for every cue.

### 7.5 Implementation cautions and target mux

- Do not Python-loop an IIR over 1.7M samples; use FFT magnitude shaping per
  short grain.
- Some FFmpeg builds abort on `asplit` → `anullsink`; duplicate the filter
  chain instead of discarding a split branch.
- Meter with `ebur128`; normalize to `loudnorm=I=-11:TP=-1.0:LRA=9`, then
  `alimiter=limit=0.97`.
- For an audio-only revision, copy video (`-c:v copy`) when the source video is
  already final and unchanged; do not needlessly re-encode it.

Target audio graph (adapt only after validating available stems and FFmpeg
filters):

```text
[6 VO inputs] atempo=per-scene,aresample=48000,stereo,adelay=per-scene
6× amix=inputs=6:normalize=0,
   highpass=f=90,
   equalizer=f=250:t=q:w=1.0:g=-4.2,
   equalizer=f=430:t=q:w=1.4:g=-1.6,
   equalizer=f=3100:t=q:w=1.3:g=3.6,
   treble=g=2.8:f=7400,
   acompressor=threshold=0.045:ratio=3.6:attack=10:release=170:makeup=1.5,
   volume=1.92 -> VO stem
bed volume=0.60; sidechaincompress threshold=0.024:ratio=5:attack=6:release=260
VO stem + bed stem -> amix -> treble=g=3.4:f=9000
-> loudnorm=I=-11:TP=-1.0:LRA=9 -> alimiter=limit=0.97
```

Final target: H.264 High@4.0, 1080×1920, 30 fps, yuv420p, `+faststart`,
AAC 192k/48 kHz, exact duration; video `libx264 -preset slow -crf 23`,
2800k maxrate / 5600k bufsize. Confirm mux/filter support in the actual
FFmpeg build.

## 8. Timing contract

Lock before the first frame. This supplied 37-second contract is immutable
unless the approved duration changes; if it changes, re-fit each scene's VO
rate independently.

```text
TEMPO = 1.45
RAW   = [7.13, 10.15, 9.31, 6.40, 9.02, 8.33]
LEAD  = 0.30

S  start    end     dur    voAt     f0   f1    nf
1  0.000   5.567   5.567   0.300     0   166  167
2  5.567  12.867   7.300   5.617   167   385  219
3 12.867  19.588   6.721  12.917   386   587  202
4 19.588  24.302   4.714  19.638   588   728  141
5 24.302  30.823   6.521  24.352   729   924  196
6 30.823  37.000   6.177  30.873   925  1109 185
                                     sum nf = 1110
SPB = 0.535714 s (112 BPM)
VO atempo/adelay:
  1.446/300 · 1.351/5617 · 1.441/12917 · 1.525/19638 · 1.484/24352 · 1.487/30873
```

The picture's transition window is centred on the cut, and the picture-energy
peak must land on the audio impact frame. Do not trim or cross-fade to fake a
fit.

## 9. Build and environment constraints

- Use two parallel shards on two cores when supported; encode each shard to
  MP4 inline (raw-frame shards can require ~3.4 GB each). Reference cost is
  about 0.17–0.25 s/frame at 1080×1920 on two cores; measure the active host.
- Concatenate encoded shards with FFmpeg concat and stream-copy when compatible.
- All animation functions must be pure functions of absolute `t`; shard seam
  frames must be bit-identical.
- Long renders belong in a background process. Do not use a shell call with a
  30-minute cap, and do not pipe a long render through `tail` (it buffers).
- `ffprobe` may not be available with `imageio_ffmpeg`; inspect with the actual
  bundled `ffmpeg -i file 2>&1 | grep -E "Duration|Stream"` when needed.
- `/tmp`, installed packages, and build directories may not persist between
  sessions; recreate them. Verify dependencies rather than assuming.
- For code edits, inspect long files in bounded slices (`sed -n 'A,Bp'`);
  `cat -n` can truncate. Put multiline Python in a script/heredoc rather than
  an f-string containing a literal source newline.
- Do not claim source paths or build commands exist until checking the active
  repository. This reference's timing/filters are not a Monarch CLI contract.

## 10. Rejected designs

Do not re-propose:

- Hoodie as a closed trapezoid.
- Outlined circle + pupil eyes.
- Filled rectangle collar.
- Mitten hands.
- Mono SFX.
- Five transition types in one film.
- Flat chalk-line stickman (client explicitly rejected it).
- High element density (client explicitly rejected it).

## 11. QA gate — no ship on a failure

### Container

- [ ] Exact duration to the frame.
- [ ] 1080×1920, 30 fps, yuv420p, H.264 High@4.0, `+faststart`.
- [ ] `ffmpeg -v error -f null -` decodes with zero errors.
- [ ] Frame 0 is not black: check mean luma and bright-pixel count (thumbnail).

### Design

- [ ] All content inside y=180…1500.
- [ ] Every accent/background and text/fill pair ≥4.5:1.
- [ ] No more than three colours on screen.
- [ ] Exactly one motion-graphic cluster per scene.
- [ ] Character colours are identical in every scene.

### Motion

- [ ] Zero frames with `abs(Δluma)>8`; darkest frame within ~25 of mean.
- [ ] Every scene's p10 frame-diff >0.20; global minimum >0.05.
- [ ] Every scene's p95 jerk <2.0.
- [ ] Transition-energy peak is on the cut frame, not before it.
- [ ] No text/character collision in any scene.
- [ ] `foot_drop == 0.0` for each standing pose.

### Audio

- [ ] L/R correlation 0.55–0.80; side/mid energy >0.25.
- [ ] 120–500 Hz share <58%; 1–4 kHz share >7%.
- [ ] Short-term minimum within 9 LU of mean; loudness range <16 LU.
- [ ] Integrated −12 to −11 LUFS; true peak ≤−0.5 dBFS.
- [ ] Separate-stem VO vs bed is +9 to +11 dB during speech.

A failed or unmeasured gate is a stop-and-fix, not a waived condition.

## 12. Delivery artifacts

Ship alongside each Style-B video:

1. MP4 with recorded SHA-256 prefix.
2. `VIDEO_Vn_NOTES.md`: changes with before → after numbers.
3. `FORENSIC_AUDIT.md`: measured defect list for the next pass.
4. Character-sheet PNG: front views, expressions, pose studies.
5. ASMR event-ledger CSV.
6. QA contact sheet: 6×2 frames spanning all scenes.
7. Restore points for every rewritten source file (`*_backup.py`).

Only include assets that were actually generated, measured, and inspected.

## 13. Ten laws

1. Measure; never eyeball. Decode the delivered file and run telemetry.
2. Check safe area first: y=180…1500.
3. Measure every colour pair; large type can hide small-type failures.
4. Tint transitions; never flood. Luma must not crash.
5. Animate in depth; a flat rig stays a puppet.
6. Clamp every joint: elbows forward only, knees backward only.
7. Nothing is perfectly still; no animated value may quantize through `int()`.
8. Keep VO centred and the ASMR bed wide.
9. Fill measured loudness holes; do not let the mix breathe out.
10. Premium is subtraction; when in doubt, delete it.
