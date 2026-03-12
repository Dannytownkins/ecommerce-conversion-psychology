# Changelog

## 2.1.0 — 2026-03-12

### Reference Library Audit & Accuracy Pass

#### Data Quality
- Removed 4 unverifiable statistics: "1617% sales increase" (WordStream), "FOMO = 60% of impulse purchases" (Research & Metric), "rounded corners 17-55% CTR" (no primary source), "BNPL 78% conversion improvement" (vendor-reported)
- Replaced 7 statistics with stronger, independently sourced data (BNPL, Shop Pay, coupon behavior, Q&A conversion, Amazon recommendations, Google blue experiment, Norton trust seal)
- Reconciled 4 cross-file metric inconsistencies (desktop vs mobile conversion, mobile cart abandonment, checkout form fields, website error abandonment)
- Added freshness warnings to 4 dated data points (Hoober 2013, Baymard search 2014, trust seal demographics mid-2010s, Monetate Q4 2017)

#### Ethics Gate Expansion
- Updated FTC penalty to 2025 inflation-adjusted amount ($53,088)
- Added Amazon Prime FTC settlement ($2.5B, Sep 2025) — largest dark patterns enforcement action
- Added 7 missing regulations: EU AI Act, GDPR, CCPA/CPRA ADMT, US state privacy laws (20+ states), CA SB 243, FTC Click-to-Cancel vacatur, EU DSA Art 25 enforcement precedent (X/Twitter €120M fine)

#### Citation Architecture
- Created `citations/sources.md` — single-file citation index (~350 source URLs) for human verification
- Stripped all URLs from 13 reference files to reduce agent context token usage
- Researched and added DOI links for 20 academic sources in pricing-psychology.md
- Researched and added URLs for 29 named sources in mobile-conversion-psychology-principles.md

#### Totals
- 229 findings in reference library — 0 deleted, 12 modified, 4 bad stats removed
- ~305 URLs extracted from reference files, ~50 URLs researched and added
- Net impact: stronger data, current legal compliance, lower agent context cost

## 2.0.0 — 2026-03-11

### Breaking Changes
- `/ecommerce-conversion-psychology` replaced by `/cro` command family (deprecation stub retained)
- Baton file format changed from single `docs/cro-action-plan.md` with HTML markers to per-engagement directories under `docs/cro/`
- References, workflows, platforms, and templates moved from `skills/ecommerce-conversion-psychology/` to plugin root

### New Commands
- `/cro` — Router/help menu. Lists all CRO commands. Auto-discovered when users mention CRO.
- `/cro:audit` — Full 4-phase CRO relay on an existing page (audit, plan, review, build)
- `/cro:build` — Full 4-phase relay from scratch with structured intake
- `/cro:quick-scan` — Single-cluster quick scan, 3-5 quick wins, one-and-done
- `/cro:compare` — 1:1 competitor comparison with gap analysis

### New Features
- **Multi-file baton system** — Per-engagement directories with separate files per phase. No more HTML comment markers.
- **Severity filtering** — `--min-priority` flag filters findings by priority level (critical/high/medium/low)
- **Cost/impact scoring** — Action plan table includes Effort and Impact columns
- **Platform-specific templates** — Shopify and Next.js platform references loaded by the builder
- **HTML report export** — Self-contained report with inline CSS, WCAG AA compliant, print-friendly
- **Progress memory** — Re-auditing a previously audited URL shows what changed since last audit
- **A/B test scaffolding** — Generates test hypotheses, variant code, and measurement plans per platform
- **Screenshot/URL-based audit** — Visual audit via agent-browser when source code unavailable
- **Competitor comparison** — Side-by-side scoring with gap analysis and ethics checking

### Agent-Native Improvements
- `--auto` flag for checkpoint-free automation (audit, build)
- Structured argument acceptance for all commands
- `--export-report`, `--ab-scaffold`, `--cluster`, `--engagement-id` flags
- Deterministic `--auto` path with mandatory safety gates

### Security
- HTML report includes CSP header blocking all script execution
- All report content HTML-entity-escaped before insertion
- URL validation with IPv4/IPv6 SSRF prevention (references/url-validation.md)
- Ethics gate passed to compare workflow for synthesized recommendation validation

### New Reference Files
- `references/url-validation.md` — SSRF prevention rules
- `references/platform-detection.md` — Platform detection heuristics with .liquid disambiguation
- `references/ab-testing-patterns.md` — A/B testing methodology and patterns
- `platforms/shopify.md` — Shopify OS 2.0, Liquid patterns, Shop Pay, Checkout Extensions
- `platforms/nextjs.md` — App Router, RSC boundaries, Server Actions, middleware A/B testing

### Architecture
- Nested directory namespacing (`skills/cro/audit/SKILL.md` → `/cro:audit`)
- Shared infrastructure at plugin root (references, workflows, platforms, templates)
- Canonical SECTION slug registry for deterministic finding matching
- meta.json with `schema_version: 1` for future migration safety
- Atomic go-back protocol (write-then-rename)
