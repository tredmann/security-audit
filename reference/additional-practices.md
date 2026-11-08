# Additional practices

Twelve practices outside ASVS, reported in a separate group. Each entry has four fields after the header, in this order: **Reference** (the source of the practice), **Where to look**, **Implemented when**, **Not implemented when**. Statuses are the same four as for ASVS checks: `implemented`, `partial`, `not implemented`, `n/a`. Cite `path:line` or a config key for every `implemented`. Do not assume a default; cite the file and key.

The header gives the applicability. `core` entries apply to every repository. `conditional: <key>` entries apply only when the condition holds; the detection rules are in `reference/detection.md`. If the condition does not hold, the status is `n/a`.

Absence of the feature is `n/a`. Absence of an unsafe pattern is `implemented` with the search cited (patterns, directories, hit count). `partial` means the primary instance is correct and secondary ones are missing; it never describes the same situation as `not implemented`.

## Containers

### AP-1: Dockerfile runs as a non-root user (conditional: dockerfile)
**Reference:** CIS Docker Benchmark 4.1
**Where to look:** Find every Dockerfile (`**/Dockerfile*`, `*.dockerfile`). Read the final stage of each: the last `FROM` and everything after it. Look for a `USER` instruction naming a non-root user or numeric id, and for `useradd`, `adduser`, `addgroup` or `groupadd` before it. Check that `USER root` does not follow. Compose `user:` keys and Kubernetes `runAsUser` or `runAsNonRoot` in committed manifests count as additional evidence for the same service. Images whose base sets a non-root user must be shown by a `USER` line in the repository, not assumed.
**Implemented when:** The final stage of every Dockerfile sets `USER` to a non-root user (not `root`, not `0`) and no later `USER root` undoes it. Cite Dockerfile:line.
**Not implemented when:** The final stage of the primary Dockerfile has no `USER` instruction or ends as `root`. `partial` is the case where the primary Dockerfile is correct and a secondary one (worker, cron, tooling image) is not; name it as path:line.

### AP-2: Base images pinned to a version or digest, not `latest` (conditional: dockerfile)
**Reference:** OpenSSF Scorecard: Pinned-Dependencies
**Where to look:** Read every `FROM` line in every Dockerfile, including multi-stage builds and `ARG`-driven images (`FROM ${BASE}`; resolve the `ARG` default). Look for the tag: none, `latest`, a major tag, a full version tag, or an `@sha256:` digest. Stage names that refer to an earlier stage (`FROM build AS final`) are not external images.
**Implemented when:** Every external base image carries an explicit version tag or an `@sha256:` digest. A digest is the stronger evidence; a precise version tag is accepted. Cite the `FROM` lines at path:line.
**Not implemented when:** The primary Dockerfile uses `latest` or no tag for an external base image. `partial` is the case where the primary Dockerfile pins and a secondary one does not, or images are pinned to a floating tag such as a bare major version; name them as path:line.

### AP-3: No `privileged: true`, no Docker socket mount in Compose (conditional: compose)
**Reference:** CIS Docker Benchmark 5.4, 5.31
**Where to look:** Read every Compose file (`compose*.y*ml`, `docker-compose*.y*ml`, `**/docker-compose*.yml`, including override files). Search `privileged:`, `cap_add:` (`SYS_ADMIN`, `ALL`), `pid: host`, `network_mode: host`, and volume entries mentioning `docker.sock` (for example `/var/run/docker.sock`). Check each service, including tooling services such as reverse proxies or CI runners.
**Implemented when:** No service sets `privileged: true` and none mounts the Docker socket. Cite the search (patterns, files covered, hit count).
**Not implemented when:** A service in the primary Compose file sets `privileged: true` or mounts the Docker socket. `partial` is the case where the primary Compose file is clean and an override or secondary file (development, tooling) does it; name it as path:line and say which file is used where.

### AP-4: Database and cache ports not published to the host in Compose (conditional: compose)
**Reference:** OWASP Docker Security Cheat Sheet
**Where to look:** Read the `ports:` list of every database and cache service in every Compose file (images or service names such as `mysql`, `mariadb`, `postgres`, `redis`, `valkey`, `mongo`, `memcached`, `elasticsearch`). Compare with `expose:`, which keeps the port on the internal network only. Look at the host side of each mapping: `"3306:3306"` publishes on all interfaces; `"127.0.0.1:3306:3306"` binds to loopback. Check override files that add ports.
**Implemented when:** No database or cache service publishes a port to the host (only `expose:` or no mapping), or a mapping binds explicitly to `127.0.0.1`. Cite Compose file:line.
**Not implemented when:** A database or cache service in the primary Compose file publishes a port on all interfaces (`ports: - "5432:5432"`). `partial` is the case where the primary Compose file is clean and a secondary Compose file (override, development) publishes ports; name it as path:line. A loopback-only mapping counts as not published.

### AP-5: `.dockerignore` excludes `.git`, `.env`, dependency folders (conditional: dockerfile)
**Reference:** OWASP Docker Security Cheat Sheet
**Where to look:** Find `.dockerignore` next to each Dockerfile or at the build context root named in Compose `build.context`. Check it for `.git`, `.env` (or `.env*`), and the dependency folders of the stack (`node_modules`, `vendor`, `.venv`, `__pycache__`). Then check how the Dockerfile copies: `COPY . .` makes the ignore file matter; copying named paths only does not. Without a `.dockerignore`, a `COPY . .` sends everything in the context.
**Implemented when:** A `.dockerignore` exists for each build context and excludes `.git`, `.env` files and the dependency folders; or the Dockerfile copies only named paths and never the whole context. Cite `.dockerignore` lines or the `COPY` lines.
**Not implemented when:** A Dockerfile uses `COPY . .` or `ADD . ` and no `.dockerignore` exists, or it exists and does not exclude `.git` and `.env`. `partial` is the case where `.git` and `.env` are excluded and dependency folders are not, or only some build contexts have a correct file; name what is missing.

## Secrets and repository hygiene

### AP-6: `.env` and secret files are gitignored; an `.env.example` exists (core)
**Reference:** OWASP Secrets Management Cheat Sheet
**Where to look:** Read `.gitignore` files (root and the application root) for `.env`, `.env.*`, `*.pem`, `*.key`, `secrets/`, credentials files. Confirm with `git ls-files` that no such file is tracked, and that `.env.example` (or `.env.sample`, `.env.dist`) is tracked and holds keys with placeholder values. Check the example for real-looking values; report them by path and key name only. For stacks without env files (for example config in Vault or CI variables only), look for the equivalent template.
**Implemented when:** Real env and secret files are ignored and none is tracked (cite `.gitignore` lines and the `git ls-files` result), and a tracked example file lists the required keys with placeholders. Cite both paths.
**Not implemented when:** A real `.env` or secret file is tracked, or `.gitignore` does not cover it. `partial` is the case where files are ignored and untracked and no example file documents the required keys, or the example file holds real-looking values (never quote them).

### AP-7: No secrets in git history (pattern scan over `git log -p`) (core)
**Reference:** OWASP Secrets Management Cheat Sheet
**Where to look:** Scan the full history for patterns and keep only commit hash and path in the output. Stack-neutral recipe, run from the repository root: `git log --all -G'(AKIA[0-9A-Z]{16}|-----BEGIN (RSA |EC |OPENSSH )?PRIVATE KEY-----|APP_KEY=base64:)' --format=%H --name-only`, and a second, case-insensitive run: `git log --all -i -G'(password|passwd|secret|api_key|aws_secret_access_key|token|_key)[[:space:]]*[=:][[:space:]]*.{8,}' --format=%H --name-only`. `-i` makes `DB_PASSWORD=` and `AWS_SECRET_ACCESS_KEY=` match. `-G` takes a regular expression; with `--format=%H --name-only` the output is only the commit hash and changed file names, never the matching line. Add provider patterns that apply (for example `ghp_[0-9A-Za-z]{36}`, `xox[abp]-`, `sk_live_`). A dedicated scanner on PATH (`gitleaks`, `trufflehog`) may be used if present, with its redaction option on; never install one. Redaction rule: record hash and path, cite path and commit hash, never the value, never the line content; never run a command that prints the matching line unredacted (`git log -p | grep`, plain `git show`). Placeholders (`changeme`, `example`, empty values) are not secrets. To judge a hit, use a redacting command such as `git show <hash> -- <path> | sed -E 's/([=:]).*/\1<redacted>/'`, which keeps key names and removes values; copy nothing from it into any output file.
**Implemented when:** The scan over all refs found no real secret. Cite the command, the number of commits scanned and the hit count (0, or only placeholders with their paths).
**Not implemented when:** A real secret appears in any commit of the history, even if the file was later deleted; list path and commit hash only. `partial` is the case where the scan covered only part of the history (shallow clone, one branch) and found nothing; state what was covered. If `git` history is unavailable, the reason is "not verifiable locally, no git history".

## CI and supply chain

### AP-8: Dependency update automation configured (Dependabot, Renovate) (core)
**Reference:** OpenSSF Scorecard: Dependency-Update-Tool
**Where to look:** Look for `.github/dependabot.yml` or `.github/dependabot.yaml`, `renovate.json`, `renovate.json5`, `.renovaterc`, `.renovaterc.json`, a `renovate` key in `package.json`, `.gitlab/renovate*`, `.github/renovate.json`, and CI jobs running a renovate bot. Read the configured ecosystems (`package-ecosystem` entries, Renovate `enabledManagers`) and compare with the ecosystems found in the repository (composer, npm, pip, docker, github-actions).
**Implemented when:** `.github/dependabot.yml` (or `.yaml`), `renovate.json`, `renovate.json5` or a `.renovaterc*` file exists (or one of the other Renovate locations above), and it covers every dependency ecosystem the repository uses. Cite the file and the ecosystem entries. A CI system is not required.
**Not implemented when:** Neither a Dependabot nor a Renovate configuration exists in any of the locations above. `partial` is the case where a configuration exists and omits an ecosystem the repository uses (for example `docker` or `github-actions`); name the missing ones.

### AP-9: CI runs a dependency vulnerability audit (conditional: ci)
**Reference:** OpenSSF Scorecard: Vulnerabilities
**Where to look:** Read the CI definitions: GitHub Actions `.github/workflows/*.yml`, GitLab CI `.gitlab-ci.yml` and included files, Bitbucket Pipelines `bitbucket-pipelines.yml`, CircleCI `.circleci/config.yml`, Jenkinsfile, Azure `azure-pipelines.yml`. Search for audit steps: `composer audit`, `npm audit`, `pip-audit`, `cargo audit`, `govulncheck`, `osv-scanner`, `trivy`, `snyk`, `dependency-review-action`, GitLab `Dependency-Scanning.gitlab-ci.yml` template, Bitbucket pipes for scanning. Check the job runs on pull requests or pushes and its failure is not suppressed (`continue-on-error: true`, `|| true`, `allow_failure: true`).
**Implemented when:** A CI job runs a dependency audit on pull requests or pushes for the main ecosystem, and failures are not suppressed. Cite file:line of the step.
**Not implemented when:** No CI file contains a dependency audit step. `partial` is the case where an audit step exists and is suppressed (`continue-on-error`, `|| true`, `allow_failure`) or covers only one of several ecosystems; name which.

### AP-10: CI runs static analysis (SAST) (conditional: ci)
**Reference:** OpenSSF Scorecard: SAST
**Where to look:** In the same CI definitions as AP-9 (GitHub Actions, GitLab CI, Bitbucket Pipelines, CircleCI, Jenkinsfile, Azure Pipelines), search for security-oriented static analysis: `github/codeql-action`, `semgrep`, `bandit`, `psalm --taint-analysis`, `phpstan` with security rules, `eslint-plugin-security`, `sonar`, `njsscan`, `brakeman`, GitLab `SAST.gitlab-ci.yml` template. General linters and type checkers alone do not count. Check the job runs on pull requests or pushes and failures are not suppressed.
**Implemented when:** A CI job runs a security-oriented static analyzer on pull requests or pushes, and failures are not suppressed. Cite file:line of the step.
**Not implemented when:** No CI file runs a security static analyzer. `partial` is the case where the analyzer step exists and is suppressed or runs only on a schedule or a branch that is not the main one; name which.

### AP-11: CI workflow token permissions are minimal (GitHub Actions only) (conditional: ci)
**Reference:** OpenSSF Scorecard: Token-Permissions
**Where to look:** If the CI system is not GitHub Actions (no `.github/workflows/*.yml`), the status is `n/a` with the reason "CI is not GitHub Actions"; name the CI system found. Otherwise read each workflow file for a top-level `permissions:` block and per-job `permissions:`. Look for `permissions: write-all`, `contents: write` at workflow level, and workflows with no `permissions:` key at all (they then inherit the repository default, which the repository does not show). Read the values; job-level `write` scopes (for example `packages: write`, `id-token: write`) are acceptable when they are scoped to the job that needs them.
**Implemented when:** Every workflow sets a top-level `permissions:` block with read-only scopes (for example `contents: read`), and any write scope is granted at job level for a job that needs it. Cite file:line.
**Not implemented when:** A workflow sets `write-all` or a broad write scope at workflow level, or the main workflow has no `permissions:` key at all. `partial` is the case where the primary workflow is correct and a secondary one is not; name it as path:line.

### AP-12: `SECURITY.md` with a contact exists (core)
**Reference:** OpenSSF Scorecard: Security-Policy
**Where to look:** Look for `SECURITY.md` at the repository root, in `.github/` or in `docs/`, and run `git ls-files SECURITY.md .github/SECURITY.md docs/SECURITY.md` to see which is tracked. Two sources can name a contact. First, text outside the `security-audit` markers that names a way to report a vulnerability (an email address, a private reporting form or advisory page, a security contact URL); it counts in every case. Second, the generated "Reporting a vulnerability" section between the markers, filled from `security/contact.md`; it counts only when the file is git-tracked (`git ls-files` prints its path). A file this run creates is untracked.
**Implemented when:** Text outside the markers names a private reporting contact (cite path:line), or the file is git-tracked and the generated "Reporting a vulnerability" section names the contact from `security/contact.md` (cite the `git ls-files` command and its output, and `security/contact.md`).
**Not implemented when:** No text outside the markers names any contact, and the file is untracked or does not exist yet. The reason is then "generated, not yet committed" when this run writes the generated section, and "no `SECURITY.md`" otherwise. `partial` is the case where the file is untracked or missing and text outside the markers names only a general contact (for example a project issue tracker) and no private channel; name it as path:line.
