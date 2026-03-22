---
name: cro:resume
description: >-
  List and resume in-progress CRO engagements. Use when returning
  to a previous audit, build, or comparison to check status or
  continue where you left off.
disable-model-invocation: true
argument-hint: "[--engagement-id <id>]"
allowed-tools: Read, Bash(ls *)
---

## Objective

List in-progress CRO engagements and resume one at its last checkpoint.

## Flags

- `--engagement-id <id>` — Skip listing, resume this engagement directly.

## Behavior

### If --engagement-id is provided

1. Read `docs/cro/{id}/meta.json`.
2. If not found, report error and list available engagements instead.
3. **Schema version check:**
   - If `schema_version` is 1: use legacy phase inference (see below)
   - If `schema_version` is 2: use v2 phase inference (see below)
   - If `schema_version` is unknown (>2): skip this engagement with warning: "Engagement {id} uses schema version {N}, which this plugin version does not support. Update the plugin."
4. Determine current phase.
5. Resume at that phase's checkpoint by handing off to the relevant coordinator (`/cro:audit` or `/cro:build`) with `--engagement-id {id}`.

### If no --engagement-id

1. Scan `docs/cro/*/meta.json` for all engagements.
2. Filter: exclude engagements where `phase` is `"complete"` and where `quick_scan` is `true`.
3. Skip engagements with `schema_version` > 2 (forward compatibility).
4. Sort by `updated` descending (fall back to `created` if `updated` is missing).
5. Present numbered list:

```
Recent engagements (in-progress only):
1. {id} — {phase} phase — {url or file_path} ({page_type})
2. {id} — {phase} phase — {url or file_path} ({page_type}) [multi-PRD: 2/3 complete]

Enter number to resume, or 'all' to see completed engagements:
```

For multi-PRD engagements (schema v2 with non-empty `plans_queue`), show progress: "[multi-PRD: X/Y complete]".

6. On selection, resume at the last completed phase's checkpoint.

### Phase Inference — Schema v1 (Legacy)

For engagements with `schema_version: 1` or missing `schema_version`:

- Has `build-log.md` → phase is "complete"
- Has `review.md` but no `build-log.md` → phase is "review"
- Has `plan.md` but no `review.md` → phase is "plan"
- Has `audit.md` but no `plan.md` → phase is "audit"
- Otherwise → phase is "pending"

### Phase Inference — Schema v2

For engagements with `schema_version: 2`:

**Single-planner mode** (empty `plans_queue`): same inference as v1.

**Multi-planner mode** (non-empty `plans_queue`):
1. Read `plans_queue` from meta.json
2. **Self-healing:** verify each entry's phase against filesystem:
   - If `plans_queue` says `phase: "complete"` but `build-log-{slug}.md` doesn't exist → reset to `phase: "building"` or `"reviewing"` based on what files exist
   - If `plans_queue` says `phase: "pending"` but `review-{slug}.md` exists → update to reflect actual state
3. Derive current state:
   - `current_plan` = first entry whose phase is not `pending` or `complete`
   - If all entries are `complete` → overall phase is "complete"
   - If all entries are `pending` → overall phase is "plan" (at multi-planner checkpoint)
   - Otherwise → resume at the active PRD's current sub-phase
4. Present multi-PRD status:
   ```
   Engagement {id} — Multi-PRD engagement:
   - visual-cta: complete (6 steps built)
   - trust-conversion: reviewing (5 steps planned)
   - context-platform: pending

   Options:
   1. Continue with trust-conversion (currently in review)
   2. Skip to context-platform
   3. Go back to audit
   ```

### BLOCKED Engagements

If `meta.json` has `blocked: true` or `review.md` (or any `review-{slug}.md`) contains a BLOCK verdict, show the BLOCK reason and offer: revise plan, re-review, or abort.

### meta.json Validation on Read

When reading any meta.json, validate:
- `phase` is one of the allowed enum values
- If `plans_queue` exists, each entry's `file` matches the pattern `plan-{slug}.md` and contains no path separators
- `source_mode` (if present) is one of: `url-dual`, `manual`, `webfetch`, `url-screenshot`, `screenshot`, `file`, `description`
- `screenshot_input` (if present) is an object with at least `filename` (string)
- `schema_version` is a known value (1 or 2)

If validation fails, warn: "meta.json for engagement {id} has invalid data: [details]. This engagement may be corrupted."

### Device Context Restoration

When resuming an engagement:
1. Read `devices_scanned` and `devices_requested` from meta.json (if present).
2. If `devices_scanned` is missing (old engagement without device support): default to `["desktop"]`.
3. Pass the device context to the coordinator when handing off.
4. **Partial failure retry:** If `devices_requested` includes a device not in `devices_scanned` (e.g., user requested "both" but only desktop completed), offer:
   "Mobile scanning failed in the previous session. Would you like to retry the mobile scan?"
   If yes, hand off to the coordinator with `--device mobile`.

### Cross-Mode Re-Audit Detection

When resuming an engagement, compare the current `source_mode` in meta.json against the mode that would be used for a new engagement on the same target:
- If `source_mode` changed between engagements (e.g., previous was `url-dual`, now the user provides a screenshot via `screenshot` mode), note the mode difference to the user:
  "Previous engagement used **{old_mode}** input. This session is using **{new_mode}**. Findings may not be directly comparable due to different input sources."
- If `source_mode` is `screenshot` and `screenshot_input` is present, restore the screenshot context (filename, dimensions if stored) when handing off to the coordinator.

### Resuming

Hand off to the relevant coordinator skill (`/cro:audit` or `/cro:build`) with `--engagement-id {id}`. The coordinator reads existing baton files and presents the appropriate checkpoint.

For multi-PRD engagements, the coordinator reads `plans_queue` and resumes at the active PRD's phase.
