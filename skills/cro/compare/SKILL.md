---
name: compare
description: >-
  Compares an ecommerce page against a competitor page. Runs 1:1 same-type
  comparison with side-by-side scoring and gap analysis. Supports URLs
  (via agent-browser) and local file paths.
disable-model-invocation: true
argument-hint: "[your-url-or-path] [competitor-url-or-path] [--export-report] [--engagement-id id]"
---

<objective>
Compare your ecommerce page against a competitor's page. 1:1 same-type comparison with side-by-side scoring, gap analysis, and actionable recommendations.
</objective>

<flags>
--export-report: Generate HTML comparison report automatically.
--engagement-id [id]: Target a specific past engagement.
</flags>

<intake>
Accept both inputs as arguments: /cro:compare [your-url-or-path] [competitor-url-or-path]

Supports:
- Two URLs (via agent-browser for screenshots)
- Two local file paths (direct read — preferred when available)
- Mixed (one URL, one file path)

If only one provided, ask for the other.
For URLs: validate using ${CLAUDE_PLUGIN_ROOT}/references/url-validation.md before fetching.
</intake>

<page_type_validation>
Determine page type for both pages.
If types differ: "These appear to be different page types ([type-a] vs [type-b]). Compare anyway, or provide matching pages?"
If user proceeds despite mismatch, note it in the comparison output.
</page_type_validation>

<engagement_setup>
Same as /cro:audit but with type: "compare" in meta.json.
Store compare_target URL/path in meta.json.
</engagement_setup>

<dispatch>
1. Select clusters using page-type table (same as /cro:audit)
2. Dispatch ALL auditors in parallel (up to 6: 3 per page)
   - Each auditor gets: audit workflow, cluster references, page code/screenshots, ethics gate
   - Your page auditors write findings for audit.md
   - Competitor page auditors write findings for audit-competitor.md
3. Handle partial failure: a failed cluster produces "No data available for [cluster]"
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
Update meta.json: phase → "complete".
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
2. Export comparison report
3. Adjust — change clusters or pages
4. Done

If --export-report: generate report automatically.
</checkpoint>

<ethics>
Pass ethics gate to ALL subagents including the compare workflow.
The compare workflow must re-validate synthesized gap recommendations against the ethics gate.
</ethics>
