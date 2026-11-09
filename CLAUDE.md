# CLAUDE.md

Guidance for Claude Code sessions working on this repository.

## What this repo is

The repo is an agent skill (open Agent Skills format). `SKILL.md` at the root is the entry point. The skill runs on other people's projects (the target repository) and checks them against a curated OWASP ASVS 5.0 Level 2 subset plus 12 additional practices. It writes `security/checklist.md`, `security/TODO.md`, `security/contact.md` and `SECURITY.md` into the target. Do not confuse the two: files in this repo are the skill, files under `security/` are output in a target.

The skill has no scripts. The agent only reads files, searches and runs shell commands. `dev/` is tooling for maintaining this repo, not part of what the skill ships.

## Design authority

`docs/superpowers/specs/2026-11-08-security-audit-skill-design.md` is the source of truth. The plan is `docs/superpowers/plans/2026-11-08-security-audit-skill.md`. `handover.md` is the superseded German first design (scripts, Jinja2, German status words); read it for history only. When spec and code disagree, fix the code or change the spec on purpose.

Hard rules that tests and reviews rely on:
- Status words are exactly `implemented`, `partial`, `not implemented`, `n/a`.
- ASVS text in `reference/asvs-checks.md` is copied verbatim from the release, never reworded. IDs come from `dev/asvs-selection.txt`.
- `SKILL.md` body stays at or under 1200 words in the body (`sed '1,/^---$/d' SKILL.md | wc -w`; currently 1199; `dev/tests/test_consistency.py` checks it). Check the count after every edit.
- Generated texts follow the writing rules in `SKILL.md`: short sentences, no dashes, no marketing words. The forbidden-word grep in `SKILL.md` and `dev/tests/test_templates.py` is the check.

## Commands

```sh
python3 -m unittest discover -s dev/tests -v                                  # 24 tests
python3 -I dev/check_reference.py reference/asvs-checks.md dev/asvs-selected.json   # exit 0 = consistent
```

Regenerate `dev/asvs-selected.json` after editing `dev/asvs-selection.txt`:

```sh
mkdir -p dev/asvs-source   # gitignored
curl -sL -o dev/asvs-source/asvs-5.0.0.flat.json \
  "https://github.com/OWASP/ASVS/releases/download/v5.0.0_release/OWASP_Application_Security_Verification_Standard_5.0.0_en.flat.json"
python3 -I dev/extract_asvs.py dev/asvs-source/asvs-5.0.0.flat.json dev/asvs-selection.txt dev/asvs-selected.json
```

`extract_asvs.py` exits non-zero and names the ID if a selected ID is missing or is Level 3. Then run the checker; it fails if `reference/asvs-checks.md` has drifted from the JSON.

## Running a skill test

Evidence lives in `docs/superpowers/testing/`. Runs on the private acceptance target `../inv` are not kept in the repo, because they list that project's open weaknesses. Prompts are in `docs/superpowers/testing/prompts/`.

1. Install: `ln -sfn "$(pwd)" ~/.claude/skills/security-audit`.
2. Start from a clean target: `git status --short` empty. A test run writes into the target repo. After a run reset only the skill's outputs: `git clean -fd -- security SECURITY.md` (check with `git clean -nd -- security SECURITY.md` first), plus `git checkout -- SECURITY.md` when the target already tracked a `SECURITY.md`.
3. Dispatch the test agent as a subagent. Subagents share this repo as cwd, so the prompt must say "read nothing outside <target> except the skill directory".
4. The skill's three questions (scope, contact, existing `SECURITY.md`) cannot be answered through a relay: test agents refuse answers relayed by another agent. Put an "Owner answers" block in the prompt instead (`docs/superpowers/testing/prompts/owner-answers.md`). To test that the skill asks, omit the answer and check that the agent stops and asks.
5. Check mechanically: row count 105, statuses in the 4 values, TODO ids equal open ids, per-chapter counts in `SECURITY.md` equal the checklist, forbidden-word grep from `SKILL.md` exits 1.
6. Record the result, including failures, in a new file under `docs/superpowers/testing/`. Fix `SKILL.md` or `reference/`, then re-run the case that failed.

Counts vary between runs (judgement of partial vs implemented). Compare statuses and Changes lines, not exact totals.

## Open items after v1 (2026-11-08)

Parked at the final review of v1, not yet fixed. Start here before re-reviewing.

Minor fixes:
- `SKILL.md` says "never cite an unlisted path", but AP-7 cites paths from git history. Decide the scope of the rule.
- Public open-item text uses the first clause of the requirement, which can cut the meaning. Use the ASVS section name instead.
- "Every run rewrites the generated `SECURITY.md` block" needs "carry Changes lines over verbatim".
- Which HTML comments from the templates are copied into the output is undefined.

Decisions for the owner:
- The public `SECURITY.md` lists open items by ASVS ID, which names unfixed weaknesses. Keep, or show counts only?
- The contact question is asked in step 5. It could move to step 2, next to the scope question.
- "Loads in Codex and Cursor" is unverified; neither is installed here.
- V5.3.2 (path traversal) is gated on the `uploads` condition.
- The licence of this repo is undecided (`README.md`).
