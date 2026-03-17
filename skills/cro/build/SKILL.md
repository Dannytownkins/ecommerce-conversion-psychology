---
name: build
description: >-
  Builds a new ecommerce page from scratch using conversion psychology
  principles. Four-phase relay with structured intake for product pages,
  landing pages, pricing pages, and checkout flows.
disable-model-invocation: true
argument-hint: "[description-or-structured-intake] [--auto] [--min-priority level] [--platform shopify|nextjs] [--export-report] [--ab-scaffold] [--ab-tool tool-name]"
---

<objective>
Build a new ecommerce page from scratch using conversion psychology principles. Four-phase relay: plan from intake, review, build. You are the coordinator.
</objective>

<flags>
Same flags as /cro:audit (including --force). See audit SKILL.md for details.
</flags>

<intake>
Gather these 6 items conversationally (one at a time) OR accept as structured key-value pairs in $ARGUMENTS:

1. product: What's being sold, price range, purchase complexity (impulse vs. considered)
2. audience: Who's buying, what they care about, likely objections
3. assets: Reviews, images, copy, data they already have
4. platform: Shopify, Next.js, custom React, WordPress, etc.
5. constraints: Brand guidelines, regulatory requirements, existing design system
6. competitive_context: Even one sentence ("competing against X, differentiator is Y")

Structured format in $ARGUMENTS:
```
product: Premium wireless headphones, $299, considered purchase
audience: Tech-savvy 25-45, care about sound quality
assets: 47 reviews, professional photos
platform: nextjs
constraints: Dark mode design system, WCAG AA
competitive_context: Competing against Sony WH-1000XM6
```

If structured args provided: skip conversational gathering, only ask for missing fields.
If --auto and fields missing: abort with error listing missing fields.
Use sensible defaults for anything the user doesn't care about.
</intake>

<engagement_setup>
Same as /cro:audit — generate engagement ID, create directory, write context.md and meta.json with type: "build".

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
Same as /cro:audit — use ${CLAUDE_PLUGIN_ROOT}/references/platform-detection.md.
</platform_detection>

<domain_cluster_routing>
Same cluster selection table as /cro:audit. Determine page type from intake description.
</domain_cluster_routing>

<phase_plan>
Skip audit phase — go directly to planning from intake.

Dispatch planner with:
- Workflow instructions from ${CLAUDE_PLUGIN_ROOT}/workflows/plan.md
- Context from intake (written to context.md)
- Ethics gate from ${CLAUDE_PLUGIN_ROOT}/references/ethics-gate.md
- Conflict resolution from ${CLAUDE_PLUGIN_ROOT}/references/conflict-resolution.md
- Essential principles from ${CLAUDE_PLUGIN_ROOT}/references/essential-principles.md
- Cluster reference files based on page type

Write output to docs/cro/{engagement-id}/plan.md.
Update meta.json: phase → "plan".
</phase_plan>

<checkpoint_plan>
Same as /cro:audit plan checkpoint, plus A/B scaffold option.
</checkpoint_plan>

<phase_review>
Same as /cro:audit.
</phase_review>

<checkpoint_review>
Same as /cro:audit checkpoint_review, including BLOCK enforcement:

If --auto (without --force):
- If verdict is APPROVE or REVISE: proceed to build.
- If verdict is BLOCK: write `blocked: true` to meta.json, print "Review BLOCKED: {reason}. Use --auto --force to override.", and STOP.

If --auto AND --force:
- If verdict is BLOCK: print "⚠ WARNING: Review BLOCK overridden by --force. Reason was: {reason}", write `blocked: false` to meta.json, proceed to build.

Interactive mode: show BLOCK details and options as in /cro:audit.
</checkpoint_review>

<phase_build>
Same as /cro:audit. Always loads platform file if detected (this is build-from-scratch, so platform is critical).
</phase_build>

<go_back_protocol>
Same as /cro:audit.
</go_back_protocol>

<report_export>
Same as /cro:audit.
</report_export>

<ab_scaffold>
Same as /cro:audit.
</ab_scaffold>

<ethics>
Same as /cro:audit.
</ethics>
