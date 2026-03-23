---
name: ecommerce-conversion-psychology
description: Use when the user wants ecommerce CRO help: auditing an existing page, doing a quick conversion scan, comparing a page against a competitor, resuming an older engagement, or building a new ecommerce page from scratch using research-backed conversion psychology.
---

# E-Commerce Conversion Psychology

This is the Codex wrapper for the upstream CRO toolkit in this repo.

The source repo ships multiple Claude-plugin entrypoints under `skills/`:

- `skills/cro/SKILL.md`
- `skills/audit/SKILL.md`
- `skills/build/SKILL.md`
- `skills/compare/SKILL.md`
- `skills/quick-scan/SKILL.md`
- `skills/resume/SKILL.md`

In Codex, treat those as reference workflows and route the task by intent rather than by slash-command syntax.

## When to use this skill

Use it for five task shapes:

1. Audit an existing ecommerce page or component.
2. Run a quick-scan for 3-5 high-impact CRO issues.
3. Compare one page against a competitor.
4. Build or rewrite a page from scratch around conversion psychology principles.
5. Resume or inspect an existing engagement under `docs/cro/`.

## Input preference

Prefer inputs in this order:

1. Local file paths to page code or templates.
2. Screenshots, exported HTML, or existing engagement artifacts.
3. A clear written description of the page or funnel.
4. Public URLs only when the current environment can inspect them reliably.

If browser-style acquisition is unavailable, do not fake URL analysis. Ask for local source, screenshots, or pasted markup instead.

## Mode selection

Choose the lightest mode that fits the request:

- **Quick-scan** for one cluster and 3-5 findings.
- **Audit** for fuller multi-phase review with planning and implementation.
- **Compare** for two pages evaluated against the same clusters.
- **Build** for description-first page creation or rewrite.
- **Resume** when the user references an engagement ID or wants to continue prior work.

## Source-of-truth workflow files

Use the upstream skill docs as your first routing layer:

- Read `skills/quick-scan/SKILL.md` when the user wants a fast scan.
- Read `skills/audit/SKILL.md` when the user wants a full audit.
- Read `skills/compare/SKILL.md` for head-to-head analysis.
- Read `skills/build/SKILL.md` for from-scratch planning/build work.
- Read `skills/resume/SKILL.md` when resuming an engagement.

Then use the matching `workflows/*.md`, references, templates, citations, and platform guides as needed.

## Operating rules

- Keep research evidence visible and cite the supporting reference files used for recommendations.
- Apply the ethics gate on every task. Do not recommend fake urgency, hidden fees, deceptive defaults, review manipulation, or other dark patterns.
- Preserve the structured finding shape from `workflows/audit.md`, including the `ELEMENT` field used for annotation targeting.
- Reuse the supplied templates and component library instead of inventing a new report structure unless the user explicitly asks for a redesign.
- Use `scripts/generate-report.py` when it helps assemble report output from existing artifacts.
- Prefer platform-aware advice. Check `platforms/shopify.md` or `platforms/nextjs.md` when relevant.
- Load only the references needed for the current page type or cluster.

## Engagement artifacts

When the user wants a saved engagement trail, write artifacts under `docs/cro/<engagement-id>/`.

The current upstream artifact model is centered on:

- `meta.json`
- `context.md`
- `baton.json`
- `dom.html`
- `audit.md`
- `audit-mobile.md` when needed
- `plan.md`
- `review.md`
- `build-log.md`
- `visual-report.html`
- `report.html`
- `ab-scaffold.md`

Follow the schema and phase expectations described in the upstream skill files where practical, but execute the work inline in Codex rather than assuming Claude-specific command routing.

## Visual reports

If the user wants a self-contained visual report:

1. Read `workflows/visual-report.md`.
2. Reuse `templates/visual-report.html.template`.
3. Reuse `templates/components.html` and `templates/font-embed.css`.
4. Resolve citation URLs from `citations/sources.md`.
5. Position markers from `baton.json` element coordinates first, then fall back to section-level placement only when no element match exists.
6. Base64-encode screenshots at render time. Do not depend on separate `.b64` sidecar files.

If current tooling cannot capture fresh screenshots, limit the report to the screenshots or assets the user provided.

## Codex adaptation notes

- This is a Codex adaptation, not a verbatim Claude plugin runtime.
- Ignore slash-command syntax, `$ARGUMENTS`, `disable-model-invocation`, and Claude-only coordinator metadata.
- Treat browser-dependent acquisition, multi-agent relay orchestration, and checkpoint prompts as environment-dependent guidance, not hard runtime assumptions.
- The strongest support in Codex is for local file audits, screenshot-backed analysis, description-driven planning/build work, and artifact-based resume flows.
