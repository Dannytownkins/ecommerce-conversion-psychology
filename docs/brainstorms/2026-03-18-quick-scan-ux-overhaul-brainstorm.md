---
date: 2026-03-18
topic: quick-scan-ux-overhaul
---

# Quick-Scan UX Overhaul

## What We're Building

A comprehensive UX overhaul of the CRO plugin's output system — findings format, visual reports, citation credibility, screenshot-based annotation, and report consistency. The goal is to make every report feel like it came from a CRO consultancy, not an AI tool, while working equally well for non-technical founders and dev-savvy store owners.

This touches the quick-scan output primarily but applies across all engagement types (audit, build, compare).

## Why This Approach

The current system is functional but has UX problems: FAIL/PASS feels judgmental and binary, SOURCE labels confuse non-devs, wireframes look AI-generated, citation credibility is invisible, and Claude has too much creative freedom in report HTML — causing structural inconsistency across runs.

Rather than incremental patches, a holistic redesign addresses the interconnected nature of these issues: the report template, findings format, visual rendering, and export flow all need to change together.

## Key Decisions

### 1. Severity scoring: Keep CRITICAL/HIGH/MEDIUM/LOW, kill FAIL/PASS
- **Rationale:** The 4-tier priority system already exists and works. The problem is the binary PASS/FAIL stamp, not the severity model. Remove PASS/FAIL from finding headers entirely. Lead with the priority tier (color-coded). A finding's existence implies it needs attention — no need to stamp "FAIL" on it.

### 2. SOURCE labels: Collapse into progressive disclosure
- **Rationale:** Non-devs don't care whether an issue was found via screenshot or DOM. SOURCE type (VISUAL/CODE/BOTH) moves into a collapsible "Technical details" section within each finding. Devs who want it can expand; everyone else sees a clean finding.

### 3. Evidence tiers: 3-tier inline badges + quality flags
- **Tier is locked to publisher reputation — never upgraded or downgraded per citation.**
- **Tiers:**
  - **Gold** — Baymard Institute, NNGroup, peer-reviewed journals (PMC/NIH, SAGE, Oxford JCR, Springer, ScienceDirect, ACM CHI), Spiegel Research Center, Laws of UX, Google CrUX
  - **Silver** — CXL, Stripe, W3C, Shopify enterprise blog, Forrester/McKinsey/Gartner, Google Developers blog
  - **Bronze** — VWO Blog, Campaign Monitor, HubSpot, Neil Patel, GrowthSuite, Yieldify, TargetBay, any "(2026)" blog repackaging older stats
  - **Do not cite** — Dead URLs with no alternative source. Drop the specific number, keep the recommendation if supported by other citations.
- **Quality flags (optional, per-citation):** When a citation's evidence quality diverges from its tier norm, add a brief note. Examples: "methodology note: N=50,000 across 12 sites" (Bronze citation with unusually strong methodology) or "editorial; no sample data for this claim" (Gold source with a weak specific citation). Most citations won't need a flag.
- **Visibility:** Tier badge inline next to every cited stat. Quality flag shown alongside when present. Always visible, not hidden behind a click.
- **Data model per citation:** `evidence_tier` (Gold/Silver/Bronze, locked to source) + optional `quality_flag` (string, only for outliers).
- **Implementation:** Additive-only change to reference files — add `evidence_tier` and optional `quality_flag` fields to each finding. No destructive edits. Git history serves as backup. New criteria doc (`references/evidence-tiers.md`) defines the classification rules.

### 4. Visual report theme: Match the site's color mode
- **Logic:** Acquisition already extracts `bg` and `container_bg` colors. Infer light/dark from background luminance. Report inherits the site's mode.
- **Fallback:** Dark neutral theme when colors can't be extracted (screenshot-only input).
- **No user prompt needed** — automatic based on detected site colors.

### 5. Screenshots replace wireframes as primary visual
- **Primary path:** Annotated screenshots with numbered callout markers overlaid on the actual captured screenshots.
- **Fallback path:** Wireframe rendering only for sections where screenshots are obscured (modals, popups, cookie banners blocking >30% of viewport).
- **Benefit:** Eliminates the abstract wireframe generation step for most reports. Users see their actual page with problems highlighted.
- **DOM still captured** for audit analysis — just no longer used to render the report visual.

### 6. Interactive report layout: Scroll-synced split panel
- **Left panel:** Sticky annotated screenshot(s). Markers correspond to finding numbers.
- **Right panel:** Scrollable findings list.
- **Interaction:** Scrolling through findings highlights the corresponding marker on the screenshot. Clicking a marker scrolls to the finding. Bidirectional linking.
- **"Why this matters":** Collapsed by default. Click to expand rationale + clickable citation URL with evidence tier badge.
- **Typography:** Larger font, more whitespace, no system font defaults.

### 7. Screenshot-only input mode
- **Input:** User drops a screenshot + describes what it is (e.g., "this is my mobile homepage").
- **Output:** Same report format as URL-based scans. All findings are SOURCE: VISUAL by definition.
- **Banner:** "Based on screenshot only — DOM and interaction patterns not assessed."
- **Positioning:** Cheapest possible way to use the plugin. No agent-browser, no URL scanning.

### 8. Export model
- **Markdown (`audit.md`):** Always auto-saved for both quick-scan and full audit. Silent. No prompt.
- **`meta.json`:** Always auto-saved. Silent.
- **Annotated visual report:** Opt-in. Single prompt after findings: "Want an annotated visual report too?"
- **Wireframe-only report:** Only generated as fallback when screenshots are obscured.
- **No tiered gating** — all exports get identical analysis quality.

### 9. Report consistency: Component library approach
- **Method:** Define exact HTML/CSS snippets for each report component — finding card, citation badge, evidence tier badge, screenshot panel, score strip, header, etc.
- **Assembly:** Claude selects and assembles pre-defined components. Structure is fixed per component. No freestyle HTML.
- **Result:** Every report is structurally identical. Design quality is baked into the components, not dependent on Claude's creative choices per run.
- **Components to define:** Finding card, citation with evidence badge, screenshot panel with callout overlay, score summary strip, report header, technical details expander, limitations banner, export footer.

## Resolved Questions

1. **Evidence tier classification:** One-time batch classification of all ~200+ citations. Additive-only — add `evidence_tier` field to each finding in the 26 reference files. Tier locked to publisher name (see tier definitions above). New criteria doc at `references/evidence-tiers.md`. Unclassified citations default to Bronze at runtime.

2. **Screenshot overlay rendering:** SVG overlay layer. Screenshot as `<img>`, SVG layer on top with circle+number markers. Coordinates derived from acquisition metadata (section scrollY/height). Clean separation, scales well, markers stay interactive for scroll-sync.

3. **JS in reports:** Yes — inline JavaScript for scroll-sync, marker highlighting, and collapsible sections. No external dependencies. CSS `@media print` provides a static linearized fallback for printing. Reports remain self-contained single HTML files.

4. **Component library format:** Single components reference file (e.g., `templates/components.html`). All component HTML/CSS snippets in one doc with clear section markers. Claude reads once and assembles. Single source of truth.

5. **Typography:** Base64-embedded font subsets. **Inter** (Latin 400/600/700) for body and headings. **JetBrains Mono** (Latin 400/700) for code, stats, and section slugs in technical details. ~160KB total font budget. Self-contained, no external dependencies, consistent rendering offline.

## Next Steps

-> `/workflows:plan` for implementation details
