# Security Audit Skill — Design

Date: 2026-11-08
Status: draft, pending approval
Supersedes: `handover.md` where the two disagree (see "Changes from the handover").

## Intent

An agent skill that runs inside any web-application repository, checks the code and configuration against a curated subset of OWASP ASVS 5.0 plus a small group of infrastructure and repository practices, and writes the result as Markdown into the repo.

Two readers use the same findings:

1. The developer or team: what is in place, what is missing, so missing items can become tickets.
2. An outsider (customer, technical buyer): a `SECURITY.md` that states what was checked, when, with what result, and where the evidence is.

The skill does not say the system is secure. It documents which requirements were checked and what was found.

## Goals

- Works on any web application repo regardless of language or framework. Primary target: PHP applications with a database and Docker Compose, but nothing in the skill may depend on PHP.
- Every `implemented` status points at a file and line, or a configuration key. No status without evidence or a reason.
- Output is plain Markdown that is readable in GitHub without tooling.
- Re-runnable: a second run updates only what was open or partial, and records what changed.
- Agent-neutral: the skill follows the open Agent Skills format (`SKILL.md` with frontmatter, subfolders for reference material) and needs only: read files, run shell commands. No agent-specific tools, no SDK.

## Non-goals (version 1)

- No HTML page, no `security.txt`, no `tools.yml` for external scanner results. These may come later; the design keeps a slot for them (see "Later versions").
- No scanner installation, no CI changes, no code changes in the target project.
- No full ASVS catalog walk. The curated set is the scope; the rest is declared out of scope on the page.
- No ticket export format. Markdown is enough; tickets are created later by hand or by another tool.
- No runtime testing (HTTP probing, TLS checks). Everything is judged from the repository.

## Anti-goals

- A `SECURITY.md` that reads like marketing. Sentences such as "security is our top priority" must not appear.
- 100 % compliance claims. Open items are listed, not hidden.
- Inventing requirements or rewording ASVS text. Requirement text is quoted from the ASVS 5.0 release.
- Guessing. If evidence cannot be found in the repo, the status is `not implemented`, not `partial`.

## Language

Everything is English: the skill, the check definitions, the status values, all generated files. No language option.

## Scope of checks

### Selection principle

A requirement is included only if an agent can judge it from what is in the repository: application code, framework configuration, environment templates, Dockerfile, Compose files, web server configuration committed to the repo, CI workflow files, or by running a dependency audit command (`composer audit`, `npm audit`, `pip-audit`, etc.) locally. Requirements that need documentation artefacts, runtime probing, or operational knowledge are excluded.

### Core ASVS set (applies to every web application)

Injection and encoding (V1): V1.2.1, V1.2.3, V1.2.4, V1.2.5, V1.3.2, V1.5.2
Input validation (V2): V2.2.1, V2.2.2, V2.4.1
Cookies, headers, CSRF (V3): V3.3.1, V3.3.2, V3.3.4, V3.4.1, V3.4.2, V3.4.3, V3.4.4, V3.4.6, V3.5.1, V3.5.3, V3.7.2
Authentication (V6, applies when the app has its own login): V6.2.1, V6.2.2, V6.2.3, V6.2.4, V6.2.5, V6.3.1, V6.3.2, V6.3.3, V6.4.1, V6.4.2, V6.4.3
Sessions (V7): V7.2.1, V7.2.3, V7.2.4, V7.3.1, V7.3.2, V7.4.1, V7.4.3, V7.5.1
Authorization (V8): V8.2.1, V8.2.2, V8.3.1
Cryptography (V11): V11.3.1, V11.3.2, V11.4.1, V11.4.2, V11.5.1
Transport (V12): V12.3.1, V12.3.2
Configuration (V13): V13.2.2, V13.2.3, V13.3.1, V13.4.1, V13.4.2, V13.4.5
Data protection (V14): V14.2.1, V14.3.2
Dependencies and defensive coding (V15): V15.1.2, V15.2.1, V15.2.3, V15.3.1, V15.3.3, V15.3.4, V15.3.5
Logging and errors (V16): V16.2.5, V16.3.1, V16.3.2, V16.4.1, V16.5.1

### Conditional ASVS set (applies when the feature is present)

| Condition | Requirements |
| --- | --- |
| Rich-text / WYSIWYG input | V1.3.1 |
| Outbound requests to user-supplied URLs | V1.3.6 |
| Sends e-mail with user-supplied content | V1.3.11 |
| Parses XML | V1.5.1 |
| GraphQL API | V4.3.1, V4.3.2 |
| File uploads | V5.2.1, V5.2.2, V5.3.1, V5.3.2, V5.4.1 |
| Multi-factor authentication | V6.5.1, V6.5.3 |
| External identity provider (SAML/OIDC) | V6.8.2 |
| Multi-tenant | V8.4.1 |
| JWT or other self-contained tokens | V9.1.1, V9.1.2, V9.2.1, V9.2.3 |
| OAuth client | V10.2.1 |
| Web server config committed (nginx, Apache, Caddy) | V12.1.1, V13.4.3 |
| Browser frontend with client-side storage | V14.3.3 |
| Node.js backend | V15.3.6 |

### Additional practices (outside ASVS, reported in a separate group)

| ID | Practice | Reference |
| --- | --- | --- |
| AP-1 | Dockerfile runs as a non-root user | CIS Docker Benchmark 4.1 |
| AP-2 | Base images pinned to a version or digest, not `latest` | OpenSSF Scorecard: Pinned-Dependencies |
| AP-3 | No `privileged: true`, no Docker socket mount in Compose | CIS Docker Benchmark 5.4, 5.31 |
| AP-4 | Database and cache ports not published to the host in Compose | OWASP Docker Security Cheat Sheet |
| AP-5 | `.dockerignore` excludes `.git`, `.env`, dependency folders | OWASP Docker Security Cheat Sheet |
| AP-6 | `.env` and secret files are gitignored; an `.env.example` exists | OWASP Secrets Management Cheat Sheet |
| AP-7 | No secrets in git history (pattern scan over `git log -p`) | OWASP Secrets Management Cheat Sheet |
| AP-8 | Dependency update automation configured (Dependabot, Renovate) | OpenSSF Scorecard: Dependency-Update-Tool |
| AP-9 | CI runs a dependency vulnerability audit | OpenSSF Scorecard: Vulnerabilities |
| AP-10 | CI runs static analysis (SAST) | OpenSSF Scorecard: SAST |
| AP-11 | CI workflow token permissions are minimal (GitHub Actions only) | OpenSSF Scorecard: Token-Permissions |
| AP-12 | `SECURITY.md` with a contact exists | OpenSSF Scorecard: Security-Policy |

Branch protection was considered and dropped: it is a repository setting, not visible in the checkout.

### Source of requirement text

The selection above is 93 requirements (68 core, 25 conditional), all Level 1 or 2 in ASVS 5.0.0. The ASVS text is taken from the official release asset `OWASP_Application_Security_Verification_Standard_5.0.0_en.flat.json` (GitHub release tag `v5.0.0_release` of `OWASP/ASVS`; the `releases/latest` redirect currently points there). The builder extracts the selected IDs once and stores them in the skill. The target project never downloads anything. ASVS is CC BY-SA 4.0; the skill's reference file carries the attribution.

## Status model

Four values, exactly these strings:

| Status | Meaning | Required fields |
| --- | --- | --- |
| `implemented` | Evidence found that the requirement is implemented | Evidence (file:line or config key) and reason |
| `partial` | Evidence found for some code paths or some aspects, but not all | Evidence for what was found, reason naming what is missing |
| `not implemented` | No evidence found, or evidence that the requirement is violated | Reason. If a violation was found, cite it as evidence. |
| `n/a` | Not applicable: the requirement does not apply to this project | Reason (why the feature or context does not exist) |

Rules:

- `implemented` never without evidence.
- Never write a secret value into any output file. Evidence for a found secret is the path and, for git history, the commit hash. Never the value, never the line content.
- Not finding anything is `not implemented`, not `partial`. `partial` requires positive evidence for part of the requirement.
- A whole conditional group gets `n/a` with one shared reason when the condition is absent.
- Within the core set, `n/a` is allowed for individual requirements only with a specific reason (example: V6.* when authentication is entirely delegated to an IdP).
- Large codebases: the agent does not need to read every file. It samples the main entry points (controllers, routes, middleware, models) and says so in the reason. If sampling finds both compliant and non-compliant code, the status is `partial`.

## Procedure (what `SKILL.md` instructs)

1. **Detect the project.** Read the top-level layout, manifest files (`composer.json`, `package.json`, `pyproject.toml`, `go.mod`, ...), framework config, Dockerfile, Compose files, CI workflows, web server configs. Build a one-paragraph picture: language, framework, database, auth mechanism, deployment shape.
2. **Propose the scope.** From detection, decide which conditional groups apply. Present the detected picture and the proposed scope to the user as a single confirmation question. The user may correct it.
3. **Read existing state.** If `security/checklist.md` exists, parse it.
   - `not implemented` and `partial` rows are re-checked.
   - `implemented` rows get a cheap evidence check: the cited file still exists and the cited pattern or key is still present. If that fails, the row is re-checked in full. Otherwise it is kept with its date.
   - `n/a` rows: fresh scope detection wins. If a conditional group was `n/a` and detection now finds the feature, the group is checked.
   - New requirements not in the existing file are checked.
   - The user may ask for a full re-check when invoking the skill; then every row is re-checked.
   - Every status change is recorded with date, old and new status in the "Changes" section.
4. **Work through the checks.** For each applicable requirement, use the "where to look" hints from the reference file, search the code, decide the status, write evidence and reason. Shell commands allowed: file search, `grep`, reading files, `git log -p` for the secret scan, and the project's dependency audit command (`composer audit`, `npm audit`, `pip-audit`, ...) only if the tool and the lock file are already present. Never install tools or dependencies, never run `npm install` or similar. If the audit cannot run, V15.2.1 is `not implemented` with the reason "not verifiable locally, run `<command>`". Nothing that modifies the project.
5. **Ask for contact details** (once, if not already stored): security contact address, expected response time. Stored in `security/contact.md` so later runs do not ask again.
6. **Write outputs** (see below).
7. **Report** to the user: counts per status, the open Level 1 items, and the file paths written. The report ends with a reminder that `security/checklist.md` and `security/TODO.md` list unfixed weaknesses with file locations and should not be published (public repo, public web space) while open items remain. `SECURITY.md` carries no file paths and is meant to be public.

## Outputs

All paths relative to the target repository root. The skill writes only here.

### `security/checklist.md`

The full result and the state for the next run. One table per chapter, plus one for additional practices.

Header block: ASVS version (5.0.0), target level (2), date of the run, project picture (the paragraph from step 1), scope decisions (which conditional groups apply and why, which do not).

Per-row columns:

| Column | Content |
| --- | --- |
| ID | ASVS ID or AP-n |
| Level | 1, 2, or `—` for AP |
| Requirement | ASVS text, may be shortened to one sentence but not reworded in meaning |
| Status | `implemented`, `partial`, `not implemented`, `n/a` |
| Evidence | `path:line` or config key; empty only for `not implemented` without a violation and for `n/a` |
| Reason | One or two sentences |
| Checked | ISO date of the last check of this row |

A "Changes" section at the end: dated list of status transitions (`2026-11-08 V6.2.4 not implemented → implemented`).

### `security/TODO.md`

All rows with status `not implemented` or `partial`, sorted: ASVS Level 1 first, then Level 2, then additional practices. Each entry: ID, requirement (short), current status, what was found, and one concrete suggestion of what to do. Written so one entry can be pasted into a ticket.

### `security/contact.md`

Contact address, expected initial response time, optional PGP key URL. Maintained by the user after the first run.

### `SECURITY.md` (repo root)

Generated from `checklist.md` and `contact.md`. Sections, in order:

1. **About this document.** Three sentences: what the system is (from the project picture), that it is checked against ASVS 5.0 Level 2 (curated subset), date of the last check.
2. **Scope.** Which chapters and conditional groups were checked, which were not and why. One sentence stating that the check is a self-assessment from the source code, not a penetration test.
3. **Results.** Table per chapter: chapter name, requirements checked, implemented, partial, not implemented, n/a. One summary row. Followed by a list of all `not implemented` and `partial` items with ID and short requirement text. No evidence paths here (they are internal).
4. **Additional practices.** Same table shape for AP-1 to AP-12, with the reference column.
5. **Reporting a vulnerability.** Contact, response time, PGP key if any. From `contact.md`.
6. **Changes.** The "Changes" list from `checklist.md`, newest first.
7. **Further evidence.** Heading only, with one line: "No external assessments yet." when empty. Replaced by the user when a pentest report or badge exists.

Numbers and dates in `SECURITY.md` must match `checklist.md` exactly. If the agent writes both in one run from the same data this holds by construction; the skill says so explicitly.

**Existing `SECURITY.md` and user edits.** Sections 1 to 6 are generated and wrapped in HTML comment markers (`<!-- security-audit:start -->` / `<!-- security-audit:end -->`), which GitHub does not render. Everything outside the markers is preserved byte for byte on re-runs; this is how section 7 "Further evidence" and any other user text survive. If a `SECURITY.md` exists without markers on the first run, the skill asks once: replace the file, or append the generated block below the existing content. AP-12 is judged on the state before the run on the first run, and on the committed file afterwards.

## Writing rules for generated text

- Short sentences. No em dashes or en dashes used as sentence punctuation.
- No superlatives, no "not only ... but also", no "robust", "state of the art", "best in class", "industry leading", "cutting edge", "top priority", "take security seriously", "committed to", "world class", "enterprise grade", "military grade", "bank level". `SKILL.md` carries this list; the agent re-reads its output against it before finishing.
- Numbers, file paths and dates instead of adjectives.
- If a sentence could stand unchanged in another project's `SECURITY.md`, it says nothing and is removed. Exception: the fixed section headings and the self-assessment disclaimer.
- Empty sections stay empty with a one-line "none yet" statement. No placeholder prose.

## Skill structure

```
SKILL.md                          procedure, status rules, writing rules, forbidden-word list
reference/asvs-checks.md          curated ASVS requirements: ID, level, group/condition, text, where to look
reference/additional-practices.md AP-1 to AP-12 with reference and where to look
reference/detection.md            how to recognise frameworks, auth mechanisms, uploads, etc.
templates/checklist.md            skeleton with header block and table headers
templates/TODO.md                 skeleton
templates/SECURITY.md             skeleton with fixed headings and disclaimer sentence
```

`SKILL.md` frontmatter `description` must name the triggers: ASVS, security checklist, security audit, security self-assessment, SECURITY.md, security page, prove security practices.

No scripts in version 1. All work is done by the agent following `SKILL.md`. The builder may add a small stdlib-only Python script for extracting the selected requirements from the ASVS JSON during skill development; it is a development tool, not part of the skill's runtime.

### "Where to look" hints

Each check in the reference files carries a short list of stack-neutral search strategies and, where useful, concrete examples for common stacks (PHP/Laravel/Symfony, Node/Express/Nest, Python/Django/Flask). Example for V11.4.2:

> Look for the password hashing call at registration and password change. Search for `password_hash`, `bcrypt`, `argon2`, `Hash::make`, `make_password`, `PasswordHasher`. `implemented` if an approved algorithm (bcrypt, argon2id, scrypt, PBKDF2 with current iteration counts) is used everywhere a password is stored. `not implemented` if `md5`, `sha1`, or plain storage is found, or no hashing call is found.

Hints are guidance, not a script. The agent is expected to follow the code if the hints do not match the project.

## Changes from the handover

| Handover | This design | Why |
| --- | --- | --- |
| Full ASVS L2 catalog, loaded at runtime into `security/asvs/asvs-5.0.json` | Curated subset of ~80 ASVS + 12 practices, shipped inside the skill | Most of the catalog is not judgeable from a repo; a runtime download adds a moving part for no gain |
| German default, English option | English only | Decided 2026-11-08 |
| Four statuses in German | `implemented`, `partial`, `not implemented`, `n/a` | Language decision |
| `SECURITY.md` + `index.html` + `security.txt` + `tools.yml` | `SECURITY.md` only | Smaller first version |
| Python scripts `fetch_asvs.py`, `build_site.py`, Jinja2 templates | No runtime scripts; agent writes Markdown directly | Only Markdown output; removes the dependency question |
| One file per chapter under `security/asvs/` | One `security/checklist.md` | Fewer files to keep consistent; still one table per chapter |
| Scope asked up front | Scope detected, then confirmed in one question | Less to answer for the user |

## Later versions (slots kept open)

- `security/site/index.html`, standalone, inline CSS, same content as `SECURITY.md`.
- `.well-known/security.txt` from `contact.md`.
- `security/tools.yml` for external scanner results, rendered into a "What is checked and with what" section.
- Level 1 as a selectable target for very small systems.
- ASVS 5.x updates: the checklist header records the ASVS version; migration is manual.

## Acceptance

Primary target: the Tory project at `../tory` (sibling directory of this repo). Laravel 13 with Filament 5 (own login, so the V6 authentication block is exercised), Livewire, Sanctum and Passport (API tokens; JWT/OAuth conditional groups will be triggered), `compose.yaml`, `composer.lock` and `package-lock.json` present, PHPStan and Pest configured. The skill may write `security/` and `SECURITY.md` into that repo during testing; the outputs are reviewed by the user before any commit there.

Secondary target, if time allows: OWASP Juice Shop (Node) to check stack neutrality.

Done when:

- Scope detection names the framework, database and auth mechanism correctly and proposes the right conditional groups.
- Every applicable requirement has a status; no `implemented` without evidence.
- `TODO.md` lists exactly the `not implemented` and `partial` rows, Level 1 first.
- A second run on an unchanged repo changes no statuses and asks nothing but the confirmation question.
- Deleting a file cited as evidence for an `implemented` row and re-running moves that row to `not implemented` or `partial` with a dated entry in "Changes".
- No output file contains a secret value, including for AP-7 findings.
- `SECURITY.md` counts match `checklist.md`.
- No sentence in the generated files contains a word from the forbidden list.
- The skill loads in Claude Code and in at least one other agent (Codex or Cursor) without modification.

## Left to the builder

- Exact wording of the "where to look" hints per check.
- Detection heuristics in `reference/detection.md`.
- Table formatting details and how the agent parses the existing `checklist.md` on a re-run.
- The forbidden-word list beyond the examples given.
- Whether to shorten long ASVS requirement texts in the table and how.
