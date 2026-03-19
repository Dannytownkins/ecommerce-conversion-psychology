---
name: visual-report-generation
---

# Visual Report Generation — Coordinator Reference (v3.2)

The coordinator produces an annotated screenshot visual report by following these steps. This is NOT a subagent workflow — the coordinator reads these instructions and generates the report inline.

## Input (already available to coordinator)

1. **Section boundary metadata** — from acquisition agent output (labels, scrollY, height, cluster tags)
2. **Style metadata** — extracted colors (bg, container_bg, text, cta_bg, link) + **luminance** value (0-1)
3. **Preprocessed DOM** — cleaned HTML from `docs/cro/{engagement-id}/dom.html`
4. **Screenshot images** — 3-6 sectioned viewport captures (base64 JPEG)
5. **Audit findings** — from `audit.md` (or `audit-mobile.md`) with SOURCE, SECTION, PRIORITY, EVIDENCE_TIER, QUALITY_FLAG, OBSERVATION, RECOMMENDATION, rationale, citation
6. **Engagement metadata** — ID, date, URL, platform, clusters, device, viewport
7. **Component library** — `templates/components.html`
8. **Font CSS** — `templates/fonts.css.fragment`

## Step 1: Build Screenshot Panels

For each section screenshot from the acquisition agent:

1. **Resize to display resolution** — max 800px wide at JPEG quality 65 before base64 encoding. This reduces file size by 40-60%.

2. **Evaluate obscuration** — check if overlay elements (modals, popups, cookie banners) cover >30% of the viewport area in this screenshot:
   - **Clean screenshot** → use the `screenshot-panel` component
   - **Obscured screenshot** → use the `wireframe-fallback-section` component. Generate a simplified label from DOM content (heading text, section type).

3. **Set SVG viewBox** — match the screenshot's pixel dimensions (width x height after resize).

4. Stack all screenshot panels vertically in the left panel div. Each gets `scroll-snap-align: start`.

## Step 2: Place SVG Markers + Build Finding Cards

For each FAIL or PARTIAL finding (ordered by page position, top to bottom):

1. **Map to screenshot** — find the screenshot whose scrollY range contains the finding's SECTION scrollY:
   ```
   screenshot match: finding_scrollY >= screenshot_scrollY AND finding_scrollY < (screenshot_scrollY + screenshot_height)
   ```

2. **Calculate marker position** within the screenshot's SVG viewBox:
   ```
   marker_y = (finding_scrollY - screenshot_scrollY) / screenshot_height * viewBox_height
   marker_x = viewBox_width * 0.9   (right-aligned, out of the way)
   ```
   Do NOT estimate horizontal positions — default to 90% from left.

3. **Add SVG callout marker** — use the `svg-callout-marker` component inside the screenshot's SVG overlay. Set severity color:
   - CRITICAL → `#ef4444` (red)
   - HIGH → `#f59e0b` (amber)
   - MEDIUM → `#3b82f6` (blue)
   - LOW → `#6b7280` (gray)

4. **Build finding card** — use the `finding-card` component:
   - Number matches the SVG marker number
   - `data-finding-id` = sequential finding number (e.g., "1", "2", "3")
   - `data-screenshot` = the screenshot panel's `id` attribute
   - Title = human-readable SECTION slug (e.g., `primary-cta` → "Primary CTA")
   - Quick Win badge: include if EFFORT is "Low" or QUICK_WIN is true

5. **Build citation content** — for each finding's citation line:
   - **Sanitize URL**: reject any URL that is not `http:` or `https:` scheme. Rejected URLs render as plain text.
   - Add `rel="noopener noreferrer" target="_blank"` to all citation links
   - Insert an `evidence-tier-badge` component (Gold/Silver/Bronze) from the finding's EVIDENCE_TIER field
   - If QUALITY_FLAG is present, add italic text: `<em style="font-size: 0.8rem; color: var(--text-muted); margin-left: 0.5rem;">{quality_flag}</em>`
   - If no EVIDENCE_TIER in finding data, default to Bronze

## Step 3: Theme Selection

Read the `luminance` field from acquisition style metadata:
- If luminance > 0.5 → set `{slot:theme-class}` to `theme-light`
- If luminance <= 0.5 or absent → set `{slot:theme-class}` to `theme-dark`
- Screenshot-only mode (`source_mode: "screenshot"`) → always `theme-dark`

## Step 4: Calculate Scores

Count from the findings:
- **Total:** all FAIL + PARTIAL findings
- **Critical:** findings with PRIORITY: CRITICAL
- **High:** findings with PRIORITY: HIGH
- **Quick Wins:** findings with EFFORT: Low (or QUICK_WIN: true)

## Step 5: Generate Nonce

Generate a unique nonce for the CSP: 16 random hexadecimal characters (e.g., `a8f3k19mpq2x7b4e`). This nonce is used in both the CSP meta tag and the script tag.

## Step 6: Assemble Report

Read `templates/components.html` and `templates/fonts.css.fragment`.

**ASSEMBLY ORDER (always this exact sequence):**

```
 1. report-shell          (outer wrapper — <head>, opens <body>)
       Fill {slot:font-css} with contents of fonts.css.fragment
       Fill {slot:nonce} with the generated nonce
       Fill {slot:theme-class} from Step 3
 2.   report-header        (inside body)
 3.   score-summary-strip
 4.   [screenshot-only-banner — only if source_mode is "screenshot"]
 5.   [all-obscured-banner — only if ALL screenshots were obscured]
 6.   split-panel-layout   (opens left/right grid)
 7.     LEFT PANEL: for each screenshot section (top to bottom):
 8.       screenshot-panel  (with SVG overlay container)
 9.         OR wireframe-fallback-section (if obscured)
10.       for each finding mapped to this screenshot:
11.         svg-callout-marker (inside the SVG overlay)
12.     RIGHT PANEL:
13.       for each finding (ordered by page position, top to bottom):
14.         finding-card (with nested evidence-tier-badge in citation)
15.   print-layout-overrides
16.   interaction-script    *** COPY VERBATIM — DO NOT MODIFY ***
17.   report-footer
18. close report-shell
```

**Fill all `{slot:*}` placeholders** with engagement data. Use HTML-escaping on all text content.

**Hardcode MIME types** for base64 data: always `data:image/jpeg;base64,...` — never derive from input.

Write to `docs/cro/{engagement-id}/visual-report.html`
- For `--device both`: write `visual-report-desktop.html` and `visual-report-mobile.html` separately.

## Step 7: Security

- **HTML-escape** ALL text content before insertion (finding text, recommendations, URLs, product names, prices)
- **Sanitize citation URLs** — allowlist `http:` and `https:` schemes only. Reject `javascript:`, `data:`, and all other schemes. Rejected URLs render as plain text.
- **Nonce-based CSP** — the report shell includes a CSP meta tag with the generated nonce. Only the interaction-script (with matching nonce) can execute.
- **No external resources** — everything is inline CSS, base64 fonts, or base64 images
- **Escape `{slot:` patterns** found in user content to prevent placeholder collision
- **`rel="noopener noreferrer"`** on ALL external links

## Screenshot-Only Mode

When `source_mode` is `"screenshot"` (user provided screenshots, no URL scan):

- No acquisition metadata available — **skip SVG marker overlay entirely**
- Screenshots rendered without callout markers (no scrollY data for positioning)
- Findings reference sections by name only (no numbered markers matching to screenshots)
- Prepend `screenshot-only-banner` component after score-summary-strip
- All findings have SOURCE: VISUAL
- Theme: always `theme-dark` (no luminance data available)
- Finding cards still get `data-screenshot` attributes pointing to the closest screenshot by label match

## Post-Assembly Validation

Before writing the file, verify:

- [ ] No `{slot:*}` markers remain in the output
- [ ] No `<!-- BEGIN:` or `<!-- END:` markers remain
- [ ] Finding card count matches SVG marker count (except screenshot-only mode)
- [ ] Every finding card has `data-severity`, `data-finding-id`, and `data-screenshot` attributes
- [ ] The interaction-script is present and unmodified, with matching nonce
- [ ] CSP meta tag is present with the correct nonce
- [ ] All citation URLs are `http:` or `https:` only (no `javascript:` or `data:` schemes)
- [ ] All text content is HTML-escaped
- [ ] No external resource references (all fonts/images are base64 inline)
- [ ] Screenshots use `data:image/jpeg;base64,...` (hardcoded MIME type)
