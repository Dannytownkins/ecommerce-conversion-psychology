---
name: visual-report-generation
---

# Visual Report Generation — Component Assembly

The coordinator produces an annotated visual report by assembling pre-defined HTML components. This is NOT a subagent workflow — the coordinator reads these instructions and generates the report inline.

**CONSTRAINT: You MUST use the HTML/CSS/JS from templates/components.html exactly as written. Do not modify component structure. Do not add, remove, or rearrange HTML elements. Do not add custom CSS. Only populate content placeholders within the defined component structure.**

## Input (already available to coordinator)

1. **Component definitions** — `templates/components.html`
2. **Font stylesheet** — `templates/font-embed.css`
3. **Baton: meta.json** — engagement ID, date, URL, page type, platform, clusters, device, viewport, source_mode, version
4. **Baton: audit.md** (or **audit-mobile.md**) — findings with SOURCE, SECTION, PRIORITY, STATUS, OBSERVATION, RECOMMENDATION, WHY_THIS_MATTERS, EVIDENCE_TIER, CITATION_URL, rationale
5. **Baton: screenshots** — viewport captures (paths or base64)
6. **Baton: acquisition metadata** — section boundaries, element coordinates, naturalWidth/naturalHeight of screenshots

## Step 1: Read Component Definitions

Read `templates/components.html` for all HTML components used in the report. All subsequent steps reference components defined there.

**Performance tip:** `components.html` is ~1115 lines (~162K tokens). If you only need specific components (e.g., finding cards for a partial update), consult `templates/components-digest.md` for a line-range index so you can read only the sections you need using `offset` and `limit` parameters.

## Step 2: Inject Font Stylesheet

Copy the contents of `templates/font-embed.css` into the `<head>` of the report **verbatim**. Do not read, interpret, parse, or modify the CSS. Paste it exactly as-is inside a `<style>` tag.

## Step 3: Read Baton Files

Load the following from the engagement directory (`docs/cro/{engagement-id}/`):

- `meta.json` — parse all fields
- `audit.md` (or `audit-mobile.md`) — parse all findings
- `baton.json` — parse acquisition metadata: screenshots (paths, base64_paths, naturalWidth, naturalHeight), sections (boundaries, clusters, occlusion), styles, dom_mode. **If baton.json does not exist or `status` != `"COMPLETE"`, warn:** "Acquisition baton missing or incomplete — screenshot positions may be inaccurate."
- Screenshot `.jpg` files — base64-encoded at render time for embedding

## Step 4: Assemble Header

Populate the header component from `components.html` using `meta.json` fields:

1. **Eyebrow text:** `"Strategic Intelligence Report"`
2. **Title:** Generate a concise audit title. Wrap key CRO-relevant terms in `<span class="amber">` or `<span class="amber-light">` for visual accent. Example: `<span>CRO</span> <span class="amber">CTA</span> <span class="amber-light">Audit</span>`
3. **Subtitle:** 1-2 sentence summary of what the audit covers and the target page.

## Step 5: Assemble Metadata Grid

Populate the metadata grid with 6 items using `meta.json` fields:

| Label | Value |
|-------|-------|
| Page Type | `{{page_type}}` |
| Platform | `{{platform}}` |
| Device | `{{device}}` (`{{viewport}}`) |
| Source Mode | `{{source_mode}}` |
| Audit Date | `{{date}}` formatted as `Mon DD, YYYY` |
| Engagement ID | `{{engagement_id}}` — wrap in `<span class="highlight">` |

## Step 6: Assemble Evidence Canvas

### 6a. Screenshot carousel

Build a screenshot carousel from the engagement's JPEG files:

- **Base64-encode each screenshot** at render time: `base64 < {path}.jpg`. Embed as data URIs: `src="data:image/jpeg;base64,{encoded}"`. **VERIFY:** every `<img>` src starts with `data:image/` — never a relative file path. If a JPEG file is missing, skip that screenshot.
- **First screenshot** is the main image (`#mainImage`). All screenshots populate the thumbnail strip.
- **Build the `slideSources` JSON array** for the carousel controller — one base64 data URI per slide.
- **Thumbnail grid:** `repeat(N, 1fr)` where N = number of screenshots (max 4 columns). First thumbnail gets `class="thumb active"`.

### 6b. Callout markers

Position numbered markers on the screenshot for each finding:

- **URL mode (source_mode is url-based):** Use element coordinates from `baton.json`. Match the finding's `ELEMENT` field to entries in the baton's `elements` array. Calculate position as percentage of screenshot dimensions: `left = (x + width/2) / naturalWidth * 100`, `top = (y + height/2) / naturalHeight * 100`. If no element match, fall back to section-level centering. Subtract screenshot `scrollY` from element `y` for the correct position within that screenshot.
- **Screenshot-only mode:** Claude estimates element positions based on visual inspection.
- **Assign `data-slide`** attribute to each marker indicating which screenshot it appears on (0-indexed). Markers are only visible when their slide is active.
- **Assign `data-severity`** attribute for severity-specific marker styling: `critical` markers are larger (3.5rem) than others (3rem).
- **DPR adjustment:** For mobile screenshots at DPR > 1, element coordinates in the baton are already in screenshot pixels. If they are still in CSS pixels, multiply by the DPR before positioning.

### 6c. Metrics bar

Populate the two metric cards below the thumbnail strip:

- **Metric 1 — Intent Reliability:** Percentage based on ratio of findings with strong evidence tiers (Gold/Silver) to total findings. Round to 1 decimal.
- **Metric 2 — Projected Lift:** Estimated conversion improvement if all recommendations are implemented. Derive from severity weights: CRITICAL=5%, HIGH=3%, MEDIUM=1.5%, LOW=0.5% per finding (cap at 35%). Format as `+XX.X%` with `class="green"`.

## Step 7: Assemble Finding Cards

**Filter:** Only render FAIL and PARTIAL findings as full finding cards. PASS findings from the "What's Working Well" section are rendered separately (see Step 7b). Do NOT render PASS findings as severity-badged finding cards — they are not problems.

For each FAIL/PARTIAL finding in the audit, assemble a finding-card component from `components.html`:

1. **Select severity CSS class** based on the finding's PRIORITY field (critical, high, medium, low).

2. **Hide STATUS from rendered output.** The finding's STATUS (PASS, FAIL, PARTIAL, SKIP) is used only for internal filtering. It MUST NOT appear anywhere in the rendered HTML.

3. **Populate the card:**
   - Sequential finding number (01, 02, 03...)
   - Finding title derived from SECTION slug (e.g., `primary-cta` becomes "Primary CTA")
   - Severity badge with the appropriate CSS class and label (e.g., "Critical Impact", "High Priority", "Medium Priority", "Low Priority")
   - Source type label in the top-right corner (e.g., "Internal Behavioral Analysis", "Heuristic Review", "Interaction Flow Audit")
   - OBSERVATION text
   - RECOMMENDATION text inside the recommendation box, with severity-colored lightbulb icon
   - WHY_THIS_MATTERS text prefixed with "Why this matters: " in the why-matters section

4. **Render citation footer with evidence tier badge (MANDATORY).** For each finding:
   - Render the reference file and finding number as the `ref-id` text (e.g., `cta-design-and-placement.md, Finding 14`)
   - Render the evidence tier badge inline next to the ref — use `tier-badge--gold`, `tier-badge--silver`, or `tier-badge--bronze` class
   - **Resolve and render clickable citation URL as the "View Source" link.** Extract the reference filename and finding number from the auditor's citation line. Look up the URL in `citations/sources.md` from the plugin directory. Render as an `<a>` tag with `rel="noopener noreferrer" target="_blank"`. If no URL match found, render as plain text "(source unavailable)".
   - **A finding card without a citation footer is incomplete.**

## Step 7b: What's Working Well Section

If the audit contains a "What's Working Well" section with PASS findings, render them as a compact list between the finding cards and the summary section. Use a simple styled container — not full finding cards:

```html
<div style="margin: 2rem 0; padding: 1.5rem; background: var(--panel); border: 1px solid var(--border); border-radius: 12px;">
  <h3 style="color: var(--text); font-size: 1.1rem; margin: 0 0 1rem 0; font-family: var(--font-display);">What's Working Well</h3>
  <ul style="list-style: none; padding: 0; margin: 0;">
    <!-- For each PASS finding: -->
    <li style="padding: 0.5rem 0; border-bottom: 1px solid var(--border); color: var(--text-muted); font-size: 0.9rem;">
      <span style="color: #22c55e; margin-right: 0.5rem;">✓</span>
      <strong style="color: var(--text);">{{slug}}</strong> — {{one-line observation}}
    </li>
  </ul>
</div>
```

This section is intentionally compact. It acknowledges good practices without the visual weight of a finding card.

## Step 8: Limitations Banner

If `source_mode` is `screenshot` (file-based input without live URL access), assemble the limitations-banner component and insert it before the first finding card.

## Step 9: Summary Section

Assemble the three summary cards:

### Card 1: Evidence Confidence
Based on source mode:
- `URL + DOM`: "HIGH" (amber)
- `Screenshot + DOM`: "MODERATE-HIGH" (amber)
- `Screenshot only`: "MODERATE" (amber)
- Note: brief description of source mode

### Card 2: Severity Distribution
Horizontal bar chart with one bar per severity level that has findings > 0. Fill width proportional to count relative to highest count (highest = 100%). Use severity-specific colors.

### Card 3: Ethics Check (MANDATORY — never omit)
- **If no ethics violations:** Render the PASS state card — green "PASS" value, "No dark patterns detected" note, green checkmark icon circle.
- **If ethics violations found:** Render the FAIL state card — critical-red "FAIL" value, X icon circle, and a list of violations using `ethics-violation-item` components. Each violation renders as a red-backgrounded line item with a ✗ prefix. This card expands vertically to accommodate all violations. Checked categories: urgency/scarcity signals, pricing transparency, review authenticity, choice architecture, subscription patterns.

## Step 10: Inject JavaScript

Copy the carousel controller + scroll-sync JavaScript block from `components.html` and inject it at the bottom of the report `<body>`. Replace `{{SLIDE_SOURCES_JSON}}` with the actual JSON array of base64 data URIs.

## Step 11: Output

Write the fully assembled, self-contained HTML file:

- **Single-device audits:** `docs/cro/{engagement-id}/visual-report.html`
- **Both-mode audits:** `docs/cro/{engagement-id}/visual-report-desktop.html` and `docs/cro/{engagement-id}/visual-report-mobile.html`

## Security

- **HTML-escape** ALL text content before insertion (finding text, recommendations, URLs, product names, prices)
- **CSP meta tag** — verify it is present in the component definitions and included in output
- **No external resources** — everything is inline CSS, inline JS, or base64 images
- **Escape `{{` patterns** found in user content to prevent template placeholder collision

## Quality Check

Before writing the file, verify:

- [ ] Every finding has a corresponding finding card with correct severity class
- [ ] No STATUS values (PASS/FAIL/PARTIAL/SKIP) appear in rendered output
- [ ] Evidence tier badge is visible in every finding card footer
- [ ] Citation URLs are clickable with `rel="noopener noreferrer" target="_blank"` (or "(source unavailable)" if unresolved)
- [ ] Reference ID text is present in every finding footer
- [ ] **All screenshot `<img>` src attributes start with `data:image/`** — no relative file paths or external URLs
- [ ] Screenshot carousel has correct number of thumbnails
- [ ] Markers have `data-slide` and `data-severity` attributes
- [ ] Summary section has exactly 3 cards: Evidence Confidence, Severity Distribution, Ethics Check
- [ ] Ethics card renders correct state (PASS or FAIL with violation list)
- [ ] Limitations banner is present when source_mode is screenshot
- [ ] Carousel controller JS is injected with populated `slideSources` array
- [ ] Font CSS is injected verbatim from templates/font-embed.css
- [ ] All text content is HTML-escaped
- [ ] CSP meta tag is present — `<meta http-equiv="Content-Security-Policy">` in `<head>`
- [ ] No custom CSS or modified component HTML was added — only content placeholders were populated
