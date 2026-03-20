<!-- RESEARCH_DATE: 2026-03-09 -->
# CTA Design & Placement in E-Commerce: Research Findings

**Total Findings**: 22
**Research Date**: 2026-03-09
**Domain**: Call-to-Action button design, copy, placement, and optimization for e-commerce conversion

---

## Executive Summary

### Top 3 Most Impactful Findings

1. **Personalized CTAs convert 202% better than generic defaults** (Finding 1) — HubSpot's analysis of 330,000+ CTAs over six months remains the single largest-scale CTA study. Targeting the right CTA to the right visitor segment dwarfs any color/shape/copy optimization.

2. **Sticky "Add to Cart" on mobile increases conversions 5-37%** (Finding 11) — Multiple independent A/B tests confirm that persistent CTAs on scroll consistently lift conversion rates on mobile product pages, with the most rigorous tests showing 7.9% more completed orders at 99% statistical significance.

3. **Single CTA focus increases clicks by up to 371%** (Finding 9) — Reducing CTA competition dramatically improves conversion, though the effect is most pronounced in emails and landing pages. Product pages benefit from a clear visual hierarchy rather than strict single-CTA enforcement.

---

## Findings

### Finding 1: Personalized CTAs Convert 202% Better Than Generic Defaults

- **Source**: HubSpot, 2014 (updated/reaffirmed through 2025), HubSpot Blog
- **Methodology**: Analysis of 330,000+ CTA impressions across HubSpot's customer base over a six-month period, comparing "smart" CTAs (personalized to visitor lifecycle stage) against default static CTAs.
- **Key Finding**: Personalized CTAs converted 202% better than basic, one-size-fits-all CTAs. The study measured view-to-submission rates across the full dataset.
- **E-Commerce Application**: Serving different CTAs based on visitor status (new visitor vs. returning customer vs. cart abandoner) is the single highest-leverage CTA optimization. A first-time visitor might see "Explore Collection" while a returning visitor sees "Welcome Back — Complete Your Order."
- **Replication Status**: Reaffirmed across 2025 research without a competing study of comparable scale. Widely cited but not independently replicated at the same sample size.
- **Boundary Conditions**: Requires sufficient traffic segmentation data. Sites with low traffic or poor visitor identification may not be able to segment effectively. The 202% figure is an average — individual results vary by industry and segment quality.
- **Evidence Tier**: Bronze

---

### Finding 2: CTA Button Color — Contrast Matters, Not the Color Itself

- **Source**: CXL Institute (Peep Laja), CXL Blog; HubSpot/Performable red vs. green test, HubSpot Blog
- **Methodology**: HubSpot tested red vs. green CTA buttons over several days with ~2,000 page visits. CXL performed a comprehensive meta-analysis of published button color tests.
- **Key Finding**: The red button outperformed the green button by 21% in the HubSpot test. However, CXL's analysis revealed the critical context: the site's primary palette was green, so the green button blended in while red stood out. CXL's conclusion: "No single color is better than another — what matters is how much a button color contrasts with the area around it."
- **E-Commerce Application**: Choose a CTA button color that creates maximum contrast against your page background and surrounding elements. Do not adopt "red because HubSpot said so" — if your brand palette is already red, a contrasting color (blue, green, orange) will likely outperform. Test against your specific design context.
- **Replication Status**: The contrast principle has been replicated across multiple independent tests. No study has found a universally "best" color.
- **Boundary Conditions**: The HubSpot test had only ~2,000 visits over a few days — statistically fragile. Button color tests must account for the surrounding page design. WCAG 2.2 requires a minimum 4.5:1 contrast ratio for button text against button background, and 3:1 for button against page background.
- **Evidence Tier**: Silver

---

### Finding 3: Jackson's Art Supplies — CTA Color Differentiation Lifted Conversion 18.4%

- **Source**: Blend Commerce, A/B test on Jackson's Art Supplies (Shopify), Blend Commerce
- **Methodology**: A/B test on product detail pages. The control had all CTA buttons (Add to Cart, Rewards, Chat, Keep Me Updated) in the same color. The variant changed the Add to Cart button to a distinct, contrasting color.
- **Key Finding**: +8.14% increase in Add to Cart clicks. +18.40% increase in eCommerce conversion rate. For new visitors specifically: +66% increase in Add to Cart clicks, +10% increase in AOV, +16.40% increase in average purchase revenue per user.
- **E-Commerce Application**: When multiple interactive elements share the same visual weight, users cannot identify the primary action. Differentiating the primary CTA from secondary elements through color is a high-impact, low-effort optimization.
- **Replication Status**: Single case study. The principle (primary CTA visual differentiation) is well-supported by broader UX literature.
- **Boundary Conditions**: Sites that already differentiate their primary CTA will see minimal uplift from further color changes. The magnitude of improvement correlates with how undifferentiated the original design was.
- **Evidence Tier**: Bronze

---

### Finding 4: Fitts's Law — Larger Buttons Are Faster and Easier to Acquire

- **Source**: Fitts (1954), original research; NNGroup summary, NNGroup; ISO 9241-9 standard; Tognazzini (1999) on edge targets
- **Methodology**: Fitts's Law is derived from information theory and validated across hundreds of controlled motor-task experiments since 1954. MT = a + b * log2(D/W + 1), where D = distance and W = target width.
- **Key Finding**: Movement time to acquire a target is a logarithmic function of the distance divided by the target width. Doubling a button's size reduces acquisition time. Targets placed at screen edges are acquired fastest because the edge acts as an infinite-width target (users cannot overshoot). On touch interfaces, fingers are less precise than cursors, amplifying the size effect.
- **E-Commerce Application**: Make primary CTA buttons substantially larger than other interactive elements. On mobile, consider full-width CTA buttons. Place CTAs near screen edges where possible (bottom of viewport for mobile sticky CTAs). Do not make secondary CTAs the same size as the primary.
- **Replication Status**: Replicated. One of the most validated findings in all of HCI research — confirmed across thousands of studies since 1954.
- **Boundary Conditions**: Returns diminish once buttons exceed a reasonable size — an absurdly large button wastes space and can look unprofessional. The law describes motor performance, not visual attention or decision-making. A perfectly sized button with bad copy still fails.
- **Evidence Tier**: Gold

---

### Finding 5: Touch Target Minimums — Platform Guidelines

- **Source**: Google Material Design, Material Design; Apple Human Interface Guidelines; WCAG 2.2 SC 2.5.8, W3C
- **Methodology**: Platform-level design guidelines based on ergonomic research and device usage data. WCAG 2.2 SC 2.5.8 is a formal accessibility standard (Level AA).
- **Key Finding**: Three tiers of minimum touch target size exist:
  - **WCAG 2.2 AA minimum**: 24x24 CSS pixels (legal/compliance floor)
  - **Apple HIG**: 44x44 points (~59px on standard displays)
  - **Google Material Design**: 48x48 dp (~48px on mdpi)
  - Google explicitly chose a larger minimum to "accommodate a larger spectrum of users."
- **E-Commerce Application**: CTA buttons on mobile should be at minimum 44x44pt (Apple) or 48x48dp (Android). For primary CTAs like "Add to Cart," go larger — 48-60px height minimum with full-width or near-full-width on mobile. WCAG 2.2's 24px minimum is the accessibility floor, not the UX optimum.
- **Replication Status**: These are industry standards, not single studies. Backed by extensive internal usability testing at Apple and Google.
- **Boundary Conditions**: The 24px WCAG minimum applies even when spacing offsets are used. Physical pixel size varies by device density — design in logical pixels (pt/dp/CSS px), not physical pixels.
- **Evidence Tier**: Silver

---

### Finding 6: "Add to Cart" Outperforms "Buy Now" for Most E-Commerce

- **Source**: CXL Institute, CXL Blog; behavioral psychology principle of commitment aversion
- **Methodology**: CXL's analysis of CTA copy patterns across e-commerce sites, drawing on conversion optimization principles and practitioner A/B tests. Specific quantified lift data for this exact comparison was not found in publicly available studies.
- **Key Finding**: "Add to Cart" implies a reversible, low-commitment action — the shopper can remove the item later. "Buy Now" feels final and triggers commitment aversion. For most e-commerce contexts, "Add to Cart" performs better because it reduces perceived risk. However, "Buy Now" can perform well for impulse purchases, low-price items, or when paired with one-click checkout (Amazon's model).
- **E-Commerce Application**: Default to "Add to Cart" for standard product pages. Reserve "Buy Now" for express checkout flows, flash sales, or products under ~$30 where impulse buying is common. Consider offering both: "Add to Cart" as primary and "Buy Now" as a secondary express option.
- **Replication Status**: The principle is widely accepted in CRO practice but lacks a single definitive controlled study with published sample size. Multiple practitioners report consistent results.
- **Boundary Conditions**: Amazon's entire model is built on "Buy Now with 1-Click" — demonstrating that with sufficient trust and a frictionless checkout, "Buy Now" can dominate. Context, price point, and brand trust level matter.
- **Evidence Tier**: Silver

---

### Finding 7: "Add to Cart" vs. "Add to Bag" — Brand-Dependent Results

- **Source**: Conversion Fanatics, Conversion Fanatics; multiple A/B test case studies
- **Methodology**: Multiple independent A/B tests across different retail verticals.
- **Key Finding**: Results are contradictory and brand-dependent:
  - A premium men's lifestyle brand saw a **6.46% increase in add-to-carts** when switching to "Add to Bag" (81.81% probability of being better).
  - A different retailer saw switching FROM "Add to Bag" TO "Add to Cart" increase checkout pageviews by **95.3%** and purchase conversions by **81.4%**.
- **E-Commerce Application**: "Add to Bag" signals a premium, curated experience — appropriate for fashion, luxury, and lifestyle brands. "Add to Cart" is more universally understood and performs better for mainstream, general-purpose e-commerce. Test this with your specific audience rather than assuming.
- **Replication Status**: Contradictory results across studies — confirms this is genuinely context-dependent, not a universal truth.
- **Boundary Conditions**: The winning variant depends on brand positioning, audience expectations, and vertical. Fashion/luxury skews toward "Bag"; electronics/general retail skews toward "Cart."
- **Evidence Tier**: Bronze

---

### Finding 8: Below-the-Fold CTA Can Outperform Above-the-Fold by 20-220%

- **Source**: Marketing Experiments (MECLABS), referenced via Unbounce; Google "Importance of Being Seen" study
- **Methodology**: Marketing Experiments conducted controlled A/B tests on CTA placement. Google's study measured ad visibility rates based on page position.
- **Key Finding**: A below-the-fold CTA resulted in a **20% increase in conversions** in one test. In another test, a below-the-fold treatment increased conversion rate by **220%** over a control with both form and CTA above the fold. However, Google found that above-the-fold content has **73% visibility** vs. **44% for below-the-fold** content.
- **E-Commerce Application**: For product pages, place the primary CTA (Add to Cart) in its expected position near the product title/price — which is typically above-fold on desktop. But also provide a sticky or repeated CTA for users who scroll through reviews, specifications, and other content. The 220% lift came from landing pages where persuasive content preceded the CTA — suggesting that for complex or high-consideration products, letting users read before asking them to act is superior.
- **Replication Status**: The principle that context-rich placement can beat above-fold placement is replicated. The specific 220% figure is from a single test.
- **Boundary Conditions**: Above-fold wins when the user already has high intent or the product is simple/low-cost. Below-fold wins when the user needs persuasion (complex products, high price points, unfamiliar brands). Mobile complicates "the fold" — screen sizes vary enormously.
- **Evidence Tier**: Bronze

---

### Finding 9: Single CTA Focus — Reducing Options Lifts Conversion Up to 371%

- **Source**: Campaign Monitor; Whirlpool email A/B test; WiserNotify compilation, WiserNotify
- **Methodology**: Multiple studies. Campaign Monitor analyzed email campaigns. Whirlpool tested 4 CTAs vs. 1 CTA in email. Broader compilations measured landing page single-CTA performance.
- **Key Finding**:
  - Emails with a single CTA increased clicks by **371%** (Campaign Monitor).
  - Whirlpool's single-CTA email outperformed the 4-CTA version by **42%**.
  - Reducing CTAs to a single CTA on a landing page increased conversions by **266%**.
  - Emails with 3+ CTAs have lower click-through rates than those with fewer than 3.
- **E-Commerce Application**: For email campaigns and landing pages, ruthlessly reduce to a single primary CTA. For product pages, maintain one visually dominant primary CTA (Add to Cart) with secondary actions (Wishlist, Compare, Share) visually subordinated through smaller size, outline/ghost styling, or muted colors.
- **Replication Status**: The single-CTA advantage in emails is well-replicated across multiple studies. Product page data is more nuanced.
- **Boundary Conditions**: Product pages legitimately need multiple actions — the solution is visual hierarchy, not elimination. Category pages and homepages with multiple products inherently need multiple CTAs. The 371% figure comes from email contexts and should not be directly extrapolated to web pages.
- **Evidence Tier**: Bronze

---

### Finding 10: Rounded Corners Are Preferred Over Sharp Corners

- **Source**: Contour bias research (Bar & Neta, 2006); Fitts's Law implications for corner targeting; cognitive processing research on contour perception
- **Methodology**: Neuroscience research on contour processing and visual preference. Supported by Fitts's Law analysis of corner targeting.
- **Key Finding**: Rounded shapes are processed more efficiently by the visual system. The neurological basis: sharp edges require more cognitive processing effort (additional neuronal image tools for edge detection), while rounded shapes are processed more efficiently (Bar & Neta, 2006 — contour bias). Rounded corners also draw visual attention inward toward the button content, while sharp edges direct attention outward.
- **E-Commerce Application**: Use rounded corners (border-radius of 4-12px for standard buttons, or pill shape for very prominent CTAs) for primary CTA buttons. This aligns with the learned convention that rounded rectangles signal "pressable button."
- **Replication Status**: The cognitive processing advantage of rounded shapes is replicated in neuroscience literature (Bar & Neta, 2006; subsequent replications).
- **Boundary Conditions**: Design system consistency matters — if your entire UI uses sharp corners, a lone rounded button may look inconsistent rather than inviting. The effect may be smaller on audiences accustomed to angular design systems (e.g., some enterprise contexts).
- **Evidence Tier**: Gold

---

### Finding 11: Sticky "Add to Cart" on Mobile — 5-37% Conversion Lift

- **Source**: Multiple A/B tests: Blend Commerce, Blend Commerce sticky CTA; GrowthRock, GrowthRock; Traction Marketing NZ, Traction Marketing; FoxStark case study, EcommerceConversionChecklist
- **Methodology**: Multiple independent A/B tests on Shopify product pages, measuring conversion rate, Add to Cart rate, and revenue per visitor.
- **Key Finding**:
  - Sticky CTA on PDP: **+10% conversion rate**, -3% bounce rate, +5% cart clicks (Blend Commerce)
  - FoxStark: **+18.57% Add-to-Cart rate** at 90% statistical significance on mobile
  - GrowthRock: **+7.9% completed orders** at 99% statistical significance
  - Blend Commerce (thumbnails + sticky CTA): **+7.17% conversion rate**, +9.61% Add to Cart clicks, +6.26% revenue per visitor
  - Floating "Add to Cart" buttons: **+33% more cart adds** (aggregate)
  - Floating checkout buttons: **+37% increase in checkout starts** (aggregate)
  - Overall range: **sticky bottom CTAs improve mobile conversions by 12-27%** (aggregate estimates)
- **E-Commerce Application**: Implement a sticky "Add to Cart" bar on mobile product pages that appears when the user scrolls past the primary CTA. Include the product price and a clear button. Keep it compact to avoid obscuring content.
- **Replication Status**: Replicated across multiple independent tests on different Shopify stores. Consistent positive results, though magnitude varies (5-37%).
- **Boundary Conditions**: Less effective for products with complex variants (size/color selectors) that can't fit in a sticky bar. Can feel intrusive if the bar is too large or obscures content. Some users find persistent UI elements annoying — monitor bounce rate alongside conversion rate.
- **Evidence Tier**: Bronze

---

### Finding 12: White Space Around CTAs — Up to 232% Conversion Increase

- **Source**: VWO, VWO Blog; Microsoft Clarity, Microsoft Clarity Blog
- **Methodology**: VWO case study involving removal of clutter and addition of white space around CTA elements on landing pages.
- **Key Finding**: A CTA surrounded by fewer elements and more white space increased conversion rate by **232%**. The effect comes from the combination of removing competing visual elements and giving the CTA visual prominence through isolation.
- **E-Commerce Application**: Ensure the "Add to Cart" button has generous padding and margin. Remove unnecessary badges, links, or secondary information from the immediate vicinity of the primary CTA. On product pages, the CTA zone (price + button + key trust signals) should have clear visual separation from product descriptions and other content.
- **Replication Status**: The general principle (visual isolation improves CTA performance) is well-supported. The specific 232% figure is from a single case study and likely reflects a heavily cluttered starting point.
- **Boundary Conditions**: Too much white space can disconnect the CTA from its supporting context (price, product name). The 232% figure is extreme and should not be expected as typical — it reflects going from very bad to good, not from good to great. Product pages need supporting information near the CTA (price, availability, trust badges).
- **Evidence Tier**: Bronze

---

### Finding 13: Baymard Institute — CTA Label Honesty Prevents Abandonment

- **Source**: Baymard Institute, Baymard Blog; usability testing across major e-commerce sites
- **Methodology**: Qualitative usability testing with real users across leading e-commerce sites. Part of Baymard's ongoing large-scale UX research program (130,000+ hours of research referenced on their site).
- **Key Finding**: When users clicked a CTA labeled generically (like "Get Started") and were immediately asked for personal information or shown a promotion, **73% of users were surprised** and **41% voiced frustration at being misled**. Several users abandoned the site altogether. Users developed negative brand perceptions, interpreting unexpected requests as a "hard sell."
- **E-Commerce Application**: CTA button labels must accurately describe what happens next. "Add to Cart" should add to cart — not open a popup, trigger a survey, or redirect to a different flow. If clicking "Add to Cart" triggers an upsell modal, users will feel deceived. Reserve interstitial experiences for after the expected action completes.
- **Replication Status**: Consistent with NNGroup's findings on CTA label clarity. Well-supported by usability research.
- **Boundary Conditions**: Users are more tolerant of intermediate steps when the CTA label implies them (e.g., "Customize & Add to Cart" sets expectations for a configuration step).
- **Evidence Tier**: Gold

---

### Finding 14: NNGroup — Specific Labels Outperform Generic Labels

- **Source**: NNGroup, NNGroup - Better Link Labels; NNGroup - Get Started Stops Users
- **Methodology**: Eyetracking studies and qualitative usability testing. Users scan rather than read UI, so labels must communicate meaning independently of surrounding text.
- **Key Finding**: Generic labels ("Get Started," "Continue," "Submit," "Click Here") perform poorly because users scan and encounter them without context. Specific labels ("Add to Cart — $49.99," "Start Free Trial," "Download PDF Guide") outperform because they communicate the action and its outcome in a single glance. When links set expectations that aren't met, users "cut their click budget" and reduce engagement with the site.
- **E-Commerce Application**: Use action-specific CTA labels: "Add to Cart," "Buy Now — Free Shipping," "Reserve Your Size." Avoid generic labels like "Continue," "Proceed," or "Go." Including the price or a key benefit in the CTA can reduce uncertainty and increase clicks.
- **Replication Status**: Replicated. NNGroup's eyetracking methodology has been applied across hundreds of studies consistently showing the same scanning behavior.
- **Boundary Conditions**: There is a practical length limit — buttons with too much text become hard to scan. Keep CTA text to 2-5 words maximum. Multi-step flows may legitimately need "Continue" or "Next" when the context is clear from surrounding UI.
- **Evidence Tier**: Gold

---

### Finding 15: VWO Data — 30% of All A/B Tests Target CTAs; Winners Average 49% Lift

- **Source**: Wingify/VWO, VWO Blog
- **Methodology**: Meta-analysis of A/B tests run across VWO's customer base (Wingify is the parent company of VWO).
- **Key Finding**: Approximately **30% of all A/B tests** run by VWO customers focus on CTA buttons — making it the most commonly tested element. However, only **1 in 7** CTA tests produces a statistically significant improvement. When a CTA test does win, the **average conversion increase is 49%**.
- **E-Commerce Application**: CTA testing is high-leverage but low hit-rate. Expect to run ~7 CTA tests to find one significant winner. When you do find a winner, the payoff is substantial. Prioritize CTA tests that change multiple properties simultaneously (copy + color + size) for higher chances of significance, then isolate variables in follow-up tests.
- **Replication Status**: This is platform-level aggregate data from VWO, not a single study. Represents a broad cross-section of real-world testing.
- **Boundary Conditions**: The 49% average is skewed by outliers — the median lift is likely much lower. "Statistically significant" depends on each test's sample size and duration. Sites with already-optimized CTAs will see smaller gains.
- **Evidence Tier**: Bronze

---

### Finding 16: SAP — Replacing Text Link with Orange Button Lifted Conversions 32.5%

- **Source**: Referenced via multiple CRO case study compilations including Neil Patel and Capturly
- **Methodology**: A/B test replacing a small blue text download link with a large orange CTA button on a landing page.
- **Key Finding**: The large orange button produced a **32.5% increase in conversions** compared to the text link.
- **E-Commerce Application**: Ensure CTAs are visually identifiable as buttons, not text links. This applies to "Add to Cart," "Checkout," and any primary action. A styled button with background color, padding, and clear affordances will always outperform a styled text link for primary actions.
- **Replication Status**: The principle (buttons outperform links for primary actions) is extremely well-replicated. The specific 32.5% figure is from a single test.
- **Boundary Conditions**: Applies to primary actions. Secondary and tertiary actions (terms of service, FAQ links) are appropriately presented as text links to maintain visual hierarchy.
- **Evidence Tier**: Bronze

---

### Finding 17: GoSquared — Shorter CTA Copy Increased Trial Starts by 104%

- **Source**: Referenced via Unbounce CRO case studies
- **Methodology**: A/B test on GoSquared's website comparing a longer CTA label against a shorter, more direct variant.
- **Key Finding**: The shorter CTA won with a **104% month-over-month increase in premium trial start rates**. Brevity and clarity beat verbosity.
- **E-Commerce Application**: Keep CTA copy short — 2-4 words maximum. "Add to Cart" beats "Add This Item to Your Shopping Cart." "Buy Now" beats "Purchase This Product Now." Every additional word introduces cognitive load and scanning friction.
- **Replication Status**: The principle (shorter CTAs outperform longer ones) is consistent with NNGroup's scanning research. The specific 104% figure is a single case study.
- **Boundary Conditions**: There's a floor — a CTA needs enough words to be clear. "Go" or "Yes" alone may be too ambiguous. The sweet spot is 2-5 words that clearly communicate the action.
- **Evidence Tier**: Bronze

---

### Finding 18: Secondary CTAs Should Use Ghost/Outline Styling

- **Source**: NerdCow, NerdCow CTA Hierarchy; DesignCourse, DesignCourse; LogRocket UX, LogRocket
- **Methodology**: UX design pattern analysis and practitioner consensus across CRO and design communities.
- **Key Finding**: Secondary CTAs (Wishlist, Compare, Share) should be visually subordinate to the primary CTA through: outline/ghost button styling (border only, no fill), smaller size, muted or neutral colors, or text-link styling with an icon. The primary CTA should have a solid fill, the strongest contrast color, and the largest tap target.
- **E-Commerce Application**: On product pages: "Add to Cart" gets a solid, high-contrast filled button. "Add to Wishlist" gets an outline/ghost button or icon-only treatment. "Share" and "Compare" get text links or small icon buttons. Never give a secondary action equal or greater visual weight than the primary CTA.
- **Replication Status**: This is established design convention rather than a single A/B test result. Supported by the Jackson's Art Supplies test (Finding 3) which showed the cost of NOT differentiating.
- **Boundary Conditions**: Some businesses may want to promote secondary actions (e.g., a subscription box might elevate "Gift This" to near-primary status during holiday seasons).
- **Evidence Tier**: Bronze

---

### Finding 19: Google Visibility Study — Above-Fold Content Gets 73% Visibility

- **Source**: Google, "The Importance of Being Seen" study, referenced via CXL
- **Methodology**: Large-scale analysis of ad viewability across Google's display network, measuring the percentage of ads that were actually visible to users based on page position.
- **Key Finding**: Ads above the fold had **73% visibility** to users, while ads below the fold had only **44% visibility**. This is a 29 percentage-point gap in raw visibility.
- **E-Commerce Application**: The primary CTA should be visible without scrolling on desktop. On mobile, where screen space is limited, a sticky CTA solves the visibility problem for below-fold content. Key product information (price, availability, primary CTA) should be above fold or persistently visible.
- **Replication Status**: Replicated. This aligns with extensive eyetracking research showing attention concentration in upper portions of pages.
- **Boundary Conditions**: "The fold" is not a fixed line — it varies by device and viewport size. Mobile users are more accustomed to scrolling than desktop users. Visibility does not equal conversion — a visible but poorly designed CTA still underperforms.
- **Evidence Tier**: Silver

---

### Finding 20: Snocks.com — Post-Click CTA Label Change as Confirmation

- **Source**: GoodUI, Test #429 on Snocks.com, GoodUI Tests
- **Methodology**: A/B test on Snocks.com (a Shopify store) from GoodUI's database of 595+ catalogued experiments across 128 million+ visitors.
- **Key Finding**: Upon clicking the "Add to Cart" button, the button label changed to a cheering/congratulatory message confirming the action and noting free shipping. This micro-interaction pattern reinforces the user's decision and reduces uncertainty about whether the click registered.
- **E-Commerce Application**: After a user clicks "Add to Cart," provide immediate visual feedback: change the button text (e.g., "Added!" or "In Your Cart"), show a checkmark animation, or briefly change the button color. This confirmation reduces double-clicks and builds confidence in the interaction.
- **Replication Status**: Specific conversion data for this individual test was not publicly available. The principle of feedback confirmation is well-established in HCI (Nielsen's "Visibility of System Status" heuristic).
- **Boundary Conditions**: The confirmation state should be brief (1-3 seconds) before reverting or transitioning. Overly enthusiastic messages ("Amazing choice!!!") can feel patronizing depending on brand tone.
- **Evidence Tier**: Bronze

---

### Finding 21: WCAG 2.2 SC 2.5.8 — 24px Minimum Target Size Is Legal Floor

- **Source**: W3C, WCAG 2.2 Success Criterion 2.5.8, W3C Understanding SC 2.5.8
- **Methodology**: W3C accessibility standard, Level AA requirement. Based on ergonomic research and public comment period.
- **Key Finding**: All interactive targets must be at least **24x24 CSS pixels** (Level AA). This is a formal accessibility requirement, not a recommendation. Exceptions exist for inline text links, browser-controlled elements, and cases where spacing provides adequate offset. Note: CSS pixels don't change with zoom — 16x16 at 100% zoom remains 16x16 at 400% zoom. The enhanced target size criterion (SC 2.5.5, Level AAA) requires **44x44 CSS pixels**.
- **E-Commerce Application**: 24px is the absolute minimum for any interactive element — including small "X" close buttons, quantity selectors, and color swatches. Primary CTAs should far exceed this minimum. For "Add to Cart" buttons, target 44-60px height minimum. For mobile, Apple's 44pt and Google's 48dp recommendations should be treated as the practical minimum, not WCAG's 24px floor.
- **Replication Status**: This is a formal W3C standard, not an experimental finding. It is legally binding in jurisdictions that reference WCAG 2.2.
- **Boundary Conditions**: The 24px minimum applies per-element. Adjacent small targets that collectively form a larger interactive area may still fail if individual targets are too small. Inline text links within sentences are exempt from this criterion.
- **Evidence Tier**: Silver

---

### Finding 22: WCAG Touch Target Requirements for CTAs

- **Source**: Cross-reference to mobile-conversion.md Finding 24; (a) W3C WCAG 2.2; (b) Apple HIG; (c) Google Material Design
- **Methodology**: Standards specifications and platform guidelines. See mobile-conversion.md Finding 24 for full context on accessibility implications.
- **Key Finding**: WCAG 2.2 SC 2.5.5 (AAA) requires **44x44 CSS pixels** minimum for touch targets; SC 2.5.8 (AA) requires **24x24 CSS pixels**. Apple HIG recommends **44pt**, Google Material Design recommends **48dp**. For ecommerce CTAs specifically, **48px minimum** is the recommended floor, with **60px+ for primary conversion buttons** (Add to Cart, Buy Now, Checkout, Pay). This builds on Finding 5 (touch target minimums) and Finding 21 (WCAG 2.5.8) with additional context: the 4,187+ ADA accessibility lawsuits in 2024, with 69-77% targeting ecommerce, make CTA touch target compliance a legal exposure, not just a design preference.
- **E-Commerce Application**: Audit all CTA buttons on mobile for minimum 48px touch target height. Primary conversion CTAs should be 60px+ in height. Ensure adequate spacing between adjacent touch targets (minimum 8px gap). Sticky bottom CTAs are especially important — they must be large enough for confident one-handed thumb tapping. This is a mechanical fix requiring no A/B testing. **Cross-reference:** See mobile-conversion.md Findings 22-24 for full accessibility context including lawsuit data and platform-specific error rates.
- **Replication Status**: WCAG is the international standard. Platform guidelines are consistent. Finding 5 in this document already established Fitts's Law and touch target principles — this finding extends it with accessibility compliance context.
- **Boundary Conditions**: No peer-reviewed study directly measures the conversion impact of specific CTA touch target sizes. The legal exposure is US-specific (ADA) with EU parallel (EAA enforceable June 2025).
- **Evidence Tier**: Silver

---

## Methodology Notes

### Sources Consulted
- CXL Institute (multiple articles and meta-analyses)
- NNGroup (usability studies, eyetracking research)
- Baymard Institute (large-scale e-commerce usability testing)
- VWO/Wingify (platform-level A/B test aggregate data)
- HubSpot (personalized CTA study, button color test)
- Blend Commerce (multiple Shopify A/B test case studies)
- GoodUI / Jakub Linowski (catalogued A/B test patterns)
- Google Material Design & Apple HIG (touch target specifications)
- W3C WCAG 2.2 (accessibility standards)
- Marketing Experiments / MECLABS (CTA placement testing)
- Multiple individual CRO case studies (SAP, GoSquared, Whirlpool, Jackson's Art Supplies, Snocks.com, FoxStark)

### Limitations
- Many published A/B tests lack sufficient methodological detail (sample size, test duration, statistical power).
- CTA button color research is particularly prone to oversimplification — most "best color" claims collapse under scrutiny to "best contrast."
- Case study results from one site/vertical may not generalize. E-commerce verticals (fashion, electronics, groceries, luxury) have different user expectations and behavior patterns.
- Publication bias: successful tests are far more likely to be published than null results. The VWO data showing only 1 in 7 CTA tests winning is a useful corrective.
- Several widely-cited statistics (like the 371% email CTA click increase) come from compilations without links to the original studies, making verification difficult.

### Data Quality Assessment
- **High confidence**: Fitts's Law (Finding 4), touch target minimums (Finding 5), WCAG standards (Finding 21), Google visibility study (Finding 19), VWO aggregate data (Finding 15)
- **Medium confidence**: Personalized CTA 202% lift (Finding 1 — large sample but single organization), sticky CTA improvements (Finding 11 — multiple independent replications), rounded corners advantage (Finding 10)
- **Lower confidence**: Specific percentage lifts from individual case studies (Findings 3, 8, 12, 16, 17) — real data but single-site results that may not generalize
