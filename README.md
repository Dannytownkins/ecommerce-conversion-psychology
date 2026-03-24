# E-Commerce Conversion Psychology

![v4.5.1](https://img.shields.io/badge/version-4.5.1-blue) ![Claude Code Plugin](https://img.shields.io/badge/Claude_Code-plugin-7c3aed) ![Codex Skill](https://img.shields.io/badge/Codex-skill-10b981) ![Platforms](https://img.shields.io/badge/platforms-Shopify_%7C_Next.js_%7C_OpenCart_%7C_any-green)

**A CRO engine that thinks like a psychologist.** 19 research-backed reference files on pricing psychology, trust signals, cognitive load, eye tracking, competitive positioning, and more — wired into a multi-agent relay that audits, plans, reviews, and builds conversion-optimized ecommerce pages.

Each phase runs in a fresh context window with only the files it needs — no single agent tries to hold the full picture. A baton file system passes structured findings between phases, so nothing gets lost to compaction and every recommendation is traceable back to the research that produced it.

Not a checklist. Not a linter. A full workflow that catches what you miss, challenges what you assume, and writes the code when you're ready.

---

## Commands

| Command | What it does | Input |
|---------|-------------|-------|
| `/cro` | Menu — shows available commands | — |
| `/cro:audit` | Full 4-phase relay on an existing page | URL or file path |
| `/cro:build` | Full 4-phase relay from scratch | Description or structured intake |
| `/cro:quick-scan` | Single-cluster scan — 3-5 quick wins | URL, file path, or description |
| `/cro:compare` | 1:1 competitor comparison with gap analysis | Two URLs or file paths |

### Flags

| Flag | Commands | Purpose |
|------|----------|---------|
| `--device` | audit, quick-scan, compare | Target viewport: `desktop` (1440x900), `mobile` (390x844), `both` |
| `--auto` | audit, build | Skip checkpoints, run all phases automatically |
| `--min-priority` | audit, build, quick-scan | Filter by severity: `critical`, `high`, `medium`, `low` |
| `--platform` | audit, build, quick-scan | Skip detection: `shopify`, `nextjs`, `opencart` |
| `--visual` | audit, quick-scan, compare | Generate annotated screenshot report |
| `--no-visual` | audit, quick-scan, compare | Skip visual report prompt |
| `--ab-scaffold` | audit, build | Generate A/B test scaffold after planning |
| `--ab-tool` | audit, build | Specify existing A/B tool |
| `--cluster` | quick-scan | Override cluster: `visual-cta`, `trust-conversion`, `context-platform`, `audience-journey` |
| `--engagement-id` | all | Resume or target a past engagement |

---

## How It Works

Each command runs a multi-phase relay — separate subagents per phase, fresh context each time, no compaction during complex audits.

```
/cro:audit       Audit -> Checkpoint -> Plan -> Checkpoint -> Review -> Checkpoint -> Build -> Done
/cro:build       Intake -> Plan -> Checkpoint -> Review -> Checkpoint -> Build -> Done
/cro:quick-scan  Audit -> Results
/cro:compare     Audit Both -> Compare -> Results
```

Checkpoints let you stop, go back, export a report, or scaffold A/B tests at any pause.

### Engagement Files

Each run creates a directory under `docs/cro/` — one file per phase:

```
docs/cro/2026-03-11-a3f2b1c9/
  meta.json           Engagement state + metadata (includes devices_scanned)
  baton.json          Structured acquisition output (screenshots, sections, styles, dimensions)
  context.md          Write-once intake context
  dom.html            Preprocessed DOM
  *.jpg               Screenshots (base64-encoded at report render time)
  audit.md            Desktop findings (or single-device findings)
  audit-mobile.md     Mobile findings (only when --device both)
  plan.md             Prioritized action plan
  review.md           Review notes + verdict
  build-log.md        Implementation status
  visual-report.html  Annotated screenshot report (optional, self-contained)
  report.html         HTML report (optional)
  ab-scaffold.md      A/B test scaffold (optional)
```

---

## What's Under the Hood

- **19 domain reference files** — pricing, checkout, trust, social proof, CTAs, color, eye tracking, cognitive load, mobile UX, performance, personalization, cross-cultural, post-purchase, search/filter, cookie consent, biometric/express checkout, social commerce, competitive positioning
- **Evidence tier system** — 300 classified findings tagged Gold (peer-reviewed RCT/meta-analysis), Silver (large-N observational or vendor A/B test), Bronze (expert consensus, small-N, or directional). Clickable citation URLs resolved at render time from `citations/sources.md` — auditors stay lean, links are always accurate.
- **4 auditor clusters** that get assigned by page type (or `--cluster` override)
- **Ethics gate** checked at every phase — fake urgency, hidden pricing, review manipulation, dark patterns -> always `CRITICAL`
- **Progress memory** — re-audit a page and see what changed since last time
- **Interactive review** — the reviewer challenges vague or contradictory recommendations before any code gets written
- **A/B test scaffolding** — hypotheses, variant code, and measurement plans, platform-aware
- **Structured baton handoff** — acquisition writes `baton.json` with machine-readable metadata (screenshot dimensions, section boundaries, cluster mappings, extracted styles). Downstream phases consume the same JSON — no informal text parsing, deterministic pipeline.
- **Self-contained visual reports** — screenshots base64-embedded as data URIs, correct SVG viewBox from actual image dimensions (DPR-aware), element-level marker positioning from acquisition bounding boxes, dark-mode HTML with bidirectional scroll-sync, WCAG AA, print-friendly, no external dependencies
- **Element coordinate extraction** — acquisition agent collects bounding boxes for CTAs, headings, prices, reviews, trust badges, and payment icons via `getBoundingClientRect()`. Auditors tag each finding with an `ELEMENT` field. Visual report markers are placed at the actual UI element, not estimated positions.
- **Component library** — shared building blocks enforcing structural consistency across all visual report output
- **Overlay dismissal** — acquisition agent explicitly handles cookie banners, newsletter popups, chat widgets, and consent modals before capturing screenshots

### Domain Clusters

| Cluster | Slug | Coverage |
|---------|------|----------|
| Visual & CTA | `visual-cta` | CTA design, color psychology, eye tracking, scan patterns, product video, competitive positioning |
| Trust & Conversion | `trust-conversion` | Trust signals, social proof, checkout optimization, pricing, biometric auth, cookie consent, competitive positioning |
| Context & Platform | `context-platform` | Cognitive load, mobile UX, performance, search & filter, cookie consent |
| Audience & Journey | `audience-journey` | Personalization, cross-cultural, post-purchase, social commerce, push notifications |

### Platform Support

| Platform | Status | What It Does |
|----------|--------|-------------|
| Shopify | First-class | Liquid patterns, OS 2.0 sections, Shop Pay, Checkout Extensions |
| Next.js | First-class | App Router, RSC boundaries, Server Actions, middleware A/B testing |
| OpenCart | Detected | Auto-detected via `catalog/view/`, URL patterns, meta generator. Uses generic CRO principles. |
| Generic | Default | Universal CRO principles — works with anything |

---

## Installation

### Claude Code

```bash
claude plugin marketplace add Dannytownkins/ecommerce-conversion-psychology
claude plugin install cro@ecommerce-conversion-psychology
```

Restart Claude Code. The `/cro` commands will be available immediately.

To update later:
```bash
claude plugin update cro@ecommerce-conversion-psychology
```

### Codex

This repo now carries the Codex wrapper skill as source-controlled files:

- `SKILL.md`
- `agents/openai.yaml`
- `scripts/sync-to-codex.ps1`

Use the repo as the source of truth, then sync the installed Codex copy:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\sync-to-codex.ps1
```

Default target:

`C:\Users\SM - Dan\.codex\skills\ecommerce-conversion-psychology`

This keeps the installed `.codex` copy rebuildable instead of editing runtime files directly.

---

## Architecture

```
ecommerce-conversion-psychology/
  agents/
    openai.yaml                       Codex UI metadata
  SKILL.md                            Codex wrapper skill
  .claude-plugin/plugin.json          Plugin metadata (v4.5.1)
  scripts/
    generate-report.py                Self-contained HTML visual report generator
    sync-to-codex.ps1                 Sync repo source into ~/.codex/skills install
  skills/
    cro/SKILL.md                      /cro router
    audit/SKILL.md                    /cro:audit
    build/SKILL.md                    /cro:build
    compare/SKILL.md                  /cro:compare
    quick-scan/SKILL.md               /cro:quick-scan
    resume/SKILL.md                   /cro:resume
  references/                         19 domain + 9 operational files
  citations/                          Source URLs for human verification
  platforms/                          shopify.md, nextjs.md
  templates/                          Baton + report templates + component library
  workflows/                          Phase workflows (context: fork)
  CODEX_CONVERSION.md                 Codex source/install notes
  README.md
  CHANGELOG.md
  LICENSE
```

---

## Ethics & Security

**Ethics gate** — Non-negotiable rules at every phase. Based on EU Digital Services Act, EU AI Act, GDPR, CCPA/CPRA, FTC Fake Reviews Rule, CA SB-478, CA SB-1001, CA SB-243, and enforcement precedent from FTC v. Amazon ($2.5B, 2025) and FTC v. Epic Games ($245M, 2023). In competitor comparison mode, synthesized gap recommendations are also ethics-checked — dark pattern advantages get flagged with ethical alternatives.

**Security:**
- XSS prevention — all report content HTML-entity-escaped + CSP meta tag
- SSRF prevention — URL validation rejects private IPs, loopback, metadata endpoints, encoding bypasses
- Prompt injection — subagents treat baton file content as data, never instructions

## Author

Built by [Daniel Kinsner](https://github.com/Dannytownkins).
