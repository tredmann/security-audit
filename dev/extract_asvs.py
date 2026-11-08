"""Extract the selected ASVS requirements from the OWASP flat JSON.

Usage: python3 dev/extract_asvs.py <flat.json> <selection.txt> <out.json>

Stdlib only. Exits non-zero and names the offending ID if a selected ID is
missing from the source or is a Level 3 requirement.
"""
import json
import sys


def load_selection(path):
    ids = []
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line and not line.startswith("#"):
                ids.append(line)
    return ids


def sort_key(req_id):
    return tuple(int(x) for x in req_id[1:].split("."))


def extract(requirements, ids):
    by_id = {r["req_id"]: r for r in requirements}
    out = []
    for req_id in ids:
        src = by_id.get(req_id)
        if src is None:
            raise ValueError(f"{req_id} is selected but missing from the source")
        level = int(src["L"])
        if level == 3:
            raise ValueError(f"{req_id} is Level 3 and must not be selected")
        out.append({
            "id": req_id,
            "level": level,
            "chapter_id": src["chapter_id"],
            "chapter_name": src["chapter_name"],
            "section_id": src["section_id"],
            "section_name": src["section_name"],
            "text": src["req_description"],
        })
    out.sort(key=lambda r: sort_key(r["id"]))
    return out


def main(argv):
    if len(argv) != 3:
        print("usage: extract_asvs.py <flat.json> <selection.txt> <out.json>", file=sys.stderr)
        return 2
    flat_path, selection_path, out_path = argv
    with open(flat_path, encoding="utf-8") as fh:
        requirements = json.load(fh)["requirements"]
    try:
        result = extract(requirements, load_selection(selection_path))
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    with open(out_path, "w", encoding="utf-8") as fh:
        json.dump(result, fh, indent=2, ensure_ascii=False)
        fh.write("\n")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
