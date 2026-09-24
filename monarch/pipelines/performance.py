"""YouTube Studio CSV/TSV ingest — the offline analytics loop (W1).

The API path is blocked in-sandbox; YouTube Studio's Advanced Mode export
(CSV/Sheets download) is not. This turns that export into
``PerformanceRecord`` entries so the learn loop runs on REAL numbers:
Views, Average Percentage Viewed, Subscribers, dates — the exact columns
the playbook's audit bands come from.

Fail-closed laws:
* unknown header (no recognized title/views/apv columns) -> ValueError
* a data row that fails record validation -> ValueError (with the row),
  except explicit skip-list (empty titles / "Totals" footer rows).
* percent strings ("12.4%"), thousands ("1,234") and h:mm:ss durations
  are normalized; garbage in REQUIRED columns is an error, not a zero.
"""

from __future__ import annotations

import csv
import io
from pathlib import Path

from monarch.core.learn import PerformanceRecord

_TITLE = {"video title", "content", "title", "video"}
_VIEWS = {"views", "video views"}
_APV = {"average percentage viewed", "avg percentage viewed",
        "average view percentage", "avg. percentage viewed",
        "average % viewed", "avg % viewed"}
_SUBS = {"subscribers", "subscribers gained"}
_DATE = {"date", "video published at", "publish date", "published at"}
_LENGTH = {"duration", "video duration", "length"}
_SKIP_TITLES = {"", "totals", "total"}


def _cell(row: dict[str, str], keys: set[str]) -> str:
    for k in keys:
        v = row.get(k)
        if v is not None and str(v).strip():
            return str(v).strip()
    return ""


def _num(raw: str) -> float:
    """'1,234' / '12.4%' / ' 987 ' -> float. Garbage raises ValueError."""
    s = raw.strip().strip('"').replace(",", "").replace("%", "").strip()
    if s.startswith("(") and s.endswith(")"):          # spreadsheet negative
        s = "-" + s[1:-1]
    return float(s)


def _duration_s(raw: str) -> float:
    """'3:25' / '1:02:30' / '45' -> seconds. Unparseable -> 0.0."""
    s = raw.strip().strip('"')
    if not s:
        return 0.0
    parts = s.split(":")
    try:
        nums = [float(p) for p in parts]
    except ValueError:
        return 0.0
    out = 0.0
    for p in nums:
        out = out * 60 + p
    return out


def _split_table(text: str) -> tuple[list[str], list[list[str]]]:
    """Sniff delimiter (tab > comma > semicolon) from the first line."""
    first = text.splitlines()[0] if text.splitlines() else ""
    delim = "\t" if "\t" in first else (";" if ("," not in first and ";" in first) else ",")
    rows = list(csv.reader(io.StringIO(text), delimiter=delim))
    rows = [[c.strip() for c in r] for r in rows if any(c.strip() for c in r)]
    if not rows:
        return [], []
    return rows[0], rows[1:]


def csv_records(text: str, *, cohort: str = "", note: str = "") -> list[PerformanceRecord]:
    """Studio export text -> validated PerformanceRecords (fail-closed)."""
    header, raw_rows = _split_table(text)
    norm = [h.lower().strip() for h in header]
    rows = [dict(zip(norm, r)) for r in raw_rows]
    if not rows:
        raise ValueError("no data rows found in the export")
    if not (_TITLE & set(norm) and _VIEWS & set(norm) and _APV & set(norm)):
        raise ValueError(
            "unrecognized export: need at least a title, views and "
            f"average-percentage-viewed column; header was {norm}")
    out: list[PerformanceRecord] = []
    for i, row in enumerate(rows, 2):
        title = _cell(row, _TITLE)
        if title.lower() in _SKIP_TITLES:
            continue
        views_raw, apv_raw = _cell(row, _VIEWS), _cell(row, _APV)
        if not views_raw or not apv_raw:
            raise ValueError(f"row {i} ({title[:40]!r}): missing views or avg % viewed cell")
        try:
            rec = PerformanceRecord(
                topic=title,
                views=_num(views_raw),
                avg_pct=_num(apv_raw),
                subs=int(_num(_cell(row, _SUBS) or "0")),
                cohort=cohort,
                length_s=_duration_s(_cell(row, _LENGTH)),
                date=_cell(row, _DATE),
                note=note or "studio-csv",
            )
        except ValueError as e:
            raise ValueError(f"row {i} ({title[:40]!r}): {e}") from e
        out.append(rec)
    if not out:
        raise ValueError("export had a header but zero usable video rows")
    return out


def ingest_csv(path: str | Path, *, cohort: str = "", note: str = "") -> list[PerformanceRecord]:
    """File wrapper around :func:`csv_records`."""
    text = Path(path).read_text(encoding="utf-8", errors="replace")
    return csv_records(text, cohort=cohort, note=note)
