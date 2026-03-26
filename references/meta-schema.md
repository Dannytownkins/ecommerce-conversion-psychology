# meta.json Validation Schema

Schema version: 2

## Required Fields

| Field | Type | Constraint |
|-------|------|------------|
| `id` | string | Pattern: `^\d{4}-\d{2}-\d{2}-[0-9a-f]{8}$` |
| `created` | string | ISO 8601 (e.g., `2026-03-19T14:30:00.000Z`) |
| `schema_version` | integer | `2` |
| `type` | enum | `audit`, `build`, `quick-scan`, `compare` |
| `phase` | enum | `pending`, `audit`, `plan`, `review`, `build`, `complete` |
| `platform` | enum | `shopify`, `nextjs`, `opencart`, `generic` |
| `page.type` | enum | `product`, `cart`, `checkout`, `homepage`, `category`, `landing`, `pricing`, `post-purchase` |
| `clusters_used` | array | Each: `visual-cta`, `trust-conversion`, `context-platform`, `audience-journey` |

## Optional Fields

`blocked` (boolean), `quick_scan` (boolean), `compare_target` (object), `page.url` (string|null), `page.file_path` (string|null), `min_priority` (string|null), `source_mode` (string|null), `devices_requested` (array), `devices_scanned` (array), `plans_queue` (array), `reconciled` (boolean), `screenshot_input` (object|null)

## When to Validate

Validate on **resume only** — not after the coordinator writes meta.json (it just wrote it, so it will always pass). On resume, verify all required fields. If any field is missing, null, or fails its constraint: fix immediately and log the correction.

Always update the `updated` field to the current ISO timestamp on every phase transition.
