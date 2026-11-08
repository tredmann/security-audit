# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Was dieses Repo ist

Dieses Repo enthält einen Agent-Skill (offenes Agent-Skills-Format: Ordner mit `SKILL.md` plus `scripts/`, `templates/`, `reference/`). Der Skill wird auf beliebige fremde Softwareprojekte angewendet. Er prüft das Zielprojekt gegen OWASP ASVS 5.0 (Standard Level 2) und erzeugt daraus eine Checkliste und eine öffentliche Security-Seite.

Die vollständige Spezifikation steht in `handover.md`. Sie ist die maßgebliche Quelle für Anforderungen, Abnahmekriterien und offene Entscheidungen. Vor Änderungen am Skill dort nachlesen.

Stand: Es existiert bisher nur `handover.md`. Es gibt noch keinen Code, keine Build-, Lint- oder Test-Befehle.

## Zwei Ebenen nicht verwechseln

- **Dieses Repo** = Quellcode des Skills (`SKILL.md`, `scripts/fetch_asvs.py`, `scripts/build_site.py`, `templates/*.j2`, `reference/*.md`).
- **Zielprojekt** = das Repo, in dem der Skill später läuft. Nur dort entstehen die Ausgaben: `security/asvs/asvs-5.0.json`, `security/asvs/<kapitel>.md`, `security/asvs/README.md`, `security/asvs/TODO.md`, `security/tools.yml` (pflegt der Nutzer), `security/site/index.html`, `SECURITY.md`, `.well-known/security.txt`.

Alle Pfade in Skill und Skripten sind relativ zum Projektordner des Zielprojekts.

## Architektur (geplant)

Datenfluss in einer Richtung:

1. `fetch_asvs.py` lädt ASVS 5.0 einmalig aus dem GitHub-Repo `OWASP/ASVS` (JSON/CSV-Export) nach `security/asvs/asvs-5.0.json`. Danach arbeitet alles offline. ASVS-Anforderungen nie aus dem Modellgedächtnis rekonstruieren.
2. Der Agent folgt `SKILL.md`: Scope abfragen (`reference/kapitel-scope.md`), Code lesen, pro Anforderung Status vergeben (`reference/status-regeln.md`), Kapitel-Tabellen schreiben.
3. `build_site.py` liest `security/asvs/` und `security/tools.yml` und rendert `SECURITY.md` und `index.html` aus denselben Daten. Beide müssen identische Zahlen und Datum enthalten.

Die Kapitel-Markdown-Tabellen sind gleichzeitig Ausgabe und Zustand für den nächsten Lauf. Ein zweiter Lauf prüft nur Einträge mit `offen` oder `teilweise` neu. Das Tabellenformat (Felder ID, Anforderung, Level, Status, Nachweis, Begründung, Geprüft am) muss deshalb von `build_site.py` stabil parsebar bleiben.

## Harte Regeln für den Skill

- Agent-neutral: keine Abhängigkeit von Tools eines bestimmten Agenten. Der Agent braucht nur: Dateien lesen, Shell ausführen, einmal eine URL laden. Skripte sind eigenständige Programme ohne Agent-SDK.
- Der Skill ändert keinen Code im Zielprojekt. Er schreibt nur in `security/`, `SECURITY.md` und `.well-known/`. Keine Scanner installieren, keine CI ändern.
- Status-Werte exakt: `erfüllt`, `teilweise`, `offen`, `nicht anwendbar`. `erfüllt` nie ohne Dateipfad/Zeile oder Konfigurationsschlüssel. Kein Nachweis gefunden heißt `offen`, nicht `teilweise`. Nicht relevante Kapitel werden mit Begründung `nicht anwendbar`, nicht gelöscht.
- ASVS-Anforderungen nicht umformulieren und keine eigenen hinzufügen.
- `TODO.md` sortiert nach ASVS-Level, Level 1 zuerst.
- `index.html` ohne Build-Schritt und ohne externes CSS/JS. `security.txt` nach RFC 9116.
- `description` im Frontmatter von `SKILL.md` muss die Auslöser nennen: `ASVS`, `Security-Checkliste`, `Security-Seite`, `SECURITY.md`, `Sicherheitsnachweis`.
- Sprache der erzeugten Dateien konfigurierbar, Standard Deutsch, Englisch als Option.

## Stil der erzeugten Texte

Kurze Sätze. Keine Gedankenstriche. Kein `nicht nur, sondern auch`. Keine Superlative oder Marketing-Sätze (`Sicherheit hat für uns höchste Priorität`). Zahlen, Dateipfade und Datumsangaben statt Adjektiven. Die Verbotsliste gehört in `SKILL.md` und wird in den Abnahmekriterien geprüft. Eine Seite mit 100 Prozent Erfüllung ist unglaubwürdig: offene Punkte werden benannt. Leere Abschnitte bleiben leer, kein Dummy-Text.

## Bekannte Spannung in der Spezifikation

Die Templates sind als Jinja2 (`.j2`) vorgesehen und `tools.yml` ist YAML. Beides braucht Python-Pakete außerhalb der Standardbibliothek (`jinja2`, `pyyaml`), während die Skripte eigenständig laufen sollen. Vor der Implementierung klären: Abhängigkeiten dokumentieren oder auf Standardbibliothek (z. B. `string.Template`, JSON statt YAML) ausweichen.

## Testen

Abnahme erfolgt gegen ein Testprojekt mit bekannten Lücken (empfohlen: OWASP Juice Shop). Die Checkliste der Abnahmekriterien steht am Ende von `handover.md`.
