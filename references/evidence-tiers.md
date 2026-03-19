<!-- CREATED: 2026-03-18 -->
# Evidence Tier Classification Criteria

**Purpose**: Classify every citation in the CRO plugin's reference files by publisher credibility. The tier determines the inline badge shown in visual reports.

---

## Tier Definitions

### Gold — Cite with confidence
Institutional research with rigorous methodology, large samples, and peer review.

| Source | Notes |
|--------|-------|
| Baymard Institute | Gold standard CRO benchmarks, large-N qualitative + quantitative research |
| NNGroup (Nielsen Norman Group) | Decades of eye-tracking and usability research, massive sample sizes |
| Peer-reviewed journals | PMC/NIH, SAGE, Oxford JCR, Springer, ScienceDirect, ACM CHI, IEEE |
| Spiegel Research Center | Northwestern University partnership, real sales data methodology |
| Stanford Web Credibility Project | B.J. Fogg, multi-year research program |
| Laws of UX | Curated academic principles, properly sourced to original research |
| Google CrUX (Chrome UX Report) | Real-user data at massive scale |
| Fitts's Law / Hick's Law / other HCI laws | Foundational, replicated across thousands of studies |
| ISO standards | International standards bodies |
| Apple HIG / Google Material Design | Platform guidelines backed by extensive internal research |
| W3C / WCAG | Standards body, authoritative for accessibility |

### Silver — Cite with context
Established industry voices with disclosed methodology but potential vendor incentive.

| Source | Notes |
|--------|-------|
| CXL Institute | Practitioner research, methodology usually disclosed, sells CRO tools |
| Stripe | Vendor, but rigorous A/B testing methodology at massive scale |
| Shopify enterprise blog | Vendor, but huge sample sizes from platform data |
| Forrester / McKinsey / Gartner | Analyst firms, real methodology, consulting incentive |
| Google Developers blog | Authoritative but selling Chrome/Lighthouse adoption |
| MarketingSherpa | Industry surveys with disclosed methodology |
| comScore / Statista | Data aggregators, large samples |
| PowerReviews | Vendor but partners with academic institutions |
| Monetate / Dynamic Yield | Vendor personalization data, large multi-client datasets |

### Bronze — Directional only
Practitioner case studies, single-site tests, content marketing, or small samples.

| Source | Notes |
|--------|-------|
| VWO Blog | Vendor case studies, single-site tests |
| Campaign Monitor | Vendor, email context extrapolated to web |
| HubSpot | Some large studies (330K+ CTAs = Silver for that specific study), but most blog content is Bronze |
| Neil Patel / QuickSprout | Content marketing disguised as research |
| GrowthSuite / Yieldify / TargetBay | Small vendor case studies |
| Blend Commerce | Single-client A/B tests |
| Unbounce | Vendor, landing page data |
| Econsultancy | Survey-based, variable methodology |
| Any "(2026)" blog repackaging older stats | Repackaged content, not original research |
| Single anonymous A/B test | No named source, no sample size, no methodology |

### Do Not Cite — Dead or unverifiable
- Dead URLs with no alternative source and no way to verify the claim
- Stats attributed to no specific study or author
- Numbers that appear only in content marketing with no traceable origin

**Handling**: Remove the specific stat from the finding. Keep the recommendation if the underlying principle is supported by other citations in the reference file. Findings with zero remaining citations survive without a citation line.

---

## Rules

1. **Tier is locked to publisher reputation** — never upgraded or downgraded based on a single citation's methodology.
2. **Quality flags are optional per-citation annotations** — used only when a citation's evidence quality notably diverges from its tier norm:
   - Bronze with unusually strong methodology: `Quality Flag: methodology note: N=50,000 across 12 sites`
   - Gold source with weak specific citation: `Quality Flag: editorial; no sample data for this claim`
3. **Unclassified citations default to Bronze at runtime** — any finding without an `evidence_tier` field renders as Bronze in visual reports.
4. **HubSpot special case**: HubSpot's 330K+ CTA study (Finding 1 in cta-design-and-placement.md) is Silver due to scale. Most other HubSpot blog citations are Bronze.

---

## Adding Evidence Tiers to Reference Files

Add `- **Evidence Tier**: Gold|Silver|Bronze` immediately after the `- **Source**: ...` line in each finding. Optionally add `- **Quality Flag**: [text]` when the citation's quality diverges from its tier norm.

**Before:**
```markdown
- **Source**: Spiegel Research Center, Northwestern University, 2017
- **Methodology**: Analysis of actual sales data...
```

**After:**
```markdown
- **Source**: Spiegel Research Center, Northwestern University, 2017
- **Evidence Tier**: Gold
- **Methodology**: Analysis of actual sales data...
```
