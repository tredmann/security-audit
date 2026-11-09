---
name: security-audit
description: Use when asked for an ASVS check, a security checklist, a security audit or a security self-assessment of a repository, when a SECURITY.md or security page is wanted, or when a project has to prove its security practices, for example because a customer asks for security evidence.
---

# Security audit

Checks a repository against a curated OWASP ASVS 5.0 Level 2 subset and twelve additional practices, from source and configuration. Needs only reading files, searching and shell commands. `reference/` and `templates/` paths are relative to this skill's directory; output paths are relative to the target repository root.

## Outputs

| File | Template | Audience |
|---|---|---|
| `security/checklist.md` | `templates/checklist.md` | internal, state for the next run |
| `security/TODO.md` | `templates/TODO.md` | internal |
| `security/contact.md` | `templates/contact.md` | the user |
| `SECURITY.md` | `templates/SECURITY.md` | public |

Rows come only from `reference/asvs-checks.md` and `reference/additional-practices.md`: one row per entry, ID, level and requirement text copied (shortened to one sentence at most, never reworded). A row's chapter is its ID prefix (V6.2.1 is V6).

## Procedure

The questions in steps 2, 5 and 6 are mandatory. Ask by ending your turn with the question; the reply is the answer. Running non-interactively or with no user at hand is not a reason to skip them: end the turn with the question. When stopped on a question, write nothing else, not even a draft. Never invent answers or continue on assumptions.

1. **Detect the project** per `reference/detection.md`: search from the repository root, record the application root in the project picture paragraph, and mark each of the 18 condition keys detected or not detected with evidence.
2. **Confirm the scope** in one question: the project picture paragraph, then "Conditions detected: ... Conditions not detected: ... Is this correct?" Inconclusive keys go into this question.
3. **Read existing state.** If `security/checklist.md` exists, parse it.
   - `not implemented` and `partial` rows are re-checked.
   - `implemented` rows get a cheap evidence check: run `ls` on every path the row cites, a missing path fails the row, and the cited pattern or key must still be present; for a cited search, re-run it and compare the hit count. If that fails, the row is re-checked in full. Otherwise it is kept with its date.
   - `n/a` rows: fresh scope detection wins. If a conditional group was `n/a` and detection now finds the feature, the group is checked.
   - New requirements not in the existing file are checked.
   - On request, re-check every row.
   - For every re-checked row (open, partial, failed evidence check or full re-check), a status changes only when the previously cited evidence no longer holds or new evidence contradicts it, unless fresh detection changes the scope. The Changes line names which.
   - Every status change is recorded with date, old and new status in the "Changes" section. "Changes" holds only status changes, one line each, never "unchanged" lines. Changes lines are added, never removed or edited.
4. **Check.** Read the headers of `reference/asvs-checks.md` and `reference/additional-practices.md`. Per entry in scope, run "Where to look", apply "Implemented when" and "Not implemented when", fill every column. Run `ls` on every path before citing it; never cite an unlisted path, except AP-7 history paths with their commit hash. Commands: file search, `grep`, reading files, `git log` per the AP-7 recipe in `reference/additional-practices.md`, and a dependency audit (`composer audit --locked --no-plugins`, `npm audit`, `pip-audit`) only if the tool is on PATH and the lock file exists. Otherwise V15.2.1 is `not implemented`, reason "not verifiable locally, run `<command>`". "No packages - skipping audit" is not a clean result: the lock file was not audited, and V15.2.1 keeps that reason.
5. **Contact.** If `security/contact.md` is missing, ask once for contact address and response time (PGP key optional) and write it.
6. **Write outputs** in one pass from the same data, so `SECURITY.md` numbers and dates match the checklist. Every run rewrites `security/TODO.md` and the generated block from the templates; never keep the previous block.
   - `security/TODO.md`: every `not implemented` and `partial` row; Level 1, Level 2, then practices headed `### AP-7 (AP) <short practice>`.
   - `SECURITY.md`: the project summary is the project picture without component versions, file paths or line citations. No IDs: open items, practices and Changes are counts only. Checked = all rows of the chapter = implemented + partial + not implemented + n/a. Changes: one line per date, newest first; on a first run the Changes section of both `SECURITY.md` and `security/checklist.md` reads "None yet."
   - The generated block sits between `<!-- security-audit:start -->` and `<!-- security-audit:end -->`; everything outside is preserved byte for byte. Existing `SECURITY.md` without markers: ask once, replace or append. Copy no HTML comment from a template except these two markers.
7. **Report** counts per status, open Level 1 items, paths written, and remind that `security/checklist.md` and `security/TODO.md` map unfixed weaknesses and stay private while open items remain.

## Status contract

| Status | The row has |
|---|---|
| `implemented` | Evidence: `path:line` or config key. For absence of an unsafe pattern: the search (patterns, directories, hit count), plus a manifest `path:line` where relevant. For a framework default: the lock-file line of the installed version, plus the config file and key, or the middleware or package entry that enables it. |
| `partial` | Evidence for part, and a reason naming what is missing. Sink-type and coverage-type requirements split `partial` from `not implemented` as the header defines. |
| `not implemented` | A reason. No evidence of the control is `not implemented`, never `partial`. A violation is cited as evidence. |
| `n/a` | Why the feature does not exist. Undetected condition: whole group, reason "condition `<key>` not detected", search cited. Core rows need a specific reason. |

Large codebase: sample routes, controllers, middleware, models; say so in the reason.

Never write a secret value into any output. Cite the path, and for git history the commit hash and path. Never the value or line content.

| Thought | Reality |
|---|---|
| "Standard framework protections are in place." | Not evidence without lock-file line and config key. |
| "`http_only => true` shows it." | Evidence is `path:line`. |
| "The team's docs say backups are tested." | Docs are claims. Check code or config. |
| "No status changed, keep `SECURITY.md`." | Rewrite the block; rules and templates change. |
| "The detail helps the customer." | `SECURITY.md` gets counts and dates. IDs name unfixed weaknesses; customers ask for the list. |

## Writing rules

Short sentences. Numbers and dates instead of adjectives; in the internal files also paths. A sentence that could stand in another project's `SECURITY.md` is removed, except the fixed headings, the disclaimer, the "Checked against" sentence, the on-request sentence and the attribution line. Empty section: one line "None yet." Replace every `<...>` placeholder.

Final self-check; exit 1 means clean, a match means rewrite and run again, exit 2 means a file is missing (an error):

```sh
grep -n -i -E "robust|state[- ]of[- ]the[- ]art|best[- ]in[- ]class|industry[- ]leading|cutting[- ]edge|top priority|highest priority|takes? security seriously|committed to|world[- ]class|enterprise[- ]grade|military[- ]grade|bank[- ]level|not only|$(printf '\342\200\224')|$(printf '\342\200\223')" security/checklist.md security/TODO.md security/contact.md SECURITY.md
```

## Boundaries

Write only the four output files. Never change code, configuration, CI or dependencies. Never install anything.

## Common mistakes

- Own status words (Met, NV), file names or folders.
- IDs or requirement text from memory.
- Choosing the scope without the step 2 question.
