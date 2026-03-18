---
title: "feat: CRO Plugin v3 — Accuracy, Architecture & Visual Reports"
type: feat
status: active
date: 2026-03-17
deepened: 2026-03-17
origin: docs/brainstorms/2026-03-17-dual-source-auditor-brainstorm.md
---

# CRO Plugin v3 — Accuracy, Architecture & Visual Reports

## Enhancement Summary

**Deepened on:** 2026-03-17
**Research agents used:** agent-native-architecture, create-agent-skills, architecture-strategist, agent-native-reviewer, security-sentinel, pattern-recognition-specialist, performance-oracle, code-simplicity-reviewer

### Key Improvements From Deepening
1. **DOM preprocessing** added to acquisition — strip scripts/styles/SVGs/data-attrs, 60-80% size reduction, 300KB cap with skeleton fallback
2. **Nonce-prefixed markers** for QUESTION/VERDICT blocks — prevents prompt injection from malicious page content
3. **Screenshot-based visual report** replaces DOM reconstruction — simpler, cheaper (~140K tokens saved), more accurate
4. **Tiered model pinning** — Haiku for mechanical agents, Sonnet for analysis, Opus for synthesis
5. **Hybrid multi-planner** — only triggers for 3+ clusters each with 5+ findings (not a hard >10 threshold)
6. **Security hardening** — post-navigation URL re-validation, HTML allowlist for visual report, meta.json read-path validation
7. **Conditional relay iterations** — iterations 2-3 only fire when QUESTION blocks detected
8. **Explicit STATUS completion signals** on all fork agents

### New Considerations Discovered
- Malicious pages can forge QUESTION/VERDICT markers in agent output (mitigated by nonce)
- Unbounded DOM passed to auditors can exhaust context windows (mitigated by preprocessing + 300KB cap)
- Compare mode sequential penalty doubles wall-clock time unnecessarily (reverted to parallel with serialized acquisition only)
- `--auto` mode had 2 critical gaps on the heavy-audit path (multi-planner checkpoint + reconciler conflicts)
- `audit/SKILL.md` will exceed 500 lines — coordinator protocols should be extracted to reference files

---

## Overview

Comprehensive upgrade to the CRO plugin addressing 15 identified issues across audit accuracy, agent architecture, output quality, and reliability. Transforms the plugin from v2.2.0 to v3.0.0 with breaking changes to the meta.json schema, output system, and agent dispatch model.

## Problem Statement

The current plugin has structural flaws that limit audit quality and user experience:

1. **Auditors rush through full-page screenshots** — agents skim 10,000px images instead of examining sections deliberately
2. **Reviewer and builder can't actually interact** — designed as interactive agents but dispatched as single-shot forks
3. **Single planner produces shallow plans** for complex audits — 12-step cap forces cutting valid findings
4. **Text-only output** — no visual representation of where recommendations apply on the page
5. **No model quality floor** — agents inherit parent model, producing inconsistent results
6. **Multiple housekeeping issues** — meta.json staleness, no retry logic, rigid report templates, citation gaps

(See brainstorm: `docs/brainstorms/2026-03-17-dual-source-auditor-brainstorm.md`)

## Proposed Solution

Five implementation phases (consolidated from original six), each independently shippable with noted dependencies:

1. **Dual-source acquisition** with sectioned captures + DOM preprocessing
2. **Coordinator relay loops** for reviewer/builder interactivity + planner cap removal
3. **Hybrid multi-planner** with reconciler (3+ cluster threshold)
4. **Screenshot-based visual reports** with annotation overlays
5. **Output tiering + Housekeeping** — flags, meta.json, retries, citations, templates, safety

### Phase Dependency Matrix

```
Phase 1: No dependencies (ship first)
Phase 2: Works standalone; benefits from Phase 1 (SOURCE field context)
Phase 3: Works standalone; benefits from Phase 2 (relay loops for per-PRD review)
Phase 4: Requires Phase 1 (sectioned screenshots from acquisition)
Phase 5: No hard dependencies (housekeeping can ship in any order)
```

## Technical Approach

### Architecture

The plugin's core principle — **isolated context per agent, coordinator manages the relay** — is preserved and extended. No shared state between agents. The coordinator remains the only entity that writes files and presents checkpoints.

### Model Tier Strategy

| Agent | Tier | Model | Reasoning |
|-------|------|-------|-----------|
| Acquisition | Fast | Haiku | Mechanical: navigate, screenshot, extract DOM |
| Auditor | Balanced | Sonnet | Analysis + judgment against reference principles |
| Planner | Balanced | Sonnet | Structured planning from findings |
| Reconciler | Powerful | Opus | Multi-document synthesis, conflict resolution |
| Reviewer | Powerful | Opus | Nuanced judgment about plan quality, ethical concerns |
| Builder | Balanced | Sonnet | Code generation from plan steps |
| Visual Report | Fast | Haiku | Mechanical HTML construction from screenshots + findings |

Pin to tier names in implementation, not specific model versions — enables automatic improvement when newer models ship.

### Research Insights: Agent Architecture

**Best Practices (from agent-native review):**
- Use **single-line JSON** for structured agent output — more reliably parseable than multi-line delimited blocks
- Add explicit **STATUS: COMPLETE | BLOCKED | PARTIAL** terminal line to all fork agent output — eliminates heuristic completion detection
- Make prompts **outcome-oriented** ("identify conflicts and resolve them") not process-oriented ("for each pair of PRDs, check for...")
- The <=10 finding threshold should be **judgment criteria** ("when a single plan would sacrifice depth for breadth") not a rigid rule

**Pipeline flow (heavy audit with hybrid multi-planner):**
```
Input → Acquisition (Haiku) → Auditors (parallel, Sonnet)
  → [checkpoint]
  → If 3+ clusters each with 5+ findings:
      Planners (parallel, Sonnet) → Reconciler (Opus)
    Else:
      Single Planner (Sonnet)
  → [checkpoint: pick order / build all / deepen / save]
  → Review PRD-1 (relay loop, Opus) → Build PRD-1 (relay loop, Sonnet) → [checkpoint]
  → Review PRD-2 → Build PRD-2 → [checkpoint]
  → ...complete
```

---

### Implementation Phases

---

#### Phase 1: Dual-Source Acquisition & Sectioned Captures

**Goal:** Replace single full-page screenshots with focused sectioned captures + preprocessed DOM. Add SOURCE provenance to findings.

**Priority:** Highest — this is the core accuracy improvement.

##### Tasks

- [ ] **Create `workflows/acquire.md`** — new acquisition workflow
  - Frontmatter: `name: cro-acquirer`, `context: fork` (follows naming convention — no "agent" suffix)
  - Input: URL (validated), viewport dimensions (default 1280x800)
  - Process:
    1. Navigate to URL via agent-browser
    2. Wait for DOMContentLoaded + 2s settle time
    3. **Post-navigation URL validation:** verify `window.location.href` still resolves to the validated domain. If redirected to a different domain or private IP range, abort with error: "Page redirected to [URL] which failed validation. Provide the source code locally."
    4. Identify the page's major visual sections using semantic landmarks, headings, and significant layout boundaries. Target 3-6 sections that together cover the full page.
    5. Capture above-the-fold screenshot (viewport 1, **1x DPR, JPEG quality 80**)
    6. For each detected section boundary: scroll to boundary, capture viewport screenshot
    7. Cap at 6 screenshots (merge adjacent small sections). Minimum 3 (if <3 sections, capture at 33%/66% scroll depth).
    8. **DOM preprocessing** (critical for context management):
       - Extract `document.documentElement.outerHTML`
       - Strip all `<script>` tags and contents
       - Strip all `<style>` tags (preserve only inline `style` attributes on key structural elements)
       - Strip all `data-*` attributes
       - Strip SVG path data (replace with `<svg aria-label="..."/>`)
       - Strip JSON-LD blocks (extract structured data metadata separately)
       - Strip duplicate/template elements (e.g., Shopify hidden variants — keep first instance only)
       - Strip `value` attributes from password, hidden, and financial input fields
       - **Hard cap: if preprocessed DOM exceeds 300KB, switch to skeleton extraction mode** — pull only headings, buttons, links, forms, images with alt text, ARIA landmarks, prices, and review elements
    9. Extract computed background-color of `body` and primary container
  - ## Output Rules: Return ONLY the array of screenshot paths + preprocessed DOM string + section boundary metadata + extracted styles. No analysis, no findings.
  - Terminal line: `STATUS: COMPLETE | BLOCKED | PARTIAL`
  - Failure modes:
    - agent-browser unavailable → STATUS: BLOCKED, fall back to "provide file path or paste code"
    - Page requires auth (detect: DOM contains password input or URL redirected to login) → warn user
    - DOM appears pre-hydration (body has <5 visible text nodes) → retry once after 5s additional wait
    - Partial capture (some screenshots fail) → STATUS: PARTIAL, proceed with what was captured
    - Navigation timeout (>30s) → STATUS: BLOCKED, abort with timeout message

- [ ] **Update `workflows/audit.md`** — auditor receives dual-source input
  - Add to ## Input: "6. **Screenshots** — 3-6 sectioned viewport captures (if URL mode)" and "7. **Preprocessed DOM** — cleaned, post-JS-execution HTML (if URL mode)"
  - Add to ## Process: "For each screenshot, examine against cluster principles before moving to next. Cross-reference visual observations with DOM evidence."
  - Add SOURCE field to output format:
    ```
    FINDING: [PASS|FAIL|PARTIAL|SKIP]
    SECTION: [canonical-slug]
    SOURCE: [VISUAL|CODE|BOTH]
    OBSERVATION: [specific observation]
    RECOMMENDATION: [actionable recommendation]
    REFERENCE: [reference-file.md — principle name]
    PRIORITY: [CRITICAL|HIGH|MEDIUM|LOW]
    ```
  - Add instruction: "When visual and code evidence contradict, flag the contradiction in OBSERVATION and set SOURCE: BOTH."
  - Add terminal line requirement: `STATUS: COMPLETE | BLOCKED | PARTIAL`

- [ ] **Update `workflows/quick-scan.md`** — same dual-source input + SOURCE field + STATUS line

- [ ] **Update `skills/cro/audit/SKILL.md`** `<mode_detection>` and `<phase_audit>`
  - `<mode_detection>`: replace current URL acquisition logic with:
    1. File path → read directly (no acquisition step)
    2. URL → dispatch acquisition agent (model: haiku), then pass results to auditors
    3. No agent-browser and no file path → prompt user to paste code
  - `<phase_audit>`: auditor dispatch includes screenshots + preprocessed DOM
  - **Segment DOM by cluster:** pass each auditor only the DOM sections relevant to their cluster's page areas (use section boundary metadata from acquisition). This is the highest-impact token optimization.
  - Add `model: "sonnet"` to all auditor Agent dispatches

- [ ] **Update `skills/cro/quick-scan/SKILL.md`** — same acquisition step + model pinning

- [ ] **Update `skills/cro/compare/SKILL.md`** `<dispatch>`
  - **Serialize acquisition only:** acquire your page first, then acquire competitor page
  - **Keep auditors parallel:** after both acquisitions complete, dispatch all auditors (up to 6) in parallel as v2 does today
  - If your page acquisition fails entirely → stop, report error, don't proceed
  - Add model pinning to all auditor dispatches

- [ ] **Update `templates/audit.md.template`** — add SOURCE field to finding format

- [ ] **Update `templates/meta.json.template`** — add `source_mode` field + bump `schema_version` to 2
  - `source_mode` values: `url-dual`, `url-screenshot` (legacy fallback), `file`, `description`

##### Security Requirements (Phase 1)

- [ ] Post-navigation URL re-validation in `acquire.md` (Finding 1.1)
- [ ] DOM preprocessing strips sensitive form field values (Finding 1.3)
- [ ] DOM size cap at 300KB with skeleton fallback (Finding 6.1)

##### Acceptance Criteria

- [ ] URL scans produce 3-6 sectioned screenshots (JPEG, 1x DPR) + preprocessed DOM (<300KB)
- [ ] Every finding has a SOURCE field (VISUAL, CODE, or BOTH)
- [ ] Auth-protected pages are detected and user is warned
- [ ] Post-navigation URL is re-validated against url-validation.md rules
- [ ] Pre-hydration DOMs trigger a retry; navigation timeout at 30s
- [ ] Auditor agents pinned to Sonnet; acquisition agent pinned to Haiku
- [ ] Compare mode: sequential acquisition, parallel auditors
- [ ] File path and description modes are unaffected

---

#### Phase 2: Coordinator Relay Loops + Planner Cap Removal

**Goal:** Enable the reviewer and builder to interact with the user through the coordinator. Remove the 12-step plan cap.

**Priority:** High — fixes the two most fundamental architectural bugs.

##### Tasks

- [ ] **Update `workflows/review.md`** — structured question output protocol
  - Add `## Question Protocol`:
    - Coordinator generates a random nonce per dispatch and passes it to the agent
    - When the agent needs user input, emit a single-line JSON question:
      ```
      QUESTION__{nonce}: {"step": 3, "type": "VAGUE", "description": "...", "options": ["A", "B", "C"]}
      ```
    - Continue analyzing remaining steps. Emit all questions inline wherever they arise, then produce verdict.
    - Types: `VAGUE`, `CONTRADICTION`, `ETHICS`, `WCAG`
  - Add `## Auto Mode`: "If the coordinator indicates --auto mode, do NOT emit QUESTION lines. Produce best-effort verdict. Use simpler/safer interpretation for vague steps. Flag unresolved concerns in 'Remaining Concerns' section."
  - Add `## Relay Context`: "If coordinator provides previous Q&A pairs, incorporate those answers. Do not re-ask resolved questions."
  - Add terminal line: `STATUS: COMPLETE | BLOCKED | PARTIAL`
  - Add `VERDICT__{nonce}: [APPROVE|REVISE|BLOCK]` (nonce-prefixed to prevent injection)

- [ ] **Update `workflows/build.md`** — structured question output protocol
  - Same nonce-prefixed single-line JSON for Stuck states:
    ```
    QUESTION__{nonce}: {"step": 5, "type": "STUCK", "description": "...", "options": ["Skip", "Alternative approach", "Go back"]}
    ```
  - Add `ETHICS` to builder's question types (builder may encounter ethics concerns mid-implementation)
  - Remove batch preference question entirely. Builder always operates in "see everything at the end" mode (universal, not relay-mode-only).
  - Add `## Auto Mode` + `STATUS` terminal line

- [ ] **Update coordinator SKILL.md files** — relay loop protocol in `<phase_review>` and `<phase_build>`
  - Generate random nonce before each agent dispatch
  - Pass nonce to agent as part of dispatch payload
  - After receiving output, parse for `QUESTION__{nonce}:` lines (only matching nonce)
  - **Conditional relay:** iterations 2-3 ONLY fire when QUESTION lines are detected. If no questions, relay completes in one shot.
  - If questions found AND not --auto:
    1. Present questions to user (numbered, with options)
    2. Collect answers
    3. Re-dispatch with: original inputs + **Q&A pairs only** (not full previous output) + nonce
    4. Max 3 relay iterations (1 initial + 2 re-dispatches). After 3rd, present unresolved questions + best-effort output to user, let user decide: proceed, answer remaining, or stop.
  - If questions found AND --auto: ignore questions, use verdict as-is
  - Parse `VERDICT__{nonce}:` only (prevents injection from page content)
  - Handle malformed QUESTION lines: treat as question-free, proceed with verdict

- [ ] **Update reviewer checkpoint** in audit and build SKILL.md files:
  ```
  Ready to proceed?
  1. Yes — proceed to build
  2. No — go back to planning
  3. Deepen plan — add more detail to weak steps
  4. Save here and resume later

  If --auto: always select option 1 (proceed to build). Options 3 and 4 are interactive-only.
  ```

- [ ] **Update `workflows/plan.md`** — remove 12-step hard cap
  - Replace "Max 12 steps" with: "Group related changes into compound steps. Order by priority then dependency. No hard cap — if steps exceed ~20, separate into Critical+High vs Medium+Low tiers."
  - Add: "When receiving findings for a single cluster only (multi-planner mode), produce a focused plan for that area."
  - Change output rules: "Return the action plan table + Conflicts Resolved section" (not "ONLY the table")
  - Add `STATUS` terminal line

- [ ] **Extract coordinator protocols to reference files** to keep SKILL.md under 500 lines:
  - `references/relay-loop-protocol.md` — the nonce generation, parsing, conditional iteration, and re-dispatch logic
  - `references/multi-planner-protocol.md` — the finding density analysis, dispatch, reconciliation, and checkpoint logic
  - SKILL.md files reference these with concise summaries and `Read ${CLAUDE_PLUGIN_ROOT}/references/...` instructions

##### Security Requirements (Phase 2)

- [ ] Nonce-prefixed QUESTION and VERDICT markers (Finding 3.1, 3.2) — prevents forged markers from malicious page content
- [ ] Coordinator only parses markers with matching nonce

##### Acceptance Criteria

- [ ] Reviewer emits nonce-prefixed single-line JSON questions that coordinator can parse
- [ ] Coordinator relays questions to user and re-dispatches with Q&A pairs only
- [ ] Relay iterations are conditional — only fire when questions detected
- [ ] Max 3 relay iterations; after 3rd, user decides (not forced verdict)
- [ ] --auto mode: reviewer/builder produce best-effort output without questions
- [ ] Reviewer checkpoint includes "Deepen plan" and "Save and resume" (interactive-only)
- [ ] Planner step cap removed; phased grouping guidance added
- [ ] All fork agents emit STATUS terminal line

---

#### Phase 3: Hybrid Multi-Planner with Reconciler

**Goal:** Complex audits (3+ clusters each with 5+ findings) spawn parallel planners per cluster, followed by a reconciler. Sequential review/build per PRD.

**Priority:** High — improves plan quality for complex audits.

**Trigger:** Multi-planner activates when findings are numerous enough that a single plan would sacrifice depth for breadth, AND findings naturally cluster into 3+ distinct areas each with 5+ findings. Otherwise, single planner (Phase 2 behavior).

##### Tasks

- [ ] **Create `workflows/reconcile.md`** — new reconciler workflow
  - Frontmatter: `name: cro-reconciler`, `context: fork`
  - Input: all PRD files + ethics gate + conflict resolution rules
  - Process (outcome-oriented, not prescriptive):
    > "You receive multiple action plans that will be applied to the same page. Identify any conflicts — places where plans contradict each other or make incompatible assumptions about the same page elements. Use SECTION slugs from findings to detect overlapping targets. Resolve conflicts using this priority order: legal > ethics > user constraints > domain guidance. When you amend a plan, document what changed and why."
  - When a conflict is resolved, amend the lower-priority plan's step with: `[RECONCILED: adjusted from X to Y due to conflict with plan-{area}]`
  - Irreconcilable conflicts (both CRITICAL): flag for user decision. **In --auto mode:** apply tiebreaker using cluster routing table order (first cluster listed wins). Document as `[AUTO-RESOLVED]`.
  - Completion signals: `RECONCILED: N conflicts resolved` or `NO_CONFLICTS: plans are compatible`
  - Add `## Output Rules`, `## Quality Check` ("verify every cross-plan conflict has a resolution"), `STATUS` terminal line
  - Failure mode: if only one PRD exists, return unchanged with `NO_CONFLICTS`

- [ ] **Create `templates/reconciliation.md.template`** — follows convention of templates for all output types

- [ ] **Update coordinator SKILL.md files** — multi-planner dispatch
  - Finding density analysis (judgment criteria, not rigid threshold):
    > "Use multi-planner mode when 3+ clusters each have 5+ findings — indicating findings are numerous and naturally cluster into distinct areas where a single planner would sacrifice depth for breadth. Otherwise, single planner."
  - Multi-planner dispatch:
    1. Group findings by source cluster (areas = clusters)
    2. Dispatch one planner per cluster IN PARALLEL (model: sonnet)
    3. Each planner receives: its cluster's findings only + ethics gate + conflict resolution + context.md
    4. Collect all PRD outputs
    5. Write to: `plan-{cluster-slug}.md`
    6. Dispatch reconciler (model: opus) with all PRDs
    7. Write reconciler output back + write `reconciliation.md`
  - Multi-planner checkpoint:
    ```
    Separate action plans created:
    1. [Cluster Name] ([N] steps) — [priority breakdown]
    2. [Cluster Name] ([N] steps)

    [If reconciler amended: "Reconciler resolved N cross-plan conflicts."]

    Options:
    1. Build all sequentially (recommended order: [priority-sorted])
    2. Pick one to start
    3. Deepen a specific plan
    4. Save all and resume later

    If --auto: select option 1 (build all in recommended priority order). Skip checkpoint.
    ```
  - Sequential review/build: one PRD at a time. After each build, checkpoint to continue or stop.
  - **Planner failure handling:** if a planner fails, retry once. If retry fails, proceed without that cluster's plan and note the gap at checkpoint.

- [ ] **Update `templates/meta.json.template`** — add multi-PRD fields
  ```json
  {
    "schema_version": 2,
    "plans_queue": [],
    "reconciled": false
  }
  ```
  - `plans_queue`: array of objects `[{"cluster": "visual-cta", "file": "plan-visual-cta.md", "phase": "pending|reviewing|building|complete|failed"}]`
  - **`current_plan` and top-level `phase` are derived** from `plans_queue` at read time (not stored independently). Current plan = first entry whose phase is not `pending` or `complete`. Top-level phase = derived from queue state. This eliminates consistency risks.
  - **Forward compatibility:** resume skips engagements with `schema_version > 2` rather than crashing

- [ ] **Update `skills/cro/resume/SKILL.md`** — multi-PRD awareness
  - Detect schema_version: handle v1 (legacy) and v2 (new) separately
  - Show which PRDs are complete/active/pending
  - Resume at active PRD's last checkpoint
  - **Self-healing:** if `plans_queue` phase and file existence disagree, file existence wins (derive state from filesystem)

- [ ] **Update go-back protocol** for multi-PRD
  - Going back on active PRD: delete only that PRD's downstream files (use exact filenames from plans_queue — verified as children of engagement directory)
  - Going back to audit: delete ALL PRDs, reconciliation.md, and downstream files
  - **File existence is the source of truth** — meta.json is updated last; if crash occurs during cleanup, resume detects and self-heals

##### File Naming Convention

```
docs/cro/{engagement-id}/
  meta.json
  context.md
  audit.md
  plan.md                          # single-planner mode
  plan-visual-cta.md               # multi-planner mode
  plan-trust-conversion.md
  reconciliation.md                # multi-planner mode only
  review.md / review-visual-cta.md
  build-log.md / build-log-visual-cta.md
  visual-report.html               # screenshot-based (Phase 4)
  report.html                      # text report
```

Templates are reused for suffixed variants (e.g., `plan.md.template` used for both `plan.md` and `plan-visual-cta.md`).

##### Security Requirements (Phase 3)

- [ ] meta.json read-path validation on every read (Finding 5.1): validate phase enums, verify `plans_queue[].file` matches `plan-{slug}.md` pattern and exists within engagement directory (no path traversal)
- [ ] `--auto` fallback for irreconcilable reconciler conflicts

##### Acceptance Criteria

- [ ] 3+ clusters with 5+ findings each triggers multi-planner; otherwise single planner
- [ ] One planner per cluster, dispatched in parallel (Sonnet)
- [ ] Reconciler reads all PRDs and resolves conflicts (Opus)
- [ ] Review/build runs sequentially, one PRD at a time
- [ ] `current_plan` and `phase` derived from `plans_queue` (not stored independently)
- [ ] Resume handles schema v1 and v2; self-heals inconsistent state
- [ ] Go-back operates per-PRD without affecting others
- [ ] `--auto` has defined defaults at all checkpoints

---

#### Phase 4: Screenshot-Based Visual Reports

**Goal:** Generate annotated visual reports using the sectioned screenshots from Phase 1 with CRO callout overlays.

**Priority:** Medium-high — major UX improvement.

**Requires Phase 1** (sectioned screenshots from acquisition).

##### Tasks

- [ ] **Create `workflows/visual-report.md`** — visual report generator workflow
  - Frontmatter: `name: visual-report-generator`, `context: fork`
  - Input: sectioned screenshot paths, audit findings with SOURCE tags, section boundary metadata, engagement metadata
  - Process:
    1. Stitch the 3-6 sectioned screenshots into a vertical layout
    2. For each FAIL/PARTIAL finding, position an orange callout bar above/between the relevant screenshot section:
       - Callout format: `CRO CHANGE: [RECOMMENDATION SUMMARY]`
       - Map findings to screenshot sections using SECTION slugs + section boundary metadata
    3. PASS findings get subtle green checkmarks (non-intrusive)
    4. For findings referencing non-visible states (modals, accordions, hover): add text-only annotations in a "Hidden Elements" section at the bottom
    5. Add header banner: `CRO REDESIGN MOCKUP — [URL] — VISUAL GUIDE (NOT PRODUCTION CODE)`
    6. Add footer: engagement ID, date, clusters analyzed, source mode
  - Output: self-contained HTML with screenshots embedded as base64 JPEG, inline CSS, CSP meta tag
  - ## Output Rules: Return ONLY the completed HTML. No markdown, no explanation.
  - ## Quality Check: verify all FAIL/PARTIAL findings have a corresponding callout
  - `STATUS` terminal line
  - Security: CSP `default-src 'none'; style-src 'unsafe-inline'; img-src data:; script-src 'none'; connect-src 'none'; frame-src 'none'; object-src 'none'`
  - Failure modes:
    - File-path mode (no screenshots) → skip visual report, inform user: "Visual report requires URL mode"
    - Screenshots missing/corrupted → degrade gracefully, text-only annotations for missing sections

- [ ] **Update `workflows/report.md`** — dynamic section rendering
  - Strip inapplicable `SECTION:*_START/END` blocks entirely (not "Not yet completed" text)
  - Quick-scan: findings only
  - Build-from-scratch: skip audit findings section
  - Compare: use compare layout sections
  - When visual report exists, add a link from the text report header
  - **Escape `{{...}}` patterns** found in source content before template insertion (Finding 2.3)

- [ ] **Create `templates/visual-report.html.template`**
  - Header banner (dark background, warning text)
  - Screenshot container (vertical stack of base64 images)
  - Annotation overlay layer (positioned callout bars between screenshots)
  - Hidden elements section
  - Footer (metadata)
  - Print styles
  - Responsive (primary target: desktop-width)

##### Acceptance Criteria

- [ ] Visual report stitches sectioned screenshots with CRO callout overlays
- [ ] Each FAIL/PARTIAL finding has a visible callout at the relevant section
- [ ] Self-contained HTML, no external resources, CSP-restricted
- [ ] File-path mode gracefully skips visual report with explanation
- [ ] Hidden/dynamic element findings listed in separate section
- [ ] Base64-embedded screenshots (JPEG, reasonable file size)

---

#### Phase 5: Output Tiering + Housekeeping

**Goal:** Mode-specific output defaults, flag cleanup, meta.json maintenance, retries, citations, safety, templates.

**Priority:** Medium — rounds out the release.

##### Output Tiering Tasks

- [ ] **Update `skills/cro/quick-scan/SKILL.md`**
  - Default: conversation output + **silent meta.json creation** (for aggregation)
  - After presenting findings, prompt:
    ```
    Want me to save this?
    1. Visual report — annotated screenshot mockup
    2. Markdown — save findings to audit.md
    3. Both
    4. No, conversation is enough
    ```
  - Flags: `--visual` (auto-generate visual), `--no-visual` (skip prompt, conversation only + meta.json), `--save` (persist markdown)
  - **Deprecate `--ephemeral` as a no-op** with warning: "--ephemeral is deprecated, use --no-visual" (prevents breaking existing callers)
  - `--auto` mode: default to markdown + meta.json, skip prompt

- [ ] **Update `skills/cro/audit/SKILL.md`**
  - Default: markdown always written
  - After audit checkpoint, prompt:
    ```
    Want the visual report too?
    1. Yes — annotated screenshot mockup
    2. No, markdown is enough
    ```
  - Flags: `--visual` / `--no-visual`
  - Remove `--export-report` (text report available at any checkpoint, same as today)
  - `--auto` mode: markdown only unless `--visual` flag passed

- [ ] **Update `skills/cro/compare/SKILL.md`** — same tiering. Visual shows side-by-side screenshot annotations.

- [ ] **Update `skills/cro/SKILL.md`** (router) — update command descriptions for new output options

##### Housekeeping Tasks

- [ ] **meta.json `updated` field** — write current ISO timestamp on every phase transition

- [ ] **Auditor retry logic** — if auditor returns SKIP or fails: retry once automatically. If retry fails: write SKIP, offer "Re-run [cluster]" at checkpoint. Retry applies to auditors and planners.

- [ ] **`--auto` build requires clean git state** — if `git status --porcelain` returns output: abort with error. Add `--allow-dirty` flag to override (for orchestrating agents that staged changes intentionally). Interactive mode: keep existing stash suggestion.

- [ ] **Go-back atomicity fix** — delete downstream files FIRST, then update meta.json. Document invariant: if meta.json phase and file existence disagree, file existence wins.

- [ ] **Planner output format** — change output rules to "Return action plan table + Conflicts Resolved section"

- [ ] **Citation IDs** — update all 18 domain reference files + `citations/sources.md`:
  - Replace inline citations with bracketed IDs: `(Spiegel/Northwestern)` → `[SPG-2021]`
  - Document ID format constraint: `[A-Z]{2,5}-\d{4}`
  - Structure `sources.md` with matching ID entries
  - IDs must not collide with coordinator parsing markers

- [ ] **`--ab-tool` graceful fallback** — unknown tools get: "I don't have specific patterns for [tool]. I'll generate generic scaffold." Drop the hardcoded known-tools list (maintenance burden).

- [ ] **Report template dynamic sections** — report generator removes inapplicable sections entirely

- [ ] **`schema_version` migration** — resume/SKILL.md handles v1 (legacy) and v2 (new) engagements. v1 engagements work with existing logic. Unknown schema versions are skipped with warning.

- [ ] **Persistent `.gitignore` check** — verify `docs/cro/` is in `.gitignore` on every engagement setup (not just first engagement)

- [ ] **XML tag to markdown heading migration** — when modifying existing SKILL.md files, convert XML tags (`<objective>`, `<flags>`, `<phase_audit>`) to markdown headings (`## Objective`, `## Flags`, `## Phase: Audit`). New files use markdown headings only.

##### Acceptance Criteria

- [ ] Quick-scan default is conversation + silent meta.json; `--ephemeral` deprecated as no-op
- [ ] Full audit default is markdown + visual report prompt
- [ ] `--visual` / `--no-visual` / `--save` / `--allow-dirty` flags work
- [ ] `--auto` mode has defined defaults at every prompt
- [ ] meta.json `updated` field reflects last-modified time
- [ ] Failed auditors/planners get one retry before SKIP
- [ ] `--auto` build aborts on dirty git (unless `--allow-dirty`)
- [ ] All 18 reference files use bracketed citation IDs
- [ ] Report template strips inapplicable sections
- [ ] schema_version migration works for v1 and v2 engagements
- [ ] Modified SKILL.md files migrated from XML tags to markdown headings

---

## Alternative Approaches Considered

| Approach | Why Rejected |
|----------|-------------|
| Inline hybrid acquisition | Mixes data gathering with judgment; auditor may skip code analysis |
| Two-pass auditor (visual + code) | Doubles agent cost/time; merge conflict risk |
| Make reviewer/builder non-interactive | Loses specification hardening; reviewer becomes rubber stamp |
| Full multi-planner for all >10 finding audits | Over-triggers; most audits handled by single planner with lifted cap |
| Parallel review/build across PRDs | Context bloat; inconsistent quality; complex state |
| DOM reconstruction for visual report | Fragile, expensive (~140K tokens), less accurate than actual screenshots |
| Multi-line QUESTION_START/END protocol | Fragile parsing, injection risk from page content, over-engineered |
| Storing `current_plan` independently | Consistency risk with `plans_queue`; derive at read time instead |

## System-Wide Impact

### Interaction Graph

- Acquisition agent (new) dispatched before auditors → auditors depend on acquisition output
- Relay loop adds coordinator ↔ reviewer/builder ↔ user cycle (conditional, max 3 iterations)
- Multi-planner adds: audit → N planners (parallel) → reconciler → sequential review/build per PRD
- Visual report generator reads screenshots + findings → produces annotated HTML
- meta.json schema v2 adds: `plans_queue`, `reconciled`, `source_mode`

### Error Propagation

- Acquisition failure → graceful fallback to file-path mode (user prompted)
- Acquisition timeout (30s) → STATUS: BLOCKED, user prompted
- Post-navigation redirect to private IP → acquisition aborts with validation error
- Auditor/planner failure → 1 retry, then SKIP with re-run option at checkpoint
- Reconciler failure → plans proceed unreconciled; user warned at checkpoint
- Relay loop: conditional iterations; after 3rd, user decides (not forced)
- Visual report failure → text report still generated; visual skipped with message
- meta.json inconsistency → self-heals from filesystem on resume

### State Lifecycle Risks

- Multi-PRD go-back: uses exact filenames from plans_queue, verified as children of engagement directory (prevents path traversal)
- `current_plan` and `phase` derived from `plans_queue` → always regenerable from file existence
- Quick-scan meta.json without audit.md: aggregation works regardless of whether findings were saved

### API Surface Parity

All changes apply to both git repo source AND installed plugin in `~/.claude/skills/`. Reinstall script or instructions required.

## Acceptance Criteria

### Functional Requirements

- [ ] URL scans produce 3-6 sectioned screenshots + preprocessed DOM (<300KB)
- [ ] Every finding has a SOURCE tag (VISUAL, CODE, BOTH)
- [ ] Reviewer and builder can ask questions via nonce-prefixed relay (conditional, max 3 iterations)
- [ ] `--auto` mode: agents produce best-effort output; all checkpoints have defined defaults
- [ ] Complex audits (3+ clusters, 5+ findings each) spawn parallel planners + reconciler
- [ ] Review/build runs one PRD at a time, sequentially
- [ ] Visual report stitches screenshots with annotation overlays
- [ ] Model tiers: Haiku (acquisition, visual report), Sonnet (auditors, planners, builder), Opus (reconciler, reviewer)

### Non-Functional Requirements

- [ ] No external resources in generated HTML (self-contained, CSP-restricted)
- [ ] All user content HTML-escaped in reports (XSS prevention)
- [ ] Nonce-prefixed markers prevent prompt injection from page content
- [ ] Post-navigation URL re-validated against url-validation.md rules
- [ ] meta.json validated on every read (schema, enums, path safety)
- [ ] `--auto` build requires clean git state (overridable with `--allow-dirty`)
- [ ] Relay loops conditional + capped at 3 iterations

### Quality Gates

- [ ] All existing commands function correctly
- [ ] Single-planner mode unchanged for simple audits
- [ ] File-path and description modes work without acquisition
- [ ] Version bumped to 3.0.0 in CHANGELOG.md, README.md badge, plugin.json
- [ ] CHANGELOG follows existing format with per-phase categories and totals
- [ ] Modified SKILL.md files migrated from XML tags to markdown headings

## Risk Analysis & Mitigation

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Malicious page forges QUESTION/VERDICT markers | Medium | High | Nonce-prefixed markers; coordinator only parses matching nonce |
| DOM exceeds context window despite preprocessing | Low | High | 300KB hard cap with skeleton fallback; segment by cluster |
| Visual report screenshots too large as base64 | Medium | Medium | JPEG quality 80, 1x DPR; typical page = 1-3MB total HTML |
| Relay loop inconsistency across iterations | Low | Medium | Q&A delta only on re-dispatch; conditional iterations |
| Multi-planner reconciler misses conflict | Low | Medium | Reviewer still checks per-step; reconciler is additional safety net |
| Citation ID migration introduces errors | Low | High | Mechanical find-replace with diff verification per file |
| meta.json schema change breaks resume | Medium | Medium | Schema version bump; forward-compat (skip unknown versions); self-healing |
| Post-navigation redirect bypasses URL validation | Medium | High | Re-validate after DOMContentLoaded; abort on domain change |

## Documentation Plan

- [ ] Update README.md: new commands/flags, updated architecture diagram, v3.0.0 badge
- [ ] CHANGELOG.md entry for v3.0.0 following existing format
- [ ] Bump version in `.claude-plugin/plugin.json`
- [ ] Provide reinstall script for updating installed plugin copies

## Sources & References

### Origin

- **Brainstorm document:** [docs/brainstorms/2026-03-17-dual-source-auditor-brainstorm.md](docs/brainstorms/2026-03-17-dual-source-auditor-brainstorm.md)
  - Key decisions carried forward: dual-source acquisition, coordinator relay loops, multi-planner with reconciler, visual reports, output tiering, model pinning, quick-scan independence

### Internal References

- Current audit coordinator: `skills/cro/audit/SKILL.md`
- Auditor workflow: `workflows/audit.md`
- Review workflow: `workflows/review.md`
- Build workflow: `workflows/build.md`
- Report template: `templates/report.html.template`
- Meta schema: `templates/meta.json.template`
- URL validation: `references/url-validation.md`
- Conflict resolution: `references/conflict-resolution.md`
- Ethics gate: `references/ethics-gate.md`

### Research Agents (8 parallel reviews)

- **Agent-native architecture:** Single-line JSON questions, tiered model pinning, outcome-oriented prompts, STATUS completion signals
- **Skill authoring:** XML→markdown migration, Output Rules sections, 500-line SKILL.md limit, extract protocols to reference files
- **Architecture strategist:** Derive current_plan from plans_queue, phase dependency matrix, planner failure handling, DOM size limits
- **Agent parity:** --auto defaults for multi-planner checkpoint + reconciler conflicts, deprecate --ephemeral as no-op, --allow-dirty flag
- **Security sentinel:** Nonce-prefixed markers, post-navigation URL re-validation, HTML allowlist for visual report, meta.json read-path validation, DOM preprocessing strips sensitive fields
- **Pattern recognition:** Rename cro-acquirer, add Output Rules + Quality Check sections, reconciliation.md template, schema_version explicit task
- **Performance oracle:** DOM preprocessing (60-80% reduction), segment DOM by cluster, conditional relay iterations, Q&A delta only, JPEG 1x DPR, compare mode keep parallel
- **Simplicity reviewer:** Screenshot-based visual report (accepted), hybrid multi-planner threshold (accepted), simplified relay protocol (accepted via single-line JSON)

### SpecFlow Analysis

25 gaps identified and resolved. Critical gaps addressed: --auto + relay loop conflict, multi-PRD state tracking, quick-scan meta.json, auth pages, reconciler irreconcilable conflicts.
