---
name: resume
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
3. Determine current phase (see Phase Inference below).
4. Resume at that phase's checkpoint by handing off to the relevant coordinator (`/cro:audit` or `/cro:build`) with `--engagement-id {id}`.

### If no --engagement-id

1. Scan `docs/cro/*/meta.json` for all engagements.
2. Filter: exclude engagements where `phase` is `"complete"` and where `quick_scan` is `true`.
3. Sort by `updated` descending (fall back to `created` if `updated` is missing).
4. Present numbered list:

```
Recent engagements (in-progress only):
1. {id} — {phase} phase — {url or file_path} ({page_type})
2. {id} — {phase} phase — {url or file_path} ({page_type})

Enter number to resume, or 'all' to see completed engagements:
```

5. On selection, resume at the last completed phase's checkpoint.

### Phase Inference

For engagements without an explicit `phase` field in meta.json:

- Has `build-log.md` → phase is "complete"
- Has `review.md` but no `build-log.md` → phase is "review"
- Has `plan.md` but no `review.md` → phase is "plan"
- Has `audit.md` but no `plan.md` → phase is "audit"
- Otherwise → phase is "pending"

### BLOCKED Engagements

If `meta.json` has `blocked: true` or `review.md` contains a BLOCK verdict, show the BLOCK reason and offer: revise plan, re-review, or abort.

### Resuming

Hand off to the relevant coordinator skill (`/cro:audit` or `/cro:build`) with `--engagement-id {id}`. The coordinator reads existing baton files and presents the appropriate checkpoint.
