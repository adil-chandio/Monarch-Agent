# Fountain → M3_script

Monarch reads **Fountain** (`.fountain`, the plain-text screenplay format) at **M3_script**.
A real screenplay in, a gated numbered scene board out. No fake word counts, no padding.

```
monarch m3
monarch fountain script.fountain              # what does the parser see?
monarch screen-script script.fountain --length short --board-out board.json
```

## The M3 law

```
M3 deliverable: numbered scenes, quoted line, [n words] exact
STOP — WAIT: perfect | improve
```

| Rule | Where it lives |
| --- | --- |
| words/clip is fixed by the maths line | `monarch.core.scene_math.compute_math` |
| duration is `words / speaking_wps` (first clip clamped to `first_clip_s`) | `monarch.pipelines.fountain._duration` |
| too few words = **blocked**, never padded | `FountainBeat.issues` |
| every scene needs a visual + a retention job | `monarch.core.gates.gate_scenes` |
| beat count must equal `maths.scenes` | `monarch.pipelines.fountain.assert_gated` |
| visuals never count as spoken words | `::visual::` prefix is stripped before word-fit |
| no render, no VO, no upload | HAAN gate, unchanged |

`monarch screen-script` exit codes: `0` gated board + stop, `2` gate/input failure, `3` beats that
cannot hit the exact word count (`improve` territory).

## Supported Fountain

Scene headings (`INT.`/`EXT.`/`INT./EXT.`/`EST.`, `#n#` numbers at either end, forced with `.`),
action (forced with `!`), character cues (forced with `@`) with `(V.O.)` style extensions,
dialogue, parentheticals, dual dialogue (`^`), transitions (`CUT TO:`, forced `> CUT TO:`),
centered text (`> text <`), lyrics (`~`), sections (`#`), synopses (`=`), notes (`[[ ]]`),
boneyard (`/* */`), page breaks (`===`), escapes (`\`), and the title page
(`Title:`, `Credit:`, `Author:`, `Source:`, `Draft date:`, `Contact:`, `Copyright:`, `Notes:`, free keys).

Emphasis markers (`*`, `**`, `***`, `_`) and escapes are stripped from element text, because a
marker must never be spoken. Fountain's blank-line law is respected: a character cue needs a
non-empty next line (unless forced with `@`), and dialogue ends at a blank line.

## Monarch's one extension: `::visual::`

A spoken beat may carry its visual direction inline:

```
EXT. GLACIER - DAY #1#

VOICEOVER (V.O.)
::cracked glacier face:: The ice refused to melt for years
```

* `visual` = `cracked glacier face` → the scene board's visual + match-cut target
* the spoken line is `The ice refused to melt for years` → 7 words, exactly the maths count

## Length and maths

`--length` takes `short` (60s), `long` (480s) or raw seconds. The board is then:

```
60s | first clip 2.5s | body clips 3.5s | 18 scenes | 7 words/clip exact
```

At 60s that means **18 beats × 7 words**. Write them; never pad. If the board speaks less than the
requested length (e.g. 56.6s of 60s), the difference is stated so the editor can hold it for SFX and
silence beats.

Sources for `monarch screen-script`:

| Source | Command |
| --- | --- |
| `.fountain` file | `monarch screen-script script.fountain --length short` |
| paste / stdin | `cat script.fountain \| monarch screen-script --length short` |
| JSON board from an earlier run | `monarch screen-script board.json --length short` (beats are rebuilt from `vo_line`) |

Filters: `--only dialogue|action|both`, `--speaker MARA,JONAS`, `--visual-hint "stickman in a cave"`,
`--clip`, `--wps`, `--first-clip`, `--sfx`.

## Round trip

An approved board goes back out as Fountain, so a human writer (or the operator) can read the
screenplay form of what the board will say:

```
monarch screen-script script.fountain --board-out board.json
monarch script-fountain board.json --title "The ice that refused to melt" --out approved.fountain
monarch screen-script approved.fountain --length short      # identical board
```

`VOICEOVER (V.O.)` cues, inline `::visual::` lines and `[[sfx: ... | job: ...]]` notes survive the
round trip; SFX and retention jobs travel as notes so they never become spoken beats.

## Python

```python
from monarch.core.fountain import parse_file
from monarch.pipelines.fountain import beats_from_screenplay, build_script

sp = parse_file("script.fountain")
report = build_script(beats_from_screenplay(sp), 60.0)
print(report.summary())        # numbered scenes, quoted lines, exact counts
report.unfit                   # beats that need words — never autofixed
report.scenes                  # monarch.schemas.Scene clips for M4/M5
```

The parsed screenplay is kept on the project, so a rewrite never loses its lineage:

```python
from monarch.engine.project import Project

p = Project(channel=channel)
report = p.m3_from_fountain("script.fountain", 60.0, sfx="sub-hit")
p.dump("outputs/project.json")   # screenplay + maths + scenes
```
