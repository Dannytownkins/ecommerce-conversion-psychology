---
name: cro:compare
description: >-
  Compares an ecommerce page against a competitor page. Runs 1:1 same-type
  comparison with side-by-side scoring and gap analysis. Supports URLs
  (via agent-browser) and local file paths.
disable-model-invocation: true
argument-hint: "[your-url-or-path] [competitor-url-or-path] [--device desktop|mobile|both] [--visual] [--no-visual] [--engagement-id id]"
---

<objective>
Compare your ecommerce page against a competitor's page. 1:1 same-type comparison with side-by-side scoring, gap analysis, and actionable recommendations.
</objective>

<flags>
--visual: Auto-generate visual comparison report (annotated wireframe with findings).
--no-visual: Skip visual report prompt, markdown only.
--engagement-id [id]: Target a specific past engagement.
--device [desktop|mobile|both]: Target device viewport. Default: prompt user (URL mode only).
  - desktop: 1440×900, 1x DPR
  - mobile: 390×844 (iPhone 14 preset, includes DPR and user-agent)
  - both: Runs acquisition/audit for both devices on both pages (4 total acquisitions). Produces separate per-device reports.
  In --auto mode: defaults to "desktop" (no prompt).
</flags>

<intake>
Accept both inputs as arguments: /cro:compare [your-url-or-path] [competitor-url-or-path]

Supports:
- Two URLs (via acquisition agent)
- Two local file paths (direct read — preferred when available)
- Mixed (one URL, one file path)

If only one provided, ask for the other.
For URLs: validate using ${CLAUDE_PLUGIN_ROOT}/references/url-validation.md before dispatching acquisition.
</intake>

<device_selection>
**URL mode only.** After intake, before page type validation, prompt for device:

"Which device should I compare?
1. **Desktop** (1440×900) — default
2. **Mobile** (390×844, iPhone 14/15)
3. **Both** — compares both devices (4 acquisitions total, takes longer)"

**Cost warning for "both" mode:**
"Scanning 2 URLs × 2 devices = 4 acquisitions. This will take longer. Proceed?"
In --auto mode: show warning but proceed without prompt.

- If `--device` flag is set: use specified device, skip prompt.
- In `--auto` mode: default to `desktop`, skip prompt.
- For file path inputs: skip device selection entirely.

Set `devices_requested` in meta.json.
</device_selection>

<page_type_validation>
Determine page type for both pages.
If types differ: "These appear to be different page types ([type-a] vs [type-b]). Compare anyway, or provide matching pages?"
If --auto and types differ: proceed with comparison despite mismatch, note it in output.
If user proceeds despite mismatch, note it in the comparison output.
</page_type_validation>

<engagement_setup>
Same as /cro:audit but with type: "compare", schema_version: 2 in meta.json.
Store compare_target URL/path in meta.json.

After writing meta.json, re-read it and verify all required fields against these patterns:
- `id`: string, MUST match pattern `^\d{4}-\d{2}-\d{2}-[0-9a-f]{8}$` (e.g., `2026-03-19-a3f7b1c2`)
- `created`: string, valid ISO 8601 (e.g., `2026-03-19T14:30:00.000Z`)
- `type`: string, MUST be one of: `audit`, `build`, `quick-scan`, `compare`
- `phase`: string, MUST be one of: `pending`, `audit`, `plan`, `review`, `build`, `complete`
- `platform`: string, MUST be one of: `shopify`, `nextjs`, `opencart`, `generic`
- `page.type`: string, MUST be one of: `product`, `cart`, `checkout`, `homepage`, `category`, `landing`, `pricing`, `post-purchase`
- `clusters_used`: array of strings, each MUST be one of: `visual-cta`, `trust-conversion`, `context-platform`, `audience-journey`
Optional fields (valid if present): `blocked` (boolean), `quick_scan` (boolean), `compare_target` (object), `page.url` (string|null), `page.file_path` (string|null), `min_priority` (string|null), `source_mode` (string|null), `devices_requested` (array), `devices_scanned` (array), `plans_queue` (array), `reconciled` (boolean), `screenshot_input` (object|null)
If ANY required field is missing, null, or fails its pattern/enum check: fix it immediately before proceeding. Log which field was corrected.
Always update the `updated` field to current ISO timestamp on phase transitions.

Check if docs/cro/ is in .gitignore. If not, suggest adding it.
</engagement_setup>

<acquisition>
**Serialize acquisition, then parallelize auditors:**

**Step 1: Acquire your page** (if URL)
- Validate URL, dispatch acquisition agent (model: opus) with ${CLAUDE_PLUGIN_ROOT}/workflows/acquire.md
- Pass viewport dimensions and device context based on selected device:
  - Desktop: viewport 1440×900, device "desktop"
  - Mobile: viewport 390×844 (device preset "iPhone 14"), device "mobile"
  - Both: two serial passes — desktop (full) then mobile (pass `dom_file`, screenshots only)
- Collect screenshots + preprocessed DOM + metadata
- If acquisition returns STATUS: BLOCKED → stop entirely, report error, do NOT proceed to competitor
- Set source_mode in meta.json

**Step 2: Acquire competitor page** (if URL)
- Validate URL, dispatch acquisition agent (model: opus)
- Same viewport/device handling as Step 1
- Collect screenshots + preprocessed DOM + metadata
- If acquisition fails → note it, proceed with your page data only (comparison will be partial)

**File path inputs:** read directly, no acquisition needed.
</acquisition>

<dispatch>
1. Select clusters using page-type table (same as /cro:audit)
2. **Dispatch ALL auditors in parallel** (up to 6: 3 per page) using `model: "opus"`:
   - Each auditor gets: audit workflow, cluster references, ethics gate, **device context**
   - **URL mode:** pass sectioned screenshots + preprocessed DOM (segmented by cluster)
   - **File path mode:** pass source code directly
   - Your page auditors write findings for audit.md
   - Competitor page auditors write findings for audit-competitor.md
3. **Auditor retry:** if an auditor fails, retry once. If retry fails: "No data available for [cluster]"
4. After all auditors complete: dispatch compare workflow

**"Both" mode auditor dispatch:**
Run device batches sequentially to cap concurrency:
1. Desktop auditors (up to 6: 3 per page) with `device: "desktop"` → audit.md + audit-competitor.md
2. Mobile auditors (up to 6: 3 per page) with `device: "mobile"` → audit-mobile.md + audit-competitor-mobile.md
3. Write all audit files first, then update meta.json `devices_scanned` (atomicity)
4. Dispatch compare workflow twice: once for desktop findings, once for mobile findings

Dispatch compare.md workflow with:
- Both sets of findings (audit.md + audit-competitor.md) — or mobile variants for mobile pass
- Ethics gate content (explicitly — re-validate synthesized recommendations)
- Context from baton file
- **Device context** (`"desktop"` or `"mobile"`)
</dispatch>

<compare_workflow>
Read ${CLAUDE_PLUGIN_ROOT}/workflows/compare.md for comparison instructions.

The compare workflow produces:
- Side-by-side scores per domain
- Gap analysis: what competitor does better, what you do better
- Specific actionable items: "Competitor has X, you're missing it"
- Evidence tier badges on every finding: Gold (peer-reviewed RCT/meta-analysis), Silver (large-N observational or vendor A/B test), Bronze (expert consensus, small-N, or directional). Clickable citation URLs where available.
- Ethics check: if competitor uses a dark pattern, flag it: "Competitor uses [practice] — this violates [regulation]. Do not replicate. Ethical alternative: [Y]."

Write output to docs/cro/{engagement-id}/compare.md.
Also write audit.md and audit-competitor.md from auditor outputs.
Update meta.json: phase → "complete", updated → current ISO timestamp.
</compare_workflow>

<checkpoint>
## Comparison Complete

[Summary]

**Key highlights:**
- [Top gap or advantage 1]
- [Top gap or advantage 2]
- [Top gap or advantage 3]

**Options:**
1. Run full audit on your page (/cro:audit)
2. Generate visual comparison report
3. Adjust — change clusters or pages
4. Done

If --visual: generate visual report inline (see below).
If --auto: skip checkpoint, generate markdown report.

Then prompt for visual report (unless flagged):
"Want the visual comparison report? (1) Yes — annotated wireframe with findings (2) No, markdown is enough"

**Visual report generation (inline — no subagent dispatch):**
1. Read `${CLAUDE_PLUGIN_ROOT}/templates/visual-report.html.template`
2. Read `${CLAUDE_PLUGIN_ROOT}/workflows/visual-report.md` for generation instructions
3. Generate one visual report per page (your page + competitor), each with wireframe + findings
4. For "both" mode: generate per-device reports as well
Output: `docs/cro/{engagement-id}/visual-report.html` (your page) and `visual-report-competitor.html`
</checkpoint>

<ethics>
Pass ethics gate to ALL subagents including the compare workflow.
The compare workflow must re-validate synthesized gap recommendations against the ethics gate.
Ethics compliance section is mandatory in comparison output for both your page and the competitor page. Each page's findings must independently pass the ethics gate.
</ethics>
