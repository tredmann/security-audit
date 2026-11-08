"""Check reference/asvs-checks.md against the selected ASVS requirements.

Usage: python3 dev/check_reference.py <reference.md> <selected.json>

Stdlib only. Prints one line per problem and exits 1; exits 0 when clean.
Problem prefixes: missing, unknown, duplicate, reworded, field, condition.
"""
import json
import re
import sys

CONDITIONS = {
    "own-auth", "rich-text", "outbound-urls", "mail", "xml", "graphql", "uploads",
    "mfa", "idp", "multi-tenant", "jwt", "oauth-client", "webserver-config",
    "browser-storage", "node-backend",
}

FIELDS = ["Requirement", "Where to look", "Implemented when", "Not implemented when"]

HEADER_RE = re.compile(r"^### (V\d+\.\d+\.\d+) \((.*)\)$")
FIELD_RE = re.compile(r"^\*\*([^*]+):\*\*(.*)$")
LEVEL_RE = re.compile(r"^Level [1-3]$")


def parse_entries(text):
    entries = []
    current = None
    for line in text.splitlines():
        m = HEADER_RE.match(line)
        if m:
            current = {"id": m.group(1), "header": m.group(2), "fields": {}}
            entries.append(current)
            continue
        if line.startswith("### "):
            current = None
            continue
        if current is None:
            continue
        f = FIELD_RE.match(line)
        if f and f.group(1) in FIELDS:
            current["fields"][f.group(1)] = f.group(2).strip()
    return entries


def header_problem(header):
    """Return the offending text if the header is not an allowed form, else None."""
    parts = [p.strip() for p in header.split(",")]
    if not parts or not LEVEL_RE.match(parts[0]):
        return header
    if len(parts) == 2 and parts[1] == "core":
        return None
    if len(parts) == 3 and parts[1] == "core":
        return None if parts[2] in CONDITIONS else parts[2]
    if len(parts) == 2 and parts[1].startswith("conditional: "):
        key = parts[1][len("conditional: "):]
        return None if key in CONDITIONS else key
    return header


def check(entries, selected):
    problems = []
    sel_by_id = {r["id"]: r for r in selected}
    counts = {}
    for e in entries:
        counts[e["id"]] = counts.get(e["id"], 0) + 1
    for req_id in sorted(counts, key=lambda i: [int(x) for x in i[1:].split(".")]):
        if counts[req_id] > 1:
            problems.append(f"duplicate: {req_id}")
    seen = set()
    for e in entries:
        req_id = e["id"]
        if req_id in seen:
            continue
        seen.add(req_id)
        if req_id not in sel_by_id:
            problems.append(f"unknown: {req_id}")
    for e in entries:
        req_id = e["id"]
        if req_id not in sel_by_id:
            continue
        bad = header_problem(e["header"])
        if bad is not None:
            problems.append(f"condition: {req_id} {bad}")
        req_text = e["fields"].get("Requirement")
        if req_text is not None and req_text != sel_by_id[req_id]["text"]:
            problems.append(f"reworded: {req_id}")
        for name in FIELDS:
            if name not in e["fields"]:
                problems.append(f"field: {req_id} {name}")
    present = {e["id"] for e in entries}
    for req_id in sel_by_id:
        if req_id not in present:
            problems.append(f"missing: {req_id}")
    return problems


def main(argv):
    if len(argv) != 3:
        print(__doc__.strip(), file=sys.stderr)
        return 2
    with open(argv[1], encoding="utf-8") as fh:
        entries = parse_entries(fh.read())
    with open(argv[2], encoding="utf-8") as fh:
        selected = json.load(fh)
    problems = check(entries, selected)
    for line in problems:
        print(line)
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
