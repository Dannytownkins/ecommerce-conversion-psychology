---
title: "feat: Quick-Scan UX Overhaul"
type: feat
date: 2026-03-18
brainstorm: docs/brainstorms/2026-03-18-quick-scan-ux-overhaul-brainstorm.md
deepened: 2026-03-18
---

# Quick-Scan UX Overhaul

## Enhancement Summary

**Deepened on:** 2026-03-18
**Research agents used:** Security Sentinel, Architecture Strategist, Performance Oracle, Frontend Races Reviewer, Code Simplicity Reviewer, Frontend Patterns Research, Evidence Credibility Research

### Key Improvements from Research
1. **Nonce-based CSP** replaces `unsafe-inline` — strictly superior security at zero cost
2. **Unidirectional click-to-scroll** replaces bidirectional sync — eliminates ping-pong race conditions, reduces JS from ~150 to ~40 lines
3. **Assembly manifest** added — numbered component nesting order eliminates assembly drift
4. **WCAG AAA badge colors** — original Gold #D4A017 fails contrast; replaced with dark-on-light palette
5. **Font budget reduced 60%** — Inter Latin variable WOFF2 = ~64KB (not 160KB estimate)
6. **Screenshot resize** before encoding — 40-60% file size reduction
7. **Filter toggles removed** — unnecessary for 3-15 item lists; severity sorting is sufficient
8. **`file://` compatibility** verified — no `<script type="module">`, no `fetch()`, no ES imports

### Simplification Decisions
- Bidirectional scroll-sync → unidirectional click-to-scroll (architecture + simplicity + races reviewers all agreed)
- Filter toggle bar → removed (3-15 findings don't need filtering)
- 19 components → 15 (merged sub-components into parent containers)
- Quality flags kept (user's explicit design decision, validated by GRADE framework parallels)
- Light/dark theme detection kept (user's explicit decision, improved by moving luminance calc to acquisition agent)

---

## Overview

Redesign the CRO plugin's output system — findings format, visual reports, citation credibility, screenshot-based annotation, and report consistency — so every report feels like a deliverable from a CRO consultancy, not AI-generated output. Changes apply across quick-scan, audit, build, and compare engagement types.

## Problem Statement

The current output has six UX problems:
1. **FAIL/PASS is binary and harsh** — findings need proportional severity, not a judgment stamp
2. **SOURCE labels (VISUAL/CODE/BOTH) confuse non-devs** — technical detection method shouldn't be a headline
3. **No evidence credibility signal** — users can't distinguish peer-reviewed research from one vendor's blog post
4. **Wireframes look AI-generated** — abstract block diagrams when real screenshots are already captured
5. **Reports are inconsistent across runs** — Claude has too much creative freedom in HTML generation
6. **No lightweight input mode** — users must provide a URL or file path; can't just drop a screenshot

## Technical Approach

### Architecture

**Before:** Finding format → Claude freestyle assembles HTML from a loose template → hardcoded dark-theme wireframe report

**After:** Finding format (updated) → Claude assembles HTML from a component library using an explicit assembly manifest → screenshot-annotated report with site-matched theme, SVG viewBox overlays, click-to-scroll JS, evidence tier badges

**Key architectural changes:**
- `templates/visual-report.html.template` → **deleted**, replaced by `templates/components.html` + `templates/fonts.css.fragment`
- Wireframe generation (DOM → block diagram) → screenshot annotation (SVG overlay on captured images)
- Hardcoded dark theme → luminance-detected theme (computed in acquisition agent)
- Static HTML → inline JS with `@media print` static fallback
- CSP `script-src 'none'` → **nonce-based CSP** (generate unique nonce per report)
- System fonts → base64-embedded Inter variable + JetBrains Mono (~85KB total WOFF2)
- `{{PLACEHOLDER}}` tokens → **`{slot:name}`** syntax (distinct from old format during deprecation)
- **Assembly manifest** in `workflows/visual-report.md` provides deterministic component ordering
- **`BEGIN/END` paired markers** delimit components unambiguously

### Research Insights: Security

**Citation URL sanitization (CRITICAL — implement in Phase 3):**
Citation URLs are the one place external data enters the report as an executable context. Even with entity-escaping, `javascript:` URIs in `href` attributes execute on click and bypass CSP.

```javascript
// Apply at report generation time, before URL reaches HTML
function sanitizeCitationUrl(url) {
  url = url.trim().replace(/\0/g, '');
  const parsed = new URL(url);
  if (!['http:', 'https:'].includes(parsed.protocol)) return null;
  return parsed.href;
}
```

All citation links must include `rel="noopener noreferrer" target="_blank"`.

**MIME type hardcoding:** Always use `data:image/jpeg;base64,...` — never derive MIME type from input.

### Research Insights: Performance

**Screenshot resize (implement in acquisition agent):**
Resize screenshots to display resolution (max 800px wide for the report panel) before base64 encoding. A 2880x1800 retina capture resized to 1440x900 at JPEG quality 65 reduces each screenshot from ~500KB to ~200KB. Total report size drops from 2-4MB to 0.8-2MB.

**`file://` protocol compatibility checklist:**
- No `<script type="module">` — use classic `<script>` tags (modules fail silently on `file://` in Chrome)
- No `fetch()` or `XMLHttpRequest` — CORS blocks `file://` to `file://`
- `window.location.origin` returns string `"null"` on `file://` — do not construct relative URLs
- `navigator.clipboard.writeText` may fail — use `document.execCommand('copy')` fallback
- Include `font-display: swap` on `@font-face` as safety net

### Research Insights: SVG Overlays

**Use SVG `viewBox` for responsive marker positioning:**
```html
<div style="position: relative;">
  <img src="data:image/jpeg;base64,..." style="width: 100%; display: block;" />
  <svg viewBox="0 0 1440 900" preserveAspectRatio="xMinYMin meet"
       style="position: absolute; top: 0; left: 0; width: 100%; height: 100%;
              pointer-events: none;">
    <circle cx="720" cy="250" r="16" fill="#ef4444" pointer-events="auto"
            data-finding="1" style="cursor: pointer;" />
    <text x="720" y="250" text-anchor="middle" dy="0.35em"
          fill="white" font-size="12" font-weight="600">1</text>
  </svg>
</div>
```

- `viewBox` dimensions match the screenshot pixel dimensions
- Marker coordinates are absolute within the viewBox (auto-scale with container)
- `pointer-events: none` on SVG overlay, `pointer-events: auto` on interactive markers only
- Default x to section center; y from `(finding_scrollY - screenshot_scrollY) / screenshot_height * viewBox_height`

### Research Insights: JavaScript Architecture

**Unidirectional click-to-scroll (~40 lines):**
```javascript
// Click finding card → scroll screenshot panel to corresponding screenshot
document.querySelectorAll('.finding-card').forEach(card => {
  card.addEventListener('click', () => {
    const screenshotId = card.dataset.screenshot;
    const target = document.getElementById(screenshotId);
    if (target) target.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    highlightMarker(card.dataset.findingId);
  });
});

// Click SVG marker → scroll findings panel to corresponding finding card
document.querySelectorAll('.callout-marker').forEach(marker => {
  marker.addEventListener('click', () => {
    const findingId = marker.dataset.finding;
    const card = document.querySelector(`.finding-card[data-finding-id="${findingId}"]`);
    if (card) card.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    highlightMarker(findingId);
  });
});

// Marker highlight — only toggle when active marker changes
let currentActiveMarker = null;
function highlightMarker(markerId) {
  if (currentActiveMarker === markerId) return;
  if (currentActiveMarker) {
    const prev = document.querySelector(`.callout-marker[data-finding="${currentActiveMarker}"]`);
    if (prev) prev.classList.remove('marker-active');
  }
  const next = document.querySelector(`.callout-marker[data-finding="${markerId}"]`);
  if (next) next.classList.add('marker-active');
  currentActiveMarker = markerId;
}
```

**Image decode wait (required before any position calculations):**
```javascript
async function initReport() {
  const images = [...document.querySelectorAll('.screenshot-panel img')];
  await Promise.allSettled(images.map(img => img.decode()));
  // Now safe to compute positions, attach click handlers
  attachClickHandlers();
}
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', initReport);
} else { initReport(); }
```

**CSS transitions for markers (not keyframe animations):**
```css
.callout-marker { opacity: 0.7; transform: scale(1); transition: opacity 150ms ease-out, transform 150ms ease-out; }
.callout-marker.marker-active { opacity: 1; transform: scale(1.25); }
```

### Implementation Phases

---

#### Phase 1: Evidence Tier System

**Goal:** Classify all citations and create the infrastructure for evidence badges.

**New files:**

**`references/evidence-tiers.md`** — Classification criteria document
- Gold tier sources: Baymard Institute, NNGroup, peer-reviewed journals (PMC/NIH, SAGE, Oxford JCR, Springer, ScienceDirect, ACM CHI), Spiegel Research Center, Laws of UX, Google CrUX
- Silver tier sources: CXL, Stripe, W3C, Shopify enterprise blog, Forrester/McKinsey/Gartner, Google Developers blog
- Bronze tier sources: VWO Blog, Campaign Monitor, HubSpot, Neil Patel, GrowthSuite, Yieldify, TargetBay, any "(2026)" blog repackaging older stats
- Do Not Cite: dead URLs with no alternative source — drop specific stat, keep recommendation if principle is supported elsewhere
- Rules: tier locked to publisher, never upgraded/downgraded per citation
- Quality flag rules: optional per-citation annotation when evidence quality diverges from tier norm

**Modified files (additive only — add `evidence_tier` + optional `quality_flag` to each finding):**

All 26 reference files in `references/`. Per-finding change:

```
- **Source**: Spiegel Research Center, Northwestern University, 2017
- **Evidence Tier**: Gold
- **Key Finding**: Products with reviews convert 270% better than those without
```

With quality flag (when needed):
```
- **Source**: VWO, 2019
- **Evidence Tier**: Bronze
- **Quality Flag**: methodology note: N=50,000 across 12 sites
- **Key Finding**: Simplified checkout increased conversions by 232%
```

**Success criteria:**
- [ ] `references/evidence-tiers.md` created with complete classification rules
- [ ] All ~200+ citations across 26 reference files have `evidence_tier` field
- [ ] Quality flags added where citation quality diverges from tier norm
- [ ] Dead-URL citations identified and handled per Do Not Cite rules
- [ ] No existing finding text, stats, or source attributions modified

**Effort:** High (batch classification across 26 files)

---

#### Phase 2: Finding Format Updates

**Goal:** Update the structured finding format. Remove PASS/FAIL from visual rendering (keep in data model). Collapse SOURCE into technical details. Add evidence tier to citation output.

**Modified files:**

**`workflows/audit.md`**
- Lines 113-124: Update finding format template
  - `FINDING: [PASS|FAIL|PARTIAL]` → keep in structured output (backward compat)
  - Add `EVIDENCE_TIER: [Gold|Silver|Bronze]` field after citation line
  - Add optional `QUALITY_FLAG: [text]` field
- Lines 88-107: SOURCE definitions remain but add note: "SOURCE is not rendered in visual reports — collapsed into Technical Details"

**`workflows/quick-scan.md`**
- Lines 74-89: Add `EVIDENCE_TIER` and optional `QUALITY_FLAG`
- Lines 144-158: Update conversation output — lead with severity, no PASS/FAIL stamp
- Lines 162-174: Update output prompt (see Phase 6)

**`templates/audit.md.template`**
- Lines 14-24: Add `EVIDENCE_TIER` and `QUALITY_FLAG` fields

**Success criteria:**
- [ ] Finding format includes `EVIDENCE_TIER` and optional `QUALITY_FLAG`
- [ ] Conversation output leads with severity, no PASS/FAIL stamp
- [ ] SOURCE retained in data but marked as "not rendered in visual reports"
- [ ] Progress comparison unaffected (PASS/FAIL still in data)
- [ ] All 3 workflow files + 1 template updated consistently

**Effort:** Medium

---

#### Phase 3: Component Library + Interaction Script

**Goal:** Create a component library and interaction script for deterministic report assembly.

**New files:**

**`templates/components.html`** — All report components with `<!-- BEGIN:name -->` / `<!-- END:name -->` paired markers and `{slot:name}` data placeholders.

Components (15 total — merged from original 19):

1. **report-shell** — `<!DOCTYPE html>`, `<head>` with nonce-based CSP, CSS custom properties for light/dark themes, `{slot:nonce}` for CSP nonce, `{slot:font-css}` insertion point
2. **report-header** — engagement ID, page URL, device badge, date, viewport, platform
3. **score-summary-strip** — total findings, critical count, high count, quick wins count
4. **split-panel-layout** — left (scrollable screenshot stack with `scroll-snap-type: y mandatory`) + right (scrollable findings list), CSS grid
5. **screenshot-panel** — `<img>` with SVG overlay container (`viewBox` matching image dimensions), section label, `scroll-snap-align: start`
6. **svg-callout-marker** — numbered circle, severity-colored, `pointer-events: auto`, `data-finding` attribute
7. **wireframe-fallback-section** — simplified block diagram for obscured screenshots
8. **finding-card** — severity badge, finding number, title, observation, recommendation, quick-win badge, `data-finding-id` and `data-screenshot` attributes. Contains nested: citation line with evidence tier badge + optional quality flag, "Why this matters" `<details>`, "Technical details" `<details>` (SOURCE, SECTION, EFFORT)
9. **evidence-tier-badge** — Gold/Silver/Bronze badge with WCAG AAA colors
10. **screenshot-only-banner** — "Based on screenshot only — DOM and interaction patterns not assessed."
11. **all-obscured-banner** — "All screenshots were obscured — wireframe rendering used. Dismiss popups and re-scan for a screenshot-based report."
12. **print-layout-overrides** — `@media print` rules: linearize panels, `overflow: visible`, white background, `print-color-adjust: exact`, `break-inside: avoid`, show all findings
13. **interaction-script** — inline `<script>` (~40 lines): click-to-scroll between panels, marker highlighting with CSS transitions, `img.decode()` init guard. **Copy verbatim — do not modify.**
14. **report-footer** — generation date, plugin version, engagement ID
15. **csp-comment** — `<!-- Security: nonce-based CSP. Do not serve this file from a public URL. -->`

**`templates/fonts.css.fragment`** — Base64-embedded WOFF2 font data (separate from components.html to keep it parseable):
- Inter Latin variable (400-700 weights): ~48KB WOFF2, ~64KB base64
- JetBrains Mono Latin (400/700): ~15KB WOFF2, ~20KB base64
- Total: ~85KB base64 (down from 160KB estimate)
- Both with `font-display: swap` and `unicode-range: U+0000-00FF, U+0131, U+0152-0153, U+02BB-02BC`
- Generate subsets with `pyftsubset` targeting Latin glyphs only, WOFF2 output format

**Evidence tier badge colors (WCAG AAA compliant):**
```css
/* Dark-text-on-light-background — passes both light and dark report themes */
.badge--gold   { background: #F5E6D3; color: #8B5E00; border-left: 3px solid #8B5E00; } /* 7.4:1 contrast */
.badge--silver { background: #E2E8F0; color: #475569; border-left: 3px solid #475569; } /* 8.2:1 contrast */
.badge--bronze { background: #F4E4D8; color: #744210; border-left: 3px solid #744210; } /* 7.9:1 contrast */
```

**Theme system (CSS custom properties):**

Light theme (site luminance > 0.5):
```css
--bg: #ffffff; --surface: #f8f9fa; --border: #e2e4e7; --text: #1a1a2e; --text-muted: #6b7280;
```

Dark theme (site luminance <= 0.5, or fallback):
```css
--bg: #0e0e10; --surface: #18181b; --border: #2a2a2e; --text: #e4e4e7; --text-muted: #a1a1aa;
```

Severity colors (same in both themes):
```css
--critical: #ef4444; --high: #f59e0b; --medium: #3b82f6; --low: #6b7280;
```

**Luminance detection:** Computed by the acquisition agent (not the report assembler). The acquisition agent already extracts `bg` color — add a computed `luminance: 0.73` field to style metadata output. Report workflow does a simple comparison: `if luminance > 0.5, add class 'theme-light'; else 'theme-dark'`.

**Assembly manifest (add to `workflows/visual-report.md`):**
```
ASSEMBLY ORDER (always this sequence):
1. report-shell (outer wrapper — contains <head>, opens <body>)
2.   report-header
3.   score-summary-strip
4.   [screenshot-only-banner or all-obscured-banner if applicable]
5.   split-panel-layout (opens left/right grid)
6.     LEFT: for each screenshot section:
7.       screenshot-panel (with SVG overlay container)
8.       for each finding mapped to this section:
9.         svg-callout-marker (inside the SVG overlay)
10.    RIGHT:
11.      for each finding (ordered by page position top-to-bottom):
12.        finding-card (contains evidence-tier-badge, citation, collapsibles)
13.  print-layout-overrides
14.  interaction-script (COPY VERBATIM — do not modify)
15.  report-footer
16. close report-shell

POST-ASSEMBLY VALIDATION:
- [ ] No {slot:*} markers remain in the output
- [ ] No <!-- BEGIN: or <!-- END: markers remain
- [ ] Finding card count matches SVG marker count
- [ ] Every finding card has data-finding-id and data-screenshot attributes
- [ ] The interaction-script is present and unmodified
- [ ] CSP meta tag is present with a unique nonce
- [ ] All citation URLs are http: or https: only
```

**JS-to-DOM contract (data attributes, not class names):**
The interaction script targets elements via: `[data-finding-id]`, `[data-screenshot]`, `.callout-marker[data-finding]`. These are the stable interface. Class names can change without breaking interactivity.

**Citation URL sanitization:** Apply `sanitizeCitationUrl()` at report generation time. Reject any URL that is not `http:` or `https:`. Failed URLs render as plain text (not clickable).

**Success criteria:**
- [ ] `templates/components.html` contains all 15 components with `BEGIN/END` markers
- [ ] `templates/fonts.css.fragment` contains base64 WOFF2 Inter + JetBrains Mono (~85KB)
- [ ] Each component uses `{slot:name}` for data placeholders
- [ ] Light and dark theme variants defined via CSS custom properties
- [ ] Nonce-based CSP in report shell
- [ ] Click-to-scroll JS (~40 lines) handles: finding→screenshot, marker→finding, marker highlight
- [ ] `img.decode()` await before click handlers are attached
- [ ] `@media print` linearizes layout, sets `overflow: visible`, preserves badge colors
- [ ] No component requires external resources
- [ ] Evidence tier badges pass WCAG AAA contrast (7:1+)
- [ ] Assembly manifest added to `workflows/visual-report.md`
- [ ] Post-assembly validation checklist added to workflow

**Effort:** High (this is the design-heavy phase)

---

#### Phase 4: Screenshot Annotation System

**Goal:** Replace wireframe-first rendering with screenshot-first rendering using SVG overlays.

**Modified files:**

**`workflows/visual-report.md`** — Major rewrite:

**New Step 1 (Build Screenshot Panels):**
- For each section screenshot from acquisition:
  - Resize to display resolution (max 800px wide) at JPEG quality 65 before base64 encoding
  - Evaluate obscuration: if overlay elements cover >30% of viewport area, flag as obscured
  - Clean screenshots: render using `screenshot-panel` component with SVG overlay
  - Obscured screenshots: fall back to `wireframe-fallback-section` component
- Stack all panels vertically in the left panel div with `scroll-snap-align: start`
- Add section labels above each screenshot

**New Step 2 (Place SVG Markers + Build Finding Cards):**
- For each finding:
  - Map finding's SECTION slug to the relevant screenshot (via scrollY ranges in acquisition metadata)
  - Calculate marker position within the screenshot's SVG viewBox:
    ```
    marker_y = (finding_scrollY - screenshot_scrollY) / screenshot_height * viewBox_height
    marker_x = viewBox_width / 2  (centered — do not estimate horizontal position)
    ```
  - Add `svg-callout-marker` component to the screenshot's SVG overlay
  - Build `finding-card` component, numbered to match marker
  - Set `data-finding-id` and `data-screenshot` attributes on the finding card

**New Step 3 (Theme Selection):**
- Read `luminance` field from acquisition style metadata (computed by acquisition agent)
- If luminance > 0.5: add class `theme-light` to report shell
- If luminance <= 0.5 or absent: add class `theme-dark`

**Step 4 (Assemble Report):**
- Read `templates/components.html` and `templates/fonts.css.fragment`
- Follow the assembly manifest exactly
- Fill `{slot:*}` placeholders with engagement data
- Generate a unique nonce (16 random hex chars) for the CSP
- Inject font CSS fragment into the report shell's `{slot:font-css}` point
- Sanitize all citation URLs (http/https only)
- Run post-assembly validation checklist
- Write self-contained HTML file

**Screenshot-only mode (when `source_mode: "screenshot"`):**
- No acquisition metadata — skip SVG marker overlay entirely
- Screenshots rendered without callout markers
- Findings reference sections by name only
- Prepend `screenshot-only-banner` component
- All findings are SOURCE: VISUAL
- Dark theme fallback (no luminance data)

**Also modify `workflows/acquire.md`:**
- Add luminance computation to style metadata output:
  ```
  Extract bg color → compute L = 0.2126*R + 0.7152*G + 0.0722*B (normalized 0-1)
  Add to style metadata: luminance: [value]
  ```

**Success criteria:**
- [ ] URL-mode reports use annotated screenshots with SVG viewBox markers
- [ ] Wireframe renders only for obscured sections (>30% overlay)
- [ ] All-obscured edge case shows wireframe + warning banner
- [ ] Screenshot-only mode renders screenshots without markers + banner
- [ ] Marker numbers match finding card numbers
- [ ] Theme auto-detected from acquisition luminance; dark fallback when unavailable
- [ ] Screenshots resized to display resolution before encoding
- [ ] Acquisition agent outputs `luminance` field in style metadata

**Effort:** High

---

#### Phase 5: Screenshot-Only Input Mode

**Goal:** Allow users to drop screenshots + describe the page without URL scanning.

**Modified files:**

**`skills/cro/quick-scan/SKILL.md`**
- Add screenshot-only input detection: if user provides image(s) + description
- Accept up to 6 screenshots, each with a brief label
- Set `source_mode: "screenshot"` in meta.json
- Skip acquisition agent entirely
- Pass screenshots directly to quick-scan auditors
- All findings are SOURCE: VISUAL by definition

**`templates/meta.json.template`**
- Add `"screenshot"` as a valid `source_mode` value

**`skills/cro/SKILL.md`** (router)
- Update input description to mention screenshot-only mode

**Success criteria:**
- [ ] User can invoke `/cro:quick-scan` with screenshot(s) + description
- [ ] Up to 6 screenshots accepted, each with a label
- [ ] No acquisition agent spawned
- [ ] `meta.json` records `source_mode: "screenshot"`
- [ ] Findings output uses same format as URL-mode (minus CODE-source findings)
- [ ] Visual report renders screenshots without SVG markers + banner

**Effort:** Medium

---

#### Phase 6: Export Model Update

**Goal:** Simplify the output prompt. Markdown always auto-saves. Visual report is opt-in.

**Modified files:**

**`workflows/quick-scan.md`**
- Lines 162-174: New prompt: "Want an annotated visual report too?" → Yes / No
- `--visual`: skip prompt, auto-generate
- `--no-visual`: skip prompt, no report

**`workflows/audit.md`** — Apply same simplification

**Success criteria:**
- [ ] `audit.md` + `meta.json` always auto-saved silently
- [ ] Export prompt simplified to single yes/no
- [ ] `--visual` and `--no-visual` flags still work
- [ ] No behavioral change for `--auto` mode

**Effort:** Low

---

#### Phase 7: Template Cleanup + Standard Report Update

**Goal:** Update the standard report template and remove the old visual report template.

**Modified files:**

**`templates/report.html.template`**
- Update badge CSS — remove `.badge-fail`/`.badge-pass` visual prominence
- Add evidence tier badge styles (WCAG AAA colors)
- Update finding list to severity-led format
- Keep light theme

**`templates/visual-report.html.template`**
- **Delete entirely** (git history preserves it). A deprecated file that still exists will be read by Claude if the old workflow path is accidentally triggered.

**`skills/cro/quick-scan/SKILL.md`**
- Update any references to old template path (line ~188)

**Success criteria:**
- [ ] `report.html.template` shows evidence tier badges with WCAG AAA colors
- [ ] `report.html.template` leads with severity, no PASS/FAIL visual emphasis
- [ ] `visual-report.html.template` deleted
- [ ] All references to old template path updated

**Effort:** Medium

---

#### Phase 8: Version Bump + Integration Testing

**Goal:** Bump plugin version, verify all engagement types work end-to-end.

**Modified files:**

**`.claude-plugin/plugin.json`**
- `"version": "3.1.0"` → `"version": "3.2.0"`

**Test matrix (16 scenarios):**

| # | Test | Input | Expected |
|---|------|-------|----------|
| 1 | Quick-scan URL desktop | URL + `--device desktop` | Annotated screenshot report, severity-led findings, evidence badges |
| 2 | Quick-scan URL mobile | URL + `--device mobile` | Same, mobile viewport |
| 3 | Quick-scan URL both | URL + `--device both` | Two separate reports |
| 4 | Quick-scan screenshot-only | 1 screenshot + description | Report without markers, limitations banner, dark theme |
| 5 | Quick-scan screenshot-only multi | 3 screenshots + labels | Stacked screenshots, no markers, banner |
| 6 | Quick-scan `--visual` | URL + `--visual` | Auto-generates report, no prompt |
| 7 | Quick-scan `--no-visual` | URL + `--no-visual` | Markdown only, no prompt |
| 8 | Full audit | URL | Full relay, visual report at end |
| 9 | Re-audit | Same URL as previous | Progress comparison works (PASS/FAIL in data) |
| 10 | Obscured screenshots | URL with cookie banner | Wireframe fallback for obscured sections |
| 11 | All screenshots obscured | URL with full-page modal | All-wireframe + warning banner |
| 12 | Light-theme site | URL with white background | Light-theme report |
| 13 | Dark-theme site | URL with dark background | Dark-theme report |
| 14 | Print | Open report → Ctrl+P | Linearized layout, badges retain color, overflow: visible |
| 15 | Evidence tier rendering | Finding with Gold citation | Gold badge inline, WCAG AAA contrast |
| 16 | Quality flag | Bronze citation with flag | Bronze badge + italic flag text |

**Success criteria:**
- [ ] All 16 test scenarios pass
- [ ] Plugin version bumped to 3.2.0
- [ ] CHANGELOG.md updated

**Effort:** Medium

---

## Acceptance Criteria

### Functional Requirements

- [ ] Findings lead with severity tier, no PASS/FAIL stamp in visual output
- [ ] SOURCE labels collapsed into "Technical details" expander
- [ ] Every citation has an inline evidence tier badge (Gold/Silver/Bronze)
- [ ] Quality flags render when present on citations
- [ ] Visual reports use annotated screenshots (SVG viewBox overlay) as primary visual
- [ ] Wireframe renders only as fallback for obscured sections
- [ ] Report theme auto-matches site's light/dark mode (luminance from acquisition agent)
- [ ] Click-to-scroll works: finding→screenshot, marker→finding (unidirectional)
- [ ] Screenshot-only input mode works with up to 6 labeled screenshots
- [ ] Markdown always auto-saves silently
- [ ] Export prompt simplified to yes/no for visual report
- [ ] Reports are self-contained single HTML files (no external dependencies)
- [ ] Print layout is clean, linearized, with `overflow: visible`

### Non-Functional Requirements

- [ ] Every report is structurally identical (assembly manifest + component library)
- [ ] Report file size ~0.8-2MB with screenshots (resize to display resolution), ~100KB without
- [ ] Reports open correctly offline and on `file://` protocol
- [ ] Nonce-based CSP (not `unsafe-inline`)
- [ ] Base64 Inter + JetBrains Mono WOFF2 (~85KB font budget)
- [ ] Citation URLs sanitized (http/https only; rejects javascript:/data:)
- [ ] No breaking changes to engagement data model (PASS/FAIL retained in audit.md)
- [ ] Evidence tier badges pass WCAG AAA contrast (7:1+)
- [ ] No `<script type="module">`, no `fetch()`, no ES imports (file:// compat)

### Quality Gates

- [ ] All 16 integration test scenarios pass
- [ ] Component library contains all 15 components with BEGIN/END markers
- [ ] All ~200+ citations classified with evidence tiers
- [ ] Post-assembly validation checklist passes on generated reports
- [ ] CHANGELOG.md updated for v3.2.0

## Dependencies & Prerequisites

```
Phase 1 (evidence tiers) ──→ Phase 2 (finding format)
                                    ↓
Phase 3 (component library) ───────→ Phase 4 (screenshot annotation) ──→ Phase 5 (screenshot-only)
                                    ↓
Phase 6 (export model — parallel) ──┘
Phase 7 (template cleanup — after Phase 3)
Phase 8 (testing — after all)
```

## Risk Analysis & Mitigation

| Risk | Impact | Mitigation |
|------|--------|------------|
| Evidence classification errors | Wrong tier badge undermines credibility | Batch-classify before launching; unclassified defaults to Bronze |
| Assembly drift over time | Reports become inconsistent as model updates | Assembly manifest is version-pinned; post-assembly validation catches drift |
| Citation URL injection (`javascript:` URIs) | XSS via malicious citation URL | Allowlist http/https only; reject all other schemes |
| Component library too rigid | Can't handle unexpected page types | Include wireframe-fallback-section; generic section variant |
| Click-to-scroll JS breaks in browsers | Interactive features fail | Graceful degradation — numbered markers still provide visual link without JS |
| Screenshot-only annotation quality | No markers = less useful report | Acceptable trade-off for cheapest input mode |
| Image decode timing | Position calculations wrong on initial load | `Promise.allSettled(img.decode())` before attaching click handlers |
| `file://` protocol restrictions | Features silently fail | No modules, no fetch, no clipboard API without fallback |

## References & Research

### Internal References
- Brainstorm: `docs/brainstorms/2026-03-18-quick-scan-ux-overhaul-brainstorm.md`
- Finding format: `workflows/audit.md:113-124`
- Quick-scan format: `workflows/quick-scan.md:74-89`
- Visual report workflow: `workflows/visual-report.md` (full file)
- Visual report template: `templates/visual-report.html.template` (to be deleted)
- Standard report template: `templates/report.html.template`
- Audit template: `templates/audit.md.template:14-24`
- Meta.json template: `templates/meta.json.template:15`
- Plugin metadata: `.claude-plugin/plugin.json:3`
- Citation sources: `citations/sources.md`
- SOURCE definitions: `workflows/audit.md:88-107`
- Output prompt: `workflows/quick-scan.md:162-174`
- Acquisition agent: `workflows/acquire.md:140-148` (style metadata extraction)

### External Research (from deepening agents)
- GRADE framework (evidence quality classification in medical research) — validates 3-tier publisher-based approach
- WCAG 2.2 SC 1.4.3 / 1.4.11 — contrast minimums for badge text and UI components
- SVG `viewBox` + `preserveAspectRatio` — responsive overlay positioning
- `img.decode()` API — prevents layout calculation race conditions
- `pyftsubset` (fonttools) — font subsetting tool for WOFF2 generation
- IntersectionObserver API — used for visibility detection (not scroll-sync in final design)
- CSP nonce-based script allowlisting — strictly superior to `unsafe-inline`
