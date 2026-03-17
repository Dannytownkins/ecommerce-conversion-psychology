---
name: quick-scan
description: >-
  Runs a quick CRO scan of an ecommerce page. Single domain cluster,
  3-5 highest-impact quick wins, no further phases. Faster and cheaper
  than a full audit.
disable-model-invocation: true
argument-hint: "[url-or-file-path-or-description] [--cluster visual-cta|trust-conversion|context-platform|audience-journey] [--min-priority level] [--platform shopify|nextjs]"
---

<objective>
Run a quick CRO scan — single domain cluster, 3-5 highest-impact quick wins, no further phases. Fastest and cheapest option.
</objective>

<flags>
--cluster [slug]: Override auto-selected cluster. Values: visual-cta, trust-conversion, context-platform, audience-journey.
--min-priority [level]: Filter findings. Default for quick-scan: high (only HIGH and CRITICAL).
--platform [name]: Skip platform detection.
</flags>

<mode_detection>
Determine input type from $ARGUMENTS:
- URL → existing page scan (acquire code same as /cro:audit)
- File path → existing page scan (read directly)
- Description text → from-scratch scan (auditor evaluates against principles without page code, outputs "the 5 most important things to get right")
</mode_detection>

<engagement_setup>
Same as /cro:audit but with type: "quick-scan", quick_scan: true in meta.json.
</engagement_setup>

<cluster_selection>
Auto-select first cluster from page-type table:

| Page Type | Default Cluster |
|-----------|----------------|
| Product page | visual-cta |
| Cart | trust-conversion |
| Checkout | trust-conversion |
| Homepage | visual-cta |
| Category/Collection | visual-cta |
| Landing page | visual-cta |
| Pricing/Plans | trust-conversion |
| Post-purchase | audience-journey |

Override with --cluster flag. If no flag, offer the user a choice with context:

"I'll scan **[cluster name]** ([brief description]). Other options:
- `--cluster visual-cta` — CTA design, color psychology, eye tracking, product video
- `--cluster trust-conversion` — Trust signals, social proof, checkout, pricing, biometric auth, cookie consent
- `--cluster context-platform` — Mobile UX, cognitive load, performance, search & filter, cookie consent
- `--cluster audience-journey` — Personalization, cross-cultural, post-purchase, social commerce, push notifications

Or run `/cro:audit [same-input]` for full multi-cluster coverage."

In automated mode (no human interaction), use default without asking.
</cluster_selection>

<dispatch>
Dispatch ONE auditor with:
- Quick-scan workflow from ${CLAUDE_PLUGIN_ROOT}/workflows/quick-scan.md
- Reference files for selected cluster ONLY (from ${CLAUDE_PLUGIN_ROOT}/references/)
- Page code or description
- Ethics gate from ${CLAUDE_PLUGIN_ROOT}/references/ethics-gate.md

Write findings to docs/cro/{engagement-id}/audit.md.
Update meta.json: phase → "complete".
</dispatch>

<output>
Present findings directly — NO checkpoint menu. This is one-and-done.

Format as natural language with actionable recommendations:

## Quick Scan Results

[1-2 sentence summary]

**Top quick wins:**
1. [Finding + specific recommendation]
2. [Finding + specific recommendation]
3. [Finding + specific recommendation]

Scan another area with `--cluster [name]`, or run `/cro:audit [same-input]` for full multi-cluster coverage.
</output>

<ethics>
Same as /cro:audit — pass ethics gate to auditor.
</ethics>
