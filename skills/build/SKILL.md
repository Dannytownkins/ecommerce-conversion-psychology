---
name: cro:build
description: >-
  Builds a new ecommerce page from scratch using conversion psychology
  principles. Use when the user describes what they want to build rather
  than providing an existing page to audit. Three-phase relay: plan, review, build.
disable-model-invocation: true
argument-hint: "[description-or-structured-intake] [--auto] [--min-priority level] [--platform shopify|nextjs] [--visual] [--no-visual] [--ab-scaffold] [--ab-tool tool-name]"
---

<objective>
Build a new ecommerce page from scratch using conversion psychology principles. Four-phase relay: plan from intake, review, build. You are the coordinator.
</objective>

<flags>
--auto: Skip all checkpoint pauses. Halts on BLOCK verdict unless --force is also set.
--force: Override BLOCK verdicts in --auto mode. No effect without --auto.
--min-priority [level]: Filter findings. Scale: critical > high > medium > low.
--platform [name]: Skip platform detection. Values: shopify, nextjs, generic.
--visual: Auto-generate visual report (annotated screenshot mockup).
--no-visual: Skip visual report prompt, markdown only.
--ab-scaffold: Generate A/B test scaffold after plan phase. Pair with --ab-tool [tool].
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

**meta.json schema:** See ${CLAUDE_PLUGIN_ROOT}/references/meta-schema.md. Validate on resume only — not after writing.
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
Present plan checkpoint per audit/SKILL.md <checkpoint_plan>, plus A/B scaffold option.
</checkpoint_plan>

<phase_review>
Dispatch reviewer per audit/SKILL.md <phase_review>. Pass plan.md, context.md, and ethics gate.
</phase_review>

<checkpoint_review>
Present review checkpoint. BLOCK enforcement rules:

If --auto (without --force):
- If verdict is APPROVE or REVISE: proceed to build.
- If verdict is BLOCK: write `blocked: true` to meta.json, print "Review BLOCKED: {reason}. Use --auto --force to override.", and STOP.

If --auto AND --force:
- If verdict is BLOCK: print "⚠ WARNING: Review BLOCK overridden by --force. Reason was: {reason}", write `blocked: false` to meta.json, proceed to build.

Interactive mode: show BLOCK details and options as in /cro:audit.
</checkpoint_review>

<phase_build>
Dispatch builder per audit/SKILL.md <phase_build>. Always load platform file — this is build-from-scratch, so platform guidance is critical.
</phase_build>

<go_back_protocol>
Follow go-back protocol per audit/SKILL.md <go_back_protocol>.
</go_back_protocol>

<report_export>
Follow report export per audit/SKILL.md <report_export>.
</report_export>

<ab_scaffold>
Follow A/B scaffold per audit/SKILL.md <ab_scaffold>.
</ab_scaffold>

<ethics>
Pass ethics gate to all subagents per audit/SKILL.md <ethics>.
</ethics>
