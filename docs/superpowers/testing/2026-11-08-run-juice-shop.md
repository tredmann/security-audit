# Stack neutrality run on OWASP Juice Shop (2026-11-08)

Status: one run, no fixes needed. Nothing PHP-specific found in `reference/detection.md` or `reference/asvs-checks.md`.

## Setup
- `~/.claude/skills/security-audit` -> this repo (symlink resolves).
- `git clone --depth 1 https://github.com/juice-shop/juice-shop.git /private/tmp/claude-501/juice/juice-shop`; no `npm install`, nothing executed in the clone. Version 20.3.0 (package.json:3). No lock file (`.npmrc` sets `package-lock=false`).
- Original `SECURITY.md` md5 37032aebe1ff9596751b0e4f7c60acef (copy kept in the scratchpad).
- Test agent: general-purpose, sonnet, run-audit prompt with the clone path (no `src/` note), read restriction, Owner answers block (scope correct; security@example.com test fixture; 5 business days; no PGP; append). It asked no question.

## Detection vs expectations
Quotes are from `security/checklist.md` (Scope table and project line).
- Node/Express: held. "back end in TypeScript on Node.js with Express ^4.22.1 (package.json:110, server.ts)"; `node-backend | yes`.
- Angular front end: held. "Angular front end in frontend/".
- SQLite/Sequelize: held. "SQLite file through Sequelize ^6.37.3 (models/index.ts:34-41, package.json:148)".
- JWT: held. `jwt | yes | JWTs are issued and verified. package.json:112 and :129; lib/insecurity.ts:54`.
- Dockerfile: held. `dockerfile | yes | Three Dockerfiles. ...`.
- No Compose at root: expectation did not hold, but the expectation was wrong, not the skill. Juice Shop has `docker-compose.test.yml` at the root and `infrastructure/docker-compose.yml`; `compose | yes | Two Compose files. docker-compose.test.yml (test); infrastructure/docker-compose.yml (deployment)`. Correct detection.
- Other conditions: own-auth, rich-text, outbound-urls, xml, uploads, mfa, idp, oauth-client, webserver-config, browser-storage, ci applied; mail, graphql, multi-tenant not (each with a search note).
- V15.2.1: `not implemented`; reason "Not verifiable locally, run `npm audit --omit=dev` (needs package-lock.json, none exists; frontend has the same gap). Pinned old libraries are visible: express-jwt 0.1.3, jsonwebtoken 0.4.0, sanitize-html 1.4.2." npm exists on this machine but there is no lock file, so the audit could not run.

## Known weaknesses (all surfaced)
- V1.2.4 `not implemented`: "SQL text is built by interpolating request values (login email, search criteria). ..." evidence routes/login.ts:34, routes/search.ts:23.
- V11.4.2 `not implemented`: "Passwords are stored as unsalted MD5." evidence lib/insecurity.ts:41, models/user.ts:73.
- V9.1.2 `not implemented`: "Neither verify call passes an algorithms allowlist, and the public key is the secret." V9.1.1 `partial` (old jsonwebtoken 0.4.0, express-jwt 0.1.3).
- Also found: V1.3.2 eval of username, V1.5.1 XXE, V1.5.2 yaml.load, V1.3.6 SSRF.

## Mechanical checks (run in the clone)
- 105 rows (93 ASVS + 12 AP). Counts: all 105 = 11 implemented / 16 partial / 71 not implemented / 7 n/a; ASVS 93 = 7/13/66/7.
- `implemented` rows with empty Evidence: none.
- Open rows 87 = TODO.md entries 87, same ID set (script).
- SECURITY.md Results table totals 93 | 7 | 13 | 66 | 7 and per-chapter rows equal the checklist totals (read; V15 row 8|1|3|4|0 matches the TODO list).
- Forbidden-word grep (command as in run1-inv "Exact commands"): exit 1.
- Secret values: fixed-string pattern file built from the committed key material and secret literals in `lib/insecurity.ts` and `encryptionkeys/*` (8 patterns, deleted afterwards) against the four outputs: exit 1. (A first attempt had an empty pattern file and was discarded.)
- Append path: first N bytes of SECURITY.md (N = size of original) are identical to the original (`cmp`), markers at lines 128 and 292; `git status --short`: ` M SECURITY.md`, `?? security/`; no application file changed.
- AP-12 `implemented`: "SECURITY.md:20 names a reporting e-mail address outside the generated block (existing text, preserved)."

## Fixes and re-run
None needed, so no second run.

## Observations
- SECURITY.md now shows two contacts (existing owner address with PGP, and the test fixture); expected for the append answer.
- The agent noted the shallow clone limits AP-7 history scanning, and a referenced nginx.conf is missing (V12.1.1 `not implemented`, "not verifiable locally").

## Final fix verification (2026-11-08)

Skill at commits dfdf1d0, 3e1b58d, 7d784b6 (final fix wave). Reset first: `git -C /private/tmp/claude-501/juice/juice-shop checkout -- SECURITY.md && git -C /private/tmp/claude-501/juice/juice-shop clean -fd -- security`; afterwards the `SECURITY.md` md5 was 37032aebe1ff9596751b0e4f7c60acef (the original). Test agent: general-purpose, sonnet, run-audit prompt with the clone path, the read restriction, a no-install/no-execute line, and the Owner answers block (scope correct; security@example.com test fixture; 5 business days; no PGP; append). It asked no question.

Checks (quotes marked as taken from `security/checklist.md` or `SECURITY.md` in the clone):
- AP-12: `implemented`. Checklist evidence: "SECURITY.md:20 names a private reporting contact outside the generated block; `git ls-files SECURITY.md` prints SECURITY.md." The file is tracked, so both sources of the new rule count; the agent cited both. Expected `implemented`: PASS.
- AP-7 ran with `-i`. Command the agent ran (from its transcript): `git log --all -i -G'(password|passwd|secret|api_key|aws_secret_access_key|token|_key)[[:space:]]*[=:][[:space:]]*.{8,}' --format=%H --name-only`. Checklist reason: "The second pattern run listed 127 file hits, mostly code and fixtures, not judged one by one." Status `not implemented` on the first pattern (private key block, commit hash and three paths, no value). PASS. Observation: the checklist evidence names the first command only as "git log --all -G (private-key pattern)", not the full command text.
- Original text preserved: the first 7148 bytes of the new `SECURITY.md` (size of the original) have md5 37032aebe1ff9596751b0e4f7c60acef, equal to the original. `git status --short`: ` M SECURITY.md`, `?? security/`. PASS.
- First-run Changes: both `security/checklist.md` and `SECURITY.md` read "None yet." under "## Changes". PASS.
- About section of `SECURITY.md`: no versions, no paths ("It has a Node.js back end and an Angular front end, stores data in SQLite ..."). PASS.
- Rule changes visible: V3.4.6 `not implemented` ("helmet.frameguard() sets X-Frame-Options only"); V8.2.2 `not implemented` (basket loaded by URL id with no ownership check); AP-8 `not implemented` ("Only a legacy Dependabot v1 file in .dependabot/ exists").
- 105 rows; forbidden-word grep over the four outputs: 0 matches (exit 1).
- Counts (agent report): ASVS 93 = 9 implemented / 14 partial / 65 not implemented / 5 n/a; practices 12 = 4 / 3 / 5 / 0.
