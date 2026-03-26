# CRO Plugin — Development Standards

## Directory Structure

```
.claude-plugin/plugin.json    Plugin metadata
skills/                       Skill definitions (SKILL.md per command)
workflows/                    Phase workflows dispatched to subagents
references/                   Domain + operational reference files
templates/                    HTML report templates + component library
scripts/                      Python report generator + sync tools
platforms/                    Vendor-specific guidance (Shopify, Next.js)
citations/                    Source URLs for human verification
agents/                       Codex UI metadata
docs/cro/                     Engagement artifacts (gitignored)
```

## Versioning

- **MAJOR** (5.0.0): Breaking schema changes, workflow redesign
- **MINOR** (4.6.0): New skills, new reference files, new workflow phases
- **PATCH** (4.6.1): Bug fixes, wording fixes, template tweaks

Bump version in `.claude-plugin/plugin.json`. Keep `marketplace.json` description in sync.

## Pre-Commit Checklist

- [ ] Version bumped in `.claude-plugin/plugin.json`
- [ ] CHANGELOG.md updated (Keep a Changelog format)
- [ ] README.md component counts accurate (skills, workflows, references, templates)
- [ ] plugin.json description matches current component counts
- [ ] No hardcoded user paths (use `${CLAUDE_PLUGIN_ROOT}` or `%USERPROFILE%`)
- [ ] No `.DS_Store` or `__pycache__` tracked
- [ ] Line endings are LF (not CRLF)

## Skill Compliance

When adding or modifying skills:

- [ ] `name:` in frontmatter matches the skill's slash-command name (e.g., `cro:audit`)
- [ ] `description:` is third-person, starts with a verb, includes trigger context
- [ ] `argument-hint:` shows all accepted flags
- [ ] `disable-model-invocation:` is `true` for coordinator skills (audit, build, compare, quick-scan)
- [ ] XML section tags use snake_case (e.g., `<phase_audit>`, not `<phaseAudit>`)
- [ ] No duplicated content — shared schemas and specs go in `references/`
- [ ] Cross-references to other skills name the section (e.g., "see audit/SKILL.md `<phase_review>`"), not just "Same as /cro:audit"
- [ ] `${CLAUDE_PLUGIN_ROOT}` used for all internal file paths

## Reference File Standards

- Every domain reference file lives in `references/`
- Each finding is tagged with an evidence tier (Gold/Silver/Bronze) per `references/evidence-tiers.md`
- Operational files (ethics-gate, evidence-tiers, url-validation, etc.) are separate from domain files
- Citation URLs go in `citations/sources.md`, not inline in reference files

## Workflow Standards

- Workflows are dispatched to subagents with fresh context windows
- Subagents never write files (exception: acquisition agent writes baton.json, dom.html, screenshots)
- The coordinator writes all audit/plan/review/build outputs
- Baton files are the machine-readable interface between phases

## Validation Commands

```bash
# Check for duplicated meta.json schemas (should only be in references/meta-schema.md)
grep -r "MUST match pattern" skills/ --include="*.md" -l

# Check for hardcoded user paths
grep -rn "C:\\\\Users\\\\" . --include="*.md" | grep -v CHANGELOG | grep -v node_modules

# Check skill descriptions use third person
grep -A1 "^description:" skills/*/SKILL.md

# Verify .DS_Store not tracked
git ls-files | grep -i ds_store

# Check line endings
git diff --check
```

## Known Architecture Decisions

- **Coordinator pattern**: Skills are coordinators, not executors. They orchestrate subagents.
- **Fresh context per phase**: Each subagent gets only the files it needs. No compaction risk.
- **Baton hand-off**: `baton.json` carries structured data between acquisition and auditors.
- **Ethics gate**: Non-negotiable. Checked at every phase. Cannot be downgraded.
- **Code-fenced findings**: `generate-report.py` parses findings via regex. Bold-format (`**FINDING: FAIL**`) breaks parsing. Always use triple-backtick code fences.
- **File-before-meta invariant**: Write output files first, update meta.json last. Resume self-heals from inconsistent state by trusting file existence over meta.json phase.
