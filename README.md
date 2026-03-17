# 🧠 E-Commerce Conversion Psychology

![v2.2.0](https://img.shields.io/badge/version-2.2.0-blue) ![Claude Code Plugin](https://img.shields.io/badge/Claude_Code-plugin-7c3aed) ![Platforms](https://img.shields.io/badge/platforms-Shopify_%7C_Next.js_%7C_any-green)

**A CRO engine that thinks like a psychologist.** 15 research-backed reference files on pricing psychology, trust signals, cognitive load, eye tracking, and more — wired into a multi-agent relay that audits, plans, reviews, and builds conversion-optimized ecommerce pages.

Each phase runs in a fresh context window with only the files it needs — no single agent tries to hold the full picture. A baton file system passes structured findings between phases, so nothing gets lost to compaction and every recommendation is traceable back to the research that produced it.

Not a checklist. Not a linter. A full workflow that catches what you miss, challenges what you assume, and writes the code when you're ready.

---

## Commands

| Command | What it does | Input |
|---------|-------------|-------|
| `/cro` | Menu — shows available commands | — |
| `/cro:audit` | Full 4-phase relay on an existing page | URL or file path |
| `/cro:build` | Full 4-phase relay from scratch | Description or structured intake |
| `/cro:quick-scan` | Single-cluster scan → 3-5 quick wins | URL, file path, or description |
| `/cro:compare` | 1:1 competitor comparison with gap analysis | Two URLs or file paths |

### Flags

| Flag | Commands | Purpose |
|------|----------|---------|
| `--auto` | audit, build | Skip checkpoints, run all phases automatically |
| `--min-priority` | audit, build, quick-scan | Filter by severity: `critical`, `high`, `medium`, `low` |
| `--platform` | audit, build, quick-scan | Skip detection: `shopify`, `nextjs` |
| `--export-report` | audit, build, compare | Generate self-contained HTML report |
| `--ab-scaffold` | audit, build | Generate A/B test scaffold after planning |
| `--ab-tool` | audit, build | Specify existing A/B tool |
| `--cluster` | quick-scan | Override cluster: `visual-cta`, `trust-conversion`, `context-platform`, `audience-journey` |
| `--engagement-id` | all | Resume or target a past engagement |

---

## How It Works

Each command runs a multi-phase relay — separate subagents per phase, fresh context each time, no compaction during complex audits.

```
/cro:audit       Audit → ✋ → Plan → ✋ → Review → ✋ → Build → Done
/cro:build       Intake → Plan → ✋ → Review → ✋ → Build → Done
/cro:quick-scan  Audit → Results
/cro:compare     Audit Both → Compare → Results
```

✋ = checkpoint. Stop, go back, export a report, or scaffold A/B tests at any pause.

### Engagement Files

Each run creates a directory under `docs/cro/` — one file per phase:

```
docs/cro/2026-03-11-a3f2b1c9/
  meta.json           Engagement state + metadata
  context.md          Write-once intake context
  audit.md            Findings
  plan.md             Prioritized action plan
  review.md           Review notes + verdict
  build-log.md        Implementation status
  report.html         HTML report (optional)
  ab-scaffold.md      A/B test scaffold (optional)
```

---

## What's Under the Hood

- **18 domain reference files** — pricing, checkout, trust, social proof, CTAs, color, eye tracking, cognitive load, mobile UX, performance, personalization, cross-cultural, post-purchase, search/filter, cookie consent, biometric/express checkout, social commerce
- **4 auditor clusters** that get assigned by page type (or `--cluster` override)
- **Ethics gate** checked at every phase — fake urgency, hidden pricing, review manipulation, dark patterns → always `CRITICAL`
- **Progress memory** — re-audit a page and see what changed since last time
- **Interactive review** — the reviewer challenges vague or contradictory recommendations before any code gets written
- **A/B test scaffolding** — hypotheses, variant code, and measurement plans, platform-aware
- **HTML reports** — self-contained, WCAG AA, print-friendly, no external dependencies

### Domain Clusters

| Cluster | Slug | Coverage |
|---------|------|----------|
| Visual & CTA | `visual-cta` | CTA design, color psychology, eye tracking, scan patterns, product video |
| Trust & Conversion | `trust-conversion` | Trust signals, social proof, checkout optimization, pricing, biometric auth, cookie consent |
| Context & Platform | `context-platform` | Cognitive load, mobile UX, performance, search & filter, cookie consent |
| Audience & Journey | `audience-journey` | Personalization, cross-cultural, post-purchase, social commerce, push notifications |

### Platform Support

| Platform | Status | What It Does |
|----------|--------|-------------|
| Shopify | First-class | Liquid patterns, OS 2.0 sections, Shop Pay, Checkout Extensions |
| Next.js | First-class | App Router, RSC boundaries, Server Actions, middleware A/B testing |
| Generic | Default | Universal CRO principles — works with anything |

---

## Architecture

```
ecommerce-conversion-psychology/
├── .claude-plugin/plugin.json       Plugin metadata (v2.2.0)
├── references/                      18 domain + 7 principle/operational files
├── docs/citations.md                Source URLs for human verification (not loaded by agents)
├── platforms/                       shopify.md, nextjs.md
├── templates/                       Baton + report templates
├── workflows/                       Phase workflows (context: fork)
├── skills/cro/                      Command family
│   ├── SKILL.md                     /cro router
│   ├── audit/SKILL.md               /cro:audit
│   ├── build/SKILL.md               /cro:build
│   ├── quick-scan/SKILL.md          /cro:quick-scan
│   └── compare/SKILL.md             /cro:compare
├── README.md
└── CHANGELOG.md
```

---

## Plugin Metadata

`.claude-plugin/plugin.json` contains name, version, and description metadata. It exists for potential future plugin discovery systems and is **not** used by Claude Code's skill loader. The skill loader reads `skills/cro/SKILL.md` directly.

---

## Ethics & Security

**Ethics gate** — Non-negotiable rules at every phase. Based on EU Digital Services Act, EU AI Act, GDPR, CCPA/CPRA, FTC Fake Reviews Rule, CA SB-478, CA SB-1001, CA SB-243, and enforcement precedent from FTC v. Amazon ($2.5B, 2025) and FTC v. Epic Games ($245M, 2023). In competitor comparison mode, synthesized gap recommendations are also ethics-checked — dark pattern advantages get flagged with ethical alternatives.

**Security:**
- XSS prevention — all report content HTML-entity-escaped + CSP meta tag
- SSRF prevention — URL validation rejects private IPs, loopback, metadata endpoints, encoding bypasses
- Prompt injection — subagents treat baton file content as data, never instructions
