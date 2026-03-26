# Codex Source Notes

This repo is the source of truth for the Codex version of the ecommerce CRO toolkit.

The installed Codex runtime copy lives at:

`%USERPROFILE%\.codex\skills\ecommerce-conversion-psychology`

Do not treat the installed `.codex` copy as the canonical workspace. Make changes in this repo, then sync the Codex install from source.

## Managed Codex files

The Codex install is composed from this repo:

- `SKILL.md`
- `agents/openai.yaml`
- `citations/`
- `platforms/`
- `references/`
- `scripts/`
- `skills/`
- `templates/`
- `workflows/`
- `CHANGELOG.md`
- `README.md`
- `LICENSE`

## Sync workflow

Use:

`powershell -ExecutionPolicy Bypass -File .\scripts\sync-to-codex.ps1`

That script mirrors the Codex-managed directories and refreshes the root files needed by the installed skill.

## Why this setup exists

- The repo stays clean and git-backed.
- The `.codex` install stays disposable and easy to rebuild.
- Codex-specific wrapper files now live in source control instead of only in the installed copy.
- Shared CRO assets remain reusable across Codex and Claude-oriented packaging.
