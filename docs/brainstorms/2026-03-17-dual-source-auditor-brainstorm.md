# Brainstorm: CRO Plugin v3 — Accuracy, Architecture & Visual Reports

**Date:** 2026-03-17
**Status:** Ready for planning

---

## What We're Building

A comprehensive upgrade to the CRO plugin addressing 15 identified issues across accuracy, agent architecture, output quality, and reliability. The changes span every phase of the pipeline.

### Summary of Changes

1. **Dual-source acquisition** — URL scans capture sectioned screenshots + rendered DOM
2. **Sectioned viewport captures** — replace full-page screenshots with 3-6 focused captures
3. **Evidence provenance** — per-finding `SOURCE` tags (VISUAL / CODE / BOTH)
4. **Coordinator relay loops** — fix interactive workflows (reviewer, builder) that can't actually interact
5. **Multi-planner architecture** — heavy audits spawn parallel planners per area with a reconciler
6. **Annotated visual reports** — HTML reconstruction of the page with CRO callout overlays
7. **Model pinning** — auditor subagents pinned to Sonnet 4.6 minimum
8. **Quick-scan independence** — fresh scans every time with optional aggregate view
9. **Output tiering** — different defaults per mode (conversation / markdown / visual)
10. **Housekeeping** — meta.json maintenance, retry logic, citation IDs, template fixes, safety guards

---

## Part 1: Dual-Source Acquisition & Sectioned Captures

### The Problem

- URL mode relies on a single full-page screenshot. Agents never see HTML, CSS, or JS.
- Full-page screenshots are counterproductive — a 10,000px tall image overwhelms the agent, causing it to rush through analysis.
- File path mode reads source code but findings don't indicate what evidence backed each recommendation.

### Design

**New acquisition step** runs before auditor dispatch for URL inputs:
- Capture 3-6 **sectioned viewport screenshots** via agent-browser at natural content boundaries (headings, landmark elements, major dividers)
- Capture **rendered DOM** (post-JS execution) via agent-browser
- Pass both to the auditor as separate, labeled inputs

**Smart section detection:**
- Above-the-fold first (first viewport, ~1280x800)
- Agent-browser detects content section boundaries in the DOM
- Capture each section at viewport scale (3-6 depending on page length)
- Forces deliberate, section-by-section analysis

**New `SOURCE` field on every finding:**
- `VISUAL` — evidence from screenshot/visual inspection only
- `CODE` — evidence from rendered DOM / source code only
- `BOTH` — corroborated by both (highest confidence)

**Auditor workflow updates:**
- Cross-reference visual observations with code-level evidence
- Prefer `BOTH` findings (higher confidence)
- Flag contradictions (element in DOM but hidden, visual element not in code)
- Examine each sectioned screenshot against relevant cluster principles before moving to next

### Why This Approach

- **Separate acquisition step** keeps data gathering out of the auditor's judgment loop. Clean pipeline: gather → judge.
- **Sectioned captures** force deliberate analysis. 3-6 focused images > 1 massive image.
- **Smart sections** (DOM-detected) chosen over fixed viewport increments (cuts content mid-section) and key-areas-only (too rigid for unusual layouts).
- **Reusable** across `/cro:audit`, `/cro:quick-scan`, and `/cro:compare`.

---

## Part 2: Coordinator Relay Loops (Issues #1 & #2)

### The Problem

The reviewer and builder workflows describe **interactive behavior** (asking clarifying questions, presenting options, waiting for user input) but are dispatched as `context: fork` agents — single-shot execution with no back-and-forth capability. The reviewer's "specification hardening" questions and the builder's "Stuck → user decision" flow never actually fire.

### Design

**Coordinator relay loop:** Keep fork agents but have the coordinator relay questions back to the user.

1. Reviewer/builder output includes **structured question blocks** when they need input
2. Coordinator parses the output, presents questions to the user
3. Coordinator collects answers and re-dispatches (or sends follow-up context) to the agent
4. Loop continues until the agent returns a final output without questions

This preserves isolated context (fork agents stay stateless) while enabling the interactive features as designed.

**Reviewer checkpoint becomes:**
> "Ready to build? (1) Yes — proceed (2) No — go back to planning (3) Deepen plan (4) Save here and resume later"

### Why This Approach

- Preserves the plugin's core architecture: **isolated context per phase, no shared state between agents**
- Fork agents remain simple and stateless — complexity lives in the coordinator
- No new agent dispatch model needed — works with current Claude Code architecture

---

## Part 3: Multi-Planner Architecture with Reconciler

### The Problem

The planner has a hard cap of 12 steps. A full audit with 3 clusters can produce 15-25 findings. Capping at 12 forces the planner to cut valid HIGH-priority items. Bad ROI on the audit process.

Additionally, a single planner receiving findings across CTAs, trust, checkout, mobile, and performance tries to solve everything in one pass — producing a shallow plan for each area rather than a deep plan for any.

### Design

**After audit, coordinator analyzes finding density:**
- **Light audit** (≤10 findings) → single planner, business as usual
- **Heavy audit** (>10 findings spanning multiple page areas) → coordinator groups findings by area and spawns **parallel planners**, one per area

Each planner receives only the findings relevant to its area + ethics gate + conflict resolution. Each produces a focused PRD: `plan-ctas.md`, `plan-trust.md`, `plan-checkout.md`, etc.

**Reconciler agent** runs after all planners complete:
- Reads all PRDs together
- Identifies cross-plan conflicts (e.g., CTA planner says "orange buttons" while trust planner says "green trust badge next to CTA")
- Resolves conflicts using the existing priority hierarchy (legal > ethics > user constraints > domain guidance)
- Amends conflicting steps in the PRDs
- Produces `reconciliation.md` documenting what was changed and why

**Checkpoint after reconciliation:**
> "Your audit produced 23 findings across 4 areas. Separate action plans created:
> 1. CTAs & Visual Hierarchy (6 steps) — Critical + High
> 2. Trust & Social Proof (5 steps) — High + Medium
> 3. Checkout Flow (4 steps) — Critical + High
> 4. Performance & Mobile (3 steps) — Medium
>
> Options: (1) Build all sequentially (2) Pick one to start (3) Deepen a specific plan (4) Save all and resume later"

Each PRD goes through its own review → build cycle independently.

**Remove hard 12-step cap.** Replace with soft guidance:
- Group related changes into compound steps
- Order by priority, then dependency
- Phased grouping: Critical+High first, Medium+Low second

### Why This Approach

- **Parallel planners** produce deeper, focused plans instead of one shallow plan covering everything
- **Reconciler** catches cross-plan conflicts that isolated planners can't see
- **Per-PRD review/build cycles** mean the builder only holds one focused plan in context
- **User controls scope** — build one area at a time, or all sequentially
- Aligns with the plugin's core principle: **isolated context per agent, coordinator manages the relay**

---

## Part 4: Annotated Visual Reports

### The Problem

Current output is text-only (structured markdown findings or a text-based HTML report). Users can't see:
- What the agent actually perceived (was color captured correctly? was the layout understood?)
- Where recommendations apply spatially on the page
- How multiple recommendations interact visually when applied together

### Design

**Annotated HTML reconstruction:** Build a simplified HTML representation of the page layout from the rendered DOM, approximate the site's styling, and overlay CRO annotation callout bars at relevant sections.

The reconstruction:
- Shows the page structure as the agent "saw" it — transparency on agent perception
- Overlays orange/colored callout bars (e.g., `CRO CHANGE: VISUAL HIERARCHY — TOP 2 EMPHASIZED`) at specific page regions
- Is self-contained HTML (inline CSS, no external deps, same CSP as current reports)
- Doubles as a deliverable — shareable with clients, developers, stakeholders

**Full audit has an optional code diff upgrade:**
- Alongside the visual reconstruction, show actual code changes per finding
- User is informed this takes longer/costs more
- Premium tier output for users who want maximum detail

### Why This Approach

- **Shows what the agent saw** — if the reconstruction renders colors wrong, the user immediately knows the agent had bad input
- **Spatially anchors recommendations** — "move trust badges near CTA" becomes a visual placement, not a text description
- **Reveals visual conflicts** — two text recommendations that seem fine might obviously clash on the layout
- **Acts as a deliverable** — no interpretation needed, shareable as-is

---

## Part 5: Output Tiering

### The Problem

Quick-scan outputs only conversation text. Full audit writes markdown but the HTML report is hidden behind `--export-report`. `--ephemeral` conflicts with output format options. No visual report exists.

### Design

**Different defaults per mode:**

**Quick-scan:**
- Default: conversation output only (no files written)
- Prompt: "Want me to save this? (1) Visual report (2) Markdown (3) Both (4) No, conversation is enough"
- Keeps quick-scan fast and lightweight unless user opts in

**Full audit:**
- Default: markdown always written (baton system needs it for plan → review → build)
- Prompt after audit phase: "Want the visual report too? (1) Yes — annotated reconstruction (2) Yes + code diff (takes longer) (3) No, markdown is enough"

**Compare mode:**
- Same as full audit, visual report shows side-by-side reconstructions

**Flags for automation:**
- `--visual` / `--no-visual` — skip the prompt
- Remove `--ephemeral` and `--export-report` — replaced by the tiered output system

---

## Part 6: Quick-Scan Independence & Aggregation

### The Problem

Quick-scan has no progress memory (by design — full audit explicitly excludes quick-scans from comparison). But repeated scans of the same page produce no accumulated insight.

### Design

**Fresh scans every time** — no automatic memory or comparison between quick-scans.

This is intentional:
- Variability between scans reveals agent consistency — findings that appear every time are high-confidence
- Multiple independent scans give broader coverage than any single scan
- Users aren't anchored to one agent's perspective

**Optional aggregate view:** After 2+ quick-scans of the same URL exist, user can request aggregation:
- "Across N scans, these findings are consistent (high confidence) vs. appeared once (lower confidence)"
- Not automatic — user-initiated
- Implemented by coordinator scanning `docs/cro/*/meta.json` for matching URLs with `quick_scan: true`

**Full audit retains progress memory** — tracking FIXED/REGRESSED is meaningful when there's a build phase that changes things between audits.

---

## Part 7: Model Pinning

Auditor subagents pinned to **Sonnet 4.6 minimum** via the Agent tool `model` parameter. Ensures consistent analysis quality regardless of parent conversation model. Users on Opus still get Opus.

---

## Part 8: Housekeeping Fixes

### #3: Planner output format mismatch
**Problem:** Planner says "return ONLY the action plan table" but reviewer expects readable context.
**Fix:** Planner returns the action plan table + a brief "Conflicts resolved" section. Coordinator wraps it with engagement context when writing to plan.md.

### #5: --auto build mode safety
**Problem:** `--auto` runs through to build phase with no safety net for uncommitted changes.
**Fix:** In `--auto` mode, require clean git state before build phase. If `git status` shows uncommitted changes, abort with: "Build requires clean git state in --auto mode. Commit or stash first." Interactive mode keeps the existing stash suggestion.

### #7: meta.json `updated` field never maintained
**Problem:** Phase transitions update `phase` but never `updated`. Resume's sort-by-updated is meaningless.
**Fix:** Every phase transition also sets `updated` to current ISO timestamp.

### #11: No retry for failed auditors
**Problem:** If one cluster auditor fails in a multi-cluster audit, it's a permanent SKIP.
**Fix:** One automatic retry on failure. If retry fails, write SKIP and offer "Re-run [cluster]" as a checkpoint option. No full re-audit needed.

### #12: Go-back protocol atomicity
**Problem:** meta.json write and downstream file deletion aren't atomic — partial failure leaves inconsistent state.
**Fix:** Delete downstream files first, then update meta.json. If deletion fails, meta.json still reflects the old (correct) phase. Coordinator can detect and clean up orphaned files on resume.

### #13: Citation traceability
**Problem:** Findings cite reference files but there's no structured link to source URLs.
**Fix:** Add bracketed citation IDs to reference files (e.g., `[SPG-2021]`). Structure `sources.md` with matching IDs and URLs. Near-zero bloat in reference files (IDs are shorter than current inline citations).

### #14: --ab-tool validation
**Problem:** `--ab-tool` accepts any string with no validation or supported tool list.
**Fix:** Add a known-tools list (Optimizely, VWO, Shoplift, Statsig, LaunchDarkly, GA4). Unknown tools get: "I don't have specific patterns for [tool]. I'll generate generic scaffold — you may need to adapt the integration code."

### #6 & #15: Report template rigidity
**Problem:** HTML template always shows all sections regardless of engagement type.
**Fix:** Dynamic section rendering — report generator strips sections that don't apply. Quick-scan report shows findings only. Build-from-scratch skips audit findings. Compare shows side-by-side layout. Template section markers already exist (`SECTION:*_START/END`), generator just needs to remove inapplicable blocks.

---

## Key Decisions Summary

| # | Decision | Rationale |
|---|----------|-----------|
| 1 | Both sectioned screenshots AND rendered DOM for URL scans | Accuracy: visual + code evidence |
| 2 | 3-6 smart sectioned captures replace single full-page screenshot | Prevents agent rushing; forces deliberate analysis |
| 3 | Per-finding SOURCE tag (VISUAL / CODE / BOTH) | User transparency on evidence provenance |
| 4 | Coordinator relay loops for reviewer/builder interactivity | Preserves isolated-context architecture |
| 5 | Parallel planners per area + reconciler for heavy audits | Deeper plans, catches cross-plan conflicts |
| 6 | Remove 12-step hard cap, add phased grouping | Full audit ROI; Critical+High first, Medium+Low second |
| 7 | Builder stays isolated from reference files | Reviewer relay catches weak plans; builder focuses on execution |
| 8 | Annotated HTML reconstruction as visual report | Shows agent perception, spatially anchors recommendations, acts as deliverable |
| 9 | Quick-scan: conversation default, prompt to save | Keeps quick-scan fast; user opts into persistence |
| 10 | Full audit: markdown auto, visual report prompted | Baton system needs markdown; visual is opt-in |
| 11 | Full audit diff upgrade as premium option | User informed it takes longer/costs more |
| 12 | Quick-scan: fresh every time, optional aggregate | Variability reveals agent consistency; multiple perspectives > one |
| 13 | Pin auditors to Sonnet 4.6 minimum | Consistent quality floor |
| 14 | Compare mode: sequential pairs (your page → competitor) | Halves peak parallel agents (3 max instead of 6) |
| 15 | --auto build requires clean git state | Prevents accidental overwrite of uncommitted work |
| 16 | Replace --ephemeral/--export-report with --visual/--no-visual | Simpler flag system, tiered output |
| 17 | Citation IDs in reference files | Traceability: finding → principle → source URL |
| 18 | One auto-retry on auditor failure + manual re-run option | Resilience without full re-audit |

---

## Scope

### Files Modified
- `workflows/quick-scan.md` — dual-source input, SOURCE field, output tiering
- `workflows/audit.md` — dual-source input, SOURCE field, relay loop protocol
- `workflows/plan.md` — remove 12-step cap, phased grouping, multi-planner support
- `workflows/review.md` — structured question output for relay loop
- `workflows/build.md` — structured question output for relay loop
- `workflows/compare.md` — sequential dispatch, SOURCE field
- `workflows/report.md` — dynamic sections, visual reconstruction, diff mode
- `workflows/reconcile.md` — **new** — cross-plan conflict resolution
- `skills/cro/SKILL.md` — updated command descriptions
- `skills/cro/quick-scan/SKILL.md` — dual-source acquisition, output tiering, aggregate option
- `skills/cro/audit/SKILL.md` — relay loops, multi-planner dispatch, reconciler, output tiering, git safety
- `skills/cro/build/SKILL.md` — relay loops, multi-planner dispatch, reconciler
- `skills/cro/compare/SKILL.md` — sequential pairs, dual-source
- `skills/cro/resume/SKILL.md` — multi-PRD awareness, orphan cleanup
- `templates/audit.md.template` — add SOURCE field
- `templates/meta.json.template` — add source_mode, updated field maintenance
- `templates/report.html.template` — dynamic sections, visual reconstruction layout
- `references/*.md` (all 18 domain files) — add citation IDs
- `citations/sources.md` — structured citation entries with IDs
- Installed plugin copies in `~/.claude/skills/`

### New Files
- `workflows/reconcile.md` — reconciler agent workflow
- `workflows/visual-report.md` — visual reconstruction generator workflow (or extend report.md)

### Out of Scope
- Platform detection logic (unchanged)
- Ethics gate content (unchanged)
- A/B scaffold workflow (unchanged beyond --ab-tool validation)
- Reference file research content (unchanged — only citation IDs added)

---

## Updated Pipeline Flows

### Quick-Scan
```
Input → Acquisition (sectioned screenshots + DOM) → Auditor (single cluster, Sonnet 4.6) → Results
                                                                                            ↓
                                                                              "Save this?" → Visual / Markdown / Both / No
```

### Full Audit (Light — ≤10 findings)
```
Input → Acquisition → Auditors (parallel, Sonnet 4.6) → [checkpoint]
  → Planner (single) → [checkpoint: proceed/deepen/save/resume]
  → Reviewer (relay loop) → [checkpoint]
  → Builder (relay loop) → Done
  ↳ Visual report prompted at audit checkpoint
```

### Full Audit (Heavy — >10 findings)
```
Input → Acquisition → Auditors (parallel, Sonnet 4.6) → [checkpoint]
  → Planners (parallel, per area) → Reconciler → [checkpoint: build all/pick one/deepen/save]
  → Review per PRD (relay loop) → [checkpoint]
  → Build per PRD (relay loop) → Done
  ↳ Visual report prompted at audit checkpoint
```

### Compare
```
Your Input → Acquisition → Your Auditors (parallel) → collect
Competitor Input → Acquisition → Competitor Auditors (parallel) → collect
  → Comparison Analyst → [checkpoint]
  ↳ Visual report: side-by-side reconstructions
```

---

## Open Questions

_None — all key decisions resolved during brainstorming._
