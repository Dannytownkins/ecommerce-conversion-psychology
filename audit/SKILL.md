---
name: audit
description: >-
  Runs a full CRO audit of an existing ecommerce page via four-phase relay
  (audit, plan, review, build). Covers product pages, checkout flows, carts,
  pricing, landing pages, and category pages using research-backed psychology.
disable-model-invocation: true
argument-hint: "[url-or-file-path] [--auto] [--force] [--min-priority critical|high|medium|low] [--platform shopify|nextjs] [--export-report] [--ab-scaffold] [--engagement-id id]"
---

<objective>
Run a four-phase CRO relay (audit, plan, review, build) on an existing ecommerce page. You are the coordinator — you orchestrate phases, present checkpoints, and write baton files. Subagents never write files.
</objective>

<flags>
--auto: Skip all checkpoint pauses. Deterministic path: audit → plan → review → build → done. Abort with error if interactive input required. Halts on BLOCK verdict unless --force is also set.
--force: Override BLOCK verdicts in --auto mode. No effect without --auto.
--min-priority [level]: Filter findings. Scale: critical > high > medium > low. Always include CRITICAL regardless.
--platform [name]: Skip platform detection. Values: shopify, nextjs, generic.
--export-report: Generate HTML report after final phase (or current phase if stopping early).
--ab-scaffold: Generate A/B test scaffold after plan phase. Pair with --ab-tool [tool] to specify existing tool.
--engagement-id [id]: Resume or target a specific past engagement instead of creating new.
</flags>

<mode_detection>
$ARGUMENTS must contain a URL or file path. If ambiguous, ask: "Are we auditing an existing page? Provide a URL or file path."

How to acquire page code:
1. File path provided → read directly
2. URL provided → ask: "Do you have the source code locally? Provide the file path, or I can use agent-browser to capture the page visually."
3. agent-browser available → screenshot mode (visual audit, no build phase)
4. agent-browser unavailable → prompt user to paste code or provide file path
5. Never silently fail — always tell the user what is happening

For URLs: validate using rules in ${CLAUDE_PLUGIN_ROOT}/references/url-validation.md before any agent-browser fetch.
</mode_detection>

<progress_memory>
Before dispatching auditors:
1. Normalize input URL (strip protocol, www, trailing slash, query params, fragments; lowercase)
2. Scan docs/cro/*/meta.json for matching url_normalized
3. Filter out quick-scan engagements
4. If match found, read previous audit.md for comparison after current audit completes
5. After audit: diff findings by SECTION slug. Present: "Compared to [date]: X resolved, Y new, Z regressions"
6. If no match, skip silently
</progress_memory>

<engagement_setup>
1. Generate engagement ID: YYYY-MM-DD-{8-hex} via `openssl rand -hex 4` (fallback: `python -c "import secrets; print(secrets.token_hex(4))"`)
2. Create directory: docs/cro/{engagement-id}/
3. On first engagement ever: check if docs/cro/ is in .gitignore. If not, suggest adding it.
4. Detect legacy file: if docs/cro-action-plan.md exists, inform user it will be preserved but not used.
5. Write context.md (write-once, locked after this step)
6. Write meta.json with schema_version: 1, phase: "pending"

After writing meta.json, re-read it and verify all required fields are present:
- `id`: string, format YYYY-MM-DD-{8hex}
- `created`: ISO 8601 string
- `type`: one of [audit, build, quick-scan, compare]
- `phase`: one of [pending, audit, plan, review, build, complete]
- `platform`: one of [shopify, nextjs, generic]
- `page.type`: must match the page type table
- `clusters_used`: array of cluster slug strings
Optional: `blocked` (boolean), `quick_scan` (boolean), `compare_target` (object), `page.url`, `page.file_path`, `min_priority`
If any required field is missing or invalid, fix it before proceeding.
</engagement_setup>

<platform_detection>
Load and follow ${CLAUDE_PLUGIN_ROOT}/references/platform-detection.md for heuristics.
Accept --platform flag to skip detection.
</platform_detection>

<domain_cluster_routing>
Select 1-3 clusters based on page type:

| Page Type | Cluster 1 | Cluster 2 | Cluster 3 |
|-----------|-----------|-----------|-----------|
| Product page | visual-cta | trust-conversion | context-platform |
| Cart | trust-conversion | visual-cta | — |
| Checkout | trust-conversion | context-platform | — |
| Homepage | visual-cta | trust-conversion | — |
| Category/Collection | visual-cta | trust-conversion | context-platform |
| Landing page | visual-cta | trust-conversion | — |
| Pricing/Plans | trust-conversion | visual-cta | — |
| Post-purchase | audience-journey | trust-conversion | — |

Cluster reference files:
- visual-cta: cta-design-and-placement.md, color-psychology.md, eye-tracking-and-scan-patterns.md
- trust-conversion: trust-and-credibility.md, social-proof-patterns.md, checkout-optimization.md, pricing-psychology.md, biometric-and-express-checkout.md, cookie-consent-and-compliance.md
- context-platform: cognitive-load-management.md, mobile-conversion.md, page-performance-psychology.md, search-and-filter-ux.md
- audience-journey: personalization-psychology.md, cross-cultural-considerations.md, post-purchase-psychology.md, social-commerce-psychology.md

Override rules:
- Non-Western market → add audience-journey
- Significant price display → ensure trust-conversion
- Mobile-first → ensure context-platform
</domain_cluster_routing>

<phase_audit>
Dispatch 1-3 domain auditors IN PARALLEL using multiple Agent tool calls in a single message.

Each Agent call contains:
- The audit workflow instructions (read from ${CLAUDE_PLUGIN_ROOT}/workflows/audit.md)
- Reference file paths for that cluster ONLY (at ${CLAUDE_PLUGIN_ROOT}/references/)
- The page code or screenshots
- Ethics gate content (read from ${CLAUDE_PLUGIN_ROOT}/references/ethics-gate.md)
- Min-priority filter if specified

Collect all outputs. Write combined findings to docs/cro/{engagement-id}/audit.md.
Update meta.json: phase → "audit".

If an auditor fails: write SKIP finding for that cluster, inform user at checkpoint.

If --min-priority set and zero findings remain after filter: "No findings at [PRIORITY] or above. Options: (1) Lower the filter, (2) View all findings, (3) Stop here."
</phase_audit>

<progress_comparison>
After writing audit.md but before presenting the checkpoint:

1. Determine if a previous engagement exists:
   a. If --engagement-id was provided, look up that engagement's audit.md directly
   b. Otherwise, scan docs/cro/*/meta.json for a matching url_normalized (exclude the current engagement and quick-scan engagements)
   c. If multiple matches, use the most recent by date
   d. If no match found, skip this section entirely

2. Read the previous engagement's audit.md. Parse each finding block, extracting:
   - SECTION slug (the canonical slug)
   - FINDING verdict (PASS, FAIL, PARTIAL, SKIP)

3. Parse the current audit.md the same way.

4. Compare by SECTION slug and classify each:
   - FIXED: was FAIL or PARTIAL in previous, now PASS in current
   - REGRESSED: was PASS in previous, now FAIL or PARTIAL in current
   - UNCHANGED: same verdict in both
   - NEW: present in current but not in previous
   - RESOLVED: present in previous but not in current

5. Append a `## Progress Comparison` section to the current engagement's audit.md:

```markdown
## Progress Comparison

Compared against engagement `{previous-id}` ({date}).

| Section | Previous | Current | Status |
|---------|----------|---------|--------|
| {slug} | {verdict} | {verdict} | {status} |

Summary: X FIXED, Y REGRESSED, Z UNCHANGED, W NEW, V RESOLVED
```

6. Use the summary counts when presenting the checkpoint message.
</progress_comparison>

<checkpoint_audit>
Present natural language summary (not raw tables):

## Audit Complete

[2-3 sentence summary]

**Key highlights:**
- [Top finding 1]
- [Top finding 2]
- [Top finding 3]

[If progress memory found previous: "Compared to your last audit on [date]: X resolved, Y new, Z regressions"]

**Options:**
1. Proceed to planning
2. Adjust — tell me what to change
3. Export report
4. Stop here

If --auto: skip this checkpoint, proceed to plan.
Wait for user response before proceeding.
</checkpoint_audit>

<phase_plan>
Read ${CLAUDE_PLUGIN_ROOT}/workflows/plan.md for planner instructions.

Dispatch planner subagent with:
- Workflow instructions
- Audit findings (from docs/cro/{engagement-id}/audit.md)
- Context (from docs/cro/{engagement-id}/context.md)
- Ethics gate content
- Conflict resolution rules (from ${CLAUDE_PLUGIN_ROOT}/references/conflict-resolution.md)

Collect output. Write to docs/cro/{engagement-id}/plan.md.
Update meta.json: phase → "plan".
</phase_plan>

<checkpoint_plan>
## Plan Complete

[Summary]

**Options:**
1. Proceed to review
2. Adjust — tell me what to change
3. Go back to audit
4. Generate A/B test scaffold
5. Export report
6. Stop here

If --auto: skip checkpoint, proceed to review. If --ab-scaffold: generate scaffold after writing plan.
</checkpoint_plan>

<phase_review>
Read ${CLAUDE_PLUGIN_ROOT}/workflows/review.md for reviewer instructions.

Dispatch reviewer subagent with:
- Workflow instructions
- Context, audit findings, and action plan from baton files
- Ethics gate content
- Verification checklist (from ${CLAUDE_PLUGIN_ROOT}/references/verification-checklist.md)

Collect output. Write to docs/cro/{engagement-id}/review.md.
Update meta.json: phase → "review".
</phase_review>

<checkpoint_review>
## Review Complete

[Summary including verdict: APPROVE, REVISE, or BLOCK]

**Options:**
1. Proceed to build
2. Adjust plan based on review
3. Go back to planning
4. Export report
5. Stop here

If --auto (without --force):
- If verdict is APPROVE or REVISE: proceed to build.
- If verdict is BLOCK: write `blocked: true` to meta.json, print "Review BLOCKED: {reason}. Use --auto --force to override.", and STOP. Do not proceed to build.

If --auto AND --force:
- If verdict is BLOCK: print "WARNING: Review BLOCK overridden by --force. Reason was: {reason}", write `blocked: false` to meta.json, proceed to build.
</checkpoint_review>

<pre_build_snapshot>
Before dispatching the builder:
1. Check if project is a git repo. If not, skip.
2. If no uncommitted changes: "Current HEAD is your restore point."
3. If uncommitted changes: suggest `git stash push -m "pre-cro-build-{engagement-id}"`
4. Verify git exit code. If fails, warn and ask whether to proceed without snapshot.
5. Tell user: "Created snapshot. Restore with `git stash apply` if needed."

Skip entirely if not a git repo.
</pre_build_snapshot>

<phase_build>
Read ${CLAUDE_PLUGIN_ROOT}/workflows/build.md for builder instructions.

If platform detected, also load ${CLAUDE_PLUGIN_ROOT}/platforms/{platform}.md.

Dispatch builder subagent with:
- Workflow instructions
- Action plan and review notes from baton files
- Platform reference (if applicable)
- Context from baton file

Collect output. Write to docs/cro/{engagement-id}/build-log.md.
Update meta.json: phase → "build".

If screenshot mode: skip build, present recommendations only.
</phase_build>

<checkpoint_build>
## Build Complete

[Summary of what was built]

**Options:**
1. Export report
2. Generate A/B test scaffold
3. Go back to review
4. Done

If --auto and --export-report: generate report. Otherwise present summary and done.
Update meta.json: phase → "complete".
</checkpoint_build>

<go_back_protocol>
When user chooses to go back:
1. Write updated meta.json to temp file, rename over original (atomic replace)
2. Delete downstream phase files (e.g., going back to audit deletes plan.md, review.md, build-log.md)
3. If builder has modified files: warn user about code divergence, suggest git restore
4. Re-dispatch target phase with fresh agents
</go_back_protocol>

<report_export>
Available at any checkpoint or via --export-report flag.
Read ${CLAUDE_PLUGIN_ROOT}/workflows/report.md for report generator instructions.
Dispatch report subagent with all baton files from the engagement directory.
Output: docs/cro/{engagement-id}/report.html
</report_export>

<ab_scaffold>
Available at plan checkpoint or via --ab-scaffold flag.
Read ${CLAUDE_PLUGIN_ROOT}/workflows/ab-scaffold.md for scaffold generator instructions.
Dispatch scaffold subagent with action plan from baton file.
If --ab-tool specified, scaffold for that tool.
Output: docs/cro/{engagement-id}/ab-scaffold.md
</ab_scaffold>

<ethics>
Read ethics gate from ${CLAUDE_PLUGIN_ROOT}/references/ethics-gate.md.
Pass full content to EVERY subagent dispatch. Ethics violations are always PRIORITY: CRITICAL.
</ethics>

<reference_freshness>
Each reference file has a RESEARCH_DATE watermark. If older than 12 months, warn at checkpoint.
</reference_freshness>
