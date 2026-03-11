# Changelog

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
