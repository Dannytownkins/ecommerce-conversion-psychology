# Components Digest — Line Range Index

Use this file to read only the sections of `components.html` you need, instead of reading all 1115 lines. Pass `offset` and `limit` parameters to the Read tool.

**Source file:** `templates/components.html` (v4.5.0, ~1115 lines, ~162K tokens)

| # | Component | Lines | Tokens (approx) |
|---|-----------|-------|-----------------|
| 1 | Design Tokens (CSS custom properties) | 36–134 | ~2K |
| 2 | Font Embed Reference (instruction only) | 137–144 | ~0.2K |
| 3 | Report Header (eyebrow + hero title) | 147–218 | ~2K |
| 4 | Metadata Grid (3-column key-value pairs) | 221–254 | ~1K |
| 5 | Evidence Canvas (screenshot carousel + markers + thumbnails) | 257–418 | ~5K |
| 6 | Finding Card (numbered, severity-accented, with recommendation) | 421–636 | ~7K |
| 7 | Evidence Tier Badge (Gold/Silver/Bronze pill) | 639–674 | ~1K |
| 8 | Metrics Bar (intent reliability + projected lift) | 677–744 | ~2K |
| 9 | Summary Section (evidence confidence, severity dist, ethics placeholder) | 747–895 | ~5K |
| 10 | Limitations Banner | 898–924 | ~1K |
| 11 | Carousel Controller + Scroll-Sync (JavaScript) | 927–1018 | ~3K |
| 12 | Ethics Compliance (PASS + FAIL states) | 1021–1081 | ~2K |
| 13 | Escape Hatches (custom-note block) | 1084–1115 | ~1K |

## Common read patterns

**Building a visual report (full):** Read the entire file — all components needed.

**Adding/modifying a finding card only:** Read lines 421–674 (Finding Card + Evidence Tier Badge).

**Updating carousel/JS behavior:** Read lines 257–418 (Evidence Canvas) + 927–1018 (Carousel JS).

**Summary section changes:** Read lines 747–895 (Summary) + 1021–1081 (Ethics).

**CSS/design token changes:** Read lines 36–134 (Design Tokens).
