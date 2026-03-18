# Multi-Planner Protocol

When an audit produces findings that are numerous and naturally cluster into distinct areas, the coordinator spawns parallel planners — one per cluster — instead of a single planner. This produces deeper, more focused plans per area.

## Trigger Criteria

Use multi-planner mode when findings meet BOTH conditions:
- **3 or more clusters** produced findings
- **Each cluster has 5+ findings** of its own

If either condition is not met, use single-planner mode (one planner receives all findings).

This is guidance, not a rigid rule. If findings are numerous but all concentrated in one cluster, a single planner is more appropriate regardless of total count.

## Dispatch

1. Group audit findings by the source cluster that produced them
2. Dispatch one planner per cluster IN PARALLEL using `model: "sonnet"`:
   - Each planner receives: its cluster's findings only + ethics gate + conflict resolution rules + context.md
   - Each planner is instructed to "produce a focused plan for this area only"
3. Collect all planner outputs
4. Write each to: `plan-{cluster-slug}.md` (e.g., `plan-visual-cta.md`, `plan-trust-conversion.md`)

**Planner retry:** If a planner fails, retry once. If retry fails, proceed without that cluster's plan and note the gap at the checkpoint.

## Reconciliation

After all planners complete, dispatch the reconciler (using `model: "opus"`):
- Read ${CLAUDE_PLUGIN_ROOT}/workflows/reconcile.md for instructions
- Pass all PRD files + ethics gate + conflict resolution rules
- Pass auto mode flag if --auto is active
- Collect output: reconciliation report + any amended plan steps
- Write amended steps back to the relevant PRD files
- Write reconciliation.md to the engagement directory

If reconciler fails: plans proceed unreconciled. Warn user at checkpoint.

## Checkpoint

Present the multi-planner checkpoint:

```
Your audit produced [N] findings across [M] areas. Separate action plans created:
1. [Cluster Name] ([N] steps) — [priority breakdown]
2. [Cluster Name] ([N] steps) — [priority breakdown]
3. [Cluster Name] ([N] steps) — [priority breakdown]

[If reconciler amended steps: "Reconciler resolved N cross-plan conflicts. See reconciliation.md for details."]

Options:
1. Build all sequentially (recommended order: [priority-sorted list])
2. Pick one to start
3. Deepen a specific plan
4. Save all and resume later
```

**If --auto:** select option 1 (build all in recommended priority order). Skip checkpoint.

## Sequential Review/Build

After the user picks an order (or --auto selects priority order):

1. Set `current_plan` in meta.json to the first cluster slug
2. Run the full review → build cycle for that PRD:
   - Reviewer receives only that PRD's plan + audit findings + context
   - Builder receives only that PRD's plan + review notes + context
   - Both use the relay loop protocol (see relay-loop-protocol.md)
3. After build completes, update that PRD's entry in `plans_queue` to `phase: "complete"`
4. Present a mini-checkpoint: "PRD [cluster] complete. Continue to next, or stop here?"
5. If --auto: continue to next PRD automatically
6. Repeat for each PRD in order

## File Naming

Multi-planner mode uses `{phase}-{cluster-slug}` naming:

```
plan-visual-cta.md
plan-trust-conversion.md
plan-context-platform.md
reconciliation.md
review-visual-cta.md        (written during that PRD's review cycle)
build-log-visual-cta.md     (written during that PRD's build cycle)
```

Templates (plan.md.template, review.md.template, build-log.md.template) are reused for the suffixed variants — same format, different filenames.

## meta.json State

Multi-planner adds these fields:

```json
{
  "plans_queue": [
    {"cluster": "visual-cta", "file": "plan-visual-cta.md", "phase": "complete"},
    {"cluster": "trust-conversion", "file": "plan-trust-conversion.md", "phase": "reviewing"},
    {"cluster": "context-platform", "file": "plan-context-platform.md", "phase": "pending"}
  ],
  "reconciled": true
}
```

Valid phases per entry: `pending`, `reviewing`, `building`, `complete`, `failed`

**Derived fields (not stored, computed at read time):**
- `current_plan` = first entry whose phase is not `pending` or `complete`
- Top-level `phase` = derived from queue state (e.g., if any entry is `reviewing`, top-level is `review`)

**Self-healing:** If `plans_queue` phase and file existence disagree, file existence wins. Resume and go-back protocols should verify filesystem state.

## Go-Back Protocol

- **Going back on active PRD:** delete only that PRD's downstream files (e.g., `review-{slug}.md`, `build-log-{slug}.md`). Verify file paths are children of the engagement directory before deletion. Reset that entry's phase in `plans_queue`.
- **Going back to audit:** delete ALL PRD files, reconciliation.md, and all downstream files. Reset plans_queue to empty. Re-run audit.
- **Order:** delete files FIRST, then update meta.json. If deletion fails partway, meta.json still reflects the previous (correct) state.
