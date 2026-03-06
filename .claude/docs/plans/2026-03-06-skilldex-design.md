# Skilldex Design

## Problem
1.016+ Skills installiert, kein schneller Weg den richtigen zu finden. Scrolling durch Skill-Listen ist langsam und unstrukturiert.

## Solution
Interaktives TUI-Verzeichnis aufrufbar via `/skilldex`. Kategorisiert alle Skills nach Purpose ("Warum brauche ich diesen Skill?"), navigierbar mit Pfeiltasten und Fuzzy-Search via fzf.

## Architecture

### Components

| Datei | Zweck |
|-------|-------|
| `~/.claude/commands/skilldex.md` | Slash-Command, ruft `skilldex.sh` auf |
| `~/.claude/bin/skilldex.sh` | Hauptscript |
| `~/.claude/skilldex-rules.json` | 10 Kategorien mit Keywords + Subkategorien |
| `~/.claude/skilldex-overrides.json` | Manuelle Zuordnungen (Skill → Kategorie) |
| `~/.claude/skilldex-cache.tsv` | Generierter Index |

### Flow

```
/skilldex → skilldex.sh
  → Cache aktuell? → ja → lade Cache
                    → nein → scanne ~/.claude/skills/*/SKILL.md
                           → kategorisiere per Rules + Overrides
                           → schreibe Cache
  → fzf mit Preview
  → User wählt → Output: /skill-name
```

### Dependencies
- `fzf` (install via `brew install fzf`)
- Standard Unix tools (grep, sed, jq)

## 10 Kategorien

Jede Kategorie beantwortet "Warum brauche ich diesen Skill?"

| # | Kategorie | Why? | Subkategorien |
|---|-----------|------|---------------|
| 1 | Planen | "Weil ich etwas strukturiert angehen muss" | Projektplanung, Architektur, Brainstorming |
| 2 | Code | "Weil ich am Code arbeiten muss" | Schreiben, Review, Debugging |
| 3 | Testen | "Weil ich Qualitat sicherstellen muss" | Unit/E2E, Performance, Security-Tests |
| 4 | Deployen | "Weil ich ausliefern oder Infra managen muss" | CI/CD, Cloud, Container |
| 5 | Security | "Weil ich Sicherheit pruefen muss" | Audit, Pentest, Hardening |
| 6 | Automatisieren | "Weil ich Services anbinden muss" | SaaS-Tools, Workflows, Bots |
| 7 | Content | "Weil ich Inhalte erstellen muss" | Writing, Marketing, SEO |
| 8 | Daten | "Weil ich mit Daten arbeiten muss" | Datenbanken, Pipelines, ML/AI |
| 9 | Recherche | "Weil ich erst verstehen muss" | Analyse, Deep Research, Docs |
| 10 | Agenten | "Weil ich Agenten orchestrieren muss" | Multi-Agent, Swarm, Memory |

## Kategorisierung

### Hybrid-Ansatz
1. `skilldex-rules.json` definiert Keywords pro Kategorie/Subkategorie
2. Script matcht Skill-Name + Description gegen Keywords
3. Ein Skill darf in mehreren Kategorien erscheinen (Multi-Match)
4. `skilldex-overrides.json` erlaubt manuelle Korrekturen

### Cache-Invalidierung
Cache wird neu gebaut wenn:
- `skilldex-cache.tsv` nicht existiert
- Skill-Anzahl in `~/.claude/skills/` sich geaendert hat
- Rules oder Overrides neuer als Cache

## fzf-Interface

```bash
fzf --ansi \
    --header="Skilldex - Pfeiltasten navigieren, Enter bestaetigen, Esc abbrechen" \
    --preview="cat ~/.claude/skills/{skill}/SKILL.md | head -40" \
    --preview-window=right:50%:wrap
```

Format der Eintraege: `Kategorie > Subkategorie > skill-name`
Fuzzy-Search durchsucht alle drei Ebenen gleichzeitig.

## Output
Bei Enter: gibt `/skill-name` aus, bereit zum Einfuegen ins Claude Code CLI.
Bei Esc: bricht ab, keine Ausgabe.
