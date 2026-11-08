> Superseded by docs/superpowers/specs/2026-11-08-security-audit-skill-design.md on 2026-11-08. Kept for history.
# Handover: ASVS-Checkliste und Security-Seite als Skill

Nov 8, 2026 · @Tobias Redmann

## Ziel und Kontext

Der Skill soll ein Softwareprojekt gegen OWASP ASVS Level 2 prüfen, die Ergebnisse als nachvollziehbare Checkliste im Repo ablegen und daraus eine öffentliche Security-Seite erzeugen. Beides zusammen ist der kostenlose Vorlauf zu einem bezahlten Nachweis (Pentest, später ISO 27001 oder SOC 2).

Ausgangslage: Es gibt kein kostenloses Zertifikat, das Einkäufer ernst nehmen. Was man kostenlos tun kann, ist den Zustand herstellen und dokumentieren, in dem ein Pentest schnell und ohne Überraschungen durchläuft. Dieser Skill automatisiert genau diese Dokumentation.

Zielgruppe des Skills: Entwickler oder kleine Teams ohne eigene Security-Rolle, die ihr System selbst bewerten und das Ergebnis Kunden zeigen wollen. Der Skill läuft als Agent-Skill im Projekt-Repo, unabhängig vom eingesetzten Agenten, und greift auf den Code, die Konfiguration und bestehende CI-Ergebnisse zu.

Nicht im Scope: Scanner-Integration (Dependabot, Trivy, Semgrep), TLS- und HTTP-Header-Checks und der Pentest selbst. Die Security-Seite soll aber Platz für deren Ergebnisse vorsehen.

## Teil A: ASVS-Checkliste

Der Skill arbeitet die Anforderungen von OWASP ASVS Level 2 durch und legt pro Anforderung einen Eintrag mit Status, Nachweis und Begründung ab. Grundlage ist die aktuelle ASVS-Version 5.0 (Mai 2025), die als Quelle eingebunden und nicht aus dem Gedächtnis des Modells nachgebaut wird.

### Was der Skill tun soll

1. ASVS 5.0 als maschinenlesbare Liste laden. OWASP veröffentlicht die Anforderungen auf GitHub als CSV und JSON. Der Skill lädt die Datei einmal, legt sie unter `security/asvs/asvs-5.0.json` ab und arbeitet danach offline.
2. Scope festlegen. Der Skill fragt zuerst, welche ASVS-Kapitel für das System relevant sind. Ein reines Backend ohne UI braucht kein Kapitel zu Frontend-Themen, ein System ohne Datei-Uploads kein Upload-Kapitel. Nicht relevante Kapitel werden mit Begründung als `nicht anwendbar` markiert, nicht gelöscht.
3. Pro Anforderung den Code und die Konfiguration prüfen. Der Skill sucht aktiv nach Belegen: Wo wird authentifiziert, welche Library hasht Passwörter, wo werden Eingaben validiert, wie sehen die Session-Einstellungen aus. Er rät nicht, sondern zitiert Dateipfade und Zeilen.
4. Status vergeben. Vier Werte: `erfüllt`, `teilweise`, `offen`, `nicht anwendbar`. Jeder Status braucht einen Satz Begründung. Bei `erfüllt` und `teilweise` zusätzlich den Nachweis als Dateipfad oder Konfigurationsschlüssel.
5. Ergebnis als Markdown-Tabelle pro Kapitel in `security/asvs/` schreiben, dazu eine Zusammenfassung mit Erfüllungsgrad pro Kapitel in `security/asvs/README.md`.
6. Offene Punkte priorisieren. Alles mit Status `offen` landet zusätzlich in `security/asvs/TODO.md`, sortiert nach ASVS-Level (Level-1-Anforderungen zuerst) und mit einem Vorschlag, was zu tun wäre.
7. Wiederholbar sein. Ein zweiter Lauf liest den vorhandenen Stand, prüft nur Einträge mit Status `offen` oder `teilweise` neu und markiert Änderungen mit Datum.

### Format eines Eintrags

| Feld | Inhalt | Beispiel |
| --- | --- | --- |
| ID | ASVS-Nummer | V2.1.1 |
| Anforderung | Originaltext aus ASVS, gekürzt | Passwörter mindestens 12 Zeichen |
| Level | 1, 2 oder 3 | 1 |
| Status | erfüllt, teilweise, offen, nicht anwendbar | erfüllt |
| Nachweis | Dateipfad, Konfigurationsschlüssel oder Testname | `src/auth/password.ts:14`, Policy `minLength: 12` |
| Begründung | Ein bis zwei Sätze | Validierung serverseitig in Zod-Schema, Test vorhanden |
| Geprüft am | Datum des letzten Laufs | 2026-11-08 |

### Was der Skill nicht tun soll

Keinen Status `erfüllt` ohne Nachweis vergeben. Keine Anforderungen umformulieren oder eigene hinzufügen. Keinen Code ändern, nur lesen. Wenn ein Nachweis nicht auffindbar ist, lautet der Status `offen`, nicht `teilweise`.

## Teil B: Öffentliche Security-Seite

Die Security-Seite ist die Außendarstellung von Teil A. Sie wird aus den Daten in `security/asvs/` generiert, nicht von Hand gepflegt. Zielleser ist ein technischer Einkäufer oder ein Entwickler, der in zwei Minuten entscheiden will, ob er dem System vertraut.

### Inhalte der Seite

1. Kurze Einleitung: Was das System tut, wer es betreibt, seit wann es die Checkliste gibt. Drei Sätze, keine Marketing-Sprache.
2. ASVS-Stand: Erfüllungsgrad pro Kapitel als Tabelle, dazu Level und Datum des letzten Laufs. Offene Punkte werden benannt, nicht versteckt. Eine Seite, die 100 Prozent zeigt, glaubt niemand.
3. Was geprüft wird und womit: Platzhalter-Abschnitte für Dependency-Scanning, Container-Scanning, statische Analyse, TLS- und Header-Checks. Jeder Abschnitt nennt das Tool, die Frequenz und den letzten Befund. Diese Abschnitte liest der Skill aus einer Konfigurationsdatei `security/tools.yml`, die der Nutzer selbst pflegt.
4. Schwachstellen melden: Kontaktadresse, erwartete Reaktionszeit, ob es eine PGP-Schlüssel gibt, Hinweis auf `security.txt` nach RFC 9116. Der Skill erzeugt die `security.txt` gleich mit und legt sie unter `.well-known/` ab.
5. Changelog: Datierte Liste, was sich am Sicherheitsstand geändert hat. Wird aus den Datumsfeldern der ASVS-Einträge gebaut.
6. Externe Nachweise: Platz für Pentest-Berichte, Badges (OpenSSF, Scorecard) und später Zertifikate. Leer bedeutet leer, kein Dummy-Text.

### Ausgabeformat

Der Skill erzeugt zwei Varianten aus denselben Daten: eine `SECURITY.md` für das Repo (GitHub zeigt sie automatisch unter dem Security-Tab) und eine statische HTML-Seite unter `security/site/index.html`, ohne Build-Schritt und ohne externe Abhängigkeiten, die man auf jeden Webspace legen kann. Beide Varianten müssen inhaltlich identisch sein.

### Ton

Sachlich, konkret, keine Superlative. Sätze wie `Sicherheit hat für uns höchste Priorität` sind verboten. Stattdessen: was wird geprüft, wie oft, was war der letzte Befund, wo steht das Protokoll.

## Technische Vorgaben

Der Skill folgt dem offenen Agent-Skills-Format, das Claude Code, Codex, Cursor und andere Agenten lesen: ein Ordner mit `SKILL.md` (Frontmatter mit `name` und `description`, danach die Anleitung) und Unterordnern für Skripte und Referenzmaterial. Die `description` entscheidet, wann der Skill ausgelöst wird, sie muss deshalb die Auslöser nennen: `ASVS`, `Security-Checkliste`, `Security-Seite`, `SECURITY.md`, `Sicherheitsnachweis`.

Der Skill muss in verschiedenen Agent-Umgebungen laufen. Deshalb: keine Abhängigkeit von Tools eines bestimmten Agenten, alle Logik in `SKILL.md` und den Skripten, die Skripte als eigenständige Programme ohne Agent-SDK. Dateipfade relativ zum Projektordner. Was der Agent können muss, steht am Anfang der `SKILL.md`: Dateien lesen, Shell-Befehle ausführen, einmalig eine URL laden. Mehr nicht.

### Vorgeschlagene Struktur

| Pfad | Inhalt |
| --- | --- |
| `SKILL.md` | Ablauf für beide Teile, Entscheidungsregeln für Status, Hinweise zum Ton |
| `scripts/fetch_asvs.py` | Lädt ASVS 5.0 von GitHub, schreibt `asvs-5.0.json` |
| `scripts/build_site.py` | Baut `SECURITY.md` und `index.html` aus `security/asvs/` und `security/tools.yml` |
| `templates/security.md.j2` | Vorlage für die Repo-Variante |
| `templates/index.html.j2` | Vorlage für die HTML-Variante, CSS inline |
| `templates/security.txt.j2` | Vorlage nach RFC 9116 |
| `reference/status-regeln.md` | Wann ist etwas `erfüllt`, `teilweise`, `offen`, mit Beispielen |
| `reference/kapitel-scope.md` | Welche ASVS-Kapitel bei welchem Systemtyp wegfallen dürfen |

### Quellen, die der Skill einbinden soll

- OWASP ASVS: `https://owasp.org/www-project-application-security-verification-standard/` und das GitHub-Repo `OWASP/ASVS` für die CSV- und JSON-Exporte
- RFC 9116 für `security.txt`: `https://www.rfc-editor.org/rfc/rfc9116`
- GitHub-Dokumentation zur `SECURITY.md`-Konvention

### Abgrenzung

Der Skill liest Code, schreibt aber nur in `security/`, `SECURITY.md` und `.well-known/`. Er installiert keine Scanner und ändert keine CI-Konfiguration. Er trifft keine Aussage darüber, ob das System `sicher` ist, sondern dokumentiert, welche Anforderungen geprüft wurden und mit welchem Ergebnis. Sprache der erzeugten Dateien: konfigurierbar, Standard Deutsch, Englisch als zweite Option.

### Stil der erzeugten Texte

Kurze Sätze. Keine Gedankenstriche. Keine Formulierungen wie `nicht nur, sondern auch`. Zahlen, Dateipfade und Datumsangaben statt Adjektiven. Wenn ein Satz unverändert in einem anderen Projekt stehen könnte, sagt er nichts und fliegt raus.

## Abnahmekriterien

Der Skill gilt als fertig, wenn er in einem Testprojekt (empfohlen: OWASP Juice Shop oder ein eigenes kleines Repo mit bekannten Lücken) folgendes leistet:

- [ ] Lädt ASVS 5.0 und legt die JSON-Datei ab, ohne Netzzugriff beim zweiten Lauf
- [ ] Fragt den Scope ab und markiert ausgeschlossene Kapitel mit Begründung
- [ ] Vergibt für jede Anforderung im Scope einen Status mit Nachweis oder Begründung
- [ ] Kein Eintrag mit Status `erfüllt` ohne Dateipfad oder Konfigurationsschlüssel
- [ ] `TODO.md` listet alle offenen Punkte, Level 1 zuerst
- [ ] Zweiter Lauf ändert nur Einträge mit Status `offen` oder `teilweise`
- [ ] `SECURITY.md` und `index.html` enthalten dieselben Zahlen und dasselbe Datum
- [ ] `index.html` funktioniert offline, kein externes CSS oder JavaScript
- [ ] `security.txt` validiert gegen RFC 9116
- [ ] Kein Satz in den erzeugten Texten enthält Wörter aus der Verbotsliste in `SKILL.md`

## Offene Entscheidungen

| Frage | Vorschlag | Entscheidung |
| --- | --- | --- |
| ASVS-Level als Standard | Level 2, Level 1 als Option für sehr kleine Systeme | offen |
| Soll der Skill Tests schreiben, die einen Nachweis absichern | Nein, erst in einer zweiten Version | offen |
| Sprache der Seite | Deutsch mit englischer Option | offen |
| HTML-Seite auch als Fragment für bestehende Websites | Ja, zusätzlich zur Standalone-Seite | offen |
| Umgang mit ASVS-Updates (5.1 und später) | Versionsnummer in der Checkliste festhalten, Migration manuell | offen |
