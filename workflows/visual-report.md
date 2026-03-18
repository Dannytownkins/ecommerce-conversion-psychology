---
name: visual-report-generation
---

# Visual Report Generation — Coordinator Reference

The coordinator produces an annotated wireframe visual report by following these steps. This is NOT a subagent workflow — the coordinator reads these instructions and generates the report inline.

## Input (already available to coordinator)

1. **Section boundary metadata** — from acquisition agent output (labels, scrollY, height, cluster tags)
2. **Style metadata** — extracted colors (bg, container_bg, text, cta_bg, link)
3. **Preprocessed DOM** — cleaned HTML from `docs/cro/{engagement-id}/dom.html`
4. **Screenshot paths** — 3-6 sectioned viewport captures
5. **Audit findings** — from `audit.md` (or `audit-mobile.md`) with SOURCE, SECTION, PRIORITY, OBSERVATION, RECOMMENDATION, rationale, citation
6. **Engagement metadata** — ID, date, URL, platform, clusters, device, viewport
7. **Template** — `templates/visual-report.html.template`

## Step 1: Build Wireframe Sections

For each section identified by the acquisition agent:

1. **Identify section type** from the label and cluster tags:

| Label Pattern | Section Type | Wireframe Block |
|---|---|---|
| announcement, banner, promo | Announcement bar | Dark strip with text content + link text |
| header, nav, navigation | Navigation | Logo text + nav link names + icon placeholders |
| hero, vehicle, selector, main banner | Hero | Dark block with key heading + form elements + CTA button |
| category, categories, collection grid | Category grid | Row of small labeled cards |
| product, featured, collection, shop | Product grid/carousel | Row of product card outlines with actual names/prices |
| newsletter, email, subscribe | Newsletter | Centered heading + email input mockup |
| footer, copyright | Footer | Two-column text links + payment icon placeholders |
| (unmatched) | Generic section | Labeled block with "Content section" placeholder |

2. **Extract key elements from DOM** for this section's scroll range:
   - Headings (h1-h3): use actual text
   - Buttons/CTAs: use actual button text
   - Navigation links: use actual link text (first 6)
   - Product cards: use actual product name + price (first 3 per section, then "N more items" note)
   - Form fields: show as input outlines with placeholder text
   - Images: show as gray placeholder boxes with dimensions or alt text

3. **Apply extracted colors** from style metadata:
   - Section backgrounds: use `bg` or `container_bg` as appropriate
   - CTA buttons: use `cta_bg` for background, white text
   - Text: use `text` color for headings, `text-muted` for body
   - Links: use `link` color

4. **Attach findings** to this section by matching SECTION slugs:
   - Use the slug-to-section mapping from the audit workflow
   - Add a numbered callout marker (colored circle) matching the finding's severity
   - Apply `has-critical` or `has-high` CSS class to the wireframe section block

5. **Embed screenshot** as a collapsible `<details>` element:
   - Summary text: "View screenshot"
   - Image: base64-encoded JPEG from the acquisition screenshots
   - Add CSS class `mobile` to screenshot images when device is mobile

## Step 2: Build Finding Cards

For each FAIL or PARTIAL finding:

1. Create a finding card with:
   - **Number** — sequential, matching the wireframe callout marker
   - **Title** — derived from SECTION slug, formatted as human-readable (e.g., `primary-cta` → "Primary CTA")
   - **Severity badge** — CRITICAL (red) or HIGH (amber)
   - **Observation** — from finding's OBSERVATION field
   - **Fix** — from finding's RECOMMENDATION field
   - **Rationale** — from finding's "Why this matters" block
   - **Citation** — from finding's citation line

2. Apply severity CSS class (`critical` or `high`) to the card

3. Numbers MUST match between wireframe callout markers and finding cards

## Step 3: Calculate Scores

Count from the findings:
- **Total:** all FAIL + PARTIAL findings
- **Critical:** findings with PRIORITY: CRITICAL
- **High:** findings with PRIORITY: HIGH
- **Quick Wins:** findings with EFFORT: Low (or QUICK_WIN: true)

## Step 4: Add Fold Line

Insert a fold line indicator in the wireframe at the approximate viewport boundary:
- Desktop (1440x900): after the section whose scrollY + height exceeds 900px
- Mobile (390x844): after the section whose scrollY + height exceeds 844px
- Label: "approximate fold ({width}x{height})"

## Step 5: Assemble Report

1. Read `templates/visual-report.html.template`
2. Replace placeholders:
   - `{{ENGAGEMENT_ID}}` — engagement ID
   - `{{DATE}}` — audit date
   - `{{PAGE_URL}}` — page URL (HTML-escaped)
   - `{{PAGE_TYPE}}` — homepage, product, etc.
   - `{{PLATFORM}}` — shopify, nextjs, generic
   - `{{CLUSTERS}}` — cluster name(s)
   - `{{DEVICE}}` — Desktop or Mobile
   - `{{DEVICE_CLASS}}` — `desktop` or `mobile` (CSS class)
   - `{{VIEWPORT}}` — e.g., "1440x900 @ 1x" or "390x844 @ iPhone 14"
   - `{{SOURCE_MODE}}` — url-dual, file, etc.
   - `{{VERSION}}` — plugin version (3.1.0)
   - `{{SCORE_TOTAL}}`, `{{SCORE_CRITICAL}}`, `{{SCORE_HIGH}}`, `{{SCORE_QUICKWINS}}` — from Step 3
   - `{{WIREFRAME_SECTIONS}}` — assembled wireframe HTML from Step 1
   - `{{FINDING_CARDS}}` — assembled finding card HTML from Step 2
   - `{{GENERATED_DATE}}` — current date/time
3. Write to `docs/cro/{engagement-id}/visual-report.html`
   - For "both" mode: `visual-report-desktop.html` and `visual-report-mobile.html`

## Step 6: Security

- **HTML-escape** ALL text content before insertion (finding text, recommendations, URLs, product names, prices)
- **CSP meta tag** already in the template — verify it's present
- **No external resources** — everything is inline CSS or base64 images
- **Escape `{{` patterns** found in user content to prevent template placeholder collision

## Quality Check

Before writing the file, verify:
- [ ] Every FAIL/PARTIAL finding has a callout marker on the wireframe AND a finding card
- [ ] Numbers match between wireframe markers and finding cards
- [ ] Screenshots are base64-embedded (if available)
- [ ] Fold line is positioned correctly
- [ ] All text content is HTML-escaped
- [ ] CSP meta tag is present
- [ ] Site colors are applied to wireframe elements
