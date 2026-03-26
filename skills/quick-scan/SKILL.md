---
name: cro:quick-scan
description: >-
  Runs a quick CRO scan of an ecommerce page — single domain cluster,
  3-5 highest-impact findings, no further phases. Use when the user wants
  a fast, cheap check or says "quick scan", "quick look", or "quick wins".
disable-model-invocation: true
argument-hint: "[url-or-file-path-or-description] [--cluster visual-cta|trust-conversion|context-platform|audience-journey] [--min-priority level] [--platform shopify|nextjs] [--device mobile|laptop|desktop|both] [--visual] [--no-visual]"
---

<objective>
Run a quick CRO scan — single domain cluster, 3-5 highest-impact quick wins, no further phases. Fastest and cheapest option.
</objective>

<flags>
--cluster [slug]: Override auto-selected cluster. Values: visual-cta, trust-conversion, context-platform, audience-journey.
--min-priority [level]: Filter findings. Default for quick-scan: high (only HIGH and CRITICAL).
--platform [name]: Skip platform detection.
--visual: Auto-generate visual report (annotated wireframe with findings) without prompting.
--no-visual: Skip output prompt, conversation output only (meta.json still created silently).
--ephemeral: DEPRECATED — behaves as --no-visual. Prints warning: "--ephemeral is deprecated, use --no-visual".
--device [mobile|laptop|desktop|both]: Target device viewport. Default: prompt user (URL mode only).
  - mobile: 390×844, 3x DPR (via `agent-browser close` + `agent-browser set device "iPhone 14"`)
  - laptop: 1440×900, 1x DPR
  - desktop: 1920×1080, 1x DPR
  - both: Runs two separate scans (first + second device serially), produces audit.md + audit-{second}.md
  In --auto mode: defaults to "laptop" (no prompt).
</flags>

<mode_detection>
Determine input type from $ARGUMENTS:
- URL → existing page scan (dispatch acquisition agent, then auditor)
- File path → existing page scan (read directly)
- Image file (PNG, JPEG, WebP, or SVG) → screenshot-only scan (see below)
- Description text → from-scratch scan (auditor evaluates against principles without page code, outputs "the 5 most important things to get right")

**Screenshot-only mode:** If the user provides an image file (detected by extension: .png, .jpg, .jpeg, .webp, .svg) or drops an image:
1. Skip acquisition workflow entirely — no agent-browser, no DOM capture
2. Set `source_mode: "screenshot"` in meta.json
3. Populate `screenshot_input`: `{ "description": "[user's description]", "device_context": "[desktop|mobile|unknown]" }`
   - Infer device_context from description ("mobile homepage" → mobile) or image dimensions (width < 500px → mobile)
   - If ambiguous, ask: "Is this a desktop or mobile screenshot?"
4. Pass the screenshot image directly to the auditor. All findings will be `SOURCE: VISUAL` by definition.
5. The auditor estimates SVG marker coordinates from visual analysis of the screenshot.
6. Add limitations banner in visual report: "Based on screenshot only — DOM and interaction patterns not assessed."

**URL acquisition:**
1. Validate URL per ${CLAUDE_PLUGIN_ROOT}/references/url-validation.md
2. Dispatch acquisition agent per audit/SKILL.md <mode_detection>: read ${CLAUDE_PLUGIN_ROOT}/workflows/acquire.md, use `model: "opus"`, pass viewport/device context.
3. For "both" mode: dispatch twice serially (first device full, second device screenshots-only). Run `agent-browser close` between passes if DPR changes.
4. **Post-acquisition file verification (mandatory):** Run `ls docs/cro/{engagement-id}/` — verify baton.json, dom.html, and at least 1 screenshot exist. If missing, fall back to manual acquisition per audit/SKILL.md.
5. Set `source_mode: "url-dual"` in meta.json.

**File path:** Set `source_mode: "file"` in meta.json.
**Description:** Set `source_mode: "description"` in meta.json.
</mode_detection>

<device_selection>
**URL mode only.** After mode detection, before cluster selection, prompt for device:

"Which device should I scan?
1. **Mobile** (390×844)
2. **Laptop** (1440×900) — default
3. **Desktop** (1920×1080)
4. **Both** (pick two, e.g., 1,3) — produces two separate reports"

- If `--device` flag is set: use specified device(s), skip prompt.
- In `--auto` mode: default to `laptop`, skip prompt.
- For file path and description modes: skip device selection entirely (no viewport rendering).
- "Both" accepts a comma pair (e.g., `--device mobile,desktop`). Max 2 per run.

Log selected device: "Scanning **[device]** at [width]×[height]."

Set `devices_requested` in meta.json to the user's choice (e.g., `["laptop"]`, `["mobile", "desktop"]`).
</device_selection>

<platform_detection>
Detect the ecommerce platform before engagement setup. Load and follow ${CLAUDE_PLUGIN_ROOT}/references/platform-detection.md for heuristics. Accept `--platform` flag to skip detection.

- **URL mode:** Check URL patterns first (`.myshopify.com` → Shopify, `.vercel.app` → likely Next.js). If no URL pattern match, check the preprocessed DOM after acquisition for platform indicators (Shopify liquid comments, OpenCart `catalog/view`, Next.js `__NEXT_DATA__`).
- **File path mode:** Check file extensions and directory structure per platform-detection.md.
- **Description mode:** Ask the user if not specified.

Set `platform` in meta.json to the detected value. Do NOT default to `"generic"` without checking — many ecommerce sites have detectable platforms.
</platform_detection>

<engagement_setup>
Always create meta.json silently (needed for aggregation). Create engagement directory and meta.json with type: "quick-scan", quick_scan: true, schema_version: 2.

**meta.json schema:** See ${CLAUDE_PLUGIN_ROOT}/references/meta-schema.md. Validate on resume only — not after writing.
Always update the `updated` field to current ISO timestamp on phase transitions.

Check if docs/cro/ is in .gitignore. If not, suggest adding it.
</engagement_setup>

<cluster_selection>
Auto-select first cluster from page-type table:

| Page Type | Default Cluster |
|-----------|----------------|
| Product page | visual-cta |
| Cart | trust-conversion |
| Checkout | trust-conversion |
| Homepage | visual-cta |
| Category/Collection | visual-cta |
| Landing page | visual-cta |
| Pricing/Plans | trust-conversion |
| Post-purchase | audience-journey |

Override with --cluster flag. If no flag, **WAIT for user confirmation** before proceeding. Present the choice and do NOT dispatch acquisition or auditors until the user responds:

"I'll scan **[cluster name]** ([brief description]). Want to proceed, or switch clusters?
- `--cluster visual-cta` — CTA design, color psychology, eye tracking, product video
- `--cluster trust-conversion` — Trust signals, social proof, checkout, pricing, biometric auth, cookie consent
- `--cluster context-platform` — Mobile UX, cognitive load, performance, search & filter, cookie consent
- `--cluster audience-journey` — Personalization, cross-cultural, post-purchase, social commerce, push notifications

Or run `/cro:audit [same-input]` for full multi-cluster coverage."

**This is a blocking prompt.** Do not proceed until the user confirms or selects a cluster. In automated mode (no human interaction), use default without asking.
</cluster_selection>

<dispatch>
Dispatch ONE auditor per device with `model: "opus"`:
- Quick-scan workflow from ${CLAUDE_PLUGIN_ROOT}/workflows/quick-scan.md
- Reference files for selected cluster ONLY (from ${CLAUDE_PLUGIN_ROOT}/references/)
- Ethics gate from ${CLAUDE_PLUGIN_ROOT}/references/ethics-gate.md
- Evidence tier definitions from ${CLAUDE_PLUGIN_ROOT}/references/evidence-tiers.md
- **Device context:** pass `"desktop"` or `"mobile"` to the auditor

**Input varies by source mode:**
- **URL mode:** Pass sectioned screenshots + preprocessed DOM from acquisition agent
- **File path mode:** Pass page source code directly
- **Description mode:** Pass the text description

**Single device (mobile, laptop, or desktop):**
Write findings to docs/cro/{engagement-id}/audit.md. Update meta.json: phase → "complete", `devices_scanned` → matches selected device.

**Both mode (two devices):**
Dispatch TWO auditors (one per device, serially) with `model: "opus"`:
1. First device auditor → write to `audit.md`
2. Second device auditor → write to `audit-{second_device}.md`
Write audit files first, THEN update meta.json: phase → "complete", `devices_scanned` → both devices.

**Partial failure in "both" mode:**
If one device's acquisition or audit fails, deliver the successful device's report + warning:
"⚠️ [Mobile/Desktop] scan failed: [reason]. Run with `--device [failed-device]` to retry."
Set `devices_scanned` to reflect only what completed. `devices_requested` preserves the original "both" intent.
</dispatch>

<output>
Present findings directly — NO checkpoint menu. This is one-and-done.

Format as natural language with actionable recommendations:

## Quick Scan Results

[1-2 sentence summary]

**Findings:**
1. **[Finding title]** — [specific recommendation] `[SOURCE]` **[SEVERITY]** [if EFFORT: Low, append: `QUICK WIN`]
2. **[Finding title]** — [specific recommendation] `[SOURCE]` **[SEVERITY]** [if EFFORT: Low, append: `QUICK WIN`]
3. **[Finding title]** — [specific recommendation] `[SOURCE]` **[SEVERITY]**

Tag each finding with its severity (CRITICAL/HIGH) and append `QUICK WIN` for findings with EFFORT: Low. This makes it immediately clear which findings are easiest to act on.

Scan another area with `--cluster [name]`, or run `/cro:audit [same-input]` for full multi-cluster coverage.

**Auto-save:** audit.md + meta.json are ALWAYS saved silently after every scan. No prompting for markdown save.

**Then prompt for visual report** (unless flagged):
- If `--visual` is set: generate visual report inline (see below)
- If `--no-visual` or `--ephemeral` is set: skip prompt
- Otherwise, ask:

"Want an annotated visual report too? (dark-mode HTML with screenshot annotations and scroll-sync)"

In --auto mode: skip prompt.

**Quick-scan aggregate:** After presenting results, if 2+ previous quick-scans exist for the same URL AND same device (check docs/cro/*/meta.json for matching `url_normalized` with `quick_scan: true` AND matching device in `devices_scanned`):

"You've scanned this page [N] times on [device]. Want to see the aggregate? Shows which findings are consistent (high confidence) vs. appeared once."

Aggregate only compares desktop-to-desktop or mobile-to-mobile — never cross-device. Display device in aggregate summary.

In --auto mode: skip aggregate prompt. Aggregate only via explicit `--aggregate` flag.
</output>

<visual_report_generation>
When generating a visual report (user says yes or --visual flag):

Generate the report inline — do NOT dispatch a subagent.
1. Read `${CLAUDE_PLUGIN_ROOT}/templates/components.html` for component definitions — this is what you assemble from
2. Copy `${CLAUDE_PLUGIN_ROOT}/templates/font-embed.css` into `<head>` verbatim (do NOT read/interpret — just copy)
3. Read `${CLAUDE_PLUGIN_ROOT}/templates/visual-report.html.template` for the HTML skeleton
4. Read `${CLAUDE_PLUGIN_ROOT}/workflows/visual-report.md` for assembly instructions
5. Assemble components: header with eyebrow + title, metadata grid, evidence canvas (screenshot carousel with markers + thumbnails), finding cards with recommendation boxes + evidence tier badges + citation URLs, summary section (evidence confidence + severity distribution + ethics), carousel + scroll-sync JS
6. Write completed self-contained HTML

**You MUST use the HTML/CSS/JS from components.html exactly as written. Do not modify component structure. Do not add custom CSS. Only populate content placeholders.**

Output: `docs/cro/{engagement-id}/visual-report.html`
For "both" mode: `visual-report-desktop.html` and `visual-report-mobile.html`
</visual_report_generation>

<ethics>
Same as /cro:audit — pass ethics gate to auditor.
</ethics>
