<!-- RESEARCH_DATE: 2026-03-09 -->
# Cognitive Load Management in E-Commerce: Research Findings

**Total Findings**: 20
**Research Date**: 2026-03-09
**Methodology Note**: Decision fatigue and ego depletion research has significant replication concerns. Findings flagged accordingly.

## Top 3 Most Impactful Findings

1. **Finding 4 (Scheibehenne Meta-Analysis)**: Choice overload has a mean effect size of virtually zero across 63 conditions -- the "paradox of choice" is far more context-dependent than popularly believed. This reframes every choice-reduction intervention as needing moderator analysis first.
2. **Finding 11 (Baymard Checkout Fields)**: Reducing checkout form fields from the average 14.88 to the ideal 8 measurably improves conversion. Concrete, replicated, and immediately actionable.
3. **Finding 15 (Default Effect)**: Pre-selecting options shifts consent/selection rates from ~42% to ~82%. Defaults are the single most powerful choice architecture lever available in e-commerce.

---

## Findings

### Finding 1: Hick-Hyman Law -- Decision Time Scales Logarithmically with Choices
- **Source**: Hick, W.E. (1952). "On the rate of gain of information." Quarterly Journal of Experimental Psychology, 4(1), 11-26. Confirmed by Hyman, R. (1953).
- **Methodology**: Laboratory reaction-time experiments with varying numbers of stimulus-response alternatives. Hyman used 8 lights in a 6x6 matrix, measuring naming response times.
- **Key Finding**: Response time = a + b * log2(N+1), where N = number of equally probable choices. Decision time increases logarithmically, not linearly, with the number of options. Each doubling of choices adds a roughly constant increment to decision time.
- **E-Commerce Application**: Navigation menus, variant selectors, and filter panels should minimize equally-weighted options. The logarithmic relationship means going from 2 to 4 options costs the same cognitive time as going from 4 to 8 -- so the first few additions are the most expensive per-item.
- **Replication Status**: Replicated extensively. One of the most robust findings in cognitive psychology, confirmed across decades of research (Proctor & Schneider, 2018 review).
- **Boundary Conditions**: Applies to equally probable, unfamiliar choices. When users have strong prior preferences or when options are visually scannable (not memorized), the law's impact is attenuated. Does NOT directly apply to navigation menus where items remain visible on screen.

### Finding 2: The Jam Study -- More Choice Can Reduce Purchase
- **Source**: Iyengar, S.S. & Lepper, M.R. (2000). "When Choice is Demotivating: Can One Desire Too Much of a Good Thing?" Journal of Personality and Social Psychology, 79(6), 995-1006.
- **Methodology**: Field experiment at an upscale grocery store (Draeger's). Tasting booth displayed either 6 or 24 varieties of jam. Measured attraction to booth and subsequent purchase behavior.
- **Key Finding**: The extensive display (24 jams) attracted more initial interest (60% stopped vs. 40% for 6 jams). However, 30% of those who sampled from the limited display (6) purchased, compared to only 3% from the extensive display (24). Roughly 10x more likely to purchase with fewer options.
- **E-Commerce Application**: Product listing pages showing fewer, curated options may convert better than exhaustive catalogs. Particularly relevant for category pages and variant selectors.
- **Replication Status**: REPLICATION CONCERNS. See Finding 4 (Scheibehenne meta-analysis). The effect is real in some contexts but not universal. The original study was a single field experiment with limited sample size.
- **Boundary Conditions**: Effect is strongest when consumers lack prior preferences, when options are similar/hard to compare, and when the choice set is complex. Does not apply when consumers are experts or have well-defined preferences.

### Finding 3: Choice Overload Moderators -- Four Key Factors
- **Source**: Chernev, A., Bockenholt, U., & Goodman, J. (2015). "Choice overload: A conceptual review and meta-analysis." Journal of Consumer Psychology, 25(2), 333-358. Meta-analysis of 99 observations, N=7,202.
- **Methodology**: Meta-analysis across 99 experimental observations from prior research.
- **Key Finding**: Four factors reliably moderate choice overload: (1) Decision task difficulty -- more attributes per option increases overload; (2) Choice set complexity -- similar or equally attractive options increase overload; (3) Preference uncertainty -- consumers without clear preferences are more vulnerable; (4) Decision goal -- effort-minimizing goals (quick purchase) amplify overload vs. browsing goals.
- **E-Commerce Application**: Choice overload interventions should target high-uncertainty shoppers (new category entrants) more than returning customers. Simplify variant presentation most aggressively for complex products where options are hard to differentiate. Browsing-mode pages (inspiration galleries) can handle more options than purchase-mode pages.
- **Replication Status**: Replicated (meta-analytic confirmation across 99 observations).
- **Boundary Conditions**: When consumers have clear preferences or expertise, larger assortments can actually be beneficial. Effect is weaker for hedonic/fun categories where browsing is the goal.

### Finding 4: Choice Overload Mean Effect is Near Zero
- **Source**: Scheibehenne, B., Greifeneder, R., & Todd, P.M. (2010). "Can There Ever Be Too Many Options? A Meta-Analytic Review of Choice Overload." Journal of Consumer Research, 37(3), 409-425. Meta-analysis of 63 conditions from 50 experiments, N=5,036.
- **Methodology**: Meta-analysis of 50 published and unpublished experiments (63 conditions, N=5,036).
- **Key Finding**: The mean effect size of choice overload was virtually zero (d near 0), with considerable variance between studies. Some studies found strong choice overload, others found the opposite. No sufficient conditions for choice overload could be identified. The effect is highly context-dependent.
- **E-Commerce Application**: Blindly reducing product assortment is NOT a reliable conversion strategy. The popular narrative of "fewer choices = more sales" is an oversimplification. Interventions should focus on the moderating conditions (preference uncertainty, set complexity) rather than raw option count.
- **Replication Status**: This IS the replication/meta-analytic check. It challenges the generalizability of Iyengar & Lepper (2000).
- **Boundary Conditions**: The near-zero mean hides significant heterogeneity. The effect IS real in specific contexts (high complexity, low expertise, similar options) -- it is just not universal.

### Finding 5: Miller's Law -- Working Memory Capacity of 7 Plus or Minus 2
- **Source**: Miller, G.A. (1956). "The Magical Number Seven, Plus or Minus Two: Some Limits on Our Capacity for Processing Information." Psychological Review, 63(2), 81-97.
- **Methodology**: Review and synthesis of experimental findings on absolute judgment and immediate memory span.
- **Key Finding**: The span of immediate (working) memory is approximately 7 items (range 5-9). This applies to items held simultaneously in working memory, not to items visible on screen.
- **E-Commerce Application**: Commonly misapplied to navigation menus. Since menu items remain visible on screen, users do not need to memorize them, and the 7-item limit does not directly constrain menu length. However, Miller's Law DOES apply to: comparison tasks (comparing more than 5-7 product attributes simultaneously is cognitively expensive), mental shortlists (users comparing products they've seen across pages), and attribute recall after leaving a product page.
- **Replication Status**: Replicated. Foundational finding in cognitive psychology.
- **Boundary Conditions**: Does NOT apply to recognition tasks (items visible on screen). Only applies when information must be held in working memory. Chunking can expand effective capacity.

### Finding 6: The F-Pattern -- How Users Scan Product Pages
- **Source**: Nielsen, J. (2006). "F-Shaped Pattern for Reading Web Content." Nielsen Norman Group. Eye-tracking study with 232 users across thousands of web pages.
- **Methodology**: Eye-tracking study, 232 participants, heatmap analysis across multiple page types including e-commerce product pages.
- **Key Finding**: Users scan in an F-shaped pattern: (1) horizontal sweep across the top, (2) shorter horizontal sweep partway down, (3) vertical scan down the left side. Users read the first two words of a line far more often than subsequent words. The F-pattern is the default when no strong visual cues redirect attention.
- **E-Commerce Application**: Place the most critical product information (name, price, primary image, CTA) in the top-left quadrant. Start bullet points and spec labels with information-carrying words. Key differentiators should appear in the first two content blocks, not buried below. Use strong visual hierarchy (headings, whitespace) to break the F-pattern and draw eyes to conversion elements.
- **Replication Status**: Replicated across multiple NNGroup studies. Confirmed on mobile with adaptations.
- **Boundary Conditions**: The F-pattern emerges when content lacks strong visual hierarchy. Well-designed pages with clear headings, images, and visual cues can redirect scanning to more useful patterns (layer-cake, spotted, commitment patterns).

### Finding 7: Progressive Disclosure Reduces Overwhelm
- **Source**: Nielsen Norman Group, multiple articles (2006-2024). Originally formulated by J.M. Keller in instructional design. NNGroup usability testing validates the principle.
- **Methodology**: Qualitative usability testing, observational studies of user behavior on product pages.
- **Key Finding**: Hiding secondary information behind tabs/accordions reduces initial cognitive load. NNGroup recommends: show primary information (price, images, key specs, CTA) immediately; place secondary details (full specs, shipping info, reviews) in accordions or tabs. Amazon's product pages exemplify this with a layered content approach. Tabs suit a few long sections; accordions suit many short sections.
- **E-Commerce Application**: Product page information hierarchy should be: (1) Above the fold: product image, title, price, variant selector, Add to Cart; (2) First accordion/tab section: key features/description; (3) Subsequent sections: full specifications, shipping/returns, reviews. This matches observed user scanning behavior.
- **Replication Status**: Replicated across multiple usability studies. Well-established UX principle.
- **Boundary Conditions**: Over-hiding information can backfire. If critical purchase-decision info (sizing charts, compatibility) is hidden too deep, users may not find it and bounce instead. Progressive disclosure works best when the primary layer contains enough information for 80% of purchase decisions.

### Finding 8: Baymard Filtering Benchmarks -- Common Failures
- **Source**: Baymard Institute (2023 benchmark update). 25 rounds of qualitative usability testing, 4,400+ test participant/site sessions. Benchmark of 68 large e-commerce sites, 6,100+ UX performance scores.
- **Methodology**: Moderated "Think Aloud" lab usability testing, plus heuristic evaluation of 327 top-grossing US/EU e-commerce sites against 771 UX guidelines.
- **Key Finding**: 32% of sites do not display an overview of applied filters, causing users to lose track of their narrowing criteria. 62% fail to explain industry-specific filter terminology. 61% do not promote important filters. 32% do not allow applying multiple values within the same filter type. 64% do not offer all four essential sort options (Price, Rating, Best-Selling, Newest).
- **E-Commerce Application**: Always show applied filters in a visible summary bar. Explain non-obvious filter terms. Promote the most-used filters (e.g., size, price) above less common ones. Allow multi-select within filter categories. These are table-stakes UX that the majority of sites still fail.
- **Replication Status**: Replicated (longitudinal benchmarking across multiple years and hundreds of sites).
- **Boundary Conditions**: Specific percentages reflect top-grossing US/EU sites and may not generalize to all markets. Small catalogs (<50 products) may not need complex filtering.

### Finding 9: Decision Fatigue and Variant Count
- **Source**: Multiple sources. Winsomemarketing.com summary of research from Journal of Marketing Research and related publications. See also: Vohs et al. (2008) on decision fatigue -- BUT NOTE replication concerns.
- **Methodology**: Various -- lab experiments, field studies, and behavioral analysis.
- **Key Finding**: Shoppers experience measurable cognitive fatigue after comparing 7-9 product options, with satisfaction decreasing and abandonment increasing. More than 12 total decision points across all product attributes (size + color + material + add-ons) correlates with slower response times and higher cart abandonment. Each additional decision dimension compounds the effect multiplicatively.
- **E-Commerce Application**: For products with many variants, limit simultaneously visible options per dimension. Show 5-7 color swatches with "more" expansion. Pre-filter sizes to likely matches. Avoid presenting all variant combinations as a flat matrix. Sequential decision-making (pick color, then size, then material) reduces simultaneous cognitive load vs. a combined matrix.
- **Replication Status**: REPLICATION CONCERNS for the ego depletion mechanism (see Finding 10). The behavioral pattern of increased abandonment with more variants is consistently observed in analytics data, but the theoretical mechanism (depleted willpower) is disputed.
- **Boundary Conditions**: Expert shoppers (e.g., someone buying their 10th pair of running shoes) handle more variants. Fashion/aesthetic categories tolerate more color options because color IS the product differentiator.

### Finding 10: Ego Depletion -- The Theoretical Foundation Has Crumbled
- **Source**: Hagger, M.S. et al. (2016). Registered Replication Report: 23 labs, 2,000+ participants. Vohs, K.D. et al. (2021). Multi-lab replication: 36 labs, 3,531 participants. Carter & McCullough (2015) meta-analysis correcting for publication bias.
- **Methodology**: Pre-registered multi-lab replications of the ego depletion effect (Baumeister's limited willpower resource model).
- **Key Finding**: The 2016 registered replication across 23 labs found NO evidence of ego depletion (effect not significantly different from zero). The 2021 replication across 36 labs found d=0.06, an order of magnitude smaller than the original meta-analytic estimate (d=0.62 from Hagger et al. 2010). Carter & McCullough (2015) showed the original 2010 meta-analysis was inflated by publication bias; correcting for this reduced the effect to d~0.2, not significantly different from zero.
- **E-Commerce Application**: Claims that "users run out of willpower after making choices" should be treated skeptically. While sequential decision-making does slow users down (Hick's Law provides the mechanism), the "depleted resource" model underlying much decision fatigue advice is not supported. Focus on information architecture and cognitive load reduction rather than "willpower conservation."
- **Replication Status**: FAILED TO REPLICATE. Two large-scale pre-registered replications found near-zero effects. This is one of the most prominent replication failures in psychology.
- **Boundary Conditions**: Fatigue, boredom, and reduced motivation during extended shopping sessions are real phenomena -- they just do not appear to operate through a "limited willpower resource" mechanism. Practical UX recommendations to simplify decisions remain valid; the theoretical justification has changed.

### Finding 11: Checkout Form Fields -- The Optimal Count
- **Source**: Baymard Institute (2024 benchmark update). "Checkout Optimization: Minimize Form Fields." Based on 25 rounds of usability testing.
- **Methodology**: Qualitative moderated usability testing + benchmarking of top US e-commerce checkout flows. Longitudinal tracking of average form field counts (2019-2024).
- **Key Finding**: The average US checkout has 14.88 form fields (23.48 total form elements). The ideal is 8 form fields (12 total elements: 7 fields, 2 checkboxes, 2 dropdowns, 1 radio button). The industry average has improved from 12.7 fields (2019) to 11.3 fields (2024). 18% of users abandon orders specifically because checkout is too long/complicated. Single-page checkout systems show up to 21.8% conversion rate increase. Inline validation yields ~22% improvement.
- **E-Commerce Application**: Audit checkout forms and eliminate every non-essential field. Use address auto-complete to reduce manual entry. Combine name into one field where possible. Default to shipping = billing. Every field removed is friction removed.
- **Replication Status**: Replicated (longitudinal benchmarking over 5+ years, consistent findings).
- **Boundary Conditions**: B2B checkouts legitimately need more fields (company name, PO number, tax ID). International shipping may require additional fields. The 8-field ideal assumes domestic single-address orders.

### Finding 12: Default Selections Dramatically Shift Behavior
- **Source**: Johnson, E.J. & Goldstein, D.G. (2003). "Do Defaults Save Lives?" Science, 302(5649), 1338-1339. Lab experiment + cross-country comparison.
- **Methodology**: Online experiment with ~160 participants randomly assigned to opt-in, opt-out, or neutral framing for organ donation. Cross-country comparison of donation consent rates.
- **Key Finding**: Opt-out default: 82% consent. Neutral framing: 79% consent. Opt-in default: 42% consent. The default option nearly doubled participation rates. Cross-country data showed consistent patterns.
- **E-Commerce Application**: Pre-selecting a default variant (e.g., the most popular size, a neutral color) reduces the number of active decisions required. Analytics data suggests black/neutral colors convert at 2-3x the rate of unusual colors -- making these the default shows the highest-converting option first. However, there is an ethical dimension: dark patterns using defaults to add unwanted items to cart erode trust.
- **Replication Status**: Replicated. The default effect is one of the most robust findings in behavioral economics, confirmed across dozens of studies and domains.
- **Boundary Conditions**: Defaults are most powerful for low-involvement decisions or when users are uncertain. For high-involvement purchases where users have strong preferences, defaults matter less. Ethically questionable defaults (pre-checked insurance add-ons) can generate backlash and regulatory scrutiny.

### Finding 13: Color Variant Defaults and Conversion
- **Source**: Peasy.nu analytics summary; CommandC e-commerce optimization data. Industry analytics data.
- **Methodology**: Aggregate e-commerce analytics across multiple stores examining variant-level conversion rates.
- **Key Finding**: Black and neutral colors convert at 2-3x the rate of bright or unusual colors. A product with 2% aggregate conversion might show black at 3.5% and yellow at 0.8%. The first variant displayed on a product page receives disproportionate views and purchases. Placing the best-converting variant as the default/first option is a significant lever.
- **E-Commerce Application**: Set the default swatch/variant to the highest-converting option (typically neutral colors). Do not bury top performers at the end of a swatch list. Consider variant-level analytics as a core optimization metric alongside page-level conversion.
- **Replication Status**: Observed consistently in industry analytics data across multiple stores. Not a controlled experiment but a robust observational pattern.
- **Boundary Conditions**: Category-dependent. Fashion/statement products may convert better with the hero colorway as default. Seasonal products may need dynamic defaults. The neutral-converts-best pattern is strongest in basics/essentials categories.

### Finding 14: Pricing Table Cognitive Load -- 3-4 Tiers Maximum
- **Source**: Multiple UX sources including NinjaTables research, Kinde SaaS pricing guidelines, CXL Institute. Rooted in Miller's Law application.
- **Methodology**: Industry best practice synthesis, A/B testing case studies, usability observations.
- **Key Finding**: 3-4 pricing tiers is the practical maximum before conversion drops. Listing more than 8-12 feature rows in a comparison table causes scanning fatigue. One case study (BaseKit) presented 23 features across 6 plans -- 138 individual comparisons -- causing decision paralysis. Highlighting a "recommended" middle tier reduces cognitive load and steers ~28% more users to annual/pro plans (from placement + "popular" label A/B tests).
- **E-Commerce Application**: Limit pricing tables to 3 tiers. Show 8-12 key differentiating features, not exhaustive lists. Highlight the recommended tier with visual emphasis and a "Most Popular" or "Best Value" label. Use checkmarks/X marks rather than text descriptions for binary features.
- **Replication Status**: Observed across multiple A/B tests and industry case studies. The 3-tier convention is strongly established in SaaS, less tested in physical product e-commerce.
- **Boundary Conditions**: Enterprise/B2B buyers may need more tiers and features for procurement justification. Highly technical products may require more feature rows. The 3-tier rule is strongest for consumer-facing pricing.

### Finding 15: Social Proof Badges Lift Conversion 12-55%
- **Source**: WiserNotify product badge analysis; Profitero analysis of Amazon badges; Plumrocket retailer case studies; various A/B tests.
- **Methodology**: A/B tests and observational analytics across e-commerce platforms.
- **Key Finding**: "Best Seller" badges increased Amazon glance views by ~45% (Profitero analysis). Amazon's Choice badge correlated with ~25% conversion uplift. Trust badge A/B test: +12.2% conversion rate, +14.3% transactions, +16.6% revenue. Fitness e-commerce social proof widget: +34.67% conversion. Industry average for social proof widgets: +15-30% sales uplift depending on placement.
- **E-Commerce Application**: Add "Best Seller," "Most Popular," or "Staff Pick" badges to top-performing products. Place trust/social proof badges near the Add to Cart button. These labels serve as decision simplification heuristics -- they reduce the cognitive cost of comparison by providing an external recommendation signal.
- **Replication Status**: Replicated across many A/B tests and platforms. Effect sizes vary but direction is consistently positive.
- **Boundary Conditions**: Badge inflation (too many badges) dilutes effectiveness. Generic badges without credible backing ("Editor's Choice" with no editor) can reduce trust. The effect is strongest for mid-consideration purchases where users lack strong preferences.

### Finding 16: Chunking Product Attributes Improves Processing
- **Source**: Laws of UX (lawsofux.com) -- Chunking principle. NNGroup, "How Chunking Helps Content Processing." Rooted in Miller (1956).
- **Methodology**: UX design principle derived from cognitive psychology experiments on working memory.
- **Key Finding**: Grouping related information into meaningful chunks reduces cognitive load by presenting fewer, larger, recognizable units. Users process grouped specifications faster than flat lists. Chunking aligns with natural categorization (e.g., "Dimensions" group vs. listing height, width, depth separately in a flat spec list).
- **E-Commerce Application**: Group product specifications into labeled categories (Physical: dimensions/weight; Performance: speed/capacity; Compatibility: OS/devices). Use visual separation (cards, borders, whitespace) between groups. For comparison tables, group rows by category rather than presenting a flat alphabetical list.
- **Replication Status**: Replicated. Chunking is a foundational cognitive principle.
- **Boundary Conditions**: Information that needs to be searched/scanned quickly should NOT be chunked into collapsed sections. Over-chunking (too many small groups) fragments information. The groupings must be meaningful to users, not just to the product team.

### Finding 17: Cart Abandonment -- 70% Average, UX is Key Driver
- **Source**: Baymard Institute (2024). "50 Cart Abandonment Rate Statistics." Meta-analysis of 50 different studies.
- **Methodology**: Aggregation of 50 independent cart abandonment studies.
- **Key Finding**: The average cart abandonment rate is 70.22%. Of those who abandon, 18% cite "checkout process too long/complicated" as the reason. 87% of shoppers abandon when faced with complicated checkouts (broader survey data). Cognitive load at checkout is one of the largest single conversion barriers in e-commerce.
- **E-Commerce Application**: Checkout simplification is the highest-ROI cognitive load intervention. Every unnecessary form field, confusing label, or surprise cost adds cognitive friction. Guest checkout, progress indicators, and inline validation are proven friction reducers.
- **Replication Status**: Replicated (meta-analysis of 50 studies, consistent findings).
- **Boundary Conditions**: Abandonment rates vary by industry (travel is higher, digital goods lower). Not all abandonment is friction-related -- price comparison shopping and "saving for later" behavior account for a portion.

### Finding 18: NNGroup Scanning Patterns -- Layer-Cake for Product Content
- **Source**: Nielsen Norman Group (2019). "The Layer-Cake Pattern of Scanning Content on the Web." Eye-tracking research.
- **Methodology**: Eye-tracking studies across multiple content types.
- **Key Finding**: When pages use strong, descriptive headings, users adopt a "layer-cake" scanning pattern -- reading headings horizontally while skipping body text. This is more efficient than the F-pattern and allows users to quickly locate relevant sections. The pattern emerges when headings are visually distinct and information-carrying.
- **E-Commerce Application**: Use clear, descriptive section headings on product pages ("What's in the Box," "Technical Specifications," "Shipping & Returns"). Bold, larger headings create the visual cues that shift users from inefficient F-scanning to efficient layer-cake scanning. This is directly actionable for product page information architecture.
- **Replication Status**: Replicated across NNGroup eye-tracking studies.
- **Boundary Conditions**: Requires well-designed visual hierarchy. Pages with weak or generic headings ("Details," "Info") do not trigger this pattern.

### Finding 19: Filter Promotion and Cognitive Cost
- **Source**: Baymard Institute. "Consider Promoting Important Filters (61% Don't)." Qualitative usability testing.
- **Methodology**: Moderated usability testing with think-aloud protocol across major e-commerce sites.
- **Key Finding**: 61% of sites do not promote their most important filters. Users confronted with 15+ filter types of equal visual weight experience scanning fatigue. Promoting 3-5 key filters (e.g., size, price, color) above the full filter list reduces cognitive cost of the filtering task. Horizontal filter bars for key filters + vertical sidebar for advanced filters is an emerging best practice.
- **E-Commerce Application**: Identify the 3-5 most-used filters per category via analytics. Promote these visually (larger, higher placement, horizontal bar). Relegate less-used filters to an expandable "More Filters" section. This applies progressive disclosure to the filtering interface itself.
- **Replication Status**: Replicated (longitudinal Baymard benchmarking).
- **Boundary Conditions**: The optimal promoted filter set varies by category. Technical categories (electronics) need different promoted filters than fashion. User research per category is required.

### Finding 20: Step-by-Step vs. All-at-Once Forms
- **Source**: Zuko analytics benchmarking data; Baymard checkout research; multiple CRO case studies.
- **Methodology**: A/B testing and form analytics across e-commerce checkouts.
- **Key Finding**: Multi-step checkout with progress indicators can increase completion rates, but single-page checkout has shown up to 21.8% conversion improvement in some tests. The key variable is not steps vs. single-page, but perceived complexity -- showing 15+ fields at once overwhelms, but forcing 5 unnecessary page loads frustrates. Inline validation improves form completion by ~22% regardless of single vs. multi-step format.
- **E-Commerce Application**: For short forms (8 or fewer fields), single-page is generally superior. For longer flows (account creation + shipping + payment + review), multi-step with a clear progress indicator reduces perceived complexity. Always implement inline validation. The cognitive goal is: never show the user more than they can process in one glance while never making them click more than necessary.
- **Replication Status**: Replicated across multiple A/B testing datasets.
- **Boundary Conditions**: Mobile vs. desktop matters significantly. Mobile screens show fewer fields at once, making multi-step more natural. Desktop can handle more fields per view. User context (returning vs. first-time) also matters -- returning users prefer speed (single page), new users prefer guidance (multi-step).

---

## Source Index

1. Hick, W.E. (1952). "On the rate of gain of information." Quarterly Journal of Experimental Psychology. https://www2.psychology.uiowa.edu/faculty/mordkoff/InfoProc/pdfs/Hick%201952.pdf
2. Miller, G.A. (1956). "The Magical Number Seven, Plus or Minus Two." Psychological Review.
3. Iyengar, S.S. & Lepper, M.R. (2000). "When Choice is Demotivating." Journal of Personality and Social Psychology. https://faculty.washington.edu/jdb/345/345%20Articles/Iyengar%20&%20Lepper%20(2000).pdf
4. Johnson, E.J. & Goldstein, D.G. (2003). "Do Defaults Save Lives?" Science. https://papers.ssrn.com/sol3/papers.cfm?abstract_id=1324774
5. Nielsen, J. (2006). "F-Shaped Pattern for Reading Web Content." NNGroup. https://www.nngroup.com/articles/f-shaped-pattern-reading-web-content-discovered/
6. Scheibehenne, B. et al. (2010). "Can There Ever Be Too Many Options?" Journal of Consumer Research. https://scheibehenne.com/ScheibehenneGreifenederTodd2010.pdf
7. Chernev, A. et al. (2015). "Choice overload: A conceptual review and meta-analysis." Journal of Consumer Psychology. https://chernev.com/wp-content/uploads/2017/02/ChoiceOverload_JCP_2015.pdf
8. Carter, E.C. & McCullough, M.E. (2015). Meta-analysis correcting for publication bias in ego depletion.
9. Hagger, M.S. et al. (2016). Registered Replication Report on ego depletion. 23 labs, 2,000+ participants.
10. Proctor, R.W. & Schneider, D.W. (2018). "Hick's law for choice reaction time: A review." https://web.ics.purdue.edu/~dws/pubs/ProctorSchneider_2018_QJEP.pdf
11. NNGroup. "The Layer-Cake Pattern of Scanning Content on the Web." https://www.nngroup.com/articles/layer-cake-pattern-scanning/
12. NNGroup. "Progressive Disclosure." https://www.nngroup.com/articles/progressive-disclosure/
13. NNGroup. "Accordions on Desktop." https://www.nngroup.com/articles/accordions-on-desktop/
14. Baymard Institute. "Checkout Optimization: Minimize Form Fields." https://baymard.com/blog/checkout-flow-average-form-fields
15. Baymard Institute. "Display Applied Filters." https://baymard.com/blog/how-to-design-applied-filters
16. Baymard Institute. "Consider Promoting Important Filters." https://baymard.com/blog/promoting-product-filters
17. Baymard Institute. "Always Explain Industry-Specific Filters." https://baymard.com/blog/explain-industry-specific-filters
18. Baymard Institute. "50 Cart Abandonment Rate Statistics." https://baymard.com/lists/cart-abandonment-rate
19. Laws of UX. Hick's Law. https://lawsofux.com/hicks-law/
20. Laws of UX. Miller's Law. https://lawsofux.com/millers-law/
21. Laws of UX. Chunking. https://lawsofux.com/chunking/
22. Vohs, K.D. et al. (2021). Multi-lab replication of ego depletion. 36 labs, 3,531 participants. https://pmc.ncbi.nlm.nih.gov/articles/PMC8186735/
23. Profitero. Amazon badge analysis (Best Seller, Amazon's Choice conversion impact).
24. NNGroup. "Text Scanning Patterns: Eyetracking Evidence." https://www.nngroup.com/articles/text-scanning-patterns-eyetracking/

---

## Replication Status Summary

| Finding | Status |
|---|---|
| Hick-Hyman Law | Replicated |
| Jam Study (Iyengar 2000) | REPLICATION CONCERNS -- context-dependent |
| Choice Overload Moderators (Chernev 2015) | Replicated (meta-analysis) |
| Choice Overload Mean Effect (Scheibehenne 2010) | This IS the replication check -- near-zero mean |
| Miller's Law | Replicated |
| F-Pattern Scanning | Replicated |
| Progressive Disclosure | Replicated |
| Baymard Filtering Benchmarks | Replicated (longitudinal) |
| Decision Fatigue / Variant Count | REPLICATION CONCERNS for mechanism |
| Ego Depletion | FAILED TO REPLICATE |
| Checkout Form Fields | Replicated (longitudinal) |
| Default Effect | Replicated |
| Social Proof Badges | Replicated (multiple A/B tests) |
| Chunking | Replicated |
| Cart Abandonment Rate | Replicated (50-study meta) |
| Layer-Cake Scanning | Replicated |
| Filter Promotion | Replicated (longitudinal) |
| Step-by-Step vs. All-at-Once | Replicated (multiple A/B tests) |
