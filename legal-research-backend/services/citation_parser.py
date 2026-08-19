"""Bluebook-ish citation extraction for public-source verification."""

from __future__ import annotations

import re
from typing import Any

# Capitalized party names only. A looser class that allowed "." and IGNORECASE
# swallowed the preceding sentence ("to arrest is... Chimel v. California").
_PARTY = (
    r"(?:In re\s+)?[A-Z][A-Za-z0-9'&.-]*(?:\s+(?:[A-Z][A-Za-z0-9'&.-]*|of|the|and|for|a|an))*"
)
CASE_FULL_RE = re.compile(
    r"(" + _PARTY + r"\s+v\.\s+" + _PARTY + r"),\s+"
    r"(\d+)\s+((?i:U\.S\.|S\.\s*Ct\.|F\.(?:2d|3d|4th)|F\.\s*Supp\.(?:\s*[23]d)?))\s+(\d+)"
    r"(?:\s+\((?:([^)]+?)\s+)?(\d{4})\))?",
)

REPORTER_RE = re.compile(
    r"(\d+)\s+(U\.S\.|S\.\s*Ct\.|F\.(?:2d|3d|4th)|F\.\s*Supp\.(?:\s*[23]d)?)\s+(\d+)"
    r"(?:\s+\((?:([^)]+?)\s+)?(\d{4})\))?",
    re.IGNORECASE,
)

STATUTE_RE = re.compile(
    rf"(\d+)\s+U\.S\.C\.\s*\u00a7+\s*([\dA-Za-z()-]+)",
    re.IGNORECASE,
)

FRCP_RE = re.compile(
    r"Fed\.\s*R\.\s*(Civ|Crim)\.\s*P\.\s*(\d+[a-z]?)",
    re.IGNORECASE,
)

CONST_RE = re.compile(
    r"U\.S\.\s*Const\.\s*(?:amend\.|amendment)\s*([IVXLCDM]+|\d+)",
    re.IGNORECASE,
)

DOCKET_RE = re.compile(
    r"((?:In re\s+)[A-Za-z0-9 .,'&-]{5,90}),\s+No\.\s+([A-Za-z0-9:-]+)"
    r"(?:\s+\(([^)]+)\))?",
)

AMBIGUOUS_RE = re.compile(
    r"\b([A-Z][A-Za-z.'-]{1,40}),\s+(\d+)\s+(U\.S\.|S\.\s*Ct\.|F\.(?:2d|3d|4th))(?!\s+\d)",
)

_SENTENCE_SPLIT = re.compile(r"(?<=[.\n])\s+")


def _norm_reporter(value: str) -> str:
    text = re.sub(r"\s+", " ", value).strip()
    text = text.replace("S. Ct.", "S. Ct.").replace("S.Ct.", "S. Ct.")
    if re.match(r"F\.\s*Supp", text, re.I):
        text = re.sub(r"F\.\s*Supp\.\s*", "F. Supp. ", text, flags=re.I).strip()
        text = re.sub(r"\s+", " ", text)
    return text


def _key(volume: str, reporter: str, page: str | None) -> str:
    if not page:
        return f"{volume} {_norm_reporter(reporter)}"
    return f"{volume} {_norm_reporter(reporter)} {page}"


def _overlaps(start: int, end: int, occupied: list[tuple[int, int]]) -> bool:
    for left, right in occupied:
        if start < right and end > left:
            return True
    return False


def _court_from_parenthetical(value: str | None) -> str | None:
    if not value:
        return None
    cleaned = re.sub(r"\s+", " ", value).strip(" ,")
    return cleaned or None


def extract_proposition(text: str, span: str) -> str | None:
    if not text or not span:
        return None
    idx = text.find(span)
    if idx == -1:
        return None
    before = text[:idx]
    stripped_before = before.rstrip()
    if stripped_before.endswith("."):
        period = text.rfind(". ", 0, max(len(stripped_before) - 1, 0))
        newline = text.rfind("\n", 0, len(stripped_before))
        start = max(period, newline)
        start = 0 if start < 0 else start + (2 if period == start else 1)
        sentence = text[start : len(stripped_before)].strip().strip(".")
        return re.sub(r"\s+", " ", sentence)[:500] or None
    start = text.rfind("\n", 0, idx)
    period = text.rfind(". ", 0, idx)
    start = max(start, period)
    start = 0 if start < 0 else start + (2 if period == start else 1)
    end = text.find(". ", idx + len(span))
    newline = text.find("\n", idx + len(span))
    candidates = [value for value in (end, newline) if value != -1]
    stop = min(candidates) if candidates else len(text)
    sentence = text[start:stop].strip().strip(".")
    return re.sub(r"\s+", " ", sentence)[:500] or None


def parse_citations(text: str) -> list[dict[str, Any]]:
    found: list[dict[str, Any]] = []
    occupied: list[tuple[int, int]] = []
    seen: set[str] = set()

    def push(item: dict[str, Any], start: int, end: int) -> None:
        raw = re.sub(r"\s+", " ", item.get("raw") or "").strip()
        if not raw:
            return
        dedupe = item.get("key") or raw
        if dedupe in seen or _overlaps(start, end, occupied):
            return
        seen.add(dedupe)
        occupied.append((start, end))
        item["raw"] = raw
        item["span"] = text[start:end]
        item["start"] = start
        item["end"] = end
        item["proposition"] = extract_proposition(text, item["span"])
        found.append(item)

    for match in CASE_FULL_RE.finditer(text):
        volume, reporter, page = match.group(2), _norm_reporter(match.group(3)), match.group(4)
        year = int(match.group(6)) if match.group(6) else None
        push(
            {
                "kind": "case",
                "parties": match.group(1).strip(),
                "volume": volume,
                "reporter": reporter,
                "page": page,
                "year": year,
                "court_hint": _court_from_parenthetical(match.group(5)),
                "key": _key(volume, reporter, page),
                "raw": match.group(0),
            },
            match.start(),
            match.end(),
        )

    for match in STATUTE_RE.finditer(text):
        title, section = match.group(1), match.group(2)
        push(
            {
                "kind": "statute",
                "title": int(title),
                "section": section,
                "volume": title,
                "reporter": "U.S.C.",
                "page": section,
                "year": None,
                "parties": None,
                "key": f"{title} U.S.C. § {section}",
                "raw": match.group(0),
            },
            match.start(),
            match.end(),
        )

    for match in FRCP_RE.finditer(text):
        suite, number = match.group(1).title(), match.group(2)
        push(
            {
                "kind": "rule",
                "rule_suite": suite,
                "rule_number": number,
                "volume": None,
                "reporter": f"Fed. R. {suite}. P.",
                "page": number,
                "year": None,
                "parties": None,
                "key": f"Fed. R. {suite}. P. {number}",
                "raw": match.group(0),
            },
            match.start(),
            match.end(),
        )

    for match in CONST_RE.finditer(text):
        amendment = match.group(1).upper()
        push(
            {
                "kind": "constitution",
                "amendment": amendment,
                "volume": None,
                "reporter": "U.S. Const.",
                "page": amendment,
                "year": None,
                "parties": None,
                "key": f"U.S. Const. amend. {amendment}",
                "raw": match.group(0),
            },
            match.start(),
            match.end(),
        )

    for match in DOCKET_RE.finditer(text):
        push(
            {
                "kind": "docket",
                "parties": match.group(1).strip(),
                "docket": match.group(2),
                "court_hint": _court_from_parenthetical(match.group(3)),
                "volume": None,
                "reporter": None,
                "page": None,
                "year": None,
                "key": f"No. {match.group(2)}",
                "raw": match.group(0),
            },
            match.start(),
            match.end(),
        )

    for match in REPORTER_RE.finditer(text):
        volume, reporter, page = match.group(1), _norm_reporter(match.group(2)), match.group(3)
        year = int(match.group(5)) if match.group(5) else None
        push(
            {
                "kind": "case",
                "parties": None,
                "volume": volume,
                "reporter": reporter,
                "page": page,
                "year": year,
                "court_hint": _court_from_parenthetical(match.group(4)),
                "key": _key(volume, reporter, page),
                "raw": match.group(0),
            },
            match.start(),
            match.end(),
        )

    for match in AMBIGUOUS_RE.finditer(text):
        volume, reporter = match.group(2), _norm_reporter(match.group(3))
        push(
            {
                "kind": "ambiguous",
                "parties": match.group(1),
                "volume": volume,
                "reporter": reporter,
                "page": None,
                "year": None,
                "key": _key(volume, reporter, None),
                "raw": match.group(0),
            },
            match.start(),
            match.end(),
        )

    found.sort(key=lambda item: item["start"])
    return found


def infer_toa_group(citation: dict[str, Any]) -> str:
    if citation.get("kind") in {"ambiguous", "docket"}:
        return "unresolved"
    blob = " ".join(
        str(citation.get(field) or "")
        for field in ("normalized", "raw", "reporter", "kind")
    ).lower()
    if "u.s.c." in blob or "fed. r." in blob or "const" in blob:
        return "statutes_rules"
    if "f. supp" in blob:
        return "district_courts"
    if re.search(r"f\.(?:2d|3d|4th)", blob):
        return "courts_of_appeals"
    if "u.s." in blob or "s. ct" in blob:
        return "us_supreme_court"
    return "unresolved"


def infer_court(citation: dict[str, Any]) -> str | None:
    if citation.get("court_hint"):
        return citation["court_hint"]
    group = infer_toa_group(citation)
    if group == "us_supreme_court":
        return "Supreme Court of the United States"
    if citation.get("kind") == "statute":
        return "United States Code"
    if citation.get("kind") == "rule":
        return "Federal Rules"
    if citation.get("kind") == "constitution":
        return "U.S. Constitution"
    return None
