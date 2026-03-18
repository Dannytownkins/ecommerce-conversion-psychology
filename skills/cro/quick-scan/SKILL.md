---
name: cro:quick-scan
description: >-
  Runs a quick CRO scan of an ecommerce page. Single domain cluster,
  3-5 highest-impact quick wins, no further phases. Faster and cheaper
  than a full audit.
disable-model-invocation: true
argument-hint: "[url-or-file-path-or-description] [--cluster visual-cta|trust-conversion|context-platform|audience-journey] [--min-priority level] [--platform shopify|nextjs] [--device desktop|mobile|both] [--visual] [--no-visual]"
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
--device [desktop|mobile|both]: Target device viewport. Default: prompt user (URL mode only).
  - desktop: 1440×900, 1x DPR
  - mobile: 390×844 (iPhone 14 preset, includes DPR and user-agent)
  - both: Runs two separate scans, produces audit.md (desktop) + audit-mobile.md (mobile)
  In --auto mode: defaults to "desktop" (no prompt).
</flags>

<mode_detection>
Determine input type from $ARGUMENTS:
- URL → existing page scan (dispatch acquisition agent, then auditor)
- File path → existing page scan (read directly)
- Description text → from-scratch scan (auditor evaluates against principles without page code, outputs "the 5 most important things to get right")

**URL acquisition:**
1. Validate URL using rules in ${CLAUDE_PLUGIN_ROOT}/references/url-validation.md
2. Dispatch acquisition agent:
   - Read ${CLAUDE_PLUGIN_ROOT}/workflows/acquire.md
   - Dispatch via Agent tool with `model: "opus"`
   - Pass the validated URL, viewport dimensions based on selected device, and device context:
     - Desktop: viewport 1440×900, device "desktop"
     - Mobile: viewport 390×844 (use device preset "iPhone 14"), device "mobile"
     - Both: dispatch twice serially:
       1. Desktop pass: full acquisition (DOM + screenshots) — viewport 1440×900, device "desktop"
       2. Mobile pass: pass `dom_file` from desktop acquisition, device "mobile" — screenshots only
   - Collect output: sectioned screenshots (3-6), preprocessed DOM, section metadata, styles
   - If acquisition returns `STATUS: BLOCKED` → present reason, ask for file path or pasted code
   - If acquisition returns `STATUS: PARTIAL` → proceed with available data
   - Set `source_mode: "url-dual"` in meta.json

**File path:** Set `source_mode: "file"` in meta.json.
**Description:** Set `source_mode: "description"` in meta.json.
</mode_detection>

<device_selection>
**URL mode only.** After mode detection, before cluster selection, prompt for device:

"Which device should I scan?
1. **Desktop** (1440×900) — default
2. **Mobile** (390×844, iPhone 14/15)
3. **Both** — produces two separate reports"

- If `--device` flag is set: use specified device, skip prompt.
- In `--auto` mode: default to `desktop`, skip prompt.
- For file path and description modes: skip device selection entirely (no viewport rendering).

Log selected device: "Scanning **[device]** at [width]×[height]."

Set `devices_requested` in meta.json to the user's choice: `["desktop"]`, `["mobile"]`, or `["desktop", "mobile"]`.
</device_selection>

<engagement_setup>
Always create meta.json silently (needed for aggregation). Create engagement directory and meta.json with type: "quick-scan", quick_scan: true, schema_version: 2.

After writing meta.json, re-read it and verify all required fields are present:
- `id`: string, format YYYY-MM-DD-{8hex}
- `created`: ISO 8601 string
- `type`: one of [audit, build, quick-scan, compare]
- `phase`: one of [pending, audit, plan, review, build, complete]
- `platform`: one of [shopify, nextjs, generic]
- `page.type`: must match the page type table
- `clusters_used`: array of cluster slug strings
Optional: `blocked`, `quick_scan`, `compare_target`, `page.url`, `page.file_path`, `min_priority`, `source_mode`, `devices_requested`, `devices_scanned`, `plans_queue`, `reconciled`
If any required field is missing or invalid, fix it before proceeding.
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

Override with --cluster flag. If no flag, offer the user a choice with context:

"I'll scan **[cluster name]** ([brief description]). Other options:
- `--cluster visual-cta` — CTA design, color psychology, eye tracking, product video
- `--cluster trust-conversion` — Trust signals, social proof, checkout, pricing, biometric auth, cookie consent
- `--cluster context-platform` — Mobile UX, cognitive load, performance, search & filter, cookie consent
- `--cluster audience-journey` — Personalization, cross-cultural, post-purchase, social commerce, push notifications

Or run `/cro:audit [same-input]` for full multi-cluster coverage."

In automated mode (no human interaction), use default without asking.
</cluster_selection>

<dispatch>
Dispatch ONE auditor per device with `model: "opus"`:
- Quick-scan workflow from ${CLAUDE_PLUGIN_ROOT}/workflows/quick-scan.md
- Reference files for selected cluster ONLY (from ${CLAUDE_PLUGIN_ROOT}/references/)
- Ethics gate from ${CLAUDE_PLUGIN_ROOT}/references/ethics-gate.md
- **Device context:** pass `"desktop"` or `"mobile"` to the auditor

**Input varies by source mode:**
- **URL mode:** Pass sectioned screenshots + preprocessed DOM from acquisition agent
- **File path mode:** Pass page source code directly
- **Description mode:** Pass the text description

**Single device (desktop or mobile):**
Write findings to docs/cro/{engagement-id}/audit.md. Update meta.json: phase → "complete", `devices_scanned` → matches selected device.

**Both mode:**
Dispatch TWO auditors (one per device, serially) with `model: "opus"`:
1. Desktop auditor → write to `audit.md`
2. Mobile auditor → write to `audit-mobile.md`
Write audit files first, THEN update meta.json: phase → "complete", `devices_scanned: ["desktop", "mobile"]`.

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

**Top quick wins:**
1. [Finding + specific recommendation] `[SOURCE]`
2. [Finding + specific recommendation] `[SOURCE]`
3. [Finding + specific recommendation] `[SOURCE]`

Scan another area with `--cluster [name]`, or run `/cro:audit [same-input]` for full multi-cluster coverage.

**Then prompt for output format** (unless flagged):
- If `--visual` is set: generate visual report inline (see below)
- If `--no-visual` or `--ephemeral` is set: skip prompt
- Otherwise, ask:

"Want me to save this?
1. Visual report — annotated wireframe with findings
2. Markdown — already saved to audit.md
3. Both
4. No, conversation is enough"

In --auto mode: skip prompt, default to markdown only (audit.md already written).

**Quick-scan aggregate:** After presenting results, if 2+ previous quick-scans exist for the same URL AND same device (check docs/cro/*/meta.json for matching `url_normalized` with `quick_scan: true` AND matching device in `devices_scanned`):

"You've scanned this page [N] times on [device]. Want to see the aggregate? Shows which findings are consistent (high confidence) vs. appeared once."

Aggregate only compares desktop-to-desktop or mobile-to-mobile — never cross-device. Display device in aggregate summary.

In --auto mode: skip aggregate prompt. Aggregate only via explicit `--aggregate` flag.
</output>

<visual_report_generation>
When generating a visual report (user selects "Visual report" or --visual flag):

Generate the report inline — do NOT dispatch a subagent.
1. Read `${CLAUDE_PLUGIN_ROOT}/templates/visual-report.html.template` for the HTML structure
2. Read `${CLAUDE_PLUGIN_ROOT}/workflows/visual-report.md` for generation instructions
3. Build wireframe sections from acquisition data (section boundaries, DOM elements, style metadata)
4. Build finding cards from audit findings (with rationale + citations)
5. Calculate scores (total, critical, high, quick wins)
6. Fill template placeholders and write completed HTML

Output: `docs/cro/{engagement-id}/visual-report.html`
For "both" mode: `visual-report-desktop.html` and `visual-report-mobile.html`
</visual_report_generation>

<ethics>
Same as /cro:audit — pass ethics gate to auditor.
</ethics>
