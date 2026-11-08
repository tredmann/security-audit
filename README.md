# security-audit

An agent skill that checks a repository against OWASP ASVS 5.0 and writes a checklist and a public `SECURITY.md`.

## What it checks

93 requirements from ASVS 5.0.0 (Level 1 and Level 2, selected for typical web applications and APIs) plus 12 additional practices such as secrets handling and dependency updates. Each is checked from source and configuration, not by running the application. Requirements for features the project does not have (for example XML parsing) are marked `n/a` with a reason. The full list is in [reference/asvs-checks.md](reference/asvs-checks.md) and [reference/additional-practices.md](reference/additional-practices.md).

Every row gets one status: `implemented`, `partial`, `not implemented` or `n/a`. `implemented` needs evidence (a `path:line` or a config key). Runs are repeatable: a second run re-checks open rows, verifies evidence of implemented rows and logs every status change with a date.

## What it writes

In the target repository:

- `security/checklist.md`: all rows with status and evidence. It is the state for the next run.
- `security/TODO.md`: open rows, Level 1 first. Regenerated on every run; hand edits are lost.
- `security/contact.md`: contact address and response time.
- `SECURITY.md`: counts per chapter, practices, changes, contact. The generated part sits between `<!-- security-audit:start -->` and `<!-- security-audit:end -->`. Text outside the markers is never touched. If a `SECURITY.md` without markers exists, the skill asks whether to replace or append.

It changes no code, configuration or CI and installs nothing.

## Install

Claude Code:

```sh
ln -sfn /path/to/this/repo ~/.claude/skills/security-audit
```

Agents that read `~/.agents/skills/`:

```sh
mkdir -p ~/.agents/skills
ln -sfn /path/to/this/repo ~/.agents/skills/security-audit
```

Verified only on Claude Code. Not verified on a second agent: neither Codex nor Cursor CLI was available when this was written.

## Use

Open your agent in the project and ask for a security audit, an ASVS check or a `SECURITY.md`. The skill asks you 2 questions (is the detected project scope correct, who is the security contact) and, if needed, a 3rd about an existing `SECURITY.md`. It waits for your answers.

## Privacy

`security/checklist.md` and `security/TODO.md` list unfixed weaknesses with file locations. Do not publish them while open items remain. `SECURITY.md` contains no file paths and is meant to be public.

## Licence

The ASVS requirement text is by OWASP under CC BY-SA 4.0 (https://github.com/OWASP/ASVS). The licence for the rest of this repository is not decided yet.

## Development

See `CLAUDE.md` for tests, regenerating the ASVS selection and running skill tests. Test records are in `docs/superpowers/testing/`.
