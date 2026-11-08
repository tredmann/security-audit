# Security Audit Skill Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build an agent skill that checks a web application repository against 93 curated ASVS 5.0 requirements plus 12 additional practices and writes `security/checklist.md`, `security/TODO.md`, `security/contact.md` and `SECURITY.md` into that repository.

**Architecture:** This repository *is* the skill: `SKILL.md` at the root, `reference/` for the check catalog and detection heuristics, `templates/` for the output skeletons. No runtime code; the agent does the work by following `SKILL.md`. A `dev/` folder holds stdlib-only Python tooling used while authoring (ASVS extraction, consistency checks) and is not part of the skill's runtime. The skill is developed test-first as the writing-skills skill prescribes: baseline run without the skill, write the skill, run again, close gaps.

**Tech Stack:** Markdown (Agent Skills format, agentskills.io), Python 3 standard library for dev tooling, `unittest` for dev tests, Claude Code subagents for skill tests. Acceptance target: `../tory` (Laravel 13).

**Spec:** `docs/superpowers/specs/2026-11-08-security-audit-skill-design.md`

## Global Constraints

- Everything is English: skill text, reference files, templates, status values, generated output.
- Status values, exactly: `implemented`, `partial`, `not implemented`, `n/a`.
- `implemented` never without evidence (`path:line` or config key). Nothing found means `not implemented`, not `partial`.
- Never write a secret value into any output. Git-history findings cite commit hash and path only.
- The skill writes only `security/checklist.md`, `security/TODO.md`, `security/contact.md`, `SECURITY.md` in the target repo. It never modifies target code, never installs tools or dependencies, never runs `npm install`, `composer install` or similar.
- Dependency audit commands run only if the tool and the lock file are already present.
- `SECURITY.md` generated block sits between `<!-- security-audit:start -->` and `<!-- security-audit:end -->`; text outside is preserved byte for byte.
- Forbidden words in generated text: `robust`, `state of the art`, `state-of-the-art`, `best in class`, `best-in-class`, `industry leading`, `industry-leading`, `cutting edge`, `cutting-edge`, `top priority`, `highest priority`, `take security seriously`, `takes security seriously`, `committed to`, `world class`, `world-class`, `enterprise grade`, `enterprise-grade`, `military grade`, `military-grade`, `bank level`, `bank-level`, `not only`. No em dash (`—`) or en dash (`–`) in generated text.
- ASVS text is quoted from release asset `OWASP_Application_Security_Verification_Standard_5.0.0_en.flat.json` (tag `v5.0.0_release`), with CC BY-SA 4.0 attribution in `reference/asvs-checks.md` and in the `SECURITY.md` template.
- `SKILL.md` frontmatter: `name: security-audit`; `description` starts with "Use when", names triggering situations only (ASVS, security checklist, security audit, security self-assessment, SECURITY.md, security page, prove security practices), does not summarise the workflow, under 1024 characters.
- Agent-neutral: `SKILL.md` requires only reading files, searching, and running shell commands. No Claude-specific tool names in the skill or reference files.
- Repo-wide: commit after every task. Attribution line per the session's git guidance.

## Review Focus

1. Target repo already has a hand-written `SECURITY.md` without markers: the skill must ask (replace or append), never silently overwrite. Test in Task 9 step 6.
2. A secret value present in the target (`.env`, git history): no output file may contain it. Test in Task 9 step 7.
3. A file cited as evidence for an `implemented` row is deleted before a re-run: the row must move to `not implemented` or `partial` with a dated "Changes" entry. Test in Task 10 step 4.
4. Dependency audit tool absent (`composer` not on PATH): V15.2.1 is `not implemented` with reason "not verifiable locally, run `composer audit`", and nothing gets installed. Test in Task 9 step 8.
5. A conditional group whose condition is absent (no uploads): all five V5 rows appear with `n/a` and one shared reason, and `SECURITY.md` counts include them in the `n/a` column rather than dropping the chapter. Test in Task 9 step 5.

---

### Task 0: Repository baseline

**Files:**
- Create: `.gitignore`
- Existing: `CLAUDE.md`, `handover.md`, `docs/superpowers/specs/2026-11-08-security-audit-skill-design.md`, this plan

- [ ] **Step 1: Write `.gitignore`**

Contents: `__pycache__/`, `*.pyc`, `.DS_Store`, `dev/asvs-source/` (the downloaded ASVS JSON is not committed).

- [ ] **Step 2: Initial commit**

```bash
git add .gitignore CLAUDE.md handover.md docs/
git commit -m "chore: initial commit with handover, design and plan"
```

---

### Task 1: ASVS extraction tool

**Files:**
- Create: `dev/extract_asvs.py`
- Create: `dev/asvs-selection.txt`
- Create: `dev/tests/test_extract_asvs.py`
- Create (generated, committed): `dev/asvs-selected.json`

**Interfaces:**
- Produces: `dev/asvs-selected.json`: a JSON list of objects `{"id": "V6.2.1", "level": 1, "chapter_id": "V6", "chapter_name": "Authentication", "section_id": "V6.2", "section_name": "Password Security", "text": "<req_description>"}` sorted by chapter number, section number, requirement number.
- Produces: `dev/asvs-selection.txt`: one ASVS ID per line, `#` comments allowed. Exactly the 93 IDs from the spec's core and conditional lists (69 core, 24 conditional).
- Produces: `python3 dev/extract_asvs.py <flat.json> <selection.txt> <out.json>`; exits non-zero and names the ID if a selected ID is missing from the source or is Level 3.

- [ ] **Step 1: Write `dev/asvs-selection.txt`**

Copy the 69 core and 24 conditional IDs from the spec section "Scope of checks". Use `# core: <chapter>` and `# conditional: <condition>` comment lines to group them.

- [ ] **Step 2: Write the failing tests**

```python
# dev/tests/test_extract_asvs.py
import json, subprocess, sys, tempfile, unittest
from pathlib import Path

SRC = {"requirements": [
    {"chapter_id": "V6", "chapter_name": "Authentication", "section_id": "V6.2",
     "section_name": "Password Security", "req_id": "V6.2.1", "req_description": "Verify eight.", "L": "1"},
    {"chapter_id": "V6", "chapter_name": "Authentication", "section_id": "V6.2",
     "section_name": "Password Security", "req_id": "V6.2.9", "req_description": "Verify sixty-four.", "L": "2"},
    {"chapter_id": "V1", "chapter_name": "Encoding", "section_id": "V1.2",
     "section_name": "Injection", "req_id": "V1.2.4", "req_description": "Verify params.", "L": "1"},
    {"chapter_id": "V6", "chapter_name": "Authentication", "section_id": "V6.3",
     "section_name": "General", "req_id": "V6.3.3", "req_description": "Verify MFA.", "L": "3"},
]}

class ExtractTests(unittest.TestCase):
    def run_tool(self, selection):
        d = Path(tempfile.mkdtemp())
        (d / "src.json").write_text(json.dumps(SRC))
        (d / "sel.txt").write_text(selection)
        p = subprocess.run([sys.executable, "dev/extract_asvs.py", d / "src.json", d / "sel.txt", d / "out.json"],
                           capture_output=True, text=True)
        return p, d / "out.json"

    def test_extracts_selected_sorted_by_number(self):
        p, out = self.run_tool("# core\nV6.2.9\nV6.2.1\nV1.2.4\n")
        self.assertEqual(p.returncode, 0, p.stderr)
        data = json.loads(out.read_text())
        self.assertEqual([r["id"] for r in data], ["V1.2.4", "V6.2.1", "V6.2.9"])
        self.assertEqual(data[1], {"id": "V6.2.1", "level": 1, "chapter_id": "V6", "chapter_name": "Authentication",
                                   "section_id": "V6.2", "section_name": "Password Security", "text": "Verify eight."})

    def test_missing_id_fails_and_names_it(self):
        p, _ = self.run_tool("V6.2.1\nV9.9.9\n")
        self.assertNotEqual(p.returncode, 0)
        self.assertIn("V9.9.9", p.stderr)

    def test_level3_id_fails_and_names_it(self):
        p, _ = self.run_tool("V6.3.3\n")
        self.assertNotEqual(p.returncode, 0)
        self.assertIn("V6.3.3", p.stderr)

if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 3: Run tests to verify they fail**

Run: `python3 -m unittest dev/tests/test_extract_asvs.py -v`
Expected: 3 failures (file not found / returncode 2).

- [ ] **Step 4: Implement `dev/extract_asvs.py`**

`main(argv) -> int` with `load_selection(path) -> list[str]`, `extract(requirements: list[dict], ids: list[str]) -> list[dict]` (raises `ValueError` naming the offending ID), sort key `tuple(int(x) for x in id[1:].split("."))`. Stdlib only.

- [ ] **Step 5: Run tests to verify they pass**

Run: `python3 -m unittest dev/tests/test_extract_asvs.py -v`
Expected: `OK`

- [ ] **Step 6: Generate the real selection**

```bash
mkdir -p dev/asvs-source
curl -sL -o dev/asvs-source/asvs-5.0.0.flat.json \
  "https://github.com/OWASP/ASVS/releases/download/v5.0.0_release/OWASP_Application_Security_Verification_Standard_5.0.0_en.flat.json"
python3 -I dev/extract_asvs.py dev/asvs-source/asvs-5.0.0.flat.json dev/asvs-selection.txt dev/asvs-selected.json
python3 -I -c "import json; d=json.load(open('dev/asvs-selected.json')); print(len(d))"
```
Expected: `93`. If the download URL 404s, use `https://github.com/OWASP/ASVS/releases/latest/download/<same filename>`.

- [ ] **Step 7: Commit**

```bash
git add dev/
git commit -m "feat: ASVS extraction tool and selected requirements"
```

---

### Task 2: Baseline run without the skill (RED)

**Files:**
- Create: `docs/superpowers/testing/prompts/run-audit.md`
- Create: `docs/superpowers/testing/2026-11-08-baseline-tory.md`

**Interfaces:**
- Produces: the test prompt reused by Tasks 9 and 10.

- [ ] **Step 1: Write the test prompt**

`docs/superpowers/testing/prompts/run-audit.md`, verbatim:

> You are working in the repository at ../tory. Produce a security self-assessment of this application against OWASP ASVS 5.0 Level 2 that a customer could read, and a list of what is missing so the team can create tickets. Write your results into the repository. Do not change application code. When you are done, list the files you wrote.

- [ ] **Step 2: Confirm Tory is clean**

Run: `git -C ../tory status --short`
Expected: no output. If there is output, stop and ask the user.

- [ ] **Step 3: Dispatch a general-purpose subagent with the prompt from step 1 and no skill loaded**

Wait for completion. Then: `git -C ../tory status --short` and read every file it created.

- [ ] **Step 4: Record the baseline**

In `docs/superpowers/testing/2026-11-08-baseline-tory.md`, record, with verbatim quotes: which files were written and where; whether statuses were given without evidence; whether ASVS IDs were real (spot-check five against `dev/asvs-selected.json`); whether requirement text was invented or reworded; forbidden words used (run the grep from Task 7 step 3 over the output); whether sampling was disclosed; whether any secret value or `.env` content appeared; whether the agent asked about scope. Classify each failure as discipline (knew better, skipped), shape (wrong form), or omission, per the writing-skills "Match the Form to the Failure" table. This classification drives the form of `SKILL.md` in Task 7.

- [ ] **Step 5: Reset Tory**

```bash
git -C ../tory clean -fdn   # dry run, read the list
git -C ../tory clean -fd
git -C ../tory checkout -- .
git -C ../tory status --short
```
Expected: no output after the last command.

- [ ] **Step 6: Commit**

```bash
git add docs/superpowers/testing/
git commit -m "test: baseline audit run on Tory without the skill"
```

---

### Task 3: Reference file format and consistency checker

**Files:**
- Create: `dev/check_reference.py`
- Create: `dev/tests/test_check_reference.py`

**Interfaces:**
- Consumes: `dev/asvs-selected.json` (Task 1).
- Produces: the block format every ASVS entry in `reference/asvs-checks.md` must follow (Tasks 4 to 6 write to it):

```markdown
### V6.2.1 (Level 1, core)
**Requirement:** Verify that user set passwords are at least 8 characters in length although a minimum of 15 characters is strongly recommended.
**Where to look:** ...
**Implemented when:** ...
**Not implemented when:** ...
```
  Header forms: `(Level 1, core)`, `(Level 2, core, own-auth)` for the V6 block, `(Level 2, conditional: uploads)` for conditional entries. Condition keys are exactly: `own-auth`, `rich-text`, `outbound-urls`, `mail`, `xml`, `graphql`, `uploads`, `mfa`, `idp`, `multi-tenant`, `jwt`, `oauth-client`, `webserver-config`, `browser-storage`, `node-backend`.
- Produces: `python3 dev/check_reference.py reference/asvs-checks.md dev/asvs-selected.json`; exit 0 when every selected ID appears exactly once, every `**Requirement:**` line equals the official text, every entry has all four bold fields, and no entry exists for an unselected ID. Otherwise exit 1 and print one line per problem.

- [ ] **Step 1: Write the failing tests**

```python
# dev/tests/test_check_reference.py
import json, subprocess, sys, tempfile, unittest
from pathlib import Path

SEL = [{"id": "V6.2.1", "level": 1, "chapter_id": "V6", "chapter_name": "Authentication",
        "section_id": "V6.2", "section_name": "Password Security", "text": "Verify eight."}]
GOOD = """### V6.2.1 (Level 1, core, own-auth)
**Requirement:** Verify eight.
**Where to look:** registration validation.
**Implemented when:** min length >= 8.
**Not implemented when:** no rule.
"""

class CheckReferenceTests(unittest.TestCase):
    def run_tool(self, md):
        d = Path(tempfile.mkdtemp())
        (d / "ref.md").write_text(md); (d / "sel.json").write_text(json.dumps(SEL))
        return subprocess.run([sys.executable, "dev/check_reference.py", d / "ref.md", d / "sel.json"],
                              capture_output=True, text=True)

    def test_good_file_passes(self):
        self.assertEqual(self.run_tool(GOOD).returncode, 0)

    def test_reworded_requirement_fails(self):
        p = self.run_tool(GOOD.replace("Verify eight.", "Verify 8."))
        self.assertEqual(p.returncode, 1); self.assertIn("V6.2.1", p.stdout)

    def test_missing_field_fails(self):
        p = self.run_tool(GOOD.replace("**Not implemented when:** no rule.\n", ""))
        self.assertEqual(p.returncode, 1); self.assertIn("Not implemented when", p.stdout)

    def test_missing_id_fails(self):
        p = self.run_tool("# nothing\n")
        self.assertEqual(p.returncode, 1); self.assertIn("V6.2.1", p.stdout)

    def test_unknown_id_fails(self):
        p = self.run_tool(GOOD + GOOD.replace("V6.2.1", "V9.9.9"))
        self.assertEqual(p.returncode, 1); self.assertIn("V9.9.9", p.stdout)

    def test_bad_condition_key_fails(self):
        p = self.run_tool(GOOD.replace("own-auth", "login"))
        self.assertEqual(p.returncode, 1); self.assertIn("login", p.stdout)

if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python3 -m unittest dev/tests/test_check_reference.py -v`
Expected: 6 failures.

- [ ] **Step 3: Implement `dev/check_reference.py`**

`parse_entries(text: str) -> list[dict]` using a regex on `^### (V\d+\.\d+\.\d+) \((.*)\)$`; `check(entries, selected) -> list[str]` returning problem lines; `main(argv) -> int`. Keep the condition-key list as a module constant `CONDITIONS`.

- [ ] **Step 4: Run tests to verify they pass**

Run: `python3 -m unittest discover -s dev/tests -v`
Expected: `OK`, 9 tests.

- [ ] **Step 5: Commit**

```bash
git add dev/
git commit -m "feat: reference file consistency checker"
```

---

### Task 4: `reference/asvs-checks.md`, part 1 (V1 to V5)

**Files:**
- Create: `reference/asvs-checks.md`

**Interfaces:**
- Consumes: block format and condition keys from Task 3; official text from `dev/asvs-selected.json`.
- Produces: the file header (attribution, how to read an entry, the condition-key table) and entries for V1, V2, V3, V4, V5. Later tasks append.

- [ ] **Step 1: Write the file header**

Title, one paragraph: ASVS version 5.0.0, selection size 93, CC BY-SA 4.0 attribution with link to `https://github.com/OWASP/ASVS`, the sentence "Requirement text is quoted verbatim from the release; do not reword it." Then a table of condition keys with a one-line meaning each (the detection rules themselves live in `reference/detection.md`, Task 6).

- [ ] **Step 2: Write entries for V1, V2, V3, V4, V5 (28 entries)**

One `## Chapter` heading per chapter using `chapter_name` from the JSON. For each entry: official text; **Where to look** as two to four stack-neutral search strategies plus PHP/Laravel, Node and Python examples where the names differ (for example V1.2.4: `DB::raw`, `whereRaw`, string concatenation into `query(`, `->prepare(` without bindings; `knex.raw`, template literals in `.query(`; `cursor.execute(f"`); **Implemented when** and **Not implemented when** as concrete observable conditions. For `partial`, the general rule in `SKILL.md` applies, so entries do not repeat it unless the split is specific (for example V3.3.x where one cookie may be set correctly and another not).

- [ ] **Step 3: Run the checker, expecting only "missing" problems for V6 onwards**

Run: `python3 -I dev/check_reference.py reference/asvs-checks.md dev/asvs-selected.json | grep -v "^missing: V\(6\|7\|8\|9\|1[0-6]\)\." ; echo "exit $?"`
Expected: no other problem lines.

- [ ] **Step 4: Commit**

```bash
git add reference/asvs-checks.md
git commit -m "docs: ASVS checks V1-V5 with search hints"
```

---

### Task 5: `reference/asvs-checks.md`, part 2 (V6 to V10)

**Files:**
- Modify: `reference/asvs-checks.md` (append)

- [ ] **Step 1: Write entries for V6, V7, V8, V9, V10 (29 entries)**

Same shape as Task 4. V6 core entries carry `own-auth`. Hints must cover framework-provided controls (Laravel `Password::defaults()`, Fortify/Breeze/Filament auth, `session.lifetime`, `Auth::logoutOtherDevices`; Django `AUTH_PASSWORD_VALIDATORS`, `SESSION_COOKIE_AGE`; Express `express-session` options, Passport.js) and explicitly say where a framework default counts as evidence (cite the config file and key, for example `config/session.php: 'lifetime'`).

- [ ] **Step 2: Run the checker, expecting only V11 onwards missing**

Run: `python3 -I dev/check_reference.py reference/asvs-checks.md dev/asvs-selected.json | grep -v "^missing: V1[1-6]\." ; echo "exit $?"`
Expected: no other problem lines.

- [ ] **Step 3: Commit**

```bash
git add reference/asvs-checks.md
git commit -m "docs: ASVS checks V6-V10 with search hints"
```

---

### Task 6: `reference/asvs-checks.md` part 3 (V11 to V16), `reference/additional-practices.md`, `reference/detection.md`

**Files:**
- Modify: `reference/asvs-checks.md` (append)
- Create: `reference/additional-practices.md`
- Create: `reference/detection.md`

**Interfaces:**
- Produces: `additional-practices.md` entries in the same four-field shape with header `### AP-1: Dockerfile runs as a non-root user (conditional: dockerfile)` and a fifth field `**Reference:**` (exact reference string from the spec table). AP-1, AP-2 carry `(conditional: dockerfile)`; AP-3, AP-4, AP-5 `(conditional: compose)`; AP-8 to AP-11 `(conditional: ci)`, AP-11 additionally GitHub Actions only; AP-6, AP-7, AP-12 `(core)`. These three extra condition keys (`dockerfile`, `compose`, `ci`) are defined in `detection.md` and added to `CONDITIONS` in `dev/check_reference.py`.
- Produces: `detection.md` with one section per condition key (all 18) giving the observable predicate ("files matching `**/Dockerfile*` exist", "`composer.json` requires `laravel/passport` or `firebase/php-jwt` or `lcobucci/jwt`, or `package.json` depends on `jsonwebtoken`/`jose`", ...), plus a "Project picture" section listing what to read to fill the one-paragraph description (manifest, framework config, routes, migrations, Compose, CI).

- [ ] **Step 1: Write entries for V11 to V16 (36 entries)**

Same shape. V15.2.1 hint names the audit commands per ecosystem (`composer audit`, `npm audit --omit=dev`, `pip-audit`, `cargo audit`, `govulncheck ./...`) and the prerequisite rule (tool on PATH and lock file present, otherwise `not implemented` with reason "not verifiable locally, run `<command>`"). V13.3.1 and AP-7 hints state the redaction rule verbatim: cite path and commit hash, never the value.

- [ ] **Step 2: Run the checker, expecting a clean pass**

Run: `python3 -I dev/check_reference.py reference/asvs-checks.md dev/asvs-selected.json; echo "exit $?"`
Expected: `exit 0`, no problem lines.

- [ ] **Step 3: Add `dockerfile`, `compose`, `ci` to `CONDITIONS` in `dev/check_reference.py`; write `reference/additional-practices.md`**

12 entries, header shape from Interfaces. Run `python3 -m unittest discover -s dev/tests` afterwards. Expected: `OK`.

- [ ] **Step 4: Write `reference/detection.md`**

18 condition sections plus "Project picture". Each predicate must be checkable with file search and `grep` only.

- [ ] **Step 5: Commit**

```bash
git add reference/ dev/check_reference.py
git commit -m "docs: ASVS checks V11-V16, additional practices, detection rules"
```

---

### Task 7: Templates and the wording check

**Files:**
- Create: `templates/checklist.md`
- Create: `templates/TODO.md`
- Create: `templates/contact.md`
- Create: `templates/SECURITY.md`
- Create: `dev/tests/test_templates.py`

**Interfaces:**
- Produces: `templates/checklist.md` with header block fields `ASVS version: 5.0.0`, `Target level: 2`, `Last run: <YYYY-MM-DD>`, `Project:` (paragraph), `Scope:` (table: condition key, applies yes/no, reason); then one `## <chapter_name>` per ASVS chapter in the selection and `## Additional practices`, each with the table header `| ID | Level | Requirement | Status | Evidence | Reason | Checked |`; then `## Changes` with the line format `- YYYY-MM-DD <ID> <old> → <new>: <one sentence>` (this arrow is the one permitted use of a non-ASCII dash-like character; it is not a sentence dash).
- Produces: `templates/TODO.md` entry format:
  ```
  ### <ID> (Level <n>) <short requirement>
  Status: <partial | not implemented>
  Found: <one or two sentences>
  Suggestion: <one concrete action>
  ```
  Sections in order: `## Level 1`, `## Level 2`, `## Additional practices`.
- Produces: `templates/contact.md` with `Contact:`, `Response time:`, `PGP key:` (optional) lines.
- Produces: `templates/SECURITY.md` with `<!-- security-audit:start -->`, the seven section headings from the spec in order, the fixed disclaimer sentence "This is a self-assessment based on the source code and configuration. It is not a penetration test and makes no claim that the system is free of vulnerabilities.", the fixed attribution line "Requirement text from OWASP ASVS 5.0.0, CC BY-SA 4.0.", `<!-- security-audit:end -->` after section 6, and section 7 outside the markers with the line "No external assessments yet."
- Produces: the forbidden-word grep used by `SKILL.md` and by tests:
  ```bash
  grep -n -i -E "robust|state[- ]of[- ]the[- ]art|best[- ]in[- ]class|industry[- ]leading|cutting[- ]edge|top priority|highest priority|takes? security seriously|committed to|world[- ]class|enterprise[- ]grade|military[- ]grade|bank[- ]level|not only|—|–" <files>
  ```
  Exit 1 (no match) means clean.

- [ ] **Step 1: Write the failing test**

```python
# dev/tests/test_templates.py
import subprocess, unittest
from pathlib import Path

GREP = r"robust|state[- ]of[- ]the[- ]art|best[- ]in[- ]class|industry[- ]leading|cutting[- ]edge|top priority|highest priority|takes? security seriously|committed to|world[- ]class|enterprise[- ]grade|military[- ]grade|bank[- ]level|not only|—|–"

class TemplateTests(unittest.TestCase):
    def test_templates_exist(self):
        for name in ["checklist.md", "TODO.md", "contact.md", "SECURITY.md"]:
            self.assertTrue(Path("templates", name).exists(), name)

    def test_templates_are_free_of_forbidden_words(self):
        p = subprocess.run(["grep", "-n", "-i", "-E", GREP] + [str(x) for x in Path("templates").glob("*.md")],
                           capture_output=True, text=True)
        self.assertEqual(p.returncode, 1, p.stdout)

    def test_security_template_has_markers_and_disclaimer(self):
        t = Path("templates/SECURITY.md").read_text()
        self.assertLess(t.index("<!-- security-audit:start -->"), t.index("<!-- security-audit:end -->"))
        self.assertIn("It is not a penetration test", t)
        self.assertLess(t.index("<!-- security-audit:end -->"), t.index("## Further evidence"))

    def test_checklist_template_has_table_header_and_changes(self):
        t = Path("templates/checklist.md").read_text()
        self.assertIn("| ID | Level | Requirement | Status | Evidence | Reason | Checked |", t)
        self.assertIn("## Changes", t)

if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run to verify it fails**

Run: `python3 -m unittest dev/tests/test_templates.py -v`
Expected: 4 failures.

- [ ] **Step 3: Write the four templates**

Per Interfaces. Placeholders in angle brackets. Chapter headings in `checklist.md` and the results table in `SECURITY.md` list all 16 ASVS chapters V1 to V16 (each has at least one selected requirement; verify with `python3 -I -c "import json; print(sorted({r['chapter_id'] for r in json.load(open('dev/asvs-selected.json'))}, key=lambda c: int(c[1:])))"`).

- [ ] **Step 4: Run to verify it passes**

Run: `python3 -m unittest discover -s dev/tests -v`
Expected: `OK`.

- [ ] **Step 5: Commit**

```bash
git add templates/ dev/tests/test_templates.py
git commit -m "feat: output templates and wording check"
```

---

### Task 8: `SKILL.md` (GREEN)

**Files:**
- Create: `SKILL.md`
- Create: `dev/tests/test_skill_md.py`

**Interfaces:**
- Consumes: `docs/superpowers/testing/2026-11-08-baseline-tory.md` (Task 2) for the failure classification; reference and template files from Tasks 4 to 7.
- Produces: the skill entry point. **REQUIRED SUB-SKILL:** superpowers:writing-skills for structure, description rules and the form-matching table.

- [ ] **Step 1: Write the failing test**

```python
# dev/tests/test_skill_md.py
import re, unittest
from pathlib import Path

class SkillMdTests(unittest.TestCase):
    def setUp(self):
        self.text = Path("SKILL.md").read_text()
        m = re.match(r"^---\n(.*?)\n---\n", self.text, re.S)
        self.assertIsNotNone(m, "frontmatter missing"); self.fm = m.group(1)

    def test_frontmatter_name_and_description(self):
        self.assertIn("name: security-audit", self.fm)
        desc = re.search(r"^description: (.*)$", self.fm, re.M).group(1)
        self.assertTrue(desc.startswith("Use when"), desc)
        self.assertLess(len(self.fm), 1024)
        for kw in ["ASVS", "security checklist", "security audit", "self-assessment", "SECURITY.md"]:
            self.assertIn(kw, desc)

    def test_status_vocabulary_and_rules(self):
        for s in ["`implemented`", "`partial`", "`not implemented`", "`n/a`"]:
            self.assertIn(s, self.text)
        self.assertIn("security-audit:start", self.text)
        self.assertIn("never", self.text.lower())

    def test_references_bundled_files(self):
        for f in ["reference/asvs-checks.md", "reference/additional-practices.md", "reference/detection.md",
                  "templates/checklist.md", "templates/TODO.md", "templates/contact.md", "templates/SECURITY.md"]:
            self.assertIn(f, self.text, f)

    def test_no_agent_specific_tool_names(self):
        for tool in ["Read tool", "Edit tool", "Bash tool", "Grep tool", "Glob tool", "TodoWrite"]:
            self.assertNotIn(tool, self.text, tool)

if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run to verify it fails**

Run: `python3 -m unittest dev/tests/test_skill_md.py -v`
Expected: fails (file missing).

- [ ] **Step 3: Write `SKILL.md`**

Sections, in this order; aim for under 700 words of body text, details stay in the reference files:

1. Frontmatter (`name`, `description` per Global Constraints).
2. **What the agent needs:** read files, search files, run shell commands. Nothing else.
3. **What this produces** and the seven-step procedure from the spec ("Procedure"), each step one to three sentences pointing at the reference or template file it uses. Step 2 names the single confirmation question shape: project picture paragraph, then "Conditions detected: ... Conditions not detected: ... Is this correct?". Step 3 contains the re-run rules verbatim from the spec. Step 5 the contact question and `security/contact.md`. Step 6 the existing-`SECURITY.md` rule (markers; ask replace or append).
4. **Status rules:** the four values, the `implemented`-needs-evidence rule, the not-found-is-`not implemented` rule, the group `n/a` rule, the sampling rule, the redaction rule. Written as a positive contract (what a row IS), per the writing-skills form table, because the baseline failures to fix are shape and omission failures. Add prohibitions only for discipline failures the baseline actually showed; quote each baseline rationalization in a small table with its counter.
5. **Writing rules** with the forbidden-word grep from Task 7 as the final self-check command, run over the four output files; "exit 1 means clean".
6. **Boundaries:** writes only the four files; never changes code; never installs; audit prerequisite rule; the closing reminder about `security/` not being public while open items remain.
7. **Common mistakes** (from the baseline), five or fewer bullets.

- [ ] **Step 4: Run to verify it passes**

Run: `python3 -m unittest discover -s dev/tests -v`
Expected: `OK`.

- [ ] **Step 5: Word count check**

Run: `sed '1,/^---$/d' SKILL.md | sed '1,/^---$/d' | wc -w`
Expected: under 900. If over, move detail into the reference files.

- [ ] **Step 6: Commit**

```bash
git add SKILL.md dev/tests/test_skill_md.py
git commit -m "feat: SKILL.md procedure, status and writing rules"
```

---

### Task 9: First run with the skill on Tory (GREEN verification)

**Files:**
- Create: `docs/superpowers/testing/2026-11-08-run1-tory.md`
- Modify (as needed): `SKILL.md`, `reference/*.md`, `templates/*.md`

- [ ] **Step 1: Install the skill for this machine**

```bash
mkdir -p ~/.claude/skills
ln -sfn "$(pwd)" ~/.claude/skills/security-audit
ls -la ~/.claude/skills/security-audit/SKILL.md
```
Expected: the symlink resolves. The symlink is not committed.

- [ ] **Step 2: Confirm Tory is clean** (as Task 2 step 2).

- [ ] **Step 3: Dispatch a general-purpose subagent with the Task 2 prompt, prefixed by one line: "Use the security-audit skill at ~/.claude/skills/security-audit/SKILL.md."**

The subagent will ask the scope confirmation and the contact question; answer "yes, correct" and "security@example.com, 5 business days, no PGP key" via SendMessage.

- [ ] **Step 4: Evaluate against the spec's acceptance list and record in `docs/superpowers/testing/2026-11-08-run1-tory.md`**

Check and quote: files written are exactly `security/checklist.md`, `security/TODO.md`, `security/contact.md`, `SECURITY.md`; scope detection named Laravel, the database, Filament login, Passport/Sanctum tokens, Compose; every row has a status; `grep -c "| implemented |" security/checklist.md` rows all have a non-empty Evidence cell (script: awk over the table, or read); `TODO.md` entry count equals the number of `partial` plus `not implemented` rows; `SECURITY.md` per-chapter counts equal the checklist's; forbidden-word grep over the four files exits 1; `git -C ../tory diff --stat` shows no changes to application files.

- [ ] **Step 5: Review Focus 5 (absent conditional group)**

Identify one condition `detection.md` says is absent in Tory (candidates: `graphql`, `node-backend`, `rich-text`). Confirm its rows appear in `checklist.md` with `n/a` and one shared reason, and that the `SECURITY.md` chapter table counts them under `n/a`. Record.

- [ ] **Step 6: Review Focus 1 (existing SECURITY.md)**

Reset Tory (Task 2 step 5). Create `../tory/SECURITY.md` containing `# Security\n\nReport issues to the maintainers.\n`. Re-run step 3. Expected: the subagent asks replace or append before writing. Answer "append". Expected: the original two lines are still at the top, byte for byte (`head -3`). Record.

- [ ] **Step 7: Review Focus 2 (secret values)**

Run: `grep -o -E "^[A-Z_]*(KEY|SECRET|PASSWORD|TOKEN)=.+$" ../tory/.env 2>/dev/null | cut -d= -f2- | grep -v '^$' > <scratchpad>/secrets.txt` then `grep -F -f <scratchpad>/secrets.txt security/checklist.md security/TODO.md SECURITY.md` in Tory. Expected: no matches (exit 1). If `.env` has no such values, place a `.env` with `APP_KEY=base64:TESTSECRETVALUE123` temporarily and repeat. Remove it afterwards. Record.

- [ ] **Step 8: Review Focus 4 (audit tool absent)**

Re-run step 3 with `PATH` restricted so `composer` is not found: prefix the subagent prompt with "Run every shell command with `PATH=/usr/bin:/bin`." Expected: V15.2.1 is `not implemented`, reason contains "not verifiable locally, run `composer audit`", `vendor/` unchanged (`git status` clean apart from the four output files). Record.

- [ ] **Step 9: Fix what failed (REFACTOR)**

For each failure, edit the owning file (`SKILL.md`, a reference entry, a template). Match the form to the failure as in Task 8 step 3. Re-run the failing step until it passes. Record each fix and its re-run in the run1 file.

- [ ] **Step 10: Reset Tory, commit**

Reset as Task 2 step 5.
```bash
git add docs/superpowers/testing/ SKILL.md reference/ templates/
git commit -m "test: first skill run on Tory and fixes"
```

---

### Task 10: Re-run behaviour

**Files:**
- Create: `docs/superpowers/testing/2026-11-08-run2-tory.md`
- Modify (as needed): `SKILL.md`

- [ ] **Step 1: Run the skill on clean Tory** (Task 9 step 3). Keep the output files in place. Save copies: `cp -r security <scratchpad>/run-a-security; cp SECURITY.md <scratchpad>/run-a-SECURITY.md` (inside Tory).

- [ ] **Step 2: Run again on the unchanged repo**

Same prompt. Expected: only the scope confirmation question (no contact question, since `security/contact.md` exists); `diff -r <scratchpad>/run-a-security security` shows no status changes and no new "Changes" lines; `diff <scratchpad>/run-a-SECURITY.md SECURITY.md` empty or date-only. Record.

- [ ] **Step 3: Full re-check on request**

Prompt suffix: "Re-check every requirement, including implemented ones." Expected: every `Checked` date is today, statuses unchanged. Record.

- [ ] **Step 4: Review Focus 3 (evidence removed)**

Pick one `implemented` row whose evidence is a single file not needed by other rows (prefer an AP row such as AP-5 `.dockerignore`, or a config file row). Move that file aside: `mv <file> <scratchpad>/aside`. Run the skill. Expected: that row is now `not implemented` or `partial`, `## Changes` has a dated line `<ID> implemented → <new>`, `SECURITY.md` "Changes" shows the same line. Restore the file. Record.

- [ ] **Step 5: Fix what failed, re-run the failing step, record.**

- [ ] **Step 6: Reset Tory, commit**

```bash
git add docs/superpowers/testing/ SKILL.md reference/ templates/
git commit -m "test: re-run behaviour on Tory and fixes"
```

---

### Task 11: Stack neutrality check (OWASP Juice Shop)

**Files:**
- Create: `docs/superpowers/testing/2026-11-08-run-juice-shop.md`
- Modify (as needed): `reference/detection.md`, `reference/asvs-checks.md`

- [ ] **Step 1: Clone into an isolated directory**

```bash
mkdir -p <scratchpad>/juice && git clone --depth 1 https://github.com/juice-shop/juice-shop.git <scratchpad>/juice/juice-shop
```
Do not run `npm install`.

- [ ] **Step 2: Run the skill** with the Task 2 prompt pointed at that path. Answer the two questions as in Task 9.

- [ ] **Step 3: Evaluate**

Expected: detection names Node/Express, Angular frontend, SQLite/Sequelize, JWT (`jsonwebtoken`), no Compose at root (Juice Shop ships a Dockerfile; `dockerfile` applies, `compose` does not); `node-backend` and `jwt` groups applied; V15.2.1 `not implemented` with the audit reason unless `npm` and lock file present and `npm audit` runs offline (it will not; record what happened). Known Juice Shop weaknesses should surface as `not implemented`: at least V1.2.4 (raw SQL in login), V11.4.2 (MD5 password hashing), V9.1.2 or V9.1.1 (JWT handling). Record which were found.

- [ ] **Step 4: Fix detection or hint gaps that are stack-specific to PHP, re-run, record.**

- [ ] **Step 5: Commit**

```bash
git add docs/superpowers/testing/ reference/
git commit -m "test: stack neutrality run on Juice Shop"
```

---

### Task 12: Repository documentation

**Files:**
- Modify: `CLAUDE.md`
- Create: `README.md`
- Modify: `handover.md` (one line at the top)

- [ ] **Step 1: Rewrite `CLAUDE.md`**

Replace the "Architektur (geplant)" and rules sections with the as-built structure: repo is the skill; `dev/` tooling and how to run the tests (`python3 -m unittest discover -s dev/tests -v`), how to regenerate `dev/asvs-selected.json` (Task 1 step 6), how to run the consistency checker, how to install for local testing (Task 9 step 1), how to run a skill test on Tory (Task 9 steps 2 to 4). Point to the design doc as the source of truth and drop the "Bekannte Spannung" section (resolved: no scripts). Keep it in English.

- [ ] **Step 2: Write `README.md`**

For a person installing the skill: what it checks (one paragraph, link to `reference/asvs-checks.md`), what it writes, how to install in Claude Code (`~/.claude/skills/security-audit`), Codex and Cursor (`~/.agents/skills/` alias), how to run it ("ask your agent to run a security audit / create a SECURITY.md"), the privacy note about `security/`, licence note for ASVS text.

- [ ] **Step 3: Mark `handover.md` as superseded**

Insert as first line: `> Superseded by docs/superpowers/specs/2026-11-08-security-audit-skill-design.md on 2026-11-08. Kept for history.`

- [ ] **Step 4: Second-agent load check**

Run: `ls ~/.agents/skills/ 2>/dev/null; which codex cursor-agent 2>/dev/null`. If Codex or Cursor CLI is installed: `ln -sfn "$(pwd)" ~/.agents/skills/security-audit`, start the agent in `../tory`, ask "which skills do you have for a security audit?" and confirm `security-audit` is listed. Record the result in the README install section. If neither is installed, write "not verified on a second agent" in the README and in the run2 test file; do not claim otherwise.

- [ ] **Step 5: Run all dev tests one last time**

Run: `python3 -m unittest discover -s dev/tests -v && python3 -I dev/check_reference.py reference/asvs-checks.md dev/asvs-selected.json`
Expected: `OK` and exit 0.

- [ ] **Step 6: Commit**

```bash
git add CLAUDE.md README.md handover.md
git commit -m "docs: README, CLAUDE.md as built, mark handover superseded"
```
