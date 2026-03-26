# Changelog

## 4.6.0 — 2026-03-26

### Structured JSON Findings Pipeline

Architectural change: findings now travel through the pipeline as structured JSON instead of regex-parsed prose. Eliminates three LLM interpretation layers where findings could silently drop or malform.

#### JSON Findings (3 changes)
- **Auditor JSON output** — Auditors now output a `FINDINGS_JSON:` block alongside prose findings. JSON array has typed fields: verdict, section, element, source, priority, observation, recommendation, reference, tier, effort, cluster. Prose preserved in audit.md for human review.
- **Coordinator JSON assembly** — Coordinator extracts JSON arrays from all auditors, merges/deduplicates by field matching (not LLM interpretation), applies ethics severity override, writes `findings.json` as source of truth. Falls back to prose parsing if auditor omits JSON.
- **Auto-matching markers** — `generate-report.py` reads `findings.json` and matches ELEMENT fields to baton entries via selector/text/tag strategies. No coordinator-provided `markers.json` needed. New `--findings` CLI argument; `--markers` retained for backwards compat.

#### Parallel Acquisition (5 changes)
- **Named sessions for two-device mode** — Two-device acquisition now dispatches both agents in parallel using `--session {device}`. Each agent gets its own browser instance with independent viewport. Cuts acquisition time nearly in half.
- **True parallel acquisition** — Both agents now do full acquisition independently (DOM + screenshots + element coordinates). Previously the second agent depended on the first agent's DOM output via `dom_file`, which forced sequential execution despite named sessions. Removed `dom_file` input parameter from acquire.md.
- **Device-specific DOM filenames** — Desktop/laptop writes `dom.html`, mobile writes `dom-mobile.html`. Prevents file collisions when two agents run in parallel. The baton's `dom_file` field carries the correct filename downstream.
- **Absolute path mandate** — Coordinator computes absolute `ENGAGEMENT_DIR` and passes to every acquisition agent. Prevents working directory mismatch that caused files written to wrong location.
- **Baton field name contract** — Explicit callout in acquire.md that field names (`path`, `naturalWidth`, `naturalHeight`, `screenshot_index`, `scrollY`) are machine-readable contracts. Prevents schema drift.

#### Quality Improvements (5 changes)
- **Ethics severity override rule** — If ethics gate defines severity for a violation class, that severity overrides the auditor's rating during audit assembly. Separate from the dedup preservation rule.
- **Findings parity validation** — After writing both audit.md and findings.json, coordinator now validates that finding counts match. If prose dedup and JSON dedup diverge (e.g., auditor returns 8 prose findings but 7 JSON entries), the coordinator reconciles by constructing missing entries from whichever source has them. Prevents the visual report from silently showing fewer findings than the markdown.
- **Mobile DOM caveat removed** — Each device now captures its own DOM at its own viewport. The `{{dom_caveat_if_mobile}}` template note ("DOM was captured at a non-mobile viewport") is no longer needed and has been removed from the auditor dispatch template.
- **EFFORT: Trivial tier** — New lowest effort tier for DOM features that exist but are disabled via attribute or config flag (e.g., `data-infinite-scroll-enabled="false"`).
- **Checkpoint prompt format** — Export sub-options use letters (a/b/c/d) instead of nested numbers to avoid decimal ambiguity.

#### Plugin Structure (17 changes)
- **CLAUDE.md** — Development standards, pre-commit checklist, skill compliance, validation commands.
- **references/meta-schema.md** — Extracted duplicated meta.json validation schema (was copy-pasted in 4 skills) to single reference file.
- **Skill descriptions** — All 6 skills rewritten with trigger phrases and third-person format for better skill matching.
- **build/SKILL.md** — 9 vague "Same as /cro:audit" replaced with specific section pointers.
- **quick-scan/SKILL.md** — 17-line URL acquisition block collapsed to 5 lines.
- **evidence-tiers.md** — Added to auditor dispatch template (was referenced indirectly but never dispatched).
- **Workflow contradictions fixed** — Ethics URL contradiction in audit.md, "user is gate" vs BLOCK in review.md, coordinator-scope content removed from reconcile.md.
- **acquire.md** — Cut 61 lines of verbose prose, consolidated DPR explanations, fixed 30% occlusion vagueness.
- **Bold-format parser warning** — `generate-report.py` detects `**FINDING: FAIL**` format and emits stderr warning. Also warns on zero parsed findings.
- **Plugin manifest** — Keywords, homepage, component counts in description.
- **README** — Components table, accurate counts, tighter architecture section.
- **.DS_Store** — Removed from git, added to .gitignore.
- **Pillow** — Pinned to `>=10.0.0,<12.0.0`.
- **Hardcoded path** — Fixed `C:\Users\SM - Dan\.codex` in CODEX_CONVERSION.md.

#### Codex Removal (4 files deleted)
- Removed `SKILL.md` (root wrapper), `agents/openai.yaml`, `scripts/sync-to-codex.ps1`, `CODEX_CONVERSION.md`. Codex integration deferred until 4.6 stable.

### Files Changed
- `skills/audit/SKILL.md` — JSON assembly, ethics override, parallel acquisition, absolute paths, meta-schema ref, description, checkpoints, findings parity validation, device-specific DOM verification, mobile DOM caveat removed
- `skills/build/SKILL.md` — Specific cross-references, meta-schema ref, description
- `skills/quick-scan/SKILL.md` — Parallel sessions, acquisition trim, meta-schema ref, description, true parallel acquisition
- `skills/compare/SKILL.md` — Parallel sessions, concurrency fix, evidence-tiers, meta-schema ref, description, true parallel acquisition
- `skills/resume/SKILL.md` — Description
- `skills/cro/SKILL.md` — Description
- `workflows/audit.md` — JSON output format, dual-format note, ethics URL fix
- `workflows/acquire.md` — ENGAGEMENT_DIR, named sessions, field name contract, verbosity cuts, device-specific DOM filenames, dom_file input removed
- `workflows/review.md` — User-is-gate clarification
- `workflows/reconcile.md` — Removed coordinator-scope content
- `workflows/plan.md` — EFFORT: Trivial tier
- `scripts/generate-report.py` — --findings arg, auto_match_markers(), findings.json loading, bold-format warning
- `.claude-plugin/plugin.json` — v4.6.0, keywords, homepage, description
- `.claude-plugin/marketplace.json` — Updated description
- `CLAUDE.md` — New file (development standards)
- `references/meta-schema.md` — New file (shared schema)
- `README.md` — Components table, Codex removal, architecture update
- `CHANGELOG.md` — This entry
- `.gitignore` — Added .DS_Store
- `requirements.txt` — Pillow upper bound

---

## 4.5.1 — 2026-03-24

### Acquisition Reliability & Ethics Accuracy

Bug fixes from two live audit runs (SlingMods product page, AWDMods product page) that exposed silent failures in screenshot capture, DPR handling, and ethics gate false positives.

#### Acquisition Fixes (3 changes)
- **JS scroll replaces agent-browser scroll** — `agent-browser scroll to` fails silently on Shopify themes and sites with `scroll-behavior: smooth`. Primary scroll method is now `window.scrollTo({behavior: 'instant'})` via `agent-browser eval`, with scrollY verification after each call. Prevents duplicate screenshots.
- **DPR fix: `set device` replaces `--args`** — `--force-device-scale-factor=2` does not work on Windows. Mobile acquisition now uses `agent-browser close` + `agent-browser set device "iPhone 14"` (3x DPR) as the only reliable high-DPR method. Documents that `set viewport` after `set device` resets DPR to 1x.
- **Post-acquisition file verification** — Coordinator now runs `ls` on the engagement directory after acquisition agent returns to verify baton.json, dom.html, and screenshots actually exist on disk. Catches silent subagent file-write failures before they propagate.

#### Ethics Gate Fix (1 change)
- **Phantom social proof visibility test** — Added explicit visibility criteria: an element is "displayed" only if `display != none`, `visibility != hidden`, and bounding box is non-zero. Loading a CSS file or having a hidden DOM node does not constitute phantom social proof. CODE-only evidence flagged as MEDIUM (verify visibility), not CRITICAL.

#### Coordinator Fixes (4 changes)
- **Baton normalization** — Coordinator normalizes simplified baton schemas (string screenshot arrays → objects, missing fields inferred from sections/viewport data) before dispatching auditors.
- **Ethics gate preservation rule** — During finding deduplication, if ANY auditor flagged a finding as CRITICAL with an ethics-gate.md reference, the deduplicated finding retains CRITICAL regardless of other auditors' ratings.
- **Subagent file-write clarification** — Objective section now explicitly states the acquisition agent is the exception to "subagents never write files."
- **DPR daemon persistence documented** — SKILL.md now notes that `agent-browser` uses a system-wide daemon and requires explicit `agent-browser close` between device passes with different DPR.

#### Report Generation Fixes (2 changes)
- **Python prerequisites** — `<report_export>` now includes a prerequisite block that detects `python` vs `python3` and auto-installs Pillow.
- **Cross-platform python command** — acquire.md base64 fallback and report generation use `python` (Windows) with `python3` (Linux/macOS) fallback.

#### Hash Verification (1 change)
- **Duplicate screenshot detection** — `md5sum` hash comparison after each screenshot capture. File-size comparison alone is insufficient — hash match triggers re-scroll and re-capture.

#### Quick-Scan Parity (3 changes)
- **Device options match audit** — Quick-scan now offers mobile (390×844), laptop (1440×900), and desktop (1920×1080). Previously only had "desktop" (actually 1440×900) and mobile.
- **Mobile DPR fix** — Same `set device "iPhone 14"` fix as audit. Replaces broken `--force-device-scale-factor=2`.
- **Post-acquisition file verification** — Same mandatory `ls` check as audit.

### Files Changed
- `skills/audit/SKILL.md` — Objective, acquisition dispatch, baton validation, deduplication, manual fallback, report export, DPR docs
- `skills/quick-scan/SKILL.md` — Device options (mobile/laptop/desktop), DPR fix, file verification, viewport dimensions
- `workflows/acquire.md` — Mobile DPR method, scroll method, hash verification, python command
- `workflows/quick-scan.md` — Device-aware evaluation for laptop vs desktop viewports, DOM caveat update
- `references/ethics-gate.md` — Phantom social proof visibility test
- `.claude-plugin/plugin.json` — Version bump to 4.5.1
- `README.md` — Version badge
- `CHANGELOG.md` — This entry

---

## 4.5.0 — 2026-03-23

### Codex Source Workflow

Codex support now lives in the repo as first-class source files instead of only in the installed `.codex` copy.

- **Codex wrapper added to source control** - Added root `SKILL.md` so Codex intent-based routing is versioned alongside the shared CRO assets.
- **Codex UI metadata added** - Added `agents/openai.yaml` for Codex display metadata and default prompt wiring.
- **Codex source/install notes added** - Added `CODEX_CONVERSION.md` documenting the repo-as-source, `.codex`-as-install workflow.
- **Codex publish script added** - Added `scripts/sync-to-codex.ps1` to mirror the repo's Codex-managed files into `~/.codex/skills/ecommerce-conversion-psychology`.
- **Python cache ignored** - `.gitignore` now ignores `__pycache__/` and `*.pyc` from report-generator verification.
- **Claude plugin metadata preserved** - `.claude-plugin/plugin.json` remains the Claude-facing package manifest; only the version was bumped for release alignment.

### Documentation

- **README Codex install workflow** - Added a Codex section covering the source-of-truth repo model and the sync command.
- **Architecture updated** - README now lists the Codex wrapper files and the sync script alongside the shared CRO assets.

---

## 4.4.1 — 2026-03-22

### Ethics Detection & Quick-Scan UX

Two targeted fixes from a live quick-scan that missed a countdown timer ethics violation.

#### Ethics Detection (1 change)
- **Urgency/timer element extraction** — acquire.md element selector now includes `[class*="countdown"]`, `[class*="timer"]`, `[class*="urgency"]`, `[class*="limited"]`, `[class*="expire"]`, `[class*="hurry"]`. Countdown timers are now explicitly surfaced in the baton's `elements` array so auditors see them during the ethics check rather than relying on finding them in the full DOM.

#### Quick-Scan UX (1 change)
- **Blocking cluster selection prompt** — quick-scan/SKILL.md cluster selection is now a blocking prompt. Coordinator must WAIT for user confirmation before dispatching acquisition or auditors. Previously the instruction said "offer the user a choice" which allowed the coordinator to proceed without waiting.

#### Files Modified
- `workflows/acquire.md` — Added 6 urgency/timer CSS selectors to element extraction
- `skills/quick-scan/SKILL.md` — Cluster selection changed from advisory to blocking prompt

---

## 4.4.0 — 2026-03-21

### Reliability, Accuracy & Performance Improvements

Batch of 19 improvements based on real-world audit feedback. Focuses on acquisition reliability, audit accuracy, mobile fidelity, and report generation performance.

#### Acquisition Reliability (7 changes)
- **agent-browser CLI note** — acquire.md now explicitly states that agent-browser is a CLI tool and all commands must run via Bash. This was the #1 source of failed acquisitions — agents tried to call agent-browser as an MCP tool.
- **Manual acquisition fallback** — When the acquisition agent fails, the coordinator now captures screenshots/DOM directly via agent-browser CLI commands, with real element coordinate extraction. Adds `source_mode: "manual"` to meta.json.
- **WebFetch fallback** — When agent-browser is unavailable, falls back to WebFetch for page content. Adds `source_mode: "webfetch"` with defined behavior (CODE-only findings, no screenshots).
- **Stale baton cleanup** — Coordinator now deletes failed agent's partial baton.json/dom.html before manual acquisition, preventing downstream agents from reading empty/partial data.
- **Sequential "both" mode** — Simplified dual-device acquisition to strictly sequential (desktop then mobile) since the browser session is shared.
- **Mobile DPR: 3x → 2x** — Mobile screenshots now use 2x DPR (780px wide) instead of 3x (1170px wide). Cuts base64 file size ~45% with negligible quality loss at carousel display sizes.
- **Screenshot compression guidance** — acquire.md now includes post-capture compression guidance (re-encode at quality 60 if >500KB).

#### Audit Accuracy (5 changes)
- **"What's Working Well" section** — PASS findings now go in a separate lightweight section at the end of audit output (slug + one-liner, no priority/recommendation). Prevents PASS findings from rendering as "Low Priority" issue cards in visual reports.
- **FAQ/accordion awareness** — Auditors now check for FAQ/accordion sections containing hidden trust signals (refund policy, payment methods, security info) that don't appear in the primary visual flow.
- **Floating chat widget detection** — Mobile auditors now check for floating chat widgets (Intercom, Chatwoot, etc.) that may occlude CTAs or touch targets.
- **`user-scalable=no` finding** — Now emitted as a MEDIUM finding under `mobile-touch-targets` when detected, instead of being noted as an ethics concern and never becoming a finding. Cites WCAG 1.4.4.
- **Enforced separate mobile audit** — "Both" mode now requires dispatching separate mobile auditors with mobile screenshots and mobile-specific principles. Explicitly prohibits reusing desktop findings for mobile reports.

#### New Reference File (1 change)
- **competitive-positioning.md** — 8 findings covering value proposition framing, process comparison sections, specificity effect, before/after framing, anchoring via competitor context, and outcome vs. feature framing. Added to visual-cta and trust-conversion cluster reference files. New canonical slugs: `value-proposition`, `competitive-comparison`, `process-differentiation`.

#### Visual Report Performance (2 changes)
- **components-digest.md** — Line-range index for components.html (1115 lines, ~162K tokens). Agents can now read only the component sections they need instead of the full file.
- **Parallel visual reports** — "Both" mode now dispatches desktop and mobile visual reports in parallel instead of sequentially (~30 min time savings).

#### Workflow Optimizations (4 changes)
- **meta.json validation on resume only** — Coordinator no longer re-reads and validates meta.json immediately after writing it. Validation now only runs when resuming engagements the coordinator didn't write.
- **Early trust-conversion dispatch** — trust-conversion auditors can now start on DOM while screenshots are still capturing, since they primarily need DOM content. visual-cta still waits for all screenshots.
- **Progress memory: "Now Passing" section** — Progress comparison now prominently surfaces FAIL→PASS transitions ("Now Passing") with their own table, emphasizing wins from previous audits.
- **Progress memory: FIXED items first** — Checkpoint presentation now leads with fixed items before regressions and new findings.

#### Files Modified
- `workflows/acquire.md` — CLI note, DPR change, compression guidance, section-to-cluster mapping
- `workflows/audit.md` — "What's Working Well" section, FAQ/accordion awareness, chat widget detection, user-scalable=no finding, new canonical slugs, device-aware evaluation updates
- `workflows/visual-report.md` — PASS finding filtering, "What's Working Well" rendering, components-digest reference
- `skills/audit/SKILL.md` — Manual/WebFetch fallback, sequential "both" mode, mobile DPR, separate mobile audit, parallel visual reports, meta.json validation, early dispatch, progress memory
- `skills/compare/SKILL.md` — Mobile DPR updates
- `skills/quick-scan/SKILL.md` — Mobile DPR updates
- `templates/audit.md.template` — "What's Working Well" section placeholder
- `templates/meta.json.template` — New source_mode values (manual, webfetch)
- `templates/components-digest.md` — New file (line-range index)
- `references/competitive-positioning.md` — New file (8 findings)
- `.claude-plugin/plugin.json` — Version bump to 4.4.0

---

## 4.3.0 — 2026-03-20

### Visual Report Redesign

Complete visual report overhaul — new design language, layout, and component library. The text-only `report.html.template` is unchanged.

#### New Design Language (1 change)
- Visual reports now use a pure-black background with subtle grid texture, amber accent system, and editorial-grade typography. Replaces the previous dark chrome design system (`#0e0e10` surfaces, split-panel layout). Design tokens fully rewritten in `components.html` — all CSS custom properties renamed to match the new system (e.g., `--bg-body` → `--bg`, `--severity-critical` → `--critical`).

#### Layout Overhaul (1 change)
- Split-panel layout replaced with a 7fr/5fr grid: sticky evidence canvas (left) with screenshot carousel, scrollable finding cards (right). Header uses large hero typography with eyebrow text and a 3-column metadata grid. Summary section at the bottom replaces the old score strip with three cards: evidence confidence, severity distribution bars, and ethics check.

#### Screenshot Carousel (1 change)
- Screenshots now display in a carousel with thumbnail strip and prev/next navigation, replacing the single stacked screenshot panel. Markers are per-slide — each marker has a `data-slide` attribute and only appears when its slide is active. Carousel controller JS replaces the old scroll-sync state machine.

#### Finding Card Redesign (1 change)
- Finding cards redesigned with: severity-colored accent stripe at top, large numbered header, pill-shaped severity badge, recommendation box with lightbulb icon, inline "Why this matters" section (always visible, not collapsible), and citation footer with evidence tier badge + clickable "View Source" link. Collapsible technical details section removed — source type shows in the card header instead.

#### Evidence Tier Badges in Footer (1 change)
- Evidence tier badges (Gold/Silver/Bronze) now render as small pill badges in each finding card's footer, next to the reference ID. Uses muted pill style consistent with severity badges. Citation URLs resolved from `citations/sources.md` and rendered as the "View Source" link.

#### Ethics Violation State (1 change)
- Ethics summary card now supports both PASS and FAIL states. PASS renders green checkmark with "No dark patterns detected". FAIL renders critical-red X icon with a vertical list of violations as red-backgrounded line items. Covers: urgency/scarcity signals, pricing transparency, review authenticity, choice architecture, subscription patterns.

#### Metrics Bar (1 change)
- New metrics bar below the screenshot carousel showing Intent Reliability (% of findings backed by Gold/Silver evidence) and Projected Lift (estimated conversion improvement from severity-weighted findings, capped at 35%).

#### Files Modified
- `templates/components.html` — Complete rewrite: new design tokens, all 13 component sections rebuilt for new design language
- `templates/visual-report.html.template` — New skeleton matching redesigned component structure
- `workflows/visual-report.md` — Rewritten assembly instructions for new layout (carousel, metadata grid, summary section, ethics states)
- `skills/audit/SKILL.md` — Updated visual report assembly steps to reference new components
- `skills/quick-scan/SKILL.md` — Updated visual report assembly steps to reference new components
- `skills/compare/SKILL.md` — Updated visual report assembly steps to reference new components
- `.claude-plugin/plugin.json` — Version bump to 4.3.0

#### Not Changed
- `templates/report.html.template` — Text-only report unchanged (separate design, separate purpose)
- `workflows/report.md` — Text report workflow unchanged
- `references/` — No reference file changes
- `citations/` — No citation changes

---

## 4.2.0 — 2026-03-20

### Visual Report Accuracy & Citation Links

Fixes SVG marker positioning, broken split-layout rendering, missing citation URLs, and panel proportions in visual reports.

#### SVG Marker Positioning (2 changes)
- Acquisition agent now extracts element bounding-box coordinates via `getBoundingClientRect()` (new Step 4b in `acquire.md`). Writes an `elements` array to `baton.json` with `{ selector, tag, text, class, x, y, width, height }` per element. Covers buttons, headings, images, ratings, prices, trust badges, payment icons, forms, and navigation.
- Auditors now output an `ELEMENT` field per finding (CSS selector or description) identifying the target UI element. Visual report generator matches `ELEMENT` to the baton's `elements` array for accurate marker placement. Falls back to section-level centering when no match found.

#### Citation URL Resolution (1 change)
- Citation URLs are now resolved at report render time by the visual report generator, not by auditors. The generator reads `citations/sources.md`, matches reference filename + finding number, and renders clickable `<a>` tags. Auditors no longer need to look up or output URLs — keeps auditor context lean and ensures a single source of truth for all citation links.

#### Split-Layout Fix (1 change)
- Fixed HTML comment in `components.html` SVG safety note that contained literal `<style>` text. Style-extraction regex matched this as a CSS block start, capturing HTML template markup into the stylesheet. This created phantom layout divs that broke the split-panel, causing finding text to render behind the screenshot panel. Comment now uses plain text element names without angle brackets.

#### Panel Proportions (1 change)
- Screenshot panel width changed from 42% to 50% in `components.html`. Gives screenshots equal visual weight against finding cards in the split-layout.

#### Per-Section Element Extraction (1 change)
- Element coordinate extraction (Step 3b) now runs during the screenshot pass at each scroll position, not as a single bulk query after DOM extraction. Lazy-loaded elements (images, reviews, carousels below the fold) are now captured because the browser has scrolled to them. Results are deduplicated by `(selector, x, y)` across sections. Capped at 100 total elements.

#### Overlapping Acquisition in "Both" Mode (1 change)
- Mobile acquisition no longer waits for desktop to fully complete. Mobile pass starts as soon as `dom.html` is written (it only needs the DOM, not desktop screenshots). Reduces total wall-clock time for dual-device scans.

#### Eliminated Duplicate .b64 Files (2 changes)
- Acquisition agent no longer creates `.b64` files alongside screenshots. Visual report generator base64-encodes JPEG files on the fly at render time. Halves disk usage per engagement (~4-8MB saved for a typical 5-screenshot scan).
- Baton schema: removed `base64_path` field from screenshot entries. Only `path` (the JPEG file) is recorded.

#### Files Modified
- `workflows/acquire.md` — Step 3b per-section element extraction (moved from Step 4b), removed .b64 file creation, removed `base64_path` from baton schema
- `workflows/audit.md` — Added ELEMENT field, removed URL requirement from auditors, citation URL resolution moved to report generator
- `workflows/visual-report.md` — Element-based marker positioning, citation URL resolution from `citations/sources.md`, render-time base64 encoding, HTML comment stripping instruction
- `templates/components.html` — SVG safety comment fix (removed literal `<style>`), screenshot panel width 42% → 50%
- `skills/audit/SKILL.md` — Overlapping acquisition dispatch in "both" mode

---

## 4.1.0 — 2026-03-20

### Deviation Audit Remediation — Reproducibility & Self-Contained Reports

Addresses all findings from the 2026-03-19 deviation audit. Focuses on three areas: making reports self-contained, introducing structured handoff between pipeline phases, and reducing model-dependent behavior.

#### Structured Baton File (1 change)
- New `baton.json` output from acquisition phase. Machine-readable JSON with device, viewport, screenshot metadata (paths, base64_paths, naturalWidth, naturalHeight), section boundaries with cluster mapping, DOM mode, extracted styles, and status. Downstream phases read `baton.json` as the authoritative acquisition output instead of parsing informal text. Coordinators and visual report generators validate `status: "COMPLETE"` before proceeding.

#### Self-Contained Reports (2 changes)
- Screenshots embedded as base64 data URIs (`data:image/jpeg;base64,...`) in visual reports. Acquisition writes `.b64` files alongside each screenshot. Visual report assembly reads `.b64` files and embeds inline. Reports are fully portable — no broken images when moved or shared.
- SVG `viewBox` now uses `naturalWidth` × `naturalHeight` from `baton.json` instead of CSS viewport dimensions. Fixes mispositioned markers on mobile (3x DPR: 1170×2532 actual vs 390×844 CSS).

#### Obstacle Handling (1 change)
- New Step 1b in `acquire.md`: explicit overlay dismissal sequence. Checks for `[role="dialog"]`, `.modal`, `.cookie-banner`, `[class*="consent"]`, newsletter popups, and OneTrust SDK. Tries close button → Escape → click outside → mark occluded. Handles chained overlays (cookie → newsletter). Eliminates model-dependent improvisation for popup handling.

#### Screenshot Format Enforcement (1 change)
- PNG validation added to acquisition. If agent-browser produces PNG, re-captures as JPEG. Falls back to ImageMagick conversion. Notes `format_override` in baton if conversion unavailable.

#### DOM Tiered Extraction (2 changes)
- DOM size threshold raised from 300KB to 500KB for skeleton mode. New intermediate tier (300–500KB): aggressive duplicate reduction (keep 2 siblings) + strip inline styles except on CTAs/prices/trust badges. Set `dom_mode: "reduced"`.
- Duplicate sibling keep count raised from 3 to 5. Ensures auditors see card-to-card variation (badges, reviews, sale prices).

#### Platform Detection (2 changes)
- OpenCart added to platform detection heuristics: `catalog/view/` directory, `route=product/product` URL patterns, `opencart` meta generator. DOM-level detection added for all platforms (Shopify `cdn.shopify.com`, Next.js `__NEXT_DATA__`, OpenCart `catalog/view/`).
- Quick-scan now runs platform detection before engagement setup. Previously defaulted to `"generic"` without checking.

#### meta.json Validation (1 change)
- Pattern-level validation for all required fields: id must match `YYYY-MM-DD-{8hex}` regex, type/phase/platform must be valid enum values, `clusters_used` entries must be valid cluster slugs. Logs corrected fields. Applied to both `/cro:audit` and `/cro:quick-scan`.

#### Screenshot Minimum (1 change)
- Minimum screenshots reduced from 3 to 1. Short pages (landing pages, above-fold-only scans) no longer require artificial padding.

#### Files Modified
- `workflows/acquire.md` — baton.json output, overlay dismissal, JPEG validation, tiered DOM extraction, duplicate sibling count
- `workflows/visual-report.md` — base64 embedding, baton.json consumption, SVG viewBox from baton
- `workflows/audit.md` — (no changes, already compliant)
- `workflows/quick-scan.md` — (no changes, already compliant)
- `skills/quick-scan/SKILL.md` — platform detection, baton.json verification, meta.json pattern validation
- `skills/audit/SKILL.md` — baton.json verification, meta.json pattern validation
- `references/platform-detection.md` — OpenCart heuristics, DOM-level detection
- `templates/meta.json.template` — opencart platform, url-dual source_mode, description source_mode
- `.claude-plugin/plugin.json` — version bump to 4.1.0

---

## 4.0.0 — 2026-03-19

### Evidence Tiers, Annotated Screenshots & Component Library — Major Release

#### Evidence Tier System (1 change)
- 300 classified findings tagged with credibility tiers: Gold (peer-reviewed RCT/meta-analysis), Silver (large-N observational or vendor A/B test), Bronze (expert consensus, small-N, or directional). Clickable citation URLs with evidence tier badges in all report output.

#### Component Library (1 change)
- New `templates/components.html` — shared component library enforcing structural consistency across all visual report output. All reports render from the same building blocks.

#### Annotated Screenshot Reports (2 changes)
- Annotated screenshots replace wireframes as the primary visual in reports. Findings are overlaid directly on captured screenshots with numbered callout markers.
- Bidirectional scroll-sync between screenshot panel and finding cards using a 4-state state machine (idle, user-scrolling-left, user-scrolling-right, programmatic-sync). Clicking a finding scrolls to the screenshot region and vice versa.

#### Screenshot-Only Input Mode (1 change)
- New `source_mode: "screenshot"` for engagements where only a screenshot is provided (no URL, no source code). `meta.json` gains `screenshot_input` object storing filename and dimensions. Resume skill detects cross-mode changes between engagements.

#### Ethics Compliance (1 change)
- Ethics compliance section is now mandatory in all reports (audit, quick-scan, compare, build). Compare mode validates ethics independently for both pages.

#### Report Design System (4 changes)
- Dark chrome design system with WCAG AA contrast ratios throughout all visual report output.
- Base64 embedded Inter and JetBrains Mono fonts — no external font requests, fully self-contained.
- Print CSS with token reassignment for clean paper output.
- PASS/FAIL/PARTIAL/SKIP verdicts hidden from visual output (kept in data model for programmatic consumers). SOURCE moved to collapsible Technical Details section.

#### Auto-Save & Export (2 changes)
- `audit.md` and `meta.json` saved silently on every phase transition — no save prompt.
- Full audit 4-option export dialogue at completion (markdown, visual, both, skip).

#### meta.json Schema (1 change)
- `meta.json` gains `screenshot_input` object and `source_mode: "screenshot"` value for screenshot-only engagements.

#### Marketplace Restructure
- Repo restructured as a Claude Code marketplace plugin. All files moved into `plugins/cro/` directory.
- Added `.claude-plugin/marketplace.json` at repo root for marketplace discovery.
- Skills flattened from `skills/cro/audit/` to `skills/audit/` for proper `cro:*` namespace registration.
- Install method changed from manual `cp`/`ln -sf` to `claude plugin marketplace add` + `claude plugin install`.

#### Files Modified
- All files moved under `plugins/cro/`
- `.claude-plugin/marketplace.json` (new)
- `plugins/cro/.claude-plugin/plugin.json` (moved, added repository/license/keywords)
- `README.md` (updated install instructions and architecture)

---

## 3.1.0 — 2026-03-18

### Viewport-Aware Scanning & Audit Accuracy

Eliminates false positives caused by agents reading source code patterns that don't match the actual rendered page at the target viewport. Adds device selection, enforces correct viewport dimensions, produces per-device reports, and embeds research rationale in every finding.

#### Device-Aware Scanning (6 changes)
- New `--device desktop|mobile|both` flag on `/cro:quick-scan`, `/cro:audit`, and `/cro:compare`. Prompts user for device choice before scanning. Defaults to desktop in `--auto` mode.
- Desktop viewport: 1440×900 at 1x DPR (up from 1280×800). Safely above most Shopify/theme breakpoints.
- Mobile viewport: 390×844 via `agent-browser set device "iPhone 14"` preset (includes DPR and mobile user-agent).
- "Both" mode produces two separate reports: `audit.md` (desktop, backward-compatible) + `audit-mobile.md` (mobile). DOM extracted once at desktop viewport, screenshots captured at both viewports.
- Partial failure in "both" mode delivers the successful device's report + warning with retry instructions. `devices_requested` preserves original intent for resume.
- Compare "both" mode displays cost warning before dispatching 4 acquisitions.

#### Acquisition Pipeline Hardening (4 changes)
- `workflows/acquire.md` now accepts parametric viewport `{ width, height }` and device context — no more hardcoded 1280×800 default.
- New `dom_file` optional input: when provided, acquisition skips DOM extraction (Steps 4-6) and captures screenshots only. Used for the second pass in "both" mode.
- Correct `agent-browser` CLI syntax: `set viewport W H` for desktop, `set device "iPhone 14"` for mobile. Documented `--args "--force-device-scale-factor=2"` alternative for custom DPR.
- WebFetch fallback blocked for URL inputs (caused the false-positive bug). File path and pasted code inputs still work without agent-browser.

#### Device-Aware Auditor Principles (3 changes)
- Auditor workflows (`audit.md`, `quick-scan.md`) receive device context and apply device-appropriate principles. Desktop emphasizes F/Z scan patterns, visual hierarchy, grid layout. Mobile emphasizes sticky CTAs, touch targets (48px+), thumb zones, single-column flow.
- DOM caveat for mobile: auditors are told "DOM was captured at desktop viewport — screenshots are primary for mobile layout judgments."
- De-emphasis rules prevent false positives: desktop auditors skip touch target analysis, mobile auditors skip left-side dominance rules.

#### Embedded Rationale & Citations (2 changes)
- Every FAIL and PARTIAL finding now includes a `**Why this matters:**` block (2-3 sentence rationale) + citation line pointing to the specific reference file, finding number, study name, and year.
- Updated finding format in `workflows/audit.md`, `workflows/quick-scan.md`, and `templates/audit.md.template`.

#### Model Upgrade (1 change)
- ALL subagent dispatches upgraded to Opus 4.6 — acquisition, auditors, planners, reconciler, reviewer, builder. No more tiered pinning. Testing showed Sonnet produced color misidentification and SOURCE attribution errors that Opus eliminated completely. Users running on Opus expect Opus quality throughout the pipeline.

#### Downstream Consumer Updates (5 changes)
- `meta.json` schema: new `devices_requested` and `devices_scanned` fields (added to template and validation lists in audit/quick-scan/compare SKILLs).
- `/cro:resume` reads device context from meta.json. Old engagements without `devices_scanned` default to `["desktop"]`. Offers retry when `devices_requested` != `devices_scanned`.
- Quick-scan aggregate filters by device — no cross-device comparison.
- Progress comparison skips if previous engagement used a different viewport width.
- Visual report template: CSS `max-width` scaling for 2x+ DPR mobile screenshots, device label in metadata bar.

#### Concurrency & Atomicity (2 changes)
- "Both" mode auditor concurrency capped at 3 per batch (desktop batch completes, then mobile batch). Prevents rate limit issues with 6 simultaneous Opus subagents.
- Write order enforced: audit files written to disk first, `devices_scanned` updated in meta.json last. Preserves "file existence wins" atomicity invariant.

#### Annotated Wireframe Visual Report (3 changes)
- Visual report rewritten as split-panel dark-mode layout: DOM-derived wireframe with numbered callout markers on the left, finding cards with rationale on the right. Screenshots embedded as expandable disclosures within wireframe sections.
- Wireframe uses the site's actual extracted colors (background, text, CTA, link) and real product names/prices from DOM. Fold line indicator shows approximate viewport boundary.
- Visual report now generated inline by the coordinator (not dispatched as a subagent). `workflows/visual-report.md` changed from subagent instructions to coordinator reference documentation.

#### SOURCE Accuracy Fix (2 changes)
- Strict SOURCE verification rules added to `workflows/audit.md` and `workflows/quick-scan.md`: SOURCE: VISUAL requires screenshot-verifiable evidence (self-check question), DOM-only evidence must be SOURCE: CODE with explicit note "detected in DOM but not visually rendered at this viewport."
- Prevents the class of false positives where auditors claim visual evidence for hover-only or CSS-hidden elements found only in the DOM.

#### Files Modified (13 + 2 rewritten)
- `workflows/acquire.md`, `workflows/audit.md`, `workflows/quick-scan.md`, `workflows/compare.md`
- `workflows/visual-report.md` (rewritten — coordinator reference, no longer subagent dispatch)
- `skills/cro/SKILL.md`, `skills/cro/audit/SKILL.md`, `skills/cro/quick-scan/SKILL.md`, `skills/cro/compare/SKILL.md`, `skills/cro/resume/SKILL.md`
- `templates/meta.json.template`, `templates/audit.md.template`, `templates/audit-competitor.md.template`
- `templates/visual-report.html.template` (rewritten — split-panel wireframe layout)

---

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
