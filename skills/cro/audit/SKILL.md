---
name: cro:audit
description: >-
  Runs a full CRO audit of an existing ecommerce page via four-phase relay
  (audit, plan, review, build). Covers product pages, checkout flows, carts,
  pricing, landing pages, and category pages using research-backed psychology.
disable-model-invocation: true
argument-hint: "[url-or-file-path] [--auto] [--force] [--min-priority critical|high|medium|low] [--platform shopify|nextjs] [--device desktop|mobile|both] [--visual] [--no-visual] [--ab-scaffold] [--engagement-id id]"
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
--device [desktop|mobile|both]: Target device viewport. Default: prompt user (URL mode only).
  - desktop: 1440×900, 1x DPR
  - mobile: 390×844 (iPhone 14 preset, includes DPR and user-agent)
  - both: Runs two separate acquisition/audit passes, produces audit.md (desktop) + audit-mobile.md (mobile)
  In --auto mode: defaults to "desktop" (no prompt).
</flags>

<mode_detection>
$ARGUMENTS must contain a URL or file path. If ambiguous, ask: "Are we auditing an existing page? Provide a URL or file path."

How to acquire page data:
1. **File path provided** → read directly. Set `source_mode: "file"` in meta.json. No acquisition agent needed.
2. **URL provided** → validate using rules in ${CLAUDE_PLUGIN_ROOT}/references/url-validation.md, then dispatch the acquisition agent:
   - Read ${CLAUDE_PLUGIN_ROOT}/workflows/acquire.md
   - Dispatch via Agent tool with `model: "sonnet"` — the acquisition agent is mechanical, not analytical
   - Pass the validated URL, viewport dimensions based on selected device, and device context:
     - Desktop: viewport 1440×900, device "desktop"
     - Mobile: viewport 390×844 (use device preset "iPhone 14"), device "mobile"
     - Both: dispatch twice serially:
       1. Desktop pass: full acquisition (DOM + screenshots) — viewport 1440×900, device "desktop"
       2. Mobile pass: pass `dom_file` from desktop acquisition, device "mobile" — screenshots only
   - Collect output: sectioned screenshots (3-6), preprocessed DOM, section metadata, style metadata
   - If acquisition returns `STATUS: BLOCKED` → present the reason to user, ask for file path or pasted code
   - If acquisition returns `STATUS: PARTIAL` → proceed with available data, note gaps at checkpoint
   - Set `source_mode: "url-dual"` in meta.json
3. **No agent-browser and no file path** → prompt user to paste code or provide file path. Set `source_mode: "file"` or `"description"`.
4. Never silently fail — always tell the user what is happening
</mode_detection>

<device_selection>
**URL mode only.** After mode detection, before engagement setup, prompt for device:

"Which device should I scan?
1. **Desktop** (1440×900) — default
2. **Mobile** (390×844, iPhone 14/15)
3. **Both** — produces two separate reports"

- If `--device` flag is set: use specified device, skip prompt.
- In `--auto` mode: default to `desktop`, skip prompt.
- For file path mode: skip device selection entirely (no viewport rendering).

Log selected device: "Scanning **[device]** at [width]×[height]."

Set `devices_requested` in meta.json to the user's choice: `["desktop"]`, `["mobile"]`, or `["desktop", "mobile"]`.
</device_selection>

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
3. Check if docs/cro/ is in .gitignore. If not, suggest adding it.
4. Detect legacy file: if docs/cro-action-plan.md exists, inform user it will be preserved but not used.
5. Write context.md (write-once, locked after this step)
6. Write meta.json with schema_version: 2, phase: "pending", source_mode from mode_detection

After writing meta.json, re-read it and verify all required fields are present:
- `id`: string, format YYYY-MM-DD-{8hex}
- `created`: ISO 8601 string
- `type`: one of [audit, build, quick-scan, compare]
- `phase`: one of [pending, audit, plan, review, build, complete]
- `platform`: one of [shopify, nextjs, generic]
- `page.type`: must match the page type table
- `clusters_used`: array of cluster slug strings
Optional: `blocked` (boolean), `quick_scan` (boolean), `compare_target` (object), `page.url`, `page.file_path`, `min_priority`, `source_mode`, `devices_requested`, `devices_scanned`, `plans_queue`, `reconciled`
If any required field is missing or invalid, fix it before proceeding.
Always update the `updated` field to the current ISO timestamp on every phase transition.
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
Dispatch 1-3 domain auditors IN PARALLEL using multiple Agent tool calls in a single message. Use `model: "opus"` for all auditor dispatches — Opus provides better reasoning for cross-referencing screenshots against DOM and applying device-appropriate principles.

Each Agent call contains:
- The audit workflow instructions (read from ${CLAUDE_PLUGIN_ROOT}/workflows/audit.md)
- Reference file paths for that cluster ONLY (at ${CLAUDE_PLUGIN_ROOT}/references/)
- Ethics gate content (read from ${CLAUDE_PLUGIN_ROOT}/references/ethics-gate.md)
- Min-priority filter if specified
- **Device context:** pass `"desktop"` or `"mobile"` to each auditor

**Input varies by source mode:**

- **URL mode (source_mode: url-dual):** Pass each auditor the sectioned screenshots AND the DOM file path from the acquisition agent (`docs/cro/{engagement-id}/dom.html`). **Segment by cluster:** use the `clusters` tags in the acquisition agent's section boundary metadata to determine which screenshots and DOM sections to pass to each auditor. Only pass an auditor the screenshots tagged with its cluster slug. The auditor reads the DOM file directly and focuses on sections relevant to its cluster. This reduces per-auditor context significantly.
- **File path mode (source_mode: file):** Pass the page source code directly. No screenshots.
- **Description mode (source_mode: description):** Pass the text description.

Collect all outputs. Verify each output ends with `STATUS: COMPLETE` or `STATUS: PARTIAL`.

**Single device (desktop or mobile):**
Write combined findings to docs/cro/{engagement-id}/audit.md.
Update meta.json: phase → "audit", `devices_scanned` → matches selected device, updated → current ISO timestamp.

**"Both" mode:**
Run auditor batches sequentially to cap concurrency at 3 simultaneous Opus subagents:
1. Dispatch desktop auditors (1 per cluster, up to 3 clusters in parallel) with `device: "desktop"` — collect findings
2. Wait for all desktop auditors to complete
3. Dispatch mobile auditors (1 per cluster, up to 3 clusters in parallel) with `device: "mobile"` — collect findings
Do NOT dispatch all 6 auditors at once — Opus rate limits make this unreliable.
4. Write `audit.md` (desktop findings) to disk
5. Write `audit-mobile.md` (mobile findings) to disk
6. **Then** update meta.json: phase → "audit", `devices_scanned: ["desktop", "mobile"]`, updated → current ISO timestamp
(Write files first, meta.json last — preserves atomicity invariant.)

**Partial failure in "both" mode:**
If one device's acquisition or audit fails, deliver the successful device's report + warning:
"⚠️ [Mobile/Desktop] scan failed: [reason]. Run with `--device [failed-device]` to retry."
Set `devices_scanned` to reflect only what completed. `devices_requested` preserves the original "both" intent.

**Plan phase with "both" mode:** The planner receives both `audit.md` and `audit-mobile.md` as input. Findings from both devices inform the action plan.

**Auditor retry:** If an auditor returns `STATUS: PARTIAL`, SKIP, or fails entirely: retry once automatically with the same inputs. If the retry also fails: write SKIP finding for that cluster, offer "Re-run [cluster]" at checkpoint.

If --min-priority set and zero findings remain after filter: "No findings at [PRIORITY] or above. Options: (1) Lower the filter, (2) View all findings, (3) Stop here."
</phase_audit>

<progress_comparison>
After writing audit.md but before presenting the checkpoint:

1. Determine if a previous engagement exists:
   a. If --engagement-id was provided, look up that engagement's audit.md directly
   b. Otherwise, scan docs/cro/*/meta.json for a matching url_normalized (exclude the current engagement and quick-scan engagements)
   c. If multiple matches, use the most recent by date
   d. If no match found, skip this section entirely
   e. **Device-aware matching:** Only compare same-device reports. Desktop `audit.md` compares to previous `audit.md`. Mobile `audit-mobile.md` compares to previous `audit-mobile.md`. If the previous engagement used a different viewport width (e.g., old 1280px vs new 1440px), skip comparison and note: "Previous scan used a different viewport width; comparison skipped."

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
Read ${CLAUDE_PLUGIN_ROOT}/references/multi-planner-protocol.md for the multi-planner protocol.

**Determine planner mode:**
Count findings by source cluster. If 3+ clusters each have 5+ findings → multi-planner mode. Otherwise → single planner.

**Single planner mode:**
Dispatch planner subagent with `model: "sonnet"`:
- Workflow instructions
- ALL audit findings (from docs/cro/{engagement-id}/audit.md)
- Context (from docs/cro/{engagement-id}/context.md)
- Ethics gate content
- Conflict resolution rules (from ${CLAUDE_PLUGIN_ROOT}/references/conflict-resolution.md)

Collect output. Write to docs/cro/{engagement-id}/plan.md.
Update meta.json: phase → "plan", updated → current ISO timestamp.

**Multi-planner mode:**
Follow ${CLAUDE_PLUGIN_ROOT}/references/multi-planner-protocol.md:
1. Group findings by source cluster
2. Dispatch parallel planners (model: sonnet), one per cluster
3. Write outputs to plan-{cluster-slug}.md
4. Dispatch reconciler (model: opus) with all PRDs
5. Write reconciliation.md, update amended PRD files
6. Update meta.json: phase → "plan", plans_queue populated, reconciled → true
</phase_plan>

<checkpoint_plan>
**Single planner mode:**
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

**Multi-planner mode:**
Follow the checkpoint format in ${CLAUDE_PLUGIN_ROOT}/references/multi-planner-protocol.md:
- Show PRD summary per cluster with step counts and priority breakdowns
- Note reconciler results if conflicts were resolved
- Offer: Build all sequentially / Pick one / Deepen a plan / Save and resume
- If --auto: select "Build all in recommended priority order", skip checkpoint
- Sequential review/build follows the protocol in multi-planner-protocol.md
</checkpoint_plan>

<phase_review>
Read ${CLAUDE_PLUGIN_ROOT}/workflows/review.md for reviewer instructions.
Read ${CLAUDE_PLUGIN_ROOT}/references/relay-loop-protocol.md for the relay loop protocol.

**Relay loop dispatch:**

1. Generate a nonce: `openssl rand -hex 4`
2. Dispatch reviewer subagent with `model: "opus"`:
   - Workflow instructions
   - Context, audit findings, and action plan from baton files
   - Ethics gate content
   - Verification checklist (from ${CLAUDE_PLUGIN_ROOT}/references/verification-checklist.md)
   - The nonce
   - Auto mode flag (true if --auto)
   - Previous Q&A pairs (empty on first dispatch)
3. Collect output. Parse for `QUESTION__{nonce}:` lines and `VERDICT__{nonce}:` line.
4. **Conditional relay:** If QUESTION lines found AND not --auto:
   - Present questions to user (numbered, with options from JSON)
   - Collect answers
   - Re-dispatch reviewer with: original inputs + Q&A pairs only (not full previous output) + same nonce
   - Max 3 total dispatches. After 3rd, present unresolved questions + best-effort verdict to user.
5. If no QUESTION lines (or --auto): use the verdict as-is.
6. Write review notes to docs/cro/{engagement-id}/review.md.
7. Update meta.json: phase → "review", updated → current ISO timestamp.
</phase_review>

<checkpoint_review>
## Review Complete

[Summary including verdict: APPROVE, REVISE, or BLOCK]

**Options:**
1. Proceed to build
2. Adjust plan based on review
3. Go back to planning
4. Deepen plan — add more detail to weak steps
5. Export report
6. Save here and resume later

If --auto: always select option 1 (proceed to build). Options 4, 5, 6 are interactive-only.

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
Read ${CLAUDE_PLUGIN_ROOT}/references/relay-loop-protocol.md for the relay loop protocol.

If platform detected, also load ${CLAUDE_PLUGIN_ROOT}/platforms/{platform}.md.

**Pre-build safety (--auto mode only):**
If `--auto` and project is a git repo: run `git status --porcelain`. If output is non-empty, abort: "Build requires clean git state in --auto mode. Commit or stash your changes first."

**Relay loop dispatch:**

1. Generate a nonce: `openssl rand -hex 4`
2. Dispatch builder subagent with `model: "sonnet"`:
   - Workflow instructions
   - Action plan and review notes from baton files
   - Platform reference (if applicable)
   - Context from baton file
   - The nonce
   - Auto mode flag
   - Previous Q&A pairs (empty on first dispatch)
3. Collect output. Parse for `QUESTION__{nonce}:` lines.
4. **Conditional relay:** If QUESTION lines found AND not --auto:
   - Present questions to user (Stuck/Ethics decisions with options)
   - Collect answers
   - Re-dispatch builder with: original inputs + Q&A pairs only + same nonce
   - Max 3 total dispatches.
5. If no QUESTION lines (or --auto): use the build output as-is.
6. Write to docs/cro/{engagement-id}/build-log.md.
7. Update meta.json: phase → "build", updated → current ISO timestamp.

If source_mode is "url-dual" and no local source code is available: skip build, present recommendations only.
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

**Atomicity order: delete files FIRST, then update meta.json.** If deletion fails partway, meta.json still reflects the previous (correct) phase. Resume can detect and self-heal from inconsistent state.

**Single-planner mode:**
1. Delete downstream phase files (e.g., going back to audit deletes plan.md, review.md, build-log.md)
2. Update meta.json: phase → target phase, updated → current ISO timestamp
3. If builder has modified files: warn user about code divergence, suggest git restore
4. Re-dispatch target phase with fresh agents

**Multi-planner mode:**
- Going back on active PRD: delete only that PRD's downstream files (review-{slug}.md, build-log-{slug}.md). Verify file paths are children of the engagement directory before deletion. Reset that entry's phase in plans_queue.
- Going back to audit: delete ALL plan-*.md, review-*.md, build-log-*.md, and reconciliation.md. Reset plans_queue to empty. Update meta.json phase.
- See ${CLAUDE_PLUGIN_ROOT}/references/multi-planner-protocol.md for details.

**Invariant:** If meta.json phase and file existence disagree, file existence wins. This is how resume self-heals.
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
