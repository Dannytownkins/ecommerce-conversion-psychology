---
name: cro:compare
description: >-
  Compares an ecommerce page against a competitor page. Runs 1:1 same-type
  comparison with side-by-side scoring and gap analysis. Supports URLs
  (via agent-browser) and local file paths.
disable-model-invocation: true
argument-hint: "[your-url-or-path] [competitor-url-or-path] [--visual] [--no-visual] [--engagement-id id]"
---

<objective>
Compare your ecommerce page against a competitor's page. 1:1 same-type comparison with side-by-side scoring, gap analysis, and actionable recommendations.
</objective>

<flags>
--visual: Auto-generate visual comparison report (side-by-side annotated screenshots).
--no-visual: Skip visual report prompt, markdown only.
--engagement-id [id]: Target a specific past engagement.
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

<page_type_validation>
Determine page type for both pages.
If types differ: "These appear to be different page types ([type-a] vs [type-b]). Compare anyway, or provide matching pages?"
If --auto and types differ: proceed with comparison despite mismatch, note it in output.
If user proceeds despite mismatch, note it in the comparison output.
</page_type_validation>

<engagement_setup>
Same as /cro:audit but with type: "compare", schema_version: 2 in meta.json.
Store compare_target URL/path in meta.json.

After writing meta.json, re-read it and verify all required fields are present:
- `id`: string, format YYYY-MM-DD-{8hex}
- `created`: ISO 8601 string
- `type`: one of [audit, build, quick-scan, compare]
- `phase`: one of [pending, audit, plan, review, build, complete]
- `platform`: one of [shopify, nextjs, generic]
- `page.type`: must match the page type table
- `clusters_used`: array of cluster slug strings
Optional: `blocked`, `quick_scan`, `compare_target`, `page.url`, `page.file_path`, `min_priority`, `source_mode`, `plans_queue`, `reconciled`
If any required field is missing or invalid, fix it before proceeding.
Always update the `updated` field to current ISO timestamp on phase transitions.

Check if docs/cro/ is in .gitignore. If not, suggest adding it.
</engagement_setup>

<acquisition>
**Serialize acquisition, then parallelize auditors:**

**Step 1: Acquire your page** (if URL)
- Validate URL, dispatch acquisition agent (model: haiku) with ${CLAUDE_PLUGIN_ROOT}/workflows/acquire.md
- Collect screenshots + preprocessed DOM + metadata
- If acquisition returns STATUS: BLOCKED → stop entirely, report error, do NOT proceed to competitor
- Set source_mode in meta.json

**Step 2: Acquire competitor page** (if URL)
- Validate URL, dispatch acquisition agent (model: haiku)
- Collect screenshots + preprocessed DOM + metadata
- If acquisition fails → note it, proceed with your page data only (comparison will be partial)

**File path inputs:** read directly, no acquisition needed.
</acquisition>

<dispatch>
1. Select clusters using page-type table (same as /cro:audit)
2. **Dispatch ALL auditors in parallel** (up to 6: 3 per page) using `model: "sonnet"`:
   - Each auditor gets: audit workflow, cluster references, ethics gate
   - **URL mode:** pass sectioned screenshots + preprocessed DOM (segmented by cluster)
   - **File path mode:** pass source code directly
   - Your page auditors write findings for audit.md
   - Competitor page auditors write findings for audit-competitor.md
3. **Auditor retry:** if an auditor fails, retry once. If retry fails: "No data available for [cluster]"
4. After all auditors complete: dispatch compare workflow

Dispatch compare.md workflow with:
- Both sets of findings (audit.md + audit-competitor.md)
- Ethics gate content (explicitly — re-validate synthesized recommendations)
- Context from baton file
</dispatch>

<compare_workflow>
Read ${CLAUDE_PLUGIN_ROOT}/workflows/compare.md for comparison instructions.

The compare workflow produces:
- Side-by-side scores per domain
- Gap analysis: what competitor does better, what you do better
- Specific actionable items: "Competitor has X, you're missing it"
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

If --visual: generate visual report automatically.
If --auto: skip checkpoint, generate markdown report.

Then prompt for visual report (unless flagged):
"Want the visual comparison report? (1) Yes — side-by-side annotated screenshots (2) No, markdown is enough"
</checkpoint>

<ethics>
Pass ethics gate to ALL subagents including the compare workflow.
The compare workflow must re-validate synthesized gap recommendations against the ethics gate.
</ethics>
