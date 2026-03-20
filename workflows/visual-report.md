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

Read `templates/components.html` in full. This file contains every HTML component used in the report. All subsequent steps reference components defined there.

## Step 2: Inject Font Stylesheet

Copy the contents of `templates/font-embed.css` into the `<head>` of the report **verbatim**. Do not read, interpret, parse, or modify the CSS. Paste it exactly as-is inside a `<style>` tag.

## Step 3: Read Baton Files

Load the following from the engagement directory (`docs/cro/{engagement-id}/`):

- `meta.json` — parse all fields
- `audit.md` (or `audit-mobile.md`) — parse all findings
- `baton.json` — parse acquisition metadata: screenshots (paths, base64_paths, naturalWidth, naturalHeight), sections (boundaries, clusters, occlusion), styles, dom_mode. **If baton.json does not exist or `status` != `"COMPLETE"`, warn:** "Acquisition baton missing or incomplete — screenshot positions and SVG viewBox may be inaccurate."
- Screenshot `.jpg` files — base64-encoded at render time for embedding

## Step 4: Assemble Header

Populate the header component from `components.html` using `meta.json` fields:

- Engagement ID
- Audit date
- Page URL (HTML-escaped)
- Page type
- Platform
- Cluster name(s)
- Device (Desktop or Mobile)
- Viewport dimensions
- Source mode

## Step 5: Assemble Score Strip

Count findings by PRIORITY from the audit file. Populate the score-strip component with counts for **CRITICAL, HIGH, MEDIUM, and LOW only**.

Do NOT include counts for STATUS values (PASS, FAIL, PARTIAL, SKIP). The score strip shows severity distribution, not pass/fail tallies.

## Step 6: Assemble Finding Cards

For each finding in the audit, assemble a finding-card component from `components.html`:

1. **Select severity CSS class** based on the finding's PRIORITY field (critical, high, medium, low).

2. **Hide STATUS from rendered output.** The finding's STATUS (PASS, FAIL, PARTIAL, SKIP) is used only for internal filtering. It MUST NOT appear anywhere in the rendered HTML.

3. **Populate the card body:**
   - Sequential finding number
   - Title derived from SECTION slug (e.g., `primary-cta` becomes "Primary CTA")
   - Severity badge with the appropriate CSS class
   - OBSERVATION text
   - RECOMMENDATION text

4. **Move SOURCE to "Technical details" collapsible section.** Render SOURCE inside a `<details><summary>Technical details</summary>...</details>` block within the finding card, using the collapsible component structure from `components.html`.

5. **Render "Why this matters" as a collapsible section.** Place WHY_THIS_MATTERS content inside a `<details><summary>Why this matters</summary>...</details>` block within the finding card.

6. **Render evidence tier badge in citation footer.** The evidence tier badge MUST be always visible (not inside a collapsible). Place it in the citation footer area of the finding card.

7. **Resolve and render clickable citation URLs (MANDATORY).** Auditors do NOT include URLs — the report generator resolves them. For each finding's `↳` citation line, extract the reference filename and finding number (e.g., `cta-design-and-placement.md, Finding 14`). Then look up the URL:
   1. Read `citations/sources.md` from the plugin directory. Find the section matching the reference filename. Find the row matching the finding number. Use the URL from that row.
   2. If `citations/sources.md` is not available or has no match, render the citation as plain text with "(source URL unavailable)".
   Render the resolved URL as an `<a>` tag with `rel="noopener noreferrer" target="_blank"` using the `finding__citation-url` class from `components.html`. **A finding card without a clickable citation link is incomplete.**

## Step 7: Assemble Screenshot Panel

### 7a. URL mode (source_mode is url-based)

Assemble the screenshot-panel component with SVG overlay markers:

- **Embed screenshots as base64 data URIs.** For each screenshot in `baton.json`, base64-encode the JPEG file at render time: `base64 < {path}.jpg` (or equivalent in the rendering environment). Embed as: `src="data:image/jpeg;base64,{encoded data}"`. **VERIFY:** every `<img>` src in the screenshot panel starts with `data:image/` — never a relative file path. If the JPEG file is missing, skip that screenshot and add a comment: `<!-- WARNING: screenshot file missing -->`.
- Set SVG `viewBox` to match the screenshot's `naturalWidth` x `naturalHeight` from `baton.json`. Do NOT use CSS viewport dimensions (e.g., 390x844) — use the actual pixel dimensions of the image (e.g., 1170x2532 for 3x DPR mobile).
- **Position overlay markers using element coordinates from `baton.json`.** For each finding, match the finding's `ELEMENT` field (CSS selector or description) to entries in the baton's `elements` array. Place the marker at the center of the matched element's bounding box (`x + width/2`, `y + height/2`), adjusted for the screenshot's `scrollY` offset (subtract the screenshot's `scrollY` from the element's `y` to get the position within that screenshot). If no element match is found, fall back to positioning the marker at the center of the section boundary (`scrollY + height/2`) from the baton's `sections` array. **DPR adjustment:** For mobile screenshots at DPR > 1, element coordinates in the baton are already in screenshot pixels (CSS px × DPR). If they are still in CSS pixels, multiply by the DPR before positioning.
- **Strip HTML comments from `components.html` before extracting `<style>` blocks via regex.** The SVG safety comment historically contained literal tag names that caused false regex matches, injecting HTML template markup into the CSS and breaking the split-layout. Always strip `<!--...-->` comments first.
- Use wireframe rendering ONLY for occluded sections (sections where `occluded: true` in the baton). Do not wireframe sections that have screenshot coverage.

### 7b. Screenshot-only mode (source_mode is file/screenshot)

Assemble the screenshot-panel component with markers positioned from Claude's estimated pixel coordinates:

- **Embed screenshots as base64 data URIs** using the same method as URL mode (base64-encode the JPEG at render time). If the input was a user-provided image file, base64-encode it directly.
- Claude estimates element positions based on visual inspection of the screenshot.
- No wireframe fallback. All sections are represented by the screenshot itself.

### 7c. Mobile reports

Wrap all screenshots in the device-frame component from `components.html`. Apply the device-frame component around each screenshot image before placing it in the screenshot panel.

## Step 8: Limitations Banner

If `source_mode` is `screenshot` (file-based input without live URL access), assemble the limitations-banner component from `components.html` and insert it after the header. This alerts readers that the audit was performed on static screenshots rather than a live page.

## Step 9: Ethics Compliance Section (MANDATORY — never omit)

This section MUST appear in every report, regardless of findings.

- **If ethics violations were found:** Render each violation as a CRITICAL finding card using the finding-card component. Add an "Ethics / Legal" badge to distinguish these from standard conversion findings.

- **If no ethics violations were found:** Render the ethics-clear line: "Ethics check: No dark patterns detected." Use the ethics-section component from `components.html`.

## Step 10: Inject Scroll-Sync JS

Copy the scroll-sync JavaScript block from `components.html` and inject it at the bottom of the report `<body>`. Use it exactly as defined — do not modify the script.

## Step 11: Assemble Export Footer

Populate the export-footer component from `components.html` with generation metadata:

- Generation date/time
- Plugin version (from `meta.json`)
- Engagement ID
- Source mode

## Step 12: Output

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
- [ ] Score strip shows only CRITICAL/HIGH/MEDIUM/LOW counts
- [ ] SOURCE is inside "Technical details" collapsible in every finding card
- [ ] Evidence tier badge is visible (not collapsed) in every finding card citation footer
- [ ] Citation URLs are clickable with `rel="noopener noreferrer" target="_blank"`
- [ ] "Why this matters" is rendered as a collapsible section
- [ ] **All screenshot `<img>` src attributes start with `data:image/`** — no relative file paths
- [ ] **SVG viewBox uses naturalWidth × naturalHeight from baton.json** — not CSS viewport dimensions
- [ ] Screenshots have SVG overlays (URL mode) or estimated markers (screenshot mode)
- [ ] Mobile screenshots are wrapped in device-frame component
- [ ] Limitations banner is present when source_mode is screenshot
- [ ] Ethics compliance section is present (violations as CRITICAL cards, or clear-line)
- [ ] Scroll-sync JS is injected from components.html
- [ ] Font CSS is injected verbatim from templates/font-embed.css
- [ ] All text content is HTML-escaped
- [ ] CSP meta tag is present — `<meta http-equiv="Content-Security-Policy">` in `<head>`
- [ ] No custom CSS or modified component HTML was added — only content placeholders were populated
