<!-- RESEARCH_DATE: 2026-03-11 -->
# Platform Detection

Heuristics for detecting the ecommerce platform of a page being audited. Used to load platform-specific reference files for enhanced recommendations.

## Detection Priority

1. **User explicitly states platform** — via intake conversation or `--platform` flag. Always trust the user.
2. **File detection** (when source code is available):
   - `.liquid` files AND (`shopify` in package.json OR `config/settings_schema.json` exists) → **Shopify**
   - `.liquid` files WITHOUT Shopify indicators → **Ask user** (could be Jekyll, Bridgetown, 11ty)
   - `next.config.*` or package.json with `"next"` dependency → **Next.js**
   - `gatsby-config.*` or package.json with `"gatsby"` dependency → **Gatsby** (use generic, no platform file)
   - `wp-content/` directory or `functions.php` → **WordPress** (use generic, no platform file yet)
   - `catalog/view/` directory OR `system/engine/` directory OR `admin/controller/` directory → **OpenCart**
3. **DOM/HTML detection** (when preprocessed DOM is available):
   - DOM contains `catalog/view/` paths, `route=product/product` URL patterns, or `opencart` in meta generator → **OpenCart**
   - DOM contains `Shopify.theme` or `cdn.shopify.com` → **Shopify**
   - DOM contains `__NEXT_DATA__` or `_next/static` → **Next.js**
4. **URL patterns** (when only URL is available):
   - `*.myshopify.com` → **Shopify**
   - `*.vercel.app` → likely **Next.js** (ask to confirm)
   - `*.netlify.app` → could be anything (ask)
   - URL contains `route=product/product` or `index.php?route=` → **OpenCart**
5. **Ask the user:** "What platform is this built on? (Shopify, Next.js, OpenCart, or other)"

## Platform File Loading

| Platform | File | When Loaded |
|----------|------|-------------|
| Shopify | `${CLAUDE_PLUGIN_ROOT}/platforms/shopify.md` | Builder phase only |
| Next.js | `${CLAUDE_PLUGIN_ROOT}/platforms/nextjs.md` | Builder phase only |
| OpenCart | No platform file yet | Detected for meta.json accuracy; builder uses generic patterns |
| Generic | No additional file | Default for all other platforms |

Platform files enhance the builder's output with platform-specific patterns, anti-patterns, and code examples. They do NOT change audit or review behavior — those remain platform-agnostic.

## Disambiguation: .liquid Files

IMPORTANT: `.liquid` is used by multiple frameworks:
- **Shopify** — most common in ecommerce context
- **Jekyll** — static site generator
- **Bridgetown** — Ruby static site framework
- **11ty** — JavaScript static site generator

Never assume Shopify from `.liquid` alone. Require a second signal:
- `shopify` in package.json
- `config/settings_schema.json` exists
- `*.myshopify.com` URL
- User confirms Shopify

If only `.liquid` files with no second signal: ask "I see Liquid templates. Is this a Shopify theme, or another framework?"

## Future Platforms

When adding a new platform:
1. Create `platforms/{platform}.md` following the existing format
2. Add detection heuristics to this file
3. Add to the Platform File Loading table above
4. No changes needed to SKILL.md files — they load platform files dynamically
