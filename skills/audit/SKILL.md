---
name: cro:audit
description: >-
  Runs a full CRO audit on an existing ecommerce page via four-phase relay
  (audit, plan, review, build). Use when the user provides a URL or file path
  and wants a comprehensive conversion analysis with actionable recommendations.
disable-model-invocation: true
argument-hint: "[url-or-file-path] [--auto] [--force] [--min-priority critical|high|medium|low] [--platform shopify|nextjs] [--device mobile|laptop|desktop] [--clusters cluster1,cluster2] [--visual] [--no-visual] [--ab-scaffold] [--engagement-id id]"
---

<objective>
Run a four-phase CRO relay (audit, plan, review, build) on an existing ecommerce page. You are the coordinator — you orchestrate phases, present checkpoints, and write baton files. Auditor, planner, reviewer, and builder subagents never write files — only the coordinator writes their output. **Exception:** the acquisition agent (dispatched to capture page screenshots and DOM) DOES write files directly (baton.json, dom.html, screenshots). After an acquisition agent returns, always verify its files exist on disk before proceeding.
</objective>

<flags>
--auto: Skip all checkpoint pauses. Deterministic path: audit → plan → review → build → done. Abort with error if interactive input required. Halts on BLOCK verdict unless --force is also set.
--force: Override BLOCK verdicts in --auto mode. No effect without --auto.
--min-priority [level]: Filter findings. Scale: critical > high > medium > low. Always include CRITICAL regardless.
--platform [name]: Skip platform detection. Values: shopify, nextjs, generic.
--export-report: Generate HTML report after final phase (or current phase if stopping early).
--ab-scaffold: Generate A/B test scaffold after plan phase. Pair with --ab-tool [tool] to specify existing tool.
--engagement-id [id]: Resume or target a specific past engagement instead of creating new.
--device [device(s)]: Target device viewport(s). Default: prompt user (URL mode only).
  - mobile: 390×844, 3x DPR (via `agent-browser close` + `agent-browser set device "iPhone 14"`)
  - laptop: 1440×900, 1x DPR
  - desktop: 1920×1080, 1x DPR
  Accepts comma-separated pairs (e.g., --device mobile,desktop). Max 2 per run.
  In --auto mode: defaults to "mobile,laptop" (no prompt).
--clusters [cluster1,cluster2,...]: Explicit cluster selection, overrides page type defaults. Values: visual-cta, trust-conversion, context-platform, audience-journey.
</flags>

<mode_detection>
$ARGUMENTS must contain a URL or file path. If ambiguous, ask: "Are we auditing an existing page? Provide a URL or file path."

How to acquire page data:
1. **File path provided** → read directly. Set `source_mode: "file"` in meta.json. No acquisition agent needed.
2. **URL provided** → validate using rules in ${CLAUDE_PLUGIN_ROOT}/references/url-validation.md.
2b. **User confirmation (URL mode only, non-auto):** Before dispatching the acquisition agent, ask: 'About to fetch **{domain}** — proceed?' Wait for user confirmation. In `--auto` mode, skip this step.
   Then dispatch the acquisition agent:
   - Read ${CLAUDE_PLUGIN_ROOT}/workflows/acquire.md
   - Dispatch via Agent tool with `model: "opus"`
   - **Compute the absolute engagement directory path** (e.g., `/c/Users/.../docs/cro/{engagement-id}/`) and pass it as `ENGAGEMENT_DIR` to every acquisition agent. Acquisition agents MUST use this absolute path for all file writes.
   - Pass the validated URL, viewport dimensions based on selected device, and device context:
     - Mobile: device "mobile" (acquire.md uses `agent-browser close` + `agent-browser set device "iPhone 14"` for 3x DPR)
     - Laptop: viewport 1440×900, device "laptop"
     - Desktop: viewport 1920×1080, device "desktop"
     - Two devices: dispatch BOTH acquisition agents in parallel using named sessions (`--session mobile`, `--session desktop`). Each agent gets its own browser instance with independent viewport and extracts its own DOM independently.
       1. First agent: full acquisition (DOM + screenshots + element coordinates) with `--session {first_device}`.
       2. Second agent: full acquisition (DOM + screenshots + element coordinates) with `--session {second_device}`.
       Both agents extract DOM independently. DOM is viewport-independent so the content is identical — the redundant extraction is cheap compared to the parallelism gained (cuts wall time in half). Each agent writes a device-specific DOM filename (`dom.html` for desktop/laptop, `dom-mobile.html` for mobile) to avoid file collisions.
       Note: if one agent needs mobile DPR (`set device "iPhone 14"`), its `agent-browser close` + `set device` only affects its own session — no conflict with the other agent's session.
   - Collect output: sectioned screenshots (1-6), preprocessed DOM, section metadata, style metadata, baton.json
   - **Post-acquisition file verification (mandatory):** After the acquisition agent returns, verify files actually exist on disk before reading them. Run `ls {ENGAGEMENT_DIR}` (the absolute engagement directory path) and check for baton.json (or baton-mobile.json), the device-specific DOM file (`dom.html` for desktop/laptop, `dom-mobile.html` for mobile), and at least 1 screenshot file. Acquisition agents sometimes report STATUS: COMPLETE but fail to write files (working directory mismatch). If files are missing, immediately fall back to manual acquisition — do not re-dispatch the subagent.
   - After file verification passes, read `docs/cro/{engagement-id}/baton.json` to verify `status: "COMPLETE"`. If missing or incomplete, warn and proceed with available data.
   - If acquisition returns `STATUS: BLOCKED` → present the reason to user, ask for file path or pasted code
   - If acquisition returns `STATUS: PARTIAL` → proceed with available data, note gaps at checkpoint
   - Set `source_mode: "url-dual"` in meta.json
3. **Acquisition agent fails entirely** (or reports COMPLETE but files are missing on disk) → fall back to manual acquisition (see below). Set `source_mode: "manual"`.
4. **No agent-browser and no file path** → fall back to WebFetch for page content. Set `source_mode: "webfetch"`.
5. Never silently fail — always tell the user what is happening

**Manual acquisition fallback:**
If the acquisition agent fails (crashes, returns malformed output, or produces a baton.json with `screenshots: []`):
1. **Delete the failed agent's stale baton.json (or baton-mobile.json) and DOM file (dom.html or dom-mobile.html)** — downstream agents will misread partial/empty data as real acquisition output if left in place.
2. The coordinator captures the page directly using Bash commands:
   ```
   agent-browser set viewport 1440 900
   agent-browser goto "{url}"
   agent-browser wait 3000
   agent-browser screenshot "docs/cro/{engagement-id}/section-1.jpg"
   ```
   For subsequent sections, scroll using JS eval (NOT `agent-browser scroll` which fails silently on many themes):
   ```
   agent-browser eval "window.scrollTo({top: 700, behavior: 'instant'}); window.scrollY"
   agent-browser wait 500
   agent-browser screenshot "docs/cro/{engagement-id}/section-2.jpg"
   ```
   Always verify the returned scrollY matches the target. If it returns 0 or the wrong value, retry with `behavior: 'instant'`.
3. Extract DOM: `agent-browser eval "document.documentElement.outerHTML"` and write to `dom.html`
4. **Extract element coordinates** at each scroll position using the JS snippet from acquire.md Step 3b via `agent-browser eval`. This gives real `getBoundingClientRect()` coordinates even in manual mode.
5. Write a valid `baton.json` with `source_mode: "manual"` and `status: "COMPLETE"`
6. Set `source_mode: "manual"` in meta.json
7. Proceed to audit phase normally

**WebFetch fallback (no agent-browser available):**
If agent-browser is not installed and the input is a URL:
1. Fetch page content via WebFetch
2. Write response to `dom.html` (note: this is source HTML, not rendered DOM)
3. Write baton.json with `source_mode: "webfetch"`, `screenshots: []`, `status: "COMPLETE"`
4. Set `source_mode: "webfetch"` in meta.json — auditors will know they have no screenshots and no computed styles
5. Proceed to audit with CODE-only findings (no VISUAL source possible)
</mode_detection>

<device_selection>
**URL mode only.** After mode detection, before engagement setup, prompt for device:

"Which devices should I scan?
1. **Mobile** (390×844, 3x DPR)
2. **Laptop** (1440×900)
3. **Desktop** (1920×1080)

Select up to two (e.g., 1,2). Scanning two devices runs both viewports sequentially."

- If `--device` flag is set: use specified device(s), skip prompt. Accepts: `mobile`, `laptop`, `desktop`, or comma-separated pairs (e.g., `--device mobile,desktop`).
- In `--auto` mode: default to `mobile,laptop`, skip prompt.
- For file path mode: skip device selection entirely (no viewport rendering).

Log selected device(s): "Scanning **[device]** at [width]×[height]."

Set `devices_requested` in meta.json to the user's choice (e.g., `["mobile", "laptop"]`).
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

**meta.json schema:** See ${CLAUDE_PLUGIN_ROOT}/references/meta-schema.md. Validate on resume only — not after writing.

Always update the `updated` field to the current ISO timestamp on every phase transition.
</engagement_setup>

<platform_detection>
Load and follow ${CLAUDE_PLUGIN_ROOT}/references/platform-detection.md for heuristics.
Accept --platform flag to skip detection.
</platform_detection>

<page_type_detection>
Detect page type from URL patterns and DOM signals:
- `/products/` or `/product/` → product
- `/cart` → cart
- `/checkout` → checkout
- `/collections/` or `/category/` → category
- Root path `/` with no product/collection path → homepage
- `/pages/` with pricing keywords → landing or pricing
- Ambiguous → check DOM: `form[action*='cart']` → product, `[class*='checkout']` → checkout
- Still ambiguous → ask the user.

Set `page.type` in meta.json. This determines cluster routing via the domain_cluster_routing table.
</page_type_detection>

<page_pattern_detection>
After acquisition completes and baton is validated, check for configurator patterns in the DOM:

1. Look for: multiple required `<select>` elements with empty/placeholder defaults, a disabled CTA button (`disabled` attribute, class containing `disabled`), dynamic price elements, validation messages requiring selections before purchase
2. Also check for: `[class*='fitment']`, `[class*='compatibility']`, `[class*='configurator']`, `[class*='vehicle']`, `[class*='year-make-model']`
3. If ≥2 required selects exist above the primary CTA AND the CTA is disabled in default state, classify as `page_pattern: 'configurator'`

If detected:
- Set `page_pattern: "configurator"` in meta.json
- Include `page_pattern: "configurator"` in every auditor dispatch (the auditor workflow has instructions for how to adjust evaluation — see workflows/audit.md "Configurator Page Context")
- This changes how auditors evaluate CTA visibility and price placement — they assess configurator UX quality rather than flagging gated CTAs as missing

If not detected, omit `page_pattern` from meta.json. Auditors will evaluate normally.
</page_pattern_detection>

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
- visual-cta: cta-design-and-placement.md, color-psychology.md, eye-tracking-and-scan-patterns.md, competitive-positioning.md
- trust-conversion: trust-and-credibility.md, social-proof-patterns.md, checkout-optimization.md, pricing-psychology.md, biometric-and-express-checkout.md, cookie-consent-and-compliance.md, competitive-positioning.md
- context-platform: cognitive-load-management.md, mobile-conversion.md, page-performance-psychology.md, search-and-filter-ux.md
- audience-journey: personalization-psychology.md, cross-cultural-considerations.md, post-purchase-psychology.md, social-commerce-psychology.md

Override rules:
- Non-Western market → add audience-journey
- Significant price display → ensure trust-conversion
- Mobile-first → ensure context-platform
</domain_cluster_routing>

<cluster_selection>
**After page type detection determines default clusters, present to the user:**

"Detected page type: {page_type}

Clusters selected for this audit:
{numbered list of selected clusters with descriptions}

Not selected:
{numbered list of unselected clusters with descriptions}

Proceed, or add/remove clusters? (e.g., 'remove 1' or 'add 4')"

Cluster descriptions:
- visual-cta: layout, visual hierarchy, scan patterns, CTA design and placement
- trust-conversion: reviews, pricing, social proof, trust signals, checkout
- context-platform: cognitive load, search/filter UX, page performance
- audience-journey: personalization, cross-cultural, post-purchase psychology

- In `--auto` mode: skip prompt, use default routing from page type table.
- `--clusters` flag: explicit cluster selection (e.g., `--clusters trust-conversion,context-platform`). Overrides page type defaults.
- Update `clusters_used` in meta.json to reflect the user's final selection.
- Removing a cluster reduces auditor count (and cost/time). Adding one increases it.
</cluster_selection>

<auditor_dispatch_template>
When dispatching an auditor, assemble the prompt as follows:

---
You are a CRO domain auditor for the **{{cluster_name}}** cluster,
auditing a **{{device}}** viewport at **{{width}}×{{height}}**.

## Your Reference Files (READ ALL BEFORE AUDITING)
Read these reference files at ${CLAUDE_PLUGIN_ROOT}/references/:
{{reference_file_list}}
- evidence-tiers.md (tier definitions: Gold, Silver, Bronze — apply to every citation)

## Page Data
- **Screenshots** (PRIMARY visual evidence): {{screenshot_paths_with_descriptions}}
- **DOM file**: {{dom_path}}
{{dom_caveat_if_mobile}}
- **Device**: {{device}} at {{width}}×{{height}}, {{dpr}}x DPR
- **Page type**: {{page_type}} ({{platform}})
- **Element coordinates**: {{filtered_elements_json}}
- **Styles**: {{styles_json}}

## Ethics Gate
{{full_ethics_gate_content}}

## Audit Instructions
[Read and include content from ${CLAUDE_PLUGIN_ROOT}/workflows/audit.md]
---

Template notes:
- {{dom_caveat_if_mobile}}: No longer needed — each device captures its own DOM at its own viewport. Omit this caveat.
- {{filtered_elements_json}}: Filter baton elements to only those within this auditor's screenshot sections (by scrollY range).
- {{full_ethics_gate_content}}: The COMPLETE text of ethics-gate.md — do not summarize, paraphrase, or excerpt. The file is ~77 lines; include in full.
</auditor_dispatch_template>

<finding_deduplication>
Before writing audit.md, deduplicate findings across clusters:
- Two findings are duplicates if they share the same SECTION slug AND target the same ELEMENT (or substantially overlapping elements)
- When duplicates are found, keep the finding with the higher PRIORITY. If equal, keep the one with the stronger evidence tier (Gold > Silver > Bronze)
- Append to the kept finding's observation: 'Also identified by {other_cluster} cluster.'
- Do NOT deduplicate findings that share a SECTION slug but target different elements (e.g., two different CTAs both flagged under primary-cta)
- **Ethics gate preservation rule:** If ANY auditor flagged a finding as PRIORITY: CRITICAL with a reference to ethics-gate.md, the deduplicated finding MUST retain PRIORITY: CRITICAL regardless of other auditors' severity ratings. Ethics violations cannot be downgraded during deduplication. This ensures the Ethics Gate summary and finding cards are consistent — a violation listed in the Ethics Gate section always appears as a CRITICAL finding card in the visual report.
- **Ethics severity override rule:** If the ethics gate defines a severity for a class of violation (e.g., "vague volume claims without verifiable evidence = CRITICAL"), that severity overrides any auditor's rating. During audit assembly, cross-check each ethics-related finding against the ethics gate definitions. If an auditor rated an ethics violation as HIGH or MEDIUM but the ethics gate classifies it as CRITICAL, upgrade to CRITICAL. Log the correction: "Upgraded {finding} from {original} to CRITICAL per ethics gate."
- Expected reduction: 20-30 raw findings typically deduplicate to 12-18 unique findings
</finding_deduplication>

<phase_audit>
Dispatch 1-3 domain auditors IN PARALLEL using multiple Agent tool calls in a single message. Use `model: "opus"` for all auditor dispatches — Opus provides better reasoning for cross-referencing screenshots against DOM and applying device-appropriate principles.

**Early dispatch (optional):** Trust-conversion auditors rely more on DOM than screenshots. If DOM is ready before all screenshots finish, dispatch trust-conversion auditors early with available screenshots. Visual-cta auditors require all screenshots — always wait for full baton.

Each Agent call contains:
- The audit workflow instructions (read from ${CLAUDE_PLUGIN_ROOT}/workflows/audit.md)
- Reference file paths for that cluster ONLY (at ${CLAUDE_PLUGIN_ROOT}/references/)
- Ethics gate content (read from ${CLAUDE_PLUGIN_ROOT}/references/ethics-gate.md)
- Min-priority filter if specified
- **Device context:** pass `"mobile"`, `"laptop"`, or `"desktop"` to each auditor

**Input varies by source mode:**

- **URL mode (source_mode: url-dual):** Pass each auditor the sectioned screenshots AND the DOM file path from the acquisition agent (`docs/cro/{engagement-id}/dom.html`). **Segment by cluster:** use the `clusters` tags in the acquisition agent's section boundary metadata to determine which screenshots and DOM sections to pass to each auditor. Only pass an auditor the screenshots tagged with its cluster slug. The auditor reads the DOM file directly and focuses on sections relevant to its cluster. This reduces per-auditor context significantly.
- **File path mode (source_mode: file):** Pass the page source code directly. No screenshots.
- **Description mode (source_mode: description):** Pass the text description.

**Baton validation and normalization:** After acquisition completes, read baton.json. Verify `status: 'COMPLETE'` and `screenshots` array has ≥1 entry. If validation fails, re-dispatch acquisition once. If second attempt fails, fall back to manual acquisition.

**Baton normalization (mandatory):** Acquisition agents sometimes simplify the baton schema. The coordinator MUST normalize before proceeding:
- If `screenshots` is an array of strings (e.g., `["section1.jpg", "section2.jpg"]`), convert each to an object: `{"index": N, "label": sections[N-1].label, "scrollY": sections[N-1].scrollY, "path": string_value, "naturalWidth": viewport.width * viewport.dpr, "naturalHeight": viewport.height * viewport.dpr}`.
- If `screenshots` entries are objects but missing `naturalWidth`/`naturalHeight`, compute from `viewport.width * viewport.dpr`.
- If `sections` entries are missing `screenshot_index`, assign sequentially (section 1 → screenshot 1, etc.).
- If `sections` entries are missing `clusters`, infer from label keywords (see fallback rules below).

**Screenshot-to-auditor routing:**
For each auditor cluster, build its screenshot list:
1. Iterate `baton.sections[]`
2. Collect entries where `clusters` array includes this auditor's cluster slug
3. Map each matching section to its `screenshot_index`
4. Collect the corresponding screenshot paths from `baton.screenshots[]`
5. Pass only those screenshots to this auditor

**Fallback (malformed baton):** If sections lack `clusters` arrays, infer from `label` keywords:
- CTA, hero, image, carousel, gallery → visual-cta
- price, review, trust, payment, badge, shipping, checkout → trust-conversion
- nav, search, filter, form, specs, footer, performance → context-platform
- personalization, recommendation, post-purchase → audience-journey

If still ambiguous, pass all screenshots to all auditors and note: 'Screenshot routing was unfiltered due to missing cluster metadata.'

Collect all outputs. Verify each output ends with `STATUS: COMPLETE` or `STATUS: PARTIAL`.

**Single device (mobile, laptop, or desktop):**
Write combined findings to docs/cro/{engagement-id}/audit.md.
Update meta.json: phase → "audit", `devices_scanned` → matches selected device, updated → current ISO timestamp.

**Two-device mode:**
Dispatch auditors by device batch — complete one device before starting the next:
1. First device: dispatch 1 auditor per cluster (up to 3 in parallel) with `device: "{first_device}"` — pass first device screenshots and DOM. Collect findings.
2. Second device: dispatch 1 auditor per cluster (up to 3 in parallel) with `device: "{second_device}"` — pass second device screenshots and DOM. Collect findings.

**CRITICAL: Each device's auditors MUST receive that device's screenshots and correct device label.** Do NOT reuse one device's audit findings for another device's report. A proper mobile audit evaluates:
- Whether CTA button heights meet the 48px minimum at mobile viewport
- Whether pricing cards have adequate touch target spacing
- Whether sticky bottom CTAs are implemented
- Thumb zone positioning at 390px width
- Font readability at mobile sizes

Reusing first device findings overlaid on second device screenshots is not a true audit — it misses device-specific issues entirely.

4. Write `audit.md` (first device findings) to disk
5. Write `audit-{second_device}.md` (second device findings) to disk
6. **Then** update meta.json: phase → "audit", `devices_scanned` → both devices, updated → current ISO timestamp
(Write files first, meta.json last — preserves atomicity invariant.)

**Partial failure in two-device mode:**
If one device's acquisition or audit fails, deliver the successful device's report + warning:
"⚠️ [{device}] scan failed: [reason]. Run with `--device [failed-device]` to retry."
Set `devices_scanned` to reflect only what completed. `devices_requested` preserves the original intent.

**Plan phase with two-device mode:** The planner receives both audit files as input. Findings from both devices inform the action plan.

**Auditor retry:** If an auditor returns `STATUS: PARTIAL`, SKIP, or fails entirely: retry once automatically with the same inputs. If the retry also fails: write SKIP finding for that cluster, offer "Re-run [cluster]" at checkpoint.

If --min-priority set and zero findings remain after filter: "No findings at [PRIORITY] or above. Options: (1) Lower the filter, (2) View all findings, (3) Stop here."
</phase_audit>

<audit_assembly>
After collecting all auditor outputs and deduplicating findings (see below), assemble audit.md.

**CRITICAL FORMAT REQUIREMENT:** Every FAIL and PARTIAL finding in audit.md **MUST** be wrapped in triple-backtick code fences. The visual report generator (`generate-report.py`) parses findings with a regex that matches code-fenced blocks. If findings are written as plain markdown (e.g., `**FINDING: FAIL**` without code fences), they will NOT appear in the DIAGNOSTIC INSIGHTS panel of the visual report — the report will show annotated screenshots with markers but zero finding cards.

**Correct finding format** (note the triple backticks on their own lines before and after):

    ```
    FINDING: FAIL
    SECTION: primary-cta
    ELEMENT: button.btn-cart
    SOURCE: VISUAL
    OBSERVATION: [observation text]
    RECOMMENDATION: [recommendation text]
    REFERENCE: [reference file and finding number]
    PRIORITY: HIGH
    **Why this matters:** [rationale]
    ↳ [citation] [Tier]
    ```

**Incorrect** (will cause zero findings in visual report):

    **FINDING: FAIL**
    SECTION: primary-cta
    ...

When assembling, copy each finding from the auditor output preserving its code fences. Do NOT reformat findings as plain markdown, bold text, or any other style. The auditors output code-fenced findings per `workflows/audit.md` — preserve that format exactly.

**Note on FINDING verdict:** Use only `FAIL` or `PARTIAL` as the verdict. `CRITICAL` is a PRIORITY value, not a verdict. A critical finding should be `FINDING: FAIL` with `PRIORITY: CRITICAL`.

Assemble audit.md with this structure:

```
# CRO Audit: {page_title} ({device_label})

**URL:** {url}
**Viewport:** {device} {width}×{height} @ {dpr}x DPR
**Platform:** {platform}
**Date:** {date}
**Engagement:** {engagement_id}

---

## Ethics Gate: {CLEAR | VIOLATIONS FOUND}
{summary line or violation list}

---

## Findings

### {cluster_name} cluster
{code-fenced findings ordered by priority: CRITICAL → HIGH → MEDIUM → LOW}

### {next_cluster_name} cluster
{code-fenced findings}

---

## What's Working Well
{deduplicated PASS findings from all auditors, as bullet list}

---

## Summary
| Priority | Count |
|----------|-------|
| CRITICAL | {n} |
| HIGH | {n} |
| MEDIUM | {n} |
| LOW | {n} |
| **Total** | **{n}** |

**Top 5 actions by expected impact:**
1. {action}
```

**JSON findings extraction (mandatory):**
After collecting all auditor outputs, extract the JSON findings array from each auditor's response. Look for the `FINDINGS_JSON:` marker followed by a JSON code block.

1. Parse each auditor's JSON array.
2. Merge all arrays into a single list.
3. Apply deduplication rules (same as prose dedup — match by `section` + `element`). Keep the higher `priority`. If equal, keep the stronger `tier` (Gold > Silver > Bronze). Append "Also identified by {cluster}" to the kept finding's `observation`.
4. Apply the ethics severity override rule: cross-check each finding's `reference` against ethics-gate.md. If the ethics gate classifies a violation class as CRITICAL, upgrade the finding's `priority` to CRITICAL regardless of the auditor's rating.
5. Sort by priority: CRITICAL → HIGH → MEDIUM → LOW.
6. Re-index: set `index` to 1-based sequential order after sorting.
7. Write the merged array to `docs/cro/{engagement-id}/findings.json`.

**findings.json is the source of truth for the report generator.** audit.md remains the human-readable view. Both must contain the same findings, but if there's any discrepancy, findings.json wins.

**Fallback:** If an auditor's response does not contain a `FINDINGS_JSON:` block, fall back to parsing its prose findings and constructing the JSON entries manually (extract SECTION, ELEMENT, SOURCE, PRIORITY, OBSERVATION, RECOMMENDATION, REFERENCE fields from code-fenced blocks). Log a warning: "Auditor {cluster} did not return JSON findings — falling back to prose parsing."

**Parity validation (mandatory):** After writing both audit.md and findings.json, verify finding counts match:
1. Count code-fenced `FINDING: FAIL` and `FINDING: PARTIAL` blocks in audit.md (grep for `^FINDING: (?:FAIL|PARTIAL)` inside code fences).
2. Count entries in the findings.json array.
3. If counts match: proceed silently.
4. If counts differ: log warning "Parity mismatch: audit.md has {N} findings, findings.json has {M}."
   - If findings.json has fewer: an auditor likely returned prose without a matching JSON entry, or JSON dedup removed an entry that prose dedup kept. For each prose finding missing from findings.json, construct a JSON entry from the prose fields and append to findings.json. Re-index.
   - If audit.md has fewer: JSON dedup kept a finding that prose dedup dropped (less common). Add the missing prose block to audit.md under its cluster heading.
   - After reconciliation, re-verify counts match. If still mismatched, log error but proceed — findings.json remains authoritative.
</audit_assembly>

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
   - FIXED: was FAIL or PARTIAL in previous, now PASS in current — **this is a win, highlight it**
   - REGRESSED: was PASS in previous, now FAIL or PARTIAL in current
   - UNCHANGED: same verdict in both
   - NEW: present in current but not in previous
   - RESOLVED: present in previous but not in current (section no longer evaluated)

5. Append a `## Progress Comparison` section to the current engagement's audit.md:

```markdown
## Progress Comparison

Compared against engagement `{previous-id}` ({date}).

### Now Passing ✓
<!-- List FIXED items prominently — these represent implemented improvements -->
| Section | Previous | Current |
|---------|----------|---------|
| {slug} | FAIL | PASS |

### Regressions
| Section | Previous | Current |
|---------|----------|---------|
| {slug} | PASS | FAIL |

### New Findings
| Section | Current |
|---------|---------|
| {slug} | {verdict} |

Summary: X FIXED, Y REGRESSED, Z UNCHANGED, W NEW, V RESOLVED
```

6. Use the summary counts when presenting the checkpoint message. **Emphasize FIXED items** — these are the user's wins. Present them first: "X issues from your last audit are now passing: [list slugs]." This gives users concrete feedback that their changes worked.
</progress_comparison>

<checkpoint_audit>
**Auto-save:** audit.md + meta.json are ALWAYS saved silently after every scan. No prompting for markdown save.

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
3. Export — How would you like this exported?
   a. Markdown only (already saved)
   b. Annotated visual report (dark-mode HTML with scroll-sync)
   c. Both markdown + visual report
   d. Skip additional exports
   After export, confirm with filenames: 'Visual report saved to `docs/cro/{engagement-id}/visual-report.html`' or for multi-device: list each file.
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
Dispatch planner subagent with `model: "opus"`:
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
2. Dispatch parallel planners (model: opus), one per cluster
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
2. Dispatch builder subagent with `model: "opus"`:
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
Available at any checkpoint when user requests a visual report.

**Visual report (annotated screenshots + findings):**

**Preferred: Python script.** Before attempting LLM-based assembly, try the Python report generator:

**Prerequisites (run once per environment):**
```bash
# Detect the working Python command (Windows uses `python`, Linux/macOS use `python3`)
python --version 2>/dev/null && PYTHON_CMD=python || PYTHON_CMD=python3

# Install Pillow if missing (required for marker burning into screenshots)
$PYTHON_CMD -c "from PIL import Image" 2>/dev/null || $PYTHON_CMD -m pip install Pillow
```

1. **Markers are auto-computed.** The report generator reads `findings.json` and `baton.json` directly, matching each finding's `element` field to baton entries internally. No `markers.json` file is needed.

2. Run the script (use `$PYTHON_CMD` from prerequisites, or `python` on Windows / `python3` on Linux/macOS):
   ```bash
   $PYTHON_CMD ${CLAUDE_PLUGIN_ROOT}/scripts/generate-report.py \
     --engagement docs/cro/{engagement-id} \
     --device {device} \
     --audit {audit-filename} \
     --baton {baton-filename} \
     --plugin-root ${CLAUDE_PLUGIN_ROOT} \
     --findings findings.json
   ```

3. The script handles: font injection (no context window consumption), marker burning via Pillow (pixel-perfect), base64 encoding, template population, click target generation, and writes a self-contained HTML file.

**Fallback: LLM assembly.** If Python or Pillow is unavailable:
1. Read `${CLAUDE_PLUGIN_ROOT}/workflows/visual-report.md` for assembly instructions
2. Follow the font concatenation approach (do NOT read font-embed.css into context)
3. Use CSS-positioned markers (less accurate but functional)

**Output naming:**
- Mobile: `visual-report-mobile.html`
- Laptop: `visual-report.html`
- Desktop: `visual-report-desktop.html`

**Two-device mode:** Generate both reports. If using the Python script, run it twice sequentially (2-5 seconds each). If using LLM assembly, dispatch as two **parallel** Agent calls — the two device reports are completely independent.

**Text report:** Read ${CLAUDE_PLUGIN_ROOT}/workflows/report.md for text report generator instructions.
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
Read ethics-gate.md into a variable. Include the COMPLETE text in every subagent prompt under a `## Ethics Gate` heading. Do not summarize, paraphrase, or excerpt — paste the full file contents. The ethics gate is ~77 lines; this is small enough to include in full. Ethics violations are always PRIORITY: CRITICAL.
</ethics>

<reference_freshness>
Each reference file has a RESEARCH_DATE watermark. If older than 12 months, warn at checkpoint.
</reference_freshness>
