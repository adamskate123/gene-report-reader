"""Utilities for parsing OCR output into structured data."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Dict, Iterable, List, Sequence, Tuple

KeyValuePairs = List[Tuple[str, str]]


_CANONICAL_FIELD_NAMES = {
    "patient": "Patient Name",
    "patient name": "Patient Name",
    "patient id": "Patient ID",
    "id": "Patient ID",
    "identifier": "Patient ID",
    "dob": "Date of Birth",
    "date of birth": "Date of Birth",
    "sample": "Sample ID",
    "sample id": "Sample ID",
    "sample date": "Sample Date",
    "collection date": "Sample Date",
    "report date": "Report Date",
    "gene": "Gene",
    "variant": "Variant",
    "transcript": "Transcript",
    "zygosity": "Zygosity",
    "classification": "Classification",
    "interpretation": "Interpretation",
    "recommendation": "Recommendations",
    "recommendations": "Recommendations",
    "notes": "Notes",
}

_VARIANT_KEYWORDS = (
    "pathogenic",
    "likely pathogenic",
    "variant of uncertain significance",
    "vus",
    "benign",
    "likely benign",
)

_VARIANT_LINE_RE = re.compile(
    r"^(?P<gene>[A-Z0-9]+)[\s,:;-]+(?P<variant>c\.[^\s]+|p\.[^\s]+|exon[^\s]+|g\.[^\s]+).*?"
    r"(?P<classification>pathogenic|likely pathogenic|variant of uncertain significance|vus|benign|likely benign)" ,
    re.IGNORECASE,
)

_KEY_VALUE_RE = re.compile(r"^(?P<key>[\w /()\-]+?)\s*[:|-]\s*(?P<value>.+)$")


@dataclass
class ParsedReport:
    """Structured representation of a clinical report."""

    key_values: KeyValuePairs

    def to_markdown(self) -> str:
        return format_markdown_table(self.key_values)


def _normalise_key(raw_key: str) -> str:
    canonical = _CANONICAL_FIELD_NAMES.get(raw_key.lower().strip())
    if canonical:
        return canonical
    return raw_key.strip().title()


def _merge_key_value_pairs(pairs: Iterable[Tuple[str, str]]) -> KeyValuePairs:
    merged: Dict[str, str] = {}
    for key, value in pairs:
        key = _normalise_key(key)
        value = value.strip()
        if not value:
            continue
        if key in merged:
            # Combine repeated values in a readable fashion.
            existing = merged[key]
            if value.lower() not in existing.lower():
                merged[key] = f"{existing}; {value}"
        else:
            merged[key] = value
    return [(key, merged[key]) for key in merged]


def _extract_key_values_from_lines(lines: Sequence[str]) -> KeyValuePairs:
    pairs: KeyValuePairs = []
    for line in lines:
        line = line.strip()
        if not line:
            continue
        match = _KEY_VALUE_RE.match(line)
        if match:
            pairs.append((match.group("key"), match.group("value")))
            continue

        variant_match = _VARIANT_LINE_RE.match(line)
        if variant_match:
            gene = variant_match.group("gene")
            variant = variant_match.group("variant")
            classification = variant_match.group("classification")
            pairs.append(("Gene", gene))
            pairs.append(("Variant", variant))
            pairs.append(("Classification", classification.title()))
            continue

        # Look for inline mentions of important keywords (e.g. "Pathogenic"),
        # and treat the whole sentence as a note if we cannot classify it better.
        if any(keyword in line.lower() for keyword in _VARIANT_KEYWORDS):
            pairs.append(("Notes", line))
    return pairs


def parse_report_text(text: str) -> ParsedReport:
    """Parse ``text`` extracted from a clinical genetic report.

    The parser relies on common conventions found in genetic reports: key/value
    pairs separated by colons or hyphens, gene annotations prefixed with the gene
    symbol, and classification keywords such as ``Pathogenic``.  The heuristics
    are intentionally conservative so that the output remains useful even when
    the OCR introduces noise.
    """

    lines = text.splitlines()
    pairs = _extract_key_values_from_lines(lines)

    # If we did not find any structured data, provide at least a Notes field so
    # the user can review the raw text from the GUI.
    if not pairs:
        cleaned = " ".join(line.strip() for line in lines if line.strip())
        if cleaned:
            pairs.append(("Notes", cleaned))

    return ParsedReport(key_values=_merge_key_value_pairs(pairs))


def format_markdown_table(pairs: KeyValuePairs) -> str:
    """Return ``pairs`` formatted as a Markdown table."""

    if not pairs:
        return "| Field | Value |\n| --- | --- |\n| _(no data)_ | |"

    header = "| Field | Value |\n| --- | --- |"
    rows = [f"| {key} | {value} |" for key, value in pairs]
    return "\n".join([header, *rows])


__all__ = [
    "ParsedReport",
    "parse_report_text",
    "format_markdown_table",
]
