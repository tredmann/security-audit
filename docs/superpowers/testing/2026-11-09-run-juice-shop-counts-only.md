# Counts-only SECURITY.md on OWASP Juice Shop (2026-11-09)

Status: one run, no fixes needed.

## Change under test

The public `SECURITY.md` lists no requirement IDs. Open items, additional practices and Changes are counts only. The list of open items stays in `security/checklist.md` and `security/TODO.md` and is given to customers on request. Reason: IDs of open items name unfixed weaknesses.

## Setup

- Fresh `git clone --depth 1` of Juice Shop into the scratchpad; `git status --short` empty; original `SECURITY.md` md5 ae5e6f5a3f8ed2ecc1d82b2631724b83.
- Test agent: general-purpose, sonnet, `prompts/run-audit.md` with the clone path, the read restriction, a no-install/no-execute line, and `prompts/owner-answers.md` (append). It asked no question.

## Checks

- First N bytes of the new `SECURITY.md` (N = size of the original) have the original md5: original text preserved.
- Generated block: an ID pattern grep (`V<n>.<n>.<n>`, `AP-<n>`) matches only the fixed table label "AP-1 to AP-12". No open item is named.
- Open items line: "Open items (partial or not implemented): 78. Level 1: 36. Level 2: 42. The list of open items is available to customers on request." The checklist has 78 open ASVS rows, 36 at Level 1 and 42 at Level 2.
- Practices row: 12 | 4 | 3 | 5 | 0, equal to the checklist.
- Chapter table total 93 | 9 | 10 | 68 | 6, equal to the checklist.
- 105 rows; TODO ids equal the open ids (diff empty); forbidden-word grep exit 1.
- `git status --short`: ` M SECURITY.md`, `?? security/`.

## Not covered

First run, so Changes reads "None yet." The count format of Changes lines (one line per date) was not exercised. It needs a second run after a status change.
