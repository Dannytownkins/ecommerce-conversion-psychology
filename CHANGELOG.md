# Changelog

## 3.0.0 — 2026-03-17

### Accuracy, Architecture & Visual Reports — Major Release

#### Breaking Changes (3 changes)
- meta.json schema bumped from v1 to v2. New fields: `source_mode`, `plans_queue`, `reconciled`. Resume skill handles both v1 and v2 schemas with forward compatibility (unknown versions skipped with warning).
- `--ephemeral` flag deprecated as no-op (prints warning, behaves as `--no-visual`). Replaced by `--visual` / `--no-visual` flags.
- `--export-report` flag removed. Text HTML report remains available at checkpoints. Visual report controlled by `--visual` flag.

#### Dual-Source Acquisition (4 changes)
- New `workflows/acquire.md`: acquisition agent captures 3-6 sectioned viewport screenshots (JPEG, 1x DPR, quality 80) + preprocessed rendered DOM before auditor dispatch. Replaces single full-page screenshot approach.
- DOM preprocessing strips scripts, styles, SVGs, data-attributes, duplicate template elements, and sensitive form fields. 60-80% size reduction. Hard cap at 300KB with skeleton extraction fallback.
- Post-navigation URL re-validation prevents SSRF via redirects. Auth-protected pages detected and warned. 30s navigation timeout.
- New SOURCE field on every finding: VISUAL (screenshot evidence), CODE (DOM evidence), or BOTH (corroborated by both sources).

#### Coordinator Relay Loops (4 changes)
- Reviewer and builder can now ask questions through the coordinator using nonce-prefixed single-line JSON markers. Coordinator relays questions to user and re-dispatches with Q&A pairs.
- Relay iterations are conditional — only fire when QUESTION blocks detected. Max 3 iterations. After 3rd, user decides (not forced verdict).
- New `references/relay-loop-protocol.md` documents the nonce system, parsing rules, conditional iterations, Q&A delta re-dispatch, and auto mode behavior.
- `--auto` mode: reviewer/builder produce best-effort output without questions. BLOCK verdicts still halt unless `--force`.

#### Multi-Planner Architecture (5 changes)
- Heavy audits (3+ clusters each with 5+ findings) spawn parallel planners per cluster, producing focused PRDs per area.
- New `workflows/reconcile.md`: reconciler identifies cross-plan conflicts by SECTION slug and resolves using priority hierarchy (legal > ethics > user constraints > domain).
- New `references/multi-planner-protocol.md` documents trigger criteria, dispatch, file naming, reconciliation, sequential review/build, plans_queue schema, and go-back protocol.
- Sequential review/build per PRD — one at a time. `current_plan` and top-level `phase` derived from `plans_queue` (not stored independently).
- Removed 12-step hard cap on planner. Replaced with tiered grouping: Critical+High first, Medium+Low second.

#### Visual Reports (3 changes)
- New `workflows/visual-report.md`: stitches sectioned screenshots with CRO callout overlays. Orange callout bars show recommendations at the relevant page section. Base64-embedded, self-contained HTML.
- New `templates/visual-report.html.template` with CSP: `default-src 'none'; style-src 'unsafe-inline'; img-src data:; script-src 'none'`.
- Text report (`workflows/report.md`) now dynamically strips inapplicable sections. Quick-scan shows findings only. Build-from-scratch skips audit. Compare uses side-by-side layout.

#### Model Pinning (1 change)
- Tiered model pinning: Haiku for mechanical agents (acquisition, visual report), Sonnet for analysis (auditors, planners, builder), Opus for synthesis (reconciler, reviewer). Ensures consistent quality regardless of parent model.

#### Output Tiering (3 changes)
- Quick-scan defaults to conversation output + silent meta.json creation. User prompted to save (visual/markdown/both).
- Full audit defaults to markdown (baton system needs it) + visual report prompt.
- Compare mode: sequential acquisition (serialize page capture, parallelize auditors).

#### Housekeeping (6 changes)
- meta.json `updated` field written on every phase transition.
- Auditor/planner retry: one automatic retry on failure before SKIP.
- `--auto` build requires clean git state (aborts on dirty working tree).
- Go-back atomicity: delete downstream files first, then update meta.json. File existence is source of truth for recovery.
- Resume skill handles schema v1 (legacy) and v2 (new). Self-healing phase inference verifies plans_queue against filesystem.
- A/B scaffold: graceful fallback for unknown tools.

#### New Files (7)
- `workflows/acquire.md` — page acquisition agent
- `workflows/reconcile.md` — cross-plan conflict reconciler
- `workflows/visual-report.md` — screenshot-based visual report generator
- `references/relay-loop-protocol.md` — relay loop specification
- `references/multi-planner-protocol.md` — multi-planner specification
- `templates/visual-report.html.template` — visual report HTML template
- `templates/reconciliation.md.template` — reconciliation output template

#### Totals
- 24 reference files, 18 domain + 9 operational (2 new operational)
- 9 workflow files (3 new: acquire, reconcile, visual-report)
- 8 template files (2 new: visual-report.html, reconciliation.md)
- 5 commands: /cro:audit, /cro:build, /cro:quick-scan, /cro:compare, /cro:resume

---

## 2.2.0 — 2026-03-17

### Plugin Hardening — Structural Consolidation, Safety, and UX

#### Reference Consolidation (2 changes)
- Merged `mobile-conversion-psychology-principles.md` into `mobile-conversion.md` — 7 psychology principles, 7 patterns, 6 anti-patterns, decision tree, and key data table now live alongside the 24 UX findings in a single file. Fixed broken cross-reference (line 6 referenced non-existent `mobile-and-performance.md`).
- Removed `cookie-consent-and-compliance.md` from `context-platform` cluster (kept in `trust-conversion` only). Added cross-reference note in `cognitive-load-management.md`. No page type loses cookie-consent coverage.

#### Workflow Safety (3 changes)
- `--auto` mode now halts on reviewer BLOCK verdict. Writes `blocked: true` to `meta.json` and stops. Use `--auto --force` to override with explicit warning.
- Builder subagent (`workflows/build.md`) now performs pre-flight BLOCK check before writing any code — defense in depth.
- Added `--force` flag to router common flags and all coordinator SKILL.md files.

#### New Command
- `/cro:resume` — lists in-progress engagements and resumes at last checkpoint. Supports `--engagement-id` for direct resume. Infers phase from baton files for v1 engagements. Handles BLOCKED engagements with explicit options. Uses markdown headings (not XML tags).

#### UX Improvements (2 changes)
- `/cro:quick-scan` now persistent-by-default (was already the behavior). Added `--ephemeral` flag to skip directory creation. `--auto` always persists regardless of `--ephemeral`.
- Progress memory diff: re-auditing a previously audited page now appends a `## Progress Comparison` table to `audit.md` showing FIXED/REGRESSED/UNCHANGED/NEW/RESOLVED status per finding.

#### Schema & Validation
- Added `phase` and `blocked` fields to `templates/meta.json.template`.
- Added inline baton validation prose to all 4 coordinator SKILL.md files (audit, build, compare, quick-scan). Validates required fields, enums, and nested objects after meta.json creation.
- Dropped standalone `meta.schema.json` plan — prose validation is more effective for LLM readers than formal JSON Schema.

#### Housekeeping
- Simplified `templates/report.html.template`: consolidated badge CSS classes, removed template hint comments. 333 → 296 lines. All conditional section blocks preserved.
- Moved `citations/sources.md` → `docs/citations.md`. Removed empty `citations/` directory. Updated all references.
- Documented `.claude-plugin/plugin.json` purpose in README (future plugin discovery, not used by Claude Code skill loader).
- Bumped version to 2.2.0 in `README.md` badge and `.claude-plugin/plugin.json`.

#### SKILL.md Authoring Convention
- New SKILL.md files (`skills/cro/resume/SKILL.md`) use markdown headings exclusively. Existing files retain XML tags — incremental migration when modified.

#### Totals
- 17 domain reference files (was 18 — mobile merge) + 7 principle/operational files
- ~272 findings in reference library (unchanged — merge consolidated, did not add/remove)
- 5 commands: `/cro`, `/cro:audit`, `/cro:build`, `/cro:quick-scan`, `/cro:compare`, `/cro:resume`

---

## 2.1.0 — 2026-03-17

### Mobile CRO Expansion — 9 New Topics, 4-Audit Verified

#### New Reference Docs (3)
- `cookie-consent-and-compliance.md` — 9 findings. Banner architecture, placement, GDPR compliance, consent fatigue, cognitive load. **Tier 1 evidence** (multiple large-N peer-reviewed field experiments including Utz 2019 on a real ecommerce site with 82,000+ users).
- `biometric-and-express-checkout.md` — 8 findings. Digital wallets, passkeys, password friction, biometric speed and trust, generational divide. **Tier 2 evidence** (Stripe A/B testing is methodologically strongest).
- `social-commerce-psychology.md` — 7 findings. Trust transfer, impulse mechanics, platform comparisons, herd effect, cross-generational targeting. **Tier 2/3 evidence** (purchase-intention vs actual-behavior gap; cultural boundary conditions).

#### Expanded Reference Docs (6 existing docs, ~43 new findings)
- `page-performance-psychology.md` — +4 findings (skeleton animation quality, shimmer direction, fidelity requirements, accessibility). Corrected NNGroup threshold and flagged Akamai citation.
- `color-psychology.md` — +2 findings (dark mode CTA/trust badge contrast, dark mode reading performance and sentiment).
- `mobile-conversion.md` — +4 findings (dark mode adoption, WCAG failure rates with ecommerce-platform-specific data, accessibility lawsuits, touch targets and font size).
- `search-and-filter-ux.md` — +4 findings (search-user correlation caveat, zero-results abandonment, mobile filter placement, visual/voice search).
- `post-purchase-psychology.md` — +4 findings (automated push vs blasts, notification fatigue with Wohllebe N=17,500, multi-channel cart recovery cascade, rich media push).
- `eye-tracking-and-scan-patterns.md` — +5 findings (usage vs beauty videos, vertical video, mere presence effect, short-form engagement, gallery placement).

#### Cross-Reference Findings (3)
- `checkout-optimization.md` — +2 findings (accessible checkout design, cart recovery channel cross-reference from post-purchase).
- `social-proof-patterns.md` — +1 finding (social commerce trust transfer cross-reference).
- `cta-design-and-placement.md` — +1 finding (WCAG touch target requirements cross-reference).

#### Routing & Infrastructure
- Added 3 new docs to cluster routing: cookie-consent → context-platform + trust-conversion; biometric → trust-conversion; social-commerce → audience-journey.
- Added 3 canonical section slugs: cookie-consent, express-checkout, social-commerce.
- Updated slug lists in all 3 workflow files (audit, quick-scan, compare).
- Quick-scan now shows all cluster options with descriptions when prompting user.
- Quick-scan output suggests other clusters and full audit as next steps.
- Planner prompt updated to require inlining implementation specifics (hex codes, ARIA attributes, regulatory requirements) since builder cannot access reference docs.
- Verification checklist expanded from 9 to 12 items (cookie consent, express checkout, dark mode contrast).

#### Evidence Quality
- All 9 topics verified through 4-audit triangulation: Critical Audit (bias/methodology), Verification Audit (87 claims, structured review), Agent Verification (URL-level source checking), Sonnet Audit (54 claims, direct URL fetching).
- 8 factual errors corrected in source data before writing (wrong authors, wrong journals, wrong stats, wrong thresholds, citation laundering flags).
- No ecommerce-specific RCTs exist across any of the 9 topics (or the existing 15 reference docs). This is a structural feature of the field, not a gap we can fill. All conversion evidence is directional.
- Evidence quality tiers applied: Tier 1 (cite with confidence), Tier 2 (cite with caveats), Tier 3 (directional only), Tier 4 (do not cite — removed).
- Cross-reference report documenting all audit findings at `docs/audit files/cross-reference-report.md`.

#### Known Limitations
- Quick-scan defaults to one cluster; new topics only surface via --cluster override or full audit.
- Social commerce reaches product pages only via cross-reference in social-proof-patterns.md, not the full standalone doc.
- Push notification cart recovery reaches cart pages only via cross-reference in checkout-optimization.md.
- Dark mode findings split across visual-cta and context-platform clusters; cart pages miss mobile adoption context.
- No A/B comparison mechanism between v2.0 and v2.1 audit quality.

#### Totals
- 18 domain reference files (was 15) + 7 principle/operational files
- ~272 findings in reference library (was ~229)
- 3 new standalone docs, 9 existing docs modified, 5 workflow/skill files updated

---

## 2.0.1 — 2026-03-12

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
- Created `docs/citations.md` — single-file citation index (~350 source URLs) for human verification
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
