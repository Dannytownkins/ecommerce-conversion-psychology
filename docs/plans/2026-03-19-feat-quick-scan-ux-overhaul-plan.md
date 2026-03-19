---
title: "feat: Quick-Scan UX Overhaul"
type: feat
date: 2026-03-19
deepened: 2026-03-19
brainstorm: docs/brainstorms/quick-scan-ux-overhaul-brainstorm-corrected.md
---

## Enhancement Summary

**Deepened on:** 2026-03-19
**Sections enhanced:** All 5 phases + architecture + acceptance criteria
**Agents used:** 11 (architecture-strategist, performance-oracle, security-sentinel, pattern-recognition, code-simplicity, frontend-races, data-migration-expert, 4x best-practices-researcher)

### Key Improvements
1. **CSP header fixed** — added `script-src 'unsafe-inline'` and `font-src data:` (scroll-sync JS and Base64 fonts would have silently failed)
2. **Component library split** — fonts moved to separate `templates/font-embed.css` to avoid wasting ~40,000 tokens of Claude's context window per report generation
3. **Scroll-sync upgraded** — replaced "debounced" with a proper 4-state state machine, IntersectionObserver root configuration, image decode gating, and `scrollend` event handling
4. **SVG overlay hardened** — element whitelist for security, `viewBox`/`preserveAspectRatio` for responsive scaling, anti-collision nudge algorithm, accessibility markup
5. **Batch classification de-risked** — actual finding count corrected to 314, rollback strategy added, verification script defined, heading normalization pre-step, multi-source tier rule added
6. **Concrete design tokens** — specific hex values, WCAG contrast ratios verified, ambient glow CSS locked down, typography scale defined
7. **"Do not cite" rewrite approach fixed** — deprecation annotation instead of destructive edits to preserve backward compatibility

### New Considerations Discovered
- `checkout-optimization.md` uses `##` headings (not `###`) — normalize before batch classification
- `ab-testing-patterns.md` has 0 findings — skip during classification
- Standard report template is light-themed — dark chrome migration is a breaking visual change for existing standard reports
- SVG `<script>`, `<foreignObject>`, `<use>` elements must be explicitly forbidden in overlay generation
- `align-self: flex-start` required on sticky panel in flex container (common browser gotcha)

---

## v3.1.0 Regression Safeguards (NON-NEGOTIABLE)

These four issues occurred in the v3.1.0 implementation and **must not recur**. Every phase must verify these explicitly.

### 1. Ethics gate MUST appear in all report outputs
The ethics gate (`references/ethics-gate.md`) is checked during audits but its findings were **not rendered** in the v3.1.0 reports. The workflows reference it, but neither `audit.md.template` nor the visual report template had a section for ethics violations.

**Fix in this plan:**
- Add an **Ethics Compliance section** to the component library (new component #13 in Phase 1.3)
- Ethics violations render as CRITICAL-severity finding cards with a distinct "Ethics/Legal" badge
- If the ethics gate flags ANY violation, it MUST appear in: audit.md, visual-report.html, and report.html
- If no violations found, render a brief "Ethics check: No dark patterns detected" line in the report footer
- Update `templates/audit.md.template` to include ethics gate output format (Phase 2.3)
- Update `workflows/audit.md` and `workflows/quick-scan.md` to explicitly output ethics findings (not just check them internally)

### 2. Citation URLs MUST be clickable in reports
The `citations/sources.md` file has all URLs but is marked "for human verification only" — agents don't consume it. The v3.1.0 audit.md.template used author/year format with **no URLs**. Users could not click through to verify citations.

**Fix in this plan:**
- The citation line in `audit.md.template` must include the source URL:
  ```
  ↳ [reference-file.md], Finding [N] ([Study/Author], [Year]) [Gold|Silver|Bronze]
    URL: https://...
  ```
- Each reference file finding already has a `**Source**` field with the URL. Auditors must copy the URL into the citation line.
- In visual reports: citation URLs render as clickable `<a href="..." rel="noopener noreferrer" target="_blank">` links
- In the "Why this matters" collapsible: the full citation with clickable URL is shown
- In audit.md markdown: URLs appear as plain text (clickable in most markdown viewers)
- `citations/sources.md` annotation should be changed from "human verification only" to "reference index" — agents CAN read it for URL lookup when the reference file's Source field is ambiguous

### 3. Screenshot panel MUST be sticky (scroll-following)
The left panel with annotated screenshots must remain fixed/visible as the user scrolls through findings in the right panel. This is the core interactive feature of the visual report. In v3.1.0, the sticky behavior was inconsistent.

**Fix in this plan:**
- CSS: `position: sticky; top: 0; height: 100dvh; overflow-y: auto; align-self: flex-start` (Phase 1.3, component 7)
- Parent flex container must NOT have `overflow` set (kills sticky)
- `align-self: flex-start` is critical (not the default `stretch`)
- `100dvh` with `100vh` fallback for mobile
- This is verified in the Quality Gates: "Bidirectional scroll-sync tested in Chrome, Firefox, Safari"

### 4. Audit analysis accuracy MUST NOT regress
The v3.1.0 audits were less accurate than their predecessor. This plan changes report **output/rendering** — it must NOT alter the audit analysis logic, reference file consumption patterns, or finding quality.

**Safeguards:**
- Phase 2.1 (evidence tier classification) adds fields to reference files but does NOT modify existing `Key Finding`, `Source`, `Methodology`, `Boundary Conditions`, or `E-Commerce Application` fields
- Phase 2.3 adds the evidence tier tag to the citation line but does NOT change the finding format (FINDING/SECTION/SOURCE/PRIORITY/OBSERVATION/RECOMMENDATION/REFERENCE fields stay identical)
- `workflows/audit.md` and `workflows/quick-scan.md` analysis instructions are NOT modified — only output formatting instructions change
- All model pinning (Opus 4.6 for all subagents) from v3.1.0 is preserved
- Quality gate added: run at least 1 side-by-side comparison of a v3.1.0 audit vs v4.0.0 audit on the same page to verify finding quality parity

---

# Quick-Scan UX Overhaul

## Overview

A comprehensive overhaul of the CRO plugin's report output system. The goal: every report feels like it came from a premium CRO consultancy, not an AI tool. This touches findings format, visual reports, citation credibility, screenshot annotation, and report structural consistency across all engagement types.

Ten interconnected decisions ship as one coordinated release. The implementation is phased so that foundational changes (component library, evidence tiers, data model) land before visual and interactive changes that depend on them.

## Problem Statement

The current output system is functional but has compounding UX problems:

- **FAIL/PASS feels judgmental and binary.** A finding's existence already implies it needs attention. The severity tier (CRITICAL/HIGH/MEDIUM/LOW) carries the weight. PASS/FAIL/PARTIAL/SKIP stamps add noise.
- **SOURCE labels confuse non-devs.** Non-technical founders don't care whether an issue was found via screenshot or DOM. Labeling every finding VISUAL/CODE/BOTH is noisy for the majority audience.
- **Citation credibility is invisible.** A stat from Baymard Institute and a stat from a 2026 blog repackaging older research look identical. Users have no way to judge evidence quality.
- **Wireframes look AI-generated.** The abstract wireframe rendering step produces visuals that feel synthetic. Users want to see their actual page with problems highlighted.
- **Claude has too much creative freedom in report HTML.** Structure varies across runs because the report workflow is generative, not assembly-based. Every report should be structurally identical.
- **Export flow is inconsistent.** Quick-scan prompts for save; audit saves differently. The model should be simple: markdown always auto-saves, visual report is opt-in.

## Proposed Solution

Ship all 10 brainstorm decisions as a coordinated release across 5 implementation phases:

1. **Foundation** — Component library, design tokens, font embedding, evidence tier criteria
2. **Data Model** — Batch evidence tier classification, meta.json updates, finding format changes
3. **Visual Report Rebuild** — Screenshot-primary rendering, SVG overlays, split-panel with scroll-sync
4. **Input & Export** — Screenshot-only input mode, auto-save model, export flow cleanup
5. **Workflow Integration** — Update all workflow files, skill files, and templates to consume the new system

## Technical Approach

### Architecture

The component library is split into two files to optimize Claude's context window usage:

- **`templates/components.html`** (~20-30KB) — All HTML/CSS snippets for every report component, locked-down scroll-sync JavaScript, CSS design tokens, and `@media print` linearization rules. This is what Claude reads.
- **`templates/font-embed.css`** (~140-200KB) — Base64-encoded `@font-face` declarations for Inter and JetBrains Mono. Claude **never reads this file** — the assembly instructions say "copy the contents of `templates/font-embed.css` into the `<head>` verbatim."

This split prevents ~40,000 tokens of Base64 font data from consuming Claude's context window on every report generation. The font data is pure binary noise to the language model.

Claude reads `components.html` once and assembles reports by selecting and populating pre-defined components. No freestyle HTML generation. Structure is fixed; only content varies per run.

**Key architectural decisions (resolved during planning):**

| Decision | Resolution |
|----------|-----------|
| Screenshot-only `source_mode` | New value: `screenshot` in meta.json |
| Marker positioning (screenshot-only) | Claude estimates pixel coordinates from visual analysis |
| PARTIAL/SKIP in visual output | All four statuses hidden. Only severity tier renders. Kept in data model. |
| Auto-save model | audit.md + meta.json always auto-saved, silent. Visual report is only opt-in prompt. |
| Desktop/mobile reports | Separate files (keep current pattern) |
| Font storage | Base64 subsets in separate `templates/font-embed.css` (copied verbatim, never parsed by Claude) |
| Scroll-sync JS | Locked-down snippet in `components.html` with 4-state state machine |

### Implementation Phases

---

#### Phase 1: Foundation

**Goal:** Build the infrastructure that all other phases depend on.

**Estimated effort:** Large (component library is the most design-intensive deliverable)

##### 1.1 Create evidence tier criteria document

**File:** `references/evidence-tiers.md` (new)

Define the classification rules:

- **Gold tier** publishers: Baymard Institute, NNGroup, peer-reviewed journals (PMC/NIH, SAGE, Oxford JCR, Springer, ScienceDirect, ACM CHI), Spiegel Research Center, Laws of UX, Google CrUX
- **Silver tier** publishers: CXL, Stripe, W3C, Shopify enterprise blog, Forrester/McKinsey/Gartner, Google Developers blog
- **Bronze tier** publishers: VWO Blog, Campaign Monitor, HubSpot, Neil Patel, GrowthSuite, Yieldify, TargetBay, any "(2026)" blog repackaging older stats
- **Do not cite** rule: Dead URLs with no alternative source. Drop the specific number, keep the recommendation if supported by other citations. If the dead URL is the only citation for a specific stat, rewrite the finding to remove the unsupported number and soften to a qualitative claim (e.g., "significant increase" instead of "232% increase").
- **Unclassified sources** default to Bronze at runtime. Document the process for adding new sources: edit `evidence-tiers.md`, add the publisher to the appropriate tier list.
- **Quality flag** guidance: Optional per-citation string. Only for outliers where evidence quality diverges from tier norm. Examples provided in the doc. Most citations need no flag.

**Acceptance criteria:**
- [ ] `references/evidence-tiers.md` exists with all tier definitions, publisher lists, quality flag guidance, and "do not cite" handling rules
- [ ] Includes a process section for adding new sources to the tier list
- [ ] Includes handling for single-citation findings with dead URLs

##### 1.2 Generate Base64 font subsets

**Output file:** `templates/font-embed.css` (new, separate from components.html)

Generate Latin subsets of Inter (400/600/700) and JetBrains Mono (400/700) as Base64-encoded `@font-face` declarations.

**Realistic size estimates (from research):**

| Font | Weights | WOFF2 (raw) | Base64 |
|------|---------|-------------|--------|
| Inter 400 | 1 | ~23 KB | ~31 KB |
| Inter 600 | 1 | ~24 KB | ~32 KB |
| Inter 700 | 1 | ~24 KB | ~32 KB |
| JetBrains Mono 400 | 1 | ~20 KB | ~27 KB |
| JetBrains Mono 700 | 1 | ~21 KB | ~28 KB |
| **Total** | **5 files** | **~112 KB** | **~150 KB** |

**Unicode range (Latin-only, sufficient for CRO reports):**
```
U+0000-00FF, U+0131, U+0152-0153, U+02BB-02BC, U+02C6,
U+02DA, U+02DC, U+2000-206F, U+2074, U+20AC, U+2122,
U+2191, U+2193, U+2212, U+2215, U+FEFF, U+FFFD
```

**Subsetting commands:**
```bash
pip install fonttools brotli

# Inter (per weight)
pyftsubset Inter-Regular.ttf \
  --unicodes="U+0000-00FF,U+0131,U+0152-0153,U+02BB-02BC,U+02C6,U+02DA,U+02DC,U+2000-206F,U+2074,U+20AC,U+2122,U+2191,U+2193,U+2212,U+2215,U+FEFF,U+FFFD" \
  --layout-features="calt,dnom,frac,locl,numr,pnum,tnum,kern" \
  --flavor=woff2 \
  --output-file=inter-latin-400.woff2

# JetBrains Mono (per weight)
pyftsubset JetBrainsMono-Regular.ttf \
  --unicodes="U+0000-00FF,U+0131,U+0152-0153,U+02BB-02BC,U+02C6,U+02DA,U+02DC,U+2000-206F,U+2074,U+20AC,U+2122,U+2191,U+2193,U+2212,U+2215,U+FEFF,U+FFFD" \
  --layout-features="calt,locl,kern,zero,ss01" \
  --flavor=woff2 \
  --output-file=jetbrains-mono-latin-400.woff2
```

**@font-face format:**
```css
@font-face {
  font-family: 'Inter';
  font-style: normal;
  font-weight: 400;
  font-display: block;  /* correct for inline fonts — no network fetch */
  src: url('data:font/woff2;base64,...') format('woff2');
}
/* ... repeat for each weight ... */

body {
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
}
code, .stat-value {
  font-family: 'JetBrains Mono', 'SF Mono', 'Fira Code', 'Consolas', monospace;
}
```

**Notes:** `font-display: block` is correct because with data URIs there is no network fetch — the font is already inline. Keep system font fallbacks in the stack for safety. MIME type `font/woff2` is the modern standard.

**Acceptance criteria:**
- [ ] `templates/font-embed.css` exists (separate file, not in components.html)
- [ ] Inter Latin subset: 400, 600, 700 weights in WOFF2
- [ ] JetBrains Mono Latin subset: 400, 700 weights in WOFF2
- [ ] Total Base64 size verified (target ~150KB, acceptable up to 200KB)
- [ ] System font fallbacks included in font-family stacks

##### 1.3 Build the component library

**File:** `templates/components.html` (new)

A single reference file containing all HTML/CSS/JS snippets for report assembly. Organized with clear section markers (HTML comments). Claude reads this file once per report generation and assembles by selecting components.

**Components to define (11 total):**

1. **Design tokens** — CSS custom properties (concrete values from research, WCAG AA verified):
   ```css
   :root {
     /* Surfaces (ascending elevation) */
     --bg-body: #0e0e10;      /* deepest — cool cast from blue channel */
     --bg-surface: #141418;   /* cards, panels — 6 steps brighter */
     --bg-elevated: #1a1a1f;  /* dropdowns, popovers */
     --bg-hover: #2e2e36;     /* interactive hover states */

     /* Borders — semi-transparent white adapts to any surface */
     --border-default: rgba(255,255,255,0.08);
     --border-strong: rgba(255,255,255,0.12);   /* card outlines */
     --border-emphasis: rgba(255,255,255,0.16);  /* focused/active */

     /* Text — all pass WCAG AA on --bg-body */
     --text-primary: #e4e4e7;    /* 15.7:1 ratio */
     --text-secondary: #a1a1aa;  /* 8.2:1 ratio */
     --text-tertiary: #71717a;   /* 4.8:1 ratio — large text only on cards */
     --text-muted: #52525b;      /* 3.1:1 — disabled states only */

     /* Severity — 400-weight variants for softer feel on near-black */
     --severity-critical: #f87171;     --severity-critical-bg: #2c1113;
     --severity-high: #fbbf24;         --severity-high-bg: #2c1d0e;
     --severity-medium: #60a5fa;       --severity-medium-bg: #0f1a2e;
     --severity-low: #a1a1aa;          --severity-low-bg: #1a1a1f;

     /* Severity card borders — semi-transparent accent at 20-25% */
     --border-critical: rgba(248,113,113,0.25);
     --border-high: rgba(251,191,36,0.20);
     --border-medium: rgba(96,165,250,0.20);
     --border-low: rgba(161,161,170,0.12);

     /* Typography */
     --font-sans: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
     --font-mono: 'JetBrains Mono', 'SF Mono', 'Fira Code', monospace;
     --text-xs: 0.75rem; --text-sm: 0.8125rem; --text-base: 0.875rem;
     --text-lg: 1rem; --text-xl: 1.25rem; --text-2xl: 1.5rem; --text-3xl: 2rem;
   }
   ```
   - **Ambient glow** (locked-down, must NOT compete with severity):
     ```css
     .report-body {
       background-color: var(--bg-body);
       background-image:
         radial-gradient(ellipse 80% 50% at 10% 0%, rgba(99,102,241,0.04), transparent 70%),
         radial-gradient(ellipse 60% 80% at 85% 100%, rgba(124,58,237,0.03), transparent 60%),
         radial-gradient(ellipse 120% 80% at 50% 30%, rgba(59,130,246,0.02), transparent 50%);
     }
     ```
   - Opacity 0.02-0.04 range. Hue 220-280 (indigo/violet/blue). Elliptical for organic feel.
   - **Typography features:** `font-feature-settings: 'cv01','cv02','cv03','cv04'` on Inter (disambiguates Il1). `'zero','ss01'` on JetBrains Mono (slashed zero).
   - **14px base** (not 16px) — matches report-density conventions (Linear, Vercel, Stripe).
   - **No box-shadow on near-black** — shadows are invisible. Use borders for elevation.

2. **Font embed reference** — Assembly instruction: "Copy contents of `templates/font-embed.css` into `<head>` verbatim." Claude does not read font-embed.css.

3. **Report header** — Title, URL, date, device badge, engagement type badge

4. **Score summary strip** — Horizontal strip showing CRITICAL/HIGH/MEDIUM/LOW counts with color-coded badges. No PASS/FAIL counts.

5. **Finding card** — The core component. Parameterized by severity (CSS class: `finding--critical`, `finding--high`, `finding--medium`, `finding--low`).
   - Numbered marker (matches SVG overlay)
   - Severity badge (color-coded, always visible)
   - Title (observation summary)
   - Observation text
   - Recommendation text
   - Citation footer: reference file + finding number + study/author + year + **clickable source URL** + evidence tier badge (always visible). The URL is a `<a href="..." rel="noopener noreferrer" target="_blank">` link.
   - Collapsible "Why this matters" section: rationale text + full citation with clickable URL + evidence tier badge
   - Collapsible "Technical details" section: SOURCE type (VISUAL/CODE/BOTH), SECTION slug, REFERENCE path

6. **Evidence tier badge** — Inline badge component.
   - Gold: gold/amber badge
   - Silver: silver/gray badge
   - Bronze: bronze/copper badge
   - Optional quality flag text rendered alongside when present
   - CSS: small, pill-shaped, monochrome-compatible

7. **Screenshot panel** — Left-panel container for the split-panel layout.
   - Split layout: `display: flex; height: 100vh` on parent (NO overflow on parent)
   - Sticky positioning: `position: sticky; top: 0; height: 100dvh; overflow-y: auto; align-self: flex-start`
   - **Critical:** `align-self: flex-start` required (not `stretch`) for sticky to work in flex containers
   - **Critical:** Use `100dvh` with `100vh` fallback for mobile dynamic viewport
   - Contains one or more screenshot `<img>` elements with SVG overlay layer
   - SVG overlay: `<svg>` positioned absolutely over the screenshot container
     - `viewBox` dimensions MUST match the screenshot's `naturalWidth x naturalHeight`
     - `preserveAspectRatio="xMinYMin meet"` — anchors top-left, no cropping, scales proportionally
     - Container: `position: relative; line-height: 0` (eliminates inline gap below img)
     - SVG: `position: absolute; top: 0; left: 0; width: 100%; height: 100%`
     - `pointer-events: none` on SVG, `pointer-events: all` on individual markers
   - **SVG safety rules (security):** Only these elements permitted: `<svg>`, `<circle>`, `<text>`, `<g>`, `<defs>`, `<style>`, `<line>`. NO `<script>`, `<foreignObject>`, `<use>`, `<image>`, `<a>`. No `on*` event handler attributes. All `<text>` content must be numeric only (finding number). All `data-finding` values must match `^[a-z0-9-]+$`.
   - **Accessibility:** `role="group"` on SVG, `role="button"` + `tabindex="0"` + `aria-label` on each marker `<g>`, `aria-hidden="true"` on the visible `<text>` number
   - Marker interaction: clickable, linked to finding card IDs via `data-finding` attributes

8. **Device frame** — Phone bezel/frame mockup for mobile screenshots.
   - CSS-only device frame (rounded rect with notch, no image dependency)
   - Wraps the screenshot `<img>` inside the frame
   - Only used for mobile reports; desktop screenshots render without a frame

9. **Limitations banner** — "Based on screenshot only" banner for screenshot-only mode, or "Wireframe fallback" banner for obscured sections.

10. **Export footer** — Report metadata: generation date, plugin version, engagement ID, device mode

11. **Scroll-sync controller** — Inline JavaScript for bidirectional scroll-sync. Implements a **4-state state machine** to prevent feedback loops (not simple debounce):

    **States:** `IDLE`, `USER_SCROLLING_FINDINGS`, `USER_SCROLLING_SCREENSHOTS`, `PROGRAMMATIC_SCROLL`

    | Current State | Event | Next State |
    |---|---|---|
    | IDLE | User scrolls findings | USER_SCROLLING_FINDINGS |
    | IDLE | User scrolls screenshots | USER_SCROLLING_SCREENSHOTS |
    | IDLE | Marker click | PROGRAMMATIC_SCROLL |
    | USER_SCROLLING_FINDINGS | Observer fires | Highlight marker + scroll screenshot (→ PROGRAMMATIC for screenshot side) |
    | USER_SCROLLING_SCREENSHOTS | Observer fires | Highlight finding (no cross-scroll) |
    | PROGRAMMATIC_SCROLL | Any observer | **Ignored** |
    | PROGRAMMATIC_SCROLL | `scrollend` or 800ms timeout | IDLE |
    | Any | `beforeprint` | IDLE (disconnect observers) |

    **Implementation requirements:**
    - `IntersectionObserver` with **explicit `root`** set to the findings panel (NOT the default viewport). Same for screenshot panel markers.
    - `rootMargin: '-10% 0px -60% 0px'` — biases active zone to top 30% of panel, prevents ambiguity when multiple findings visible
    - `threshold: [0, 0.25, 0.5, 0.75, 1.0]` — finer-grained visibility detection
    - **"Most centered" finding wins** when multiple findings are visible simultaneously — calculate which finding's bounding rect center is closest to panel viewport center
    - `requestAnimationFrame` coalescing for observer side-effects (not debounce)
    - `scrollIntoView({ behavior: 'smooth', block: 'center' })` for navigation
    - **Guard flag:** `isProgrammaticScroll` boolean, cleared by `scrollend` event (Chrome 114+, Firefox 109+, Safari 17.4+) with 800ms `setTimeout` fallback
    - **Marker clicks:** Last-write-wins (not debounce). `scrollIntoView` naturally interrupts in-progress smooth scrolls.
    - **Image decode gating:** Before initializing observers, wait for all base64 images to decode:
      ```javascript
      Promise.allSettled(
        Array.from(images).map(img => img.complete ? Promise.resolve() : img.decode().catch(() => {}))
      ).then(initScrollSync);
      ```
    - **Print safety:** `beforeprint` listener disconnects all observers and clears scroll state. `afterprint` reconnects.
    - **Collapsible section expand/collapse:** RAF coalescing naturally handles layout changes from expanding "Why this matters" sections.
    - **Never use:** `innerHTML`, `outerHTML`, `document.write`, `eval` in scroll-sync code. Use `getElementById` over `querySelector` with data attributes where possible.
    - Total JS: ~60-80 lines. No external dependencies.

**Also includes:**

12. **Print linearization** — `@media print` CSS rules using **token reassignment** (not `filter: invert()`):
    ```css
    @media print {
      :root {
        --bg-body: #ffffff; --bg-surface: #f8f8f8;
        --text-primary: #111111; --text-secondary: #444444;
        --border-default: #e0e0e0; --border-strong: #cccccc;
        --severity-critical: #dc2626; --severity-critical-bg: #fef2f2;
        --severity-high: #d97706; --severity-high-bg: #fffbeb;
        --severity-medium: #2563eb; --severity-medium-bg: #eff6ff;
        --severity-low: #6b7280; --severity-low-bg: #f3f4f6;
      }
      .report-body { background-image: none !important; }
      .split-layout { display: block; height: auto; }
      .left-panel, .right-panel { position: static; width: 100%; overflow: visible; }
      * { print-color-adjust: exact; -webkit-print-color-adjust: exact; }
      img { max-width: 100% !important; max-height: 90vh; page-break-inside: avoid; }
      .finding-card { break-inside: avoid; page-break-inside: avoid; }
      @page { margin: 1.5cm 2cm; size: A4; }
    }
    ```
    - Split-panel collapses to single column (`display: block`)
    - Interleaved layout: each screenshot followed by its associated findings
    - All "Why this matters" sections expanded
    - All "Technical details" sections expanded
    - Markers rendered as static numbers (no interactivity)
    - Token reassignment preserves severity color semantics (red stays red, not cyan from inversion)
    - `max-height: 90vh` on images prevents single screenshot from spanning more than one page

13. **Ethics compliance section** — Rendered after findings, before export footer.
    - If ethics violations found: each violation renders as a CRITICAL finding card with a distinct "Ethics/Legal" badge (different from the standard severity badge — uses a ⚖ legal icon or "ETHICS" label)
    - If no violations: single line "Ethics check: No dark patterns detected" in the report footer area
    - References specific regulations (EU DSA Art 25, FTC Fake Reviews Rule, CA SB-478) when applicable
    - This component is mandatory in every report — cannot be omitted or collapsed

**Also define in Phase 1.3:** A small set of documented **escape hatches** for edge cases — e.g., a `custom-note` block component for findings that don't fit the standard card structure. Define these in Phase 1 so Phase 3 implementers have them available.

**Acceptance criteria:**
- [ ] `templates/components.html` exists with all 11 components + print rules (~20-30KB)
- [ ] `templates/font-embed.css` exists separately (~140-200KB)
- [ ] Table of contents comment block at top of components.html listing all components
- [ ] Each component has a clear section marker (HTML comment header)
- [ ] Finding card has 4 severity variants via CSS class
- [ ] Evidence tier badge has 3 variants (Gold/Silver/Bronze)
- [ ] Scroll-sync JS implements 4-state state machine (not simple debounce)
- [ ] IntersectionObserver uses explicit `root` (not default viewport)
- [ ] Image decode gating before observer initialization
- [ ] Print linearization uses token reassignment (not filter: invert)
- [ ] All colors use CSS custom properties (design tokens) with WCAG AA verified
- [ ] Ambient glow locked-down CSS: 3 radial-gradients at 0.02-0.04 opacity
- [ ] Device frame is CSS-only (no image dependency)
- [ ] SVG safety: element whitelist enforced, no script/foreignObject/use elements
- [ ] SVG accessibility: role="group" on SVG, role="button" + tabindex="0" on markers
- [ ] Escape hatch component(s) defined for edge cases

---

#### Phase 2: Data Model Updates

**Goal:** Update reference files, meta.json, and finding format so all downstream rendering has the data it needs.

**Estimated effort:** Large (batch classification of **314 findings** across 17 files with findings is the bottleneck)

##### 2.1 Batch classify evidence tiers across all reference files

**Files:** All 18 domain reference files in `references/`:
- `cta-design-and-placement.md`
- `color-psychology.md`
- `eye-tracking-and-scan-patterns.md`
- `mobile-conversion.md`
- `cognitive-load-management.md`
- `pricing-psychology.md`
- `trust-and-credibility.md`
- `social-proof-patterns.md`
- `checkout-optimization.md`
- `page-performance-psychology.md`
- `personalization-psychology.md`
- `post-purchase-psychology.md`
- `search-and-filter-ux.md`
- `biometric-and-express-checkout.md`
- `cookie-consent-and-compliance.md`
- `cross-cultural-considerations.md`
- `social-commerce-psychology.md`
- `ab-testing-patterns.md`

**For each finding in each file, add two fields:**

```markdown
- **Evidence Tier**: [Gold|Silver|Bronze]
- **Quality Flag**: [optional string, only for outliers]
```

**Classification rules:**
- Tier is locked to the publisher name (per `references/evidence-tiers.md` from Phase 1)
- **Multi-source findings:** When a finding cites multiple sources from different tiers (e.g., CXL [Silver] + HubSpot [Bronze]), assign the tier of the **primary (first-listed) source**
- If the source URL is dead and no alternative exists: **do NOT rewrite the finding**. Instead, add a deprecation annotation: `**Citation Status**: Original source URL dead; stat unverifiable`. Keep the original stat intact so existing audit.md references remain valid.
- Sources not listed in any tier default to Bronze
- Quality flags only for genuine outliers (unusually strong methodology from a Bronze source, or unusually weak claim from a Gold source)

**Field insertion position:** Add `Evidence Tier` and `Quality Flag` as the **last two fields** in each finding block, after `Boundary Conditions`. This must be consistent across all 314 findings.

**Pre-migration cleanup (before classification):**
1. Normalize heading levels: `checkout-optimization.md` uses `## Finding N` while all other files use `### Finding N`. Normalize to `### Finding N` in a separate commit before classification begins.
2. Reconcile metadata: verify `**Total Findings**` header count matches actual heading count in each file.
3. Note: `ab-testing-patterns.md` has **0 findings** — it is a guidance document. Skip it during classification.

**Process:**
1. Create a git tag `pre-evidence-tier-classification` before starting
2. Process files in batches of 3-4 per commit (not all 17 at once)
3. After each batch, run verification (see below)
4. If a batch introduces errors, revert that commit only

**Verification script (run after each batch):**
```bash
for f in references/*.md; do
  findings=$(grep -cE "^#{2,3} Finding" "$f")
  tiers=$(grep -c "Evidence Tier" "$f")
  if [ "$findings" -ne "$tiers" ] && [ "$findings" -ne 0 ]; then
    echo "MISMATCH: $f has $findings findings but $tiers tier annotations"
  fi
done
# Check for invalid tier values
grep "Evidence Tier" references/*.md | grep -vE "(Gold|Silver|Bronze)" && echo "INVALID TIERS"
# Check no existing fields were deleted
for f in references/*.md; do
  sources=$(grep -c "^\- \*\*Source\*\*" "$f")
  findings=$(grep -cE "^#{2,3} Finding" "$f")
  if [ "$findings" -ne 0 ] && [ "$sources" -ne "$findings" ]; then
    echo "FIELD LOSS: $f has $findings findings but $sources Source fields"
  fi
done
```

**Acceptance criteria:**
- [ ] All 314 findings across 17 domain reference files (excluding ab-testing-patterns.md) have `evidence_tier` field
- [ ] Quality flags added only where genuinely warranted (expect <10% of findings)
- [ ] Dead URL citations handled with deprecation annotation (NOT destructive rewrite)
- [ ] Multi-source findings classified by primary source tier
- [ ] No existing fields removed — git diff shows only additive changes
- [ ] Heading levels normalized to `###` in all files (pre-migration commit)
- [ ] Git tag `pre-evidence-tier-classification` exists before first classification commit
- [ ] Verification script passes after final batch
- [ ] Fields inserted after `Boundary Conditions` consistently

##### 2.2 Update meta.json schema

**File:** `templates/meta.json.template`

Add new fields to support the UX overhaul:

```json
{
  "schema_version": 2,
  "source_mode": "url | file-path | pasted-code | screenshot",
  "screenshot_input": {
    "description": null,
    "device_context": null
  }
}
```

Changes:
- Add `screenshot` as a valid `source_mode` value
- Add optional `screenshot_input` object (only populated when `source_mode: "screenshot"`):
  - `description`: User's description of what the screenshot shows (e.g., "mobile homepage")
  - `device_context`: Inferred device type from the screenshot/description (`desktop` | `mobile` | `unknown`)
- Keep `schema_version: 2` (these are additive-only changes within v2)

**Acceptance criteria:**
- [ ] `templates/meta.json.template` updated with `screenshot` source_mode and `screenshot_input` fields
- [ ] Documented in template comments
- [ ] Backward compatible — existing meta.json files without `screenshot_input` are valid

##### 2.3 Update finding format for visual output

**Files:** `templates/audit.md.template`, `workflows/audit.md`, `workflows/quick-scan.md`

The finding format in audit.md **does not change structurally** — PASS/FAIL/PARTIAL/SKIP and SOURCE are retained in the data model. The changes are:

1. **Add evidence tier AND source URL to the citation line:**
   ```
   ↳ [reference-file.md], Finding [N] ([Study/Author], [Year]) [Gold|Silver|Bronze]
     URL: https://source-url-from-reference-file.com/...
   ```
   The `[Gold|Silver|Bronze]` tag and `URL:` line are appended so the visual report generator can render the badge AND clickable link without re-reading reference files. The URL comes from the finding's `**Source**` field in the reference file.

2. **Update audit.md.template** with the evidence tier tag in the citation format.

3. **Update workflow instructions** (audit.md, quick-scan.md) to include the evidence tier when writing citations. Auditors look up the tier from the reference file's `Evidence Tier` field for each cited finding.

**Acceptance criteria:**
- [ ] `templates/audit.md.template` citation line includes `[Gold|Silver|Bronze]` tag
- [ ] `workflows/audit.md` instructions include evidence tier lookup and output
- [ ] `workflows/quick-scan.md` instructions include evidence tier lookup and output
- [ ] Existing finding fields (FINDING, SECTION, SOURCE, PRIORITY, etc.) unchanged
- [ ] Evidence tier tag is parseable (bracketed, at end of citation line)

---

#### Phase 3: Visual Report Rebuild

**Goal:** Rebuild the visual report to use annotated screenshots as primary visual, component library for structure, and bidirectional scroll-sync for interactivity.

**Estimated effort:** Large (this is the most technically complex phase)

**Depends on:** Phase 1 (component library) and Phase 2 (evidence tiers in data)

##### 3.1 Update acquisition workflow for screenshot-primary rendering

**File:** `workflows/acquire.md`

Changes:
- Screenshots become the primary visual source for reports (not wireframes)
- Add acquisition metadata output: for each screenshot section, emit:
  ```json
  {
    "section_index": 1,
    "scroll_y": 0,
    "viewport_height": 900,
    "captured_sections": ["hero-layout", "primary-cta", "trust-above-fold"]
  }
  ```
  This maps SECTION slugs to screenshot sections so the SVG overlay can position markers.
- Wireframe generation logic moves to a fallback path: only triggered when a screenshot section has >30% occlusion (modals, popups, cookie banners). The acquisition agent flags occluded sections.
- Per-screenshot occlusion detection: if >30% of a single screenshot capture is blocked by overlays, flag that section for wireframe fallback. The visual report uses wireframe for that section only, not the entire report.

**Acceptance criteria:**
- [ ] Acquisition agent outputs section-to-slug mapping metadata alongside screenshots
- [ ] Occluded screenshots flagged with a boolean per section
- [ ] Wireframe generation only runs for flagged sections
- [ ] Unflagged sections use screenshot as-is
- [ ] Metadata format documented in workflow

##### 3.2 Rebuild visual-report.html.template

**File:** `templates/visual-report.html.template` (rewrite)

Replace the current template with one that assembles from `templates/components.html`:

**Structure:**
```html
<!DOCTYPE html>
<html lang="en">
<head>
  <!-- [COMPONENT: design-tokens] -->
  <!-- [COMPONENT: font-embed] -->
  <!-- [COMPONENT: print-linearization] -->
  <meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'unsafe-inline'; script-src 'unsafe-inline'; img-src data:; font-src data:;">
</head>
<body>
  <!-- [COMPONENT: report-header] -->
  <!-- [COMPONENT: score-summary-strip] -->

  <div class="split-panel">
    <!-- [COMPONENT: screenshot-panel] (left, sticky) -->
    <div class="findings-panel">
      <!-- [COMPONENT: limitations-banner] (if screenshot-only or wireframe fallback) -->
      <!-- [COMPONENT: finding-card] x N -->
    </div>
  </div>

  <!-- [COMPONENT: ethics-compliance] (mandatory — never omit) -->
  <!-- [COMPONENT: export-footer] -->
  <!-- [COMPONENT: scroll-sync-controller] -->
</body>
</html>
```

**Assembly instructions for workflows/visual-report.md:**
1. Read `templates/components.html` once. Copy contents of `templates/font-embed.css` into `<head>` verbatim (do not read/interpret font file).
2. Read baton files (meta.json, audit.md, screenshots)
3. For each finding: select finding-card component, fill severity class, populate content, add evidence tier badge to citation footer
4. For the screenshot panel: embed screenshots as base64 `<img>`, overlay SVG layer with markers positioned using acquisition metadata
5. If a screenshot section is flagged as occluded: use wireframe for that section's overlay instead
6. For mobile reports: wrap screenshots in device-frame component
7. Populate header, score strip, footer from meta.json
8. If `source_mode: screenshot`: add limitations-banner component
9. Inject scroll-sync JS from components.html
10. Output self-contained HTML

**The visual-report workflow (`workflows/visual-report.md`) must NOT generate any HTML structure.** It reads components, fills data, assembles. Structure comes from the component library.

**Acceptance criteria:**
- [ ] Template uses component markers (not inline HTML)
- [ ] Assembly workflow documented step-by-step in `workflows/visual-report.md`
- [ ] No freestyle HTML in the assembly process
- [ ] Screenshot panel is sticky with internal scroll
- [ ] SVG overlay positions markers using section metadata
- [ ] Device frame wraps mobile screenshots
- [ ] Wireframe fallback per-section (not whole-report)
- [ ] Limitations banner shows for screenshot-only mode
- [ ] All "Why this matters" sections collapsed by default
- [ ] All "Technical details" sections collapsed by default
- [ ] Citation URLs clickable with `rel="noopener noreferrer" target="_blank"`
- [ ] Evidence tier badges visible in citation footer (always visible, not behind collapse)
- [ ] Score summary strip shows severity counts only (no PASS/FAIL counts)
- [ ] CSP header: `default-src 'none'; style-src 'unsafe-inline'; script-src 'unsafe-inline'; img-src data:; font-src data:;`
- [ ] HTML-entity escaping extended to new fields: evidence tier text, quality flags, screenshot_input.description, all `data-*` attribute values
- [ ] SECTION slug values validated: must match `^[a-z0-9-]+$`
- [ ] `device_context` validated as enum: `desktop` | `mobile` | `unknown`

##### 3.3 SVG overlay marker system

**Defined within:** `templates/components.html` (screenshot-panel component)

**Marker rendering:**

For URL-based scans:
- Each finding has a SECTION slug (e.g., `hero-layout`, `primary-cta`)
- Acquisition metadata maps each slug to a screenshot section index + approximate Y offset
- SVG circle+number marker placed at the corresponding position on the screenshot
- Multiple findings on the same section: use anti-collision nudge algorithm (iterative separation with ~40px minimum distance). If nudged, draw a dashed leader line from the ideal position to the resolved position. Cap at 4-5 markers per section — if more, collapse into a cluster marker with count badge.

For screenshot-only scans:
- Claude visually analyzes the user's screenshot
- Outputs approximate pixel coordinates for each finding marker: `{ x: <px>, y: <px> }`
- Coordinates based on visual inspection of the screenshot content
- Same SVG overlay rendering, just with estimated coordinates instead of metadata-derived ones

**Marker interaction (handled by scroll-sync controller):**
- Click marker: scrolls right panel to corresponding finding card
- Finding card comes into view: corresponding marker gets `.active` class (visual highlight)
- Smooth scrolling, debounced

**Acceptance criteria:**
- [ ] SVG overlay layer renders correctly over base64 screenshots
- [ ] Markers positioned from acquisition metadata (URL mode) or estimated coordinates (screenshot mode)
- [ ] Multiple findings per section stack without overlapping
- [ ] Markers are clickable and linked to finding cards via `data-finding` attribute
- [ ] `.active` class styling defined in design tokens

---

#### Phase 4: Input & Export Changes

**Goal:** Add screenshot-only input mode and simplify the export model.

**Estimated effort:** Medium

**Depends on:** Phase 2 (meta.json schema) for screenshot-only; independent for export changes

##### 4.1 Screenshot-only input mode

**Files:**
- `skills/cro/quick-scan/SKILL.md` — Add screenshot-only input pathway
- `workflows/quick-scan.md` — Handle screenshot input without acquisition step

**Flow:**
1. User invokes quick-scan with an image (dropped or path) + text description
2. Skill detects image input (no URL provided)
3. Skip acquisition workflow entirely — no agent-browser, no DOM capture
4. Write meta.json with `source_mode: "screenshot"`, populate `screenshot_input.description` and inferred `screenshot_input.device_context`
5. Auditor receives the screenshot directly. All findings are `SOURCE: VISUAL` by definition (no CODE or BOTH possible).
6. Claude estimates SVG marker coordinates from visual analysis of the screenshot
7. Same finding format, same evidence tiers, same report components
8. Limitations banner: "Based on screenshot only — DOM and interaction patterns not assessed."
9. audit.md + meta.json auto-saved silently
10. Visual report offered as opt-in

**Re-audit compatibility:**
- If prior engagement was screenshot-only and new one is URL-based: new CODE-sourced findings show as "new" with a note that the prior engagement lacked code analysis
- If prior engagement was URL-based and new one is screenshot-only: CODE-sourced findings from prior engagement show as "not assessed" in the new scan

**Acceptance criteria:**
- [ ] Quick-scan skill accepts image input (file path or dropped image)
- [ ] No acquisition step when image is the input
- [ ] meta.json populated with `source_mode: "screenshot"` and `screenshot_input` fields
- [ ] All findings `SOURCE: VISUAL`
- [ ] Limitations banner rendered in visual report
- [ ] Re-audit comparison handles cross-mode gracefully
- [ ] Same report quality as URL-based scans (minus CODE-sourced findings)

##### 4.2 Simplify export model

**Files:**
- `skills/cro/quick-scan/SKILL.md` — Remove save prompt, add visual report opt-in (simple yes/no)
- `skills/cro/audit/SKILL.md` — Add export dialogue with 4 options after findings
- `workflows/report.md` — Update export instructions

**Changes:**
1. **audit.md + meta.json: Always auto-saved.** Remove any prompting around markdown save. These files are silently written after every scan (both quick-scan and full audit).
2. **Quick-scan export: Simple opt-in.** After findings are presented, single prompt: "Want an annotated visual report too?" Yes/No.
3. **Full audit export: Export dialogue.** After findings are presented, offer a structured choice:
   ```
   How would you like this exported?
   1. Markdown only (already saved)
   2. Annotated visual report (dark-mode HTML with scroll-sync)
   3. Both markdown + visual report
   4. Skip additional exports
   ```
   - Option 1: Confirm audit.md is saved, done
   - Option 2: Generate visual report per Phase 3
   - Option 3: Generate visual report (audit.md already saved)
   - Option 4: Done, audit.md already saved silently
4. **Wireframe-only report: Fallback only.** Never offered as a choice. Only generated when screenshot sections are occluded.
5. **No tiered gating.** All exports get identical analysis quality regardless of engagement type.

**Remove from quick-scan skill:**
- The v3 save prompt ("Want me to save these findings?")

**Acceptance criteria:**
- [ ] audit.md + meta.json written automatically after every scan, no prompt
- [ ] Quick-scan: single opt-in prompt for visual report
- [ ] Full audit: export dialogue with 4 options presented after findings
- [ ] No tiered gating language in any skill or workflow
- [ ] Wireframe-only report triggered by occlusion, not by user choice

---

#### Phase 5: Workflow & Template Integration

**Goal:** Update all workflow files, skill files, and templates to consume the new component library, evidence tiers, and rendering model.

**Estimated effort:** Medium

**Depends on:** All previous phases

##### 5.1 Update visual-report workflow

**File:** `workflows/visual-report.md` (rewrite)

Replace the current generative approach with component-assembly instructions:

1. Read `templates/components.html` — extract all component snippets
2. Read baton files — meta.json, audit.md (or audit-mobile.md), screenshots, acquisition metadata
3. Assemble header from meta.json fields
4. Assemble score strip from finding counts (CRITICAL/HIGH/MEDIUM/LOW only — no PASS/FAIL/PARTIAL/SKIP counts)
5. For each finding: assemble finding-card component
   - Select severity CSS class based on PRIORITY field
   - Hide FINDING status (PASS/FAIL/PARTIAL/SKIP) from rendered output
   - Move SOURCE to "Technical details" collapsible section
   - Render evidence tier badge in citation footer (always visible)
   - Render "Why this matters" as collapsible section
   - Clickable citation URL in expanded section
6a. **URL mode:** Assemble screenshot panel with SVG overlay markers positioned from acquisition metadata (section-to-slug mapping provides coordinates). Use wireframe for occluded sections. Set SVG `viewBox` to match screenshot `naturalWidth x naturalHeight`.
6b. **Screenshot-only mode:** Assemble screenshot panel with SVG overlay markers positioned from Claude's estimated pixel coordinates. Same SVG rendering, different coordinate source. No wireframe fallback (no DOM data).
6c. For mobile reports: wrap screenshots in device-frame component
7. Add limitations banner if `source_mode: screenshot`
8. **Assemble ethics compliance section** (mandatory — never omit):
   - If ethics gate flagged any violations during audit: render each as a CRITICAL finding card with "Ethics/Legal" badge
   - If no violations: render "Ethics check: No dark patterns detected" line
9. Inject scroll-sync JS
10. Add export footer with generation metadata
11. Output self-contained HTML

**Explicit constraint:** "You MUST use the HTML/CSS/JS from `templates/components.html` exactly as written. Do not modify component structure. Do not add, remove, or rearrange HTML elements. Do not add custom CSS. Only populate content placeholders within the defined component structure."

**Acceptance criteria:**
- [ ] Workflow instructions are assembly-only, not generative
- [ ] Explicit "no freestyle HTML" constraint documented
- [ ] All 11 components from components.html referenced by name
- [ ] Finding card rendering hides status, moves SOURCE to technical details
- [ ] Evidence tier badge placement matches spec (citation footer, always visible)

##### 5.2 Update report.html workflow

**File:** `workflows/report.md`

The standard (non-visual) report also needs updates:

1. Score summary: Show CRITICAL/HIGH/MEDIUM/LOW counts only. Remove PASS count from the summary strip.
2. Finding rendering: Hide FINDING status from display. Lead with severity badge.
3. SOURCE: Move to a "Technical details" section if present.
4. Evidence tier: Add badge inline next to cited stats.
5. Auto-save: Report workflow no longer prompts for markdown save (already done).

**Acceptance criteria:**
- [ ] Standard report hides PASS/FAIL/PARTIAL/SKIP from rendered output
- [ ] Score strip shows severity counts only
- [ ] Evidence tier badges in citation references
- [ ] SOURCE in collapsible technical details

##### 5.3 Update standard report template

**File:** `templates/report.html.template`

Update the existing standard report template to match the new design language:

1. Apply dark chrome (#0e0e10) — remove any light mode CSS. **This is a breaking visual change** from the current light theme.
2. Apply design tokens from component library (colors, typography, spacing)
3. Update finding card HTML to match component library structure
4. Add evidence tier badge to citation sections
5. Hide status values from rendered output
6. Update score strip to show severity counts only
7. Apply font embedding from `templates/font-embed.css` for consistency
8. Update CSP to: `default-src 'none'; style-src 'unsafe-inline'; img-src data:; font-src data:;` (no script-src needed — standard report has no JS)

**Acceptance criteria:**
- [ ] Dark chrome applied consistently
- [ ] Design tokens match component library
- [ ] Finding cards structurally identical to component library version
- [ ] Evidence tier badges rendered

##### 5.4 Update skill files

**Files:**
- `skills/cro/quick-scan/SKILL.md` — Screenshot-only input pathway, auto-save, visual report opt-in
- `skills/cro/audit/SKILL.md` — Auto-save, visual report opt-in, evidence tiers in output
- `skills/cro/build/SKILL.md` — No changes expected (build uses plan, not findings display)
- `skills/cro/compare/SKILL.md` — Evidence tiers in comparison output
- `skills/cro/resume/SKILL.md` — Handle new meta.json fields, cross-mode re-audit
- `skills/cro/SKILL.md` (router) — Update capability description

**Acceptance criteria:**
- [ ] Quick-scan skill documents screenshot-only input
- [ ] All skills reference auto-save behavior
- [ ] Resume skill handles `source_mode: screenshot` and cross-mode comparison
- [ ] Router skill description updated

##### 5.5 Update plugin metadata

**File:** `.claude-plugin/plugin.json`

Bump version to 4.0.0 (major version — breaking changes to visual output format, new input mode, changed export model).

Update description to mention: evidence-backed citations with credibility tiers, annotated screenshot reports with bidirectional scroll-sync, screenshot-only input mode, component-library-enforced consistency.

**File:** `CHANGELOG.md`

Add v4.0.0 entry documenting all changes.

**Acceptance criteria:**
- [ ] Version bumped to 4.0.0
- [ ] Description updated
- [ ] CHANGELOG.md entry complete

---

## Alternative Approaches Considered

1. **Incremental patches** — Fix each UX issue independently. Rejected because the issues are interconnected: the report template, findings format, visual rendering, and export flow all need to change together. Patching one without the others creates inconsistency.

2. **React/framework-based component library** — Build report components as React components compiled to static HTML. Rejected because the plugin runs in Claude Code with no build step. Self-contained HTML with CSS/JS is the only viable approach.

3. **External CSS framework (Tailwind, etc.)** — Use a utility CSS framework for the component library. Rejected because reports must be self-contained single files. External dependencies break offline viewing.

4. **Light mode option** — Offer both dark and light mode reports. Rejected per brainstorm Decision 4 (non-negotiable). Dark chrome always. Simplifies implementation and ensures consistent brand identity.

5. **Wireframe + screenshot hybrid as default** — Show both wireframe and screenshot side by side. Rejected because it doubles the left-panel complexity and wireframes add little value when screenshots are available.

## Acceptance Criteria

### Functional Requirements

- [ ] Visual reports use annotated screenshots as primary visual (wireframe only as fallback)
- [ ] Bidirectional scroll-sync works: scrolling findings highlights markers AND scrolling markers scrolls to findings
- [ ] Evidence tier badges (Gold/Silver/Bronze) visible on every citation in visual reports
- [ ] All four status values (PASS/FAIL/PARTIAL/SKIP) hidden from visual output, only severity tier shown
- [ ] SOURCE type hidden behind "Technical details" collapsible section
- [ ] Screenshot-only input mode works: drop image + describe, get full report
- [ ] audit.md + meta.json auto-saved silently on every scan
- [ ] Visual report is opt-in (quick-scan: single yes/no; full audit: 4-option export dialogue)
- [ ] All reports structurally identical (component library enforced)
- [ ] Dark chrome always, no light mode

### Non-Functional Requirements

- [ ] Visual report HTML is self-contained (no external dependencies)
- [ ] Reports render correctly offline
- [ ] Print CSS produces readable linearized output
- [ ] CSP header prevents external resource loading
- [ ] Report file size: <750KB for a typical 5-finding quick-scan (fonts ~150KB + screenshots ~300-480KB + HTML ~20KB)
- [ ] Component library file (`templates/components.html`) is the single source of truth (~20-30KB)
- [ ] Font file (`templates/font-embed.css`) is separate (~140-200KB, never read by Claude)
- [ ] All 314 findings across 17 domain reference files have evidence_tier classification (8 operational reference files excluded — they contain protocols, not citable findings)

### Quality Gates

- [ ] At least 3 test reports generated using the new system (quick-scan, full audit, screenshot-only)
- [ ] Bidirectional scroll-sync tested in Chrome, Firefox, Safari
- [ ] Screenshot panel verified as sticky (stays fixed while scrolling findings) in all 3 browsers
- [ ] Print output tested (Ctrl+P in browser)
- [ ] Screenshot-only mode tested with both mobile and desktop screenshots
- [ ] Evidence tier badges verified against `references/evidence-tiers.md` classifications
- [ ] No freestyle HTML in any generated report (verified by diffing structure against component library)
- [ ] **v3 regression checks (NON-NEGOTIABLE):**
  - [ ] Ethics gate section present in every test report (both markdown and HTML)
  - [ ] At least 1 test page with an ethics violation — verify it renders as CRITICAL finding with Ethics/Legal badge
  - [ ] Every citation in visual report has a clickable URL that opens in new tab
  - [ ] Every citation in audit.md includes `URL:` line
  - [ ] Side-by-side audit comparison: run v4.0.0 audit on same page as a v3.1.0 audit, verify finding quality is equivalent or better (not regressed)

## Risk Analysis & Mitigation

| Risk | Impact | Likelihood | Mitigation |
|------|--------|------------|------------|
| Component library is too rigid | Claude can't handle edge cases in report content | Medium | Escape hatch components defined in Phase 1. Structure is fixed but content areas are flexible. |
| Base64 font embedding bloats file size | Reports exceed 750KB budget | Low | Font budget verified at ~150KB. Screenshots are the main variable. JPEG quality 60 at max-width 1440px keeps each screenshot at 50-70KB. |
| Scroll-sync JS breaks in some browsers | Interactive feature fails silently | Medium | 4-state state machine prevents feedback loops. `scrollend` + timeout fallback for cross-browser. CSS-only fallback: findings readable without sync. |
| Batch evidence tier classification errors | Wrong tiers or mangled findings | Medium | Git tag before starting. Batched commits (3-4 files each). Verification script after each batch. Rollback to tag if needed. |
| Batch classification takes too long | Phase 2 blocks Phase 3 | High | 314 findings across 17 files. Process in parallel batches of 3-4 files. Phase 2 runs parallel with Phase 1. |
| Screenshot-only marker positions are inaccurate | Markers point to wrong areas | Medium | Acceptable: screenshot-only is the "cheap" mode. Banner sets expectations. Anti-collision nudge prevents clustering. |
| SVG overlay contains executable content | XSS via page-derived content in SVG | Medium | Element whitelist enforced (only circle, text, g, defs, style, line). No on* attributes. Numeric-only text content. |
| CSP blocks scroll-sync or fonts | Features silently fail | **Eliminated** | CSP explicitly includes `script-src 'unsafe-inline'` and `font-src data:`. Documented with rationale. |
| Standard report dark-theme is breaking visual change | Existing users surprised by different report appearance | Low | Documented in backward compatibility section. Old reports not retroactively changed. |

## Backward Compatibility

**Existing engagements (`docs/cro/2026-03-18-*`):**
- Old audit.md files without evidence tier tags: visual report renders findings without tier badges. No error.
- Old meta.json without `screenshot_input`: field defaults to null. No error.
- Old visual reports: not regenerated. New format only applies to new reports.
- Re-audit comparison: PASS/FAIL data model still intact for delta calculation, even though visual output hides it.
- Old reference file citations with dead URLs: stat preserved with deprecation annotation (not rewritten), so existing audit.md references remain valid.

**Breaking visual change:** The standard report template (`report.html.template`) currently uses a **light theme** (`background: #f8f9fa`). Phase 5.3 changes it to dark chrome. Standard reports generated after the upgrade will look significantly different. Old standard reports are not retroactively updated.

**Schema version:** Stays at 2. All changes are additive. No breaking changes to the meta.json contract.

## Dependencies & Prerequisites

- Phase 1 must complete before Phase 3 (component library needed for visual report rebuild)
- Phase 2.1 (evidence tier classification) can run in parallel with Phase 1
- Phase 2.2 and 2.3 can run in parallel with Phase 1
- Phase 4.1 (screenshot-only mode) depends on Phase 2.2 (meta.json) but not on Phase 3
- Phase 4.2 (export model) is independent of Phases 1-3
- Phase 5 depends on all previous phases

```
Phase 1 ──────────────────┐
                          ├──→ Phase 3 ──→ Phase 5
Phase 2.1 (parallel) ────┤
Phase 2.2 (parallel) ────┤
Phase 2.3 (parallel) ────┘
                          Phase 4.1 (after 2.2) ──→ Phase 5
                          Phase 4.2 (independent) ─→ Phase 5
```

## References & Research

### Internal References
- Brainstorm: `docs/brainstorms/quick-scan-ux-overhaul-brainstorm-corrected.md`
- Current visual report template: `templates/visual-report.html.template`
- Current standard report template: `templates/report.html.template`
- Acquisition workflow: `workflows/acquire.md`
- Visual report workflow: `workflows/visual-report.md`
- Quick-scan workflow: `workflows/quick-scan.md`
- Audit workflow: `workflows/audit.md`
- Report workflow: `workflows/report.md`
- Meta.json template: `templates/meta.json.template`
- Audit.md template: `templates/audit.md.template`
- Existing engagement examples: `docs/cro/2026-03-18-*/`
- Plugin metadata: `.claude-plugin/plugin.json`
- Changelog: `CHANGELOG.md`

### External Research (from deepening)
- [Scroll-sync: IntersectionObserver scrollspy pattern](https://blog.maximeheckel.com/posts/scrollspy-demystified/)
- [Scroll-sync: Sticky positioning gotchas](https://polypane.app/blog/getting-stuck-all-the-ways-position-sticky-can-fail/)
- [SVG overlay: Responsive image overlays with viewBox](https://dev.to/damjess/responsive-svg-image-overlays-4bni)
- [SVG accessibility: ARIA roles for interactive SVG](https://www.w3.org/wiki/SVG_Accessibility/ARIA_roles_for_charts)
- [Font embedding: Web font data URIs analysis](https://www.zachleat.com/web/web-font-data-uris/) (anti-pattern for web, correct for self-contained docs)
- [Font subsetting: pyftsubset workflow](https://www.naiyerasif.com/post/2024/06/27/how-i-subset-fonts-for-my-site/)
- [Dark UI: Material Design dark theme](https://codelabs.developers.google.com/codelabs/design-material-darktheme)
- [Dark UI: Ambient light effects](https://silphiumdesign.com/guide-to-ambient-light-effects-in-web-design/)
- [Print CSS: Token reassignment over filter inversion](https://www.sitepoint.com/css-printer-friendly-pages/)
- [WCAG contrast: WebAIM contrast checker methodology](https://webaim.org/articles/contrast/)

### Reference Files (17 domain files to classify, ab-testing-patterns.md has 0 findings)
- `references/cta-design-and-placement.md`
- `references/color-psychology.md`
- `references/eye-tracking-and-scan-patterns.md`
- `references/mobile-conversion.md`
- `references/cognitive-load-management.md`
- `references/pricing-psychology.md`
- `references/trust-and-credibility.md`
- `references/social-proof-patterns.md`
- `references/checkout-optimization.md`
- `references/page-performance-psychology.md`
- `references/personalization-psychology.md`
- `references/post-purchase-psychology.md`
- `references/search-and-filter-ux.md`
- `references/biometric-and-express-checkout.md`
- `references/cookie-consent-and-compliance.md`
- `references/cross-cultural-considerations.md`
- `references/social-commerce-psychology.md`
- `references/ab-testing-patterns.md`
