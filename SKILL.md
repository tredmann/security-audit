---
name: security-audit
description: Use when asked for an ASVS check, a security checklist, a security audit or a security self-assessment of a repository, when a SECURITY.md or security page is wanted, or when a project has to prove its security practices, for example because a customer asks for security evidence.
---

# Security audit

Checks a repository against a curated OWASP ASVS 5.0 Level 2 subset and twelve additional practices, from source and configuration. Needs only reading files, searching and shell commands. `reference/` and `templates/` are bundled; output paths are relative to the target repository root.

## Outputs

| File | Template | Audience |
|---|---|---|
| `security/checklist.md` | `templates/checklist.md` | internal, state for the next run |
| `security/TODO.md` | `templates/TODO.md` | internal |
| `security/contact.md` | `templates/contact.md` | the user |
| `SECURITY.md` | `templates/SECURITY.md` | public |

Rows come only from `reference/asvs-checks.md` and `reference/additional-practices.md`: one row per entry, ID, level and requirement text copied (shortened to one sentence at most, never reworded). A row's chapter is its ID prefix (V6.2.1 is V6).

## Procedure

1. **Detect the project** per `reference/detection.md`: search from the repository root, record the application root in the project picture paragraph, and mark each of the 18 condition keys detected or not detected with evidence.
2. **Confirm the scope** in one question: the project picture paragraph, then "Conditions detected: ... Conditions not detected: ... Is this correct?" Inconclusive keys go into this question.
3. **Read existing state.** If `security/checklist.md` exists, parse it.
   - `not implemented` and `partial` rows are re-checked.
   - `implemented` rows get a cheap evidence check: the cited file still exists and the cited pattern or key is still present. If that fails, the row is re-checked in full. Otherwise it is kept with its date.
   - `n/a` rows: fresh scope detection wins. If a conditional group was `n/a` and detection now finds the feature, the group is checked.
   - New requirements not in the existing file are checked.
   - The user may ask for a full re-check when invoking the skill; then every row is re-checked.
   - Every status change is recorded with date, old and new status in the "Changes" section.
4. **Check.** Read the header of `reference/asvs-checks.md`. Per entry in scope, run "Where to look", apply "Implemented when" and "Not implemented when", fill every column. Commands: file search, `grep`, reading files, `git log -p` for AP-7, and a dependency audit (`composer audit`, `npm audit`, `pip-audit`) only if the tool is on PATH and the lock file exists. Otherwise V15.2.1 is `not implemented`, reason "not verifiable locally, run `<command>`".
5. **Contact.** If `security/contact.md` is missing, ask once for contact address and response time (PGP key optional) and write it.
6. **Write outputs** in one pass from the same data, so `SECURITY.md` numbers and dates match the checklist.
   - `security/TODO.md`: every `not implemented` and `partial` row; Level 1, Level 2, then practices headed `### AP-7 (AP) <short practice>`.
   - `SECURITY.md` Checked = all rows of the chapter = implemented + partial + not implemented + n/a.
   - The generated block sits between `<!-- security-audit:start -->` and `<!-- security-audit:end -->`; everything outside is preserved byte for byte. Existing `SECURITY.md` without markers: ask once, replace or append.
7. **Report** counts per status, open Level 1 items, paths written, and remind that `security/checklist.md` and `security/TODO.md` map unfixed weaknesses and should not be public while open items remain; `SECURITY.md` carries no file paths and is meant to be public.

## Status contract

| Status | The row has |
|---|---|
| `implemented` | Evidence: `path:line` or config key. For absence of an unsafe pattern: the search (patterns, directories, hit count), plus a manifest `path:line` where relevant. For a framework default: the lock-file line of the installed version and the enabling config key. |
| `partial` | Evidence for part, and a reason naming what is missing. Sink-type and coverage-type requirements split `partial` from `not implemented` as the header defines. |
| `not implemented` | A reason. Nothing found is `not implemented`, never `partial`. A violation is cited as evidence. |
| `n/a` | Why the feature does not exist. Undetected condition: whole group, reason "condition `<key>` not detected", search cited. Core rows need a specific reason. |

Large codebase: sample routes, controllers, middleware, models; say so in the reason.

Never write a secret value into any output. Cite the path, and for git history the commit hash and path. Never the value or line content.

| Thought | Reality |
|---|---|
| "Standard framework protections are in place." | Not evidence without lock-file line and config key. |
| "`http_only => true` shows it." | Evidence is `path:line`. |
| "The team's docs say backups are tested." | Docs are claims. Check code or config. |
| "The detail helps the customer." | `SECURITY.md` gets IDs, short text, counts, dates. No paths, no exploit detail. |

## Writing rules

Short sentences. Numbers, paths and dates instead of adjectives. A sentence that could stand in another project's `SECURITY.md` is removed, except fixed headings and the disclaimer. Empty section: one line "None yet." Replace every `<...>` placeholder.

Final self-check; exit 1 means clean, a match means rewrite and run again:

```sh
grep -n -i -E "robust|state[- ]of[- ]the[- ]art|best[- ]in[- ]class|industry[- ]leading|cutting[- ]edge|top priority|highest priority|takes? security seriously|committed to|world[- ]class|enterprise[- ]grade|military[- ]grade|bank[- ]level|not only|$(printf '\342\200\224')|$(printf '\342\200\223')" security/checklist.md security/TODO.md security/contact.md SECURITY.md
```

## Boundaries

Write only the four output files. Never change code, configuration, CI or dependencies. Never install anything.

## Common mistakes

- Own status words (Met, NV), file names or folders.
- IDs or requirement text from memory.
- Choosing the scope without the step 2 question.
