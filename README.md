# E-Commerce Conversion Psychology

![v4.6.0](https://img.shields.io/badge/version-4.6.0-blue) ![Claude Code Plugin](https://img.shields.io/badge/Claude_Code-plugin-7c3aed) ![Platforms](https://img.shields.io/badge/platforms-Shopify_%7C_Next.js_%7C_OpenCart_%7C_any-green)

**A CRO engine that thinks like a psychologist.** 19 research-backed reference files on pricing psychology, trust signals, cognitive load, eye tracking, competitive positioning, and more — wired into a multi-agent relay that audits, plans, reviews, and builds conversion-optimized ecommerce pages.

Each phase runs in a fresh context window with only the files it needs. A baton file system passes structured findings between phases, so nothing gets lost to compaction and every recommendation is traceable back to the research that produced it.

Not a checklist. Not a linter. A full workflow that catches what you miss, challenges what you assume, and writes the code when you're ready.

---

## Components

| Type | Count | Description |
|------|-------|-------------|
| Skills | 6 | Coordinator commands (`/cro:audit`, `/cro:build`, `/cro:quick-scan`, `/cro:compare`, `/cro:resume`, `/cro` router) |
| Workflows | 11 | Phase workflows dispatched to subagents (acquire, audit, plan, review, build, compare, quick-scan, visual-report, report, reconcile, ab-scaffold) |
| References | 28 | 19 domain files (300+ classified findings) + 9 operational files (ethics, evidence tiers, URL validation, etc.) |
| Templates | 16 | HTML report templates, component library, device frames, metadata schemas |
| Platforms | 2 | Shopify (Liquid, OS 2.0, Shop Pay), Next.js (App Router, RSC, Server Actions) |
| Scripts | 1 | Python visual report generator (structured JSON + auto-matching markers) |

---

## Commands

| Command | What it does | Input |
|---------|-------------|-------|
| `/cro` | Menu — routes to the right command | — |
| `/cro:audit` | Full 4-phase relay on an existing page | URL or file path |
| `/cro:build` | Build a new page from scratch | Description or structured intake |
| `/cro:quick-scan` | Single-cluster scan — 3-5 findings | URL, file path, screenshot, or description |
| `/cro:compare` | 1:1 competitor comparison with gap analysis | Two URLs or file paths |
| `/cro:resume` | List and resume in-progress engagements | Optional `--engagement-id` |

### Flags

| Flag | Commands | Purpose |
|------|----------|---------|
| `--device` | audit, quick-scan, compare | Target viewport: `mobile` (390x844), `laptop` (1440x900), `desktop` (1920x1080), or comma pair |
| `--auto` | audit, build | Skip checkpoints, run all phases automatically |
| `--min-priority` | audit, build, quick-scan | Filter: `critical`, `high`, `medium`, `low` |
| `--platform` | audit, build, quick-scan | Skip detection: `shopify`, `nextjs`, `opencart` |
| `--visual` / `--no-visual` | audit, quick-scan, compare | Generate or skip annotated screenshot report |
| `--ab-scaffold` | audit, build | Generate A/B test scaffold after planning |
| `--cluster` | quick-scan | Override cluster selection |
| `--engagement-id` | all | Resume or target a past engagement |

---

## How It Works

```
/cro:audit       Audit -> Plan -> Review -> Build  (checkpoints between each phase)
/cro:build       Intake -> Plan -> Review -> Build  (checkpoints between each phase)
/cro:quick-scan  Audit -> Results
/cro:compare     Audit Both -> Compare -> Results
```

### Engagement Files

Each run creates a directory under `docs/cro/`:

```
docs/cro/2026-03-25-a3f2b1c9/
  meta.json           Engagement state + metadata
  baton.json          Structured acquisition output (screenshots, sections, styles)
  context.md          Write-once intake context
  dom.html            Preprocessed DOM
  *.jpg               Screenshots (base64-encoded at report render time)
  audit.md            Findings (+ audit-mobile.md for two-device mode)
  plan.md             Prioritized action plan
  review.md           Review notes + verdict (APPROVE / REVISE / BLOCK)
  build-log.md        Implementation status
  visual-report.html  Annotated screenshot report (optional, self-contained)
```

---

## Key Features

- **Evidence tier system** — 300+ classified findings tagged Gold (peer-reviewed), Silver (large-N observational), Bronze (expert consensus). Citation URLs resolved at render time.
- **4 auditor clusters** assigned by page type: visual-cta, trust-conversion, context-platform, audience-journey
- **Ethics gate** at every phase — fake urgency, hidden pricing, review manipulation, dark patterns are always CRITICAL
- **Progress memory** — re-audit a page and see what changed since last time
- **Interactive review** — the reviewer challenges vague or contradictory recommendations before code gets written
- **Self-contained visual reports** — dark-mode HTML with base64 screenshots, element-level markers, bidirectional scroll-sync, WCAG AA
- **Structured baton handoff** — `baton.json` carries screenshot dimensions, section boundaries, element coordinates, and extracted styles between phases
- **Multi-device support** — mobile (390x844 3x DPR), laptop (1440x900), desktop (1920x1080), or scan two devices per run
- **A/B test scaffolding** — hypotheses, variant code, and measurement plans, platform-aware

### Domain Clusters

| Cluster | Slug | Coverage |
|---------|------|----------|
| Visual & CTA | `visual-cta` | CTA design, color psychology, eye tracking, scan patterns, competitive positioning |
| Trust & Conversion | `trust-conversion` | Trust signals, social proof, checkout, pricing, biometric auth, cookie consent |
| Context & Platform | `context-platform` | Cognitive load, mobile UX, performance, search & filter |
| Audience & Journey | `audience-journey` | Personalization, cross-cultural, post-purchase, social commerce |

### Platform Support

| Platform | Status | Highlights |
|----------|--------|-----------|
| Shopify | First-class | Liquid patterns, OS 2.0 sections, Shop Pay, Checkout Extensions |
| Next.js | First-class | App Router, RSC boundaries, Server Actions, middleware A/B testing |
| OpenCart | Detected | Auto-detected, generic CRO principles |
| Generic | Default | Works with anything |

---

## Installation

### Claude Code

```bash
claude plugin marketplace add Dannytownkins/ecommerce-conversion-psychology
claude plugin install cro@ecommerce-conversion-psychology
```

Restart Claude Code. `/cro` commands are available immediately.

```bash
# Update later
claude plugin update cro@ecommerce-conversion-psychology
```

---

## Architecture

```
ecommerce-conversion-psychology/
  .claude-plugin/plugin.json          Plugin metadata (v4.6.0)
  skills/                             6 coordinator skills
    cro/SKILL.md                      /cro router
    audit/SKILL.md                    /cro:audit (4-phase relay)
    build/SKILL.md                    /cro:build (3-phase relay)
    compare/SKILL.md                  /cro:compare (1:1 comparison)
    quick-scan/SKILL.md               /cro:quick-scan (single cluster)
    resume/SKILL.md                   /cro:resume (engagement listing)
  workflows/                          11 phase workflows (dispatched to subagents)
  references/                         19 domain + 9 operational files
  templates/                          16 HTML/CSS templates + component library
  scripts/
    generate-report.py                Visual report generator (reads findings.json + auto-matches markers)
  platforms/                          shopify.md, nextjs.md
  citations/                          Source URLs for human verification
  CLAUDE.md                           Development standards
  CHANGELOG.md
  LICENSE
```

---

## Ethics & Security

**Ethics gate** — Non-negotiable rules at every phase. Based on EU Digital Services Act, EU AI Act, GDPR, CCPA/CPRA, FTC Fake Reviews Rule, CA SB-478, CA SB-1001, CA SB-243, and enforcement precedent from FTC v. Amazon ($2.5B, 2025) and FTC v. Epic Games ($245M, 2023).

**Security:**
- XSS prevention — all report content HTML-entity-escaped + CSP meta tag
- SSRF prevention — URL validation rejects private IPs, loopback, metadata endpoints
- Prompt injection — subagents treat baton content as data, never instructions

## Author

Built by [Daniel Kinsner](https://github.com/Dannytownkins).
