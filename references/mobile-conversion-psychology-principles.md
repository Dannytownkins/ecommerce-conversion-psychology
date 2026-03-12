<!-- RESEARCH_DATE: 2026-03-09 -->
# Mobile Conversion Psychology

<!-- last-validated: 2026-03-10 -->
<!-- scope: Psychology of how conversion behavior changes on mobile screens -->
<!-- does-not-cover: Mobile UX mechanics (thumb zones, page speed, touch targets, digital wallets, navigation, form optimization, Core Web Vitals) — see mobile-and-performance.md -->

<core_principles>

## 1. Mobile Decision-Making Is Interrupt-Driven, Not Linear

**What:** Mobile shopping sessions are fragmented, context-switched, and emotionally driven. Sessions happen in stolen moments — commutes, queues, couch scrolling. Mobile shoppers make faster, more heuristic-driven decisions and are more susceptible to impulse triggers.

**Evidence:**
- Huang et al. (2018, J. Retailing and Consumer Services, n=312 + n=287): Mobile cart abandonment is driven by emotional ambivalence — simultaneous approach/avoidance responses at higher intensity than desktop. Choice-process satisfaction moderates this: when shoppers feel confident in their selection, hesitation drops significantly.
- Anoop (2025, J. Consumer Behaviour, meta-analysis, 75 articles, n=139,545): Situational stimuli (ESr=0.477) are the strongest driver of online impulse buying — stronger than marketing stimuli (0.433) or platform factors (0.362). Mobile amplifies situational stimuli because the device is always present in context.
- Nyrhinen et al. (2024, Computers in Human Behavior, n=2,318): Low self-control directly enables impulsive mobile purchasing, compounding through targeted ads and social media impulsiveness.

**Implementation:**
- Front-load the purchase decision: price, primary CTA, and single most compelling value proposition within the first viewport.
- Implement persistent cart state and session recovery for interrupted sessions (see Session Recovery pattern below).
- Route by price point: impulse categories (<$50) get friction reduction; considered purchases (>$100) get save/wishlist/cross-device sync. See decision tree for full routing.

---

## 2. Mobile Scanning Collapses to a Vertical Strip

**What:** Desktop scanning patterns (F-pattern, Z-pattern) degrade on ~6" screens. Mobile users exhibit the "marking pattern" (NN/g) — eyes remain relatively fixed while the thumb scrolls content past them. Users fixate on the center 60-70% of the screen and process content sequentially, not spatially.

**Evidence:**
- NNGroup (2017, updated 2024): F-pattern persists on mobile but is compressed. The "marking pattern" is predominantly mobile: content is processed in scroll order, not by spatial position — fundamentally different from desktop F-pattern where users jump between areas.
- Xu et al. (2020, Nature Communications, n=100+): Mobile gaze patterns show stronger center bias than desktop (6" screen at 12×9° viewing angle vs 22" desktop at 33×25°). Peripheral content receives dramatically less visual attention.
- The "spotted pattern" (NN/g) — scanning for numbers, links, formatted text — becomes more dominant on mobile as users compensate for reduced reading by keyword-spotting.

**Implementation:**
- Vertical order IS priority order on mobile. Do not rely on horizontal placement for hierarchy.
- "Above the fold" on mobile ≈ first 600-700px. First viewport earns 2-3x more fixation time than subsequent viewports. Price, CTA, star rating, and primary image must appear here.
- Below-fold content should be formatted for the spotted pattern: use numerals not words, bold key phrases, break text into scannable chunks.
- On listing pages, each card gets ~1-2 seconds during scroll. Card must communicate: image, price, rating. Description text on mobile listing cards is almost never read.

---

## 3. Mobile AOV Gap Is a Shopping-Mode Effect, Not Just Friction

**What:** Mobile AOV is consistently 15-35% lower than desktop across categories. This is primarily a behavioral mode difference — mobile sessions are browsing/discovery-oriented and single-item focused — not just checkout friction.

**Evidence:**
- Cross-industry benchmarks (Dynamic Yield 2025, OpenSend 2024, Kibo 2025): Desktop AOV $122-230 vs mobile $86-149 depending on source and category. The gap persists even on sites with optimized mobile checkout.
- jmango360 (2024): App AOV (~$217) significantly exceeds mobile web (~$194), suggesting higher-intent mobile users behave more like desktop users.
- Cornell University: One-click checkout increases spending 28.5% and frequency 43%, confirming a significant friction component for purchase-ready users.

**Implementation:**
- Do not benchmark mobile against desktop as equivalent intent. Segment by device AND session intent.
- Optimize mobile for single-item conversion efficiency. Upsells should be lightweight (1-tap add, not navigation-interrupting).
- For mobile AOV: bundle offers and free shipping thresholds work well — single decisions rather than multi-item cart building.
- Price anchoring must be compact on mobile. Show original/sale prices inline on the same line — spatial separation that works on desktop kills anchoring on mobile.

---

## 4. Mobile Trust Must Be Compressed Into Fewer, Higher-Impact Signals

**What:** On desktop, 5-8 trust signals are visible simultaneously. On mobile, only 1-2 per scroll position. Trust formation on mobile is sequential, not simultaneous — each signal must earn its viewport position.

**Evidence:**
- Baymard Institute (ongoing): 17-18% abandon due to payment trust concerns. Sites can gain 35.26% conversion through better checkout design and trust elements.
- Envive.ai (2026): Trust badges deliver up to 8.72% conversion increase; 61% won't purchase without visible trust badges.
- Worldpay (2024): Digital wallets = 53% of global online transactions. Apple Pay/Google Pay users never share card numbers (tokenization) — the wallet IS the trust signal. For unknown brands, this is transformational.
- Forter (2024): Consumers spend 51% more with trusted retailers — trust creates pricing power, not just conversion lift.

**Implementation:**
- Trust signal hierarchy for mobile (by viewport priority):
  1. **Adjacent to CTA:** Star rating + review count ("★ 4.7 (2,341 reviews)") — highest-impact trust signal per pixel.
  2. **Below CTA / above fold:** One-line shipping + returns promise ("Free shipping · 30-day returns").
  3. **At checkout:** Payment logos + security indicator. Apple Pay/Google Pay buttons serve dual duty as payment AND trust.
  4. **Below fold on PDP:** Expanded reviews, guarantee details, "as seen in" badges.
- Do NOT waste above-fold mobile space on: BBB badges, generic "Secure Checkout" text, or unrecognized certification badges.
- For unknown brands: Express checkout as PRIMARY CTA — outsource trust to Apple/Google.

---

## 5. Mobile Social Proof Is Scanned by Signal, Not Read for Content

**What:** On mobile, review consumption shifts to signal extraction: aggregate rating, review count, rating distribution histogram, and photo reviews. Full text reviews are skimmed for negative signals rather than read for positive confirmation. The FORMAT of social proof matters more on mobile than individual review content.

**Evidence:**
- Chen & Samaranayake (2022, Frontiers in Psychology): Fixation on negative comments was significantly greater than positive, especially for female consumers. On mobile, where scanning is more abbreviated, negative reviews have outsized influence.
- Wang et al. (2024, Information & Management): Smaller screens shift behavior from in-depth reading to selective browsing, scanning, and keyword spotting.
- BrightLocal (2024): Shoppers aged 18-24 expect 203 reviews per product. 85% consider reviews older than 3 months irrelevant. Review volume is a trust heuristic — more important on mobile where reading individual reviews is cumbersome.
- Park & McCallister (2023, J. Student Research): Combining pop-up purchase notifications with existing reviews can REDUCE review effectiveness — notification fatigue or perceived manipulation.

**Implementation:**
- Mobile review display priority: (1) Star rating + count in first viewport, (2) rating distribution histogram, (3) photo reviews carousel, (4) one "most helpful" positive + one negative review truncated to 100-120 chars, (5) paginated full list (not infinite scroll).
- Social proof notifications: maximum one per session, tied to specific product viewed, dismissible, must not cover CTA or price.
- UGC photos/video should appear in the main product image gallery, not a separate section.

---

## 6. Mobile Checkout Commitment Must Escalate Through Perceived Progress, Not Steps

**What:** Mobile checkout psychology differs from desktop: (1) commitment escalation must feel like momentum, not bureaucracy; (2) progress indicators have disproportionate impact because users can't see the full form; (3) payment trust anxiety peaks at card number entry — where mobile wallets have their greatest *psychological* impact.

**Evidence:**
- WiserReview (2025): Exceeding 5 checkout steps = 22% abandonment increase. Mobile amplifies this because each step requires full-screen attention.
- Mobile cart abandonment averages approximately 78-80% (SaleCycle/XP2, 2025), compared to the overall cross-device average of ~70.2% (Baymard Institute, 50-study aggregate, 2025). The gap is both friction and intent.
- Apple Pay mobile conversion: 58% increase vs traditional forms (Envive). Mechanism is twofold: reduced friction AND reduced trust anxiety (no card number entry).
- BNPL: Provider-reported 40%+ AOV increases. Reduces "payment pain" barrier, which is more acute on mobile where purchases feel more impulsive.

**Implementation:**
- Progress indicators mandatory: "Step X of Y" visible at top. Ideal: 2-3 screens max or single-page with accordion sections.
- Express checkout as FIRST option, above email entry — positioned as the default path, not an alternative.
- Show order total including shipping/tax BEFORE the payment screen — neutralize the #1 abandonment reason before the trust-anxiety peak.
- BNPL on the PDP, not just checkout: "or 4 payments of $24.99" reduces price perception barrier before add-to-cart.
- Guest checkout as default flow (not a labeled option). Account creation post-purchase only.

---

## 7. Mobile Is the Discovery Layer; Optimize for the Journey, Not Just the Session

**What:** Mobile generates ~75% of e-commerce traffic but only ~57% of sales. Mobile's primary role for many categories is research and shortlisting, not final purchase. Optimizing exclusively for same-session conversion misses the dominant use case and can harm overall conversion.

**Evidence:**
- Statista (Q3 2024, 29B visits, 1B shoppers, 2,276 sites): 77% of US retail visits from smartphones but only ~65% of orders.
- Desktop conversion averages approximately 3.9% vs. mobile at 1.8% (2025 industry benchmarks; Retail Touchpoints, Blend Commerce). Desktop converts at roughly 1.7x the rate of mobile (Smart Insights, 2025). Some 2026 data shows convergence to ~2.8% each on well-optimized sites. This ratio is remarkably stable, suggesting behavioral difference not just friction.
- Monetate (Q4 2017, 2B+ sessions): Multi-device shoppers: 55% purchase rate vs 6% single-device, AOV $130 vs $115. **DATED (Q4 2017). Mobile traffic share has increased from ~50% (2017) to 60-75% (2025), and mobile conversion rates have improved from ~1.2% to ~1.8-2.8%.**
- Astound Commerce: Less than 10% of users visit the same site from multiple devices. The multi-device journey is real but less common than industry narrative suggests.

**Implementation:**
- Optimize mobile PDPs for TWO outcomes: (1) immediate purchase and (2) save-for-later/wishlist/share. Both CTAs equally prominent.
- Cross-device cart persistence is essential — incentivize lightweight account creation early.
- For high-AOV (>$150): prioritize information architecture for research over aggressive conversion CTAs.
- "Email this to yourself" functionality creates self-generated remarketing at dramatically higher conversion than standard retargeting.
- Attribute mobile's funnel role correctly — last-click by device will always make mobile look like a poor converter.

</core_principles>

<decision_tree>

```
MOBILE CONVERSION PSYCHOLOGY DECISION TREE

START: What is the page type?
│
├── Product Detail Page (PDP)
│   ├── What is the product price point?
│   │   ├── Under $50 (impulse range)
│   │   │   → Optimize for IMMEDIATE conversion
│   │   │   → Express checkout in first viewport
│   │   │   → Social proof adjacent to CTA (star + count)
│   │   │   → Minimize information: image, price, CTA, reviews
│   │   │   → BNPL display optional (low impact at this price)
│   │   │
│   │   ├── $50-$150 (considered but completable on mobile)
│   │   │   → Balance immediate conversion + save-for-later
│   │   │   → Show BNPL installment price on PDP
│   │   │   → Trust signals: reviews + shipping/returns + payment logos
│   │   │   → Enable cross-device cart sync
│   │   │
│   │   └── Over $150 (likely multi-session/multi-device)
│   │       → Optimize for RESEARCH QUALITY first, conversion second
│   │       → Prominent save/wishlist/share functionality
│   │       → Detailed specs in scannable format
│   │       → BNPL installment price prominent
│   │       → "Email this to yourself" option
│   │       → Do NOT hide info behind "show more" — make specs accessible
│   │
│   ├── Is this a new/unknown brand?
│   │   ├── Yes
│   │   │   → Express checkout (Apple Pay/Google Pay) as PRIMARY CTA
│   │   │   → Outsource trust to payment providers
│   │   │   → UGC photo reviews in main gallery
│   │   │   → If <50 reviews: show exact count (don't hide it)
│   │   │   → Consider "as seen in" if any media coverage exists
│   │   │
│   │   └── No (established brand)
│   │       → Standard CTA hierarchy (Add to Cart primary)
│   │       → Trust signals can be more subtle (brand carries trust)
│   │       → Focus on product-specific social proof over brand proof
│   │
│   └── What is the traffic source?
│       ├── Social media / ad click (high impulse intent)
│       │   → Maximize first-viewport conversion elements
│       │   → Reduce scroll required before CTA
│       │   → Social proof that mirrors the social context (UGC, not editorial)
│       │
│       ├── Search / organic (high research intent)
│       │   → Prioritize information completeness
│       │   → Comparison-friendly layout
│       │   → Review depth > review summary
│       │
│       └── Email / remarketing (returning intent)
│           → Cart recovery: show exact item + express checkout
│           → Wishlist return: show price change if applicable
│           → Skip discovery content, go straight to conversion
│
├── Product Listing Page (PLP) / Collection Page
│   → Each card gets ~1-2 seconds during scroll
│   → Card must show: image, price, star rating, title (truncated OK)
│   → Do NOT show description text on mobile cards
│   → Quick-add or quick-view on long press (not tap — tap = navigate)
│   → "X people viewing" or "Only Y left" if inventory data supports it
│   → Sort/filter must be sticky and accessible (not buried in header)
│
├── Checkout Flow
│   ├── Is express checkout available?
│   │   ├── Yes → Make it the first/default option
│   │   └── No → IMPLEMENT IT (this is the single highest-impact mobile CRO change)
│   │
│   ├── Show order total (incl. shipping + tax) BEFORE payment screen
│   ├── Progress indicator: visible, "Step X of Y" format
│   ├── Guest checkout = default (account creation post-purchase)
│   ├── BNPL options visible at payment step (and previewed on PDP)
│   └── Trust badges at payment entry point specifically
│
└── Homepage / Landing Page
    → First viewport: value proposition + primary CTA or search
    → Social proof summary (aggregate: "50,000+ customers" or "4.8★ on Trustpilot")
    → Category navigation optimized for thumb reach
    → Do NOT auto-play video (mobile data/distraction concern)
    → Personalized content for returning visitors (recently viewed, recommendations)
```

</decision_tree>

<patterns>

## Pattern: Impulse Conversion Stack

**Use when:** Product is under $50, traffic source is social/ad, category is fashion/beauty/accessories/consumables.

**Implementation:**
- First viewport: Product image (swipeable) + price + star rating + "Add to Cart" + express checkout buttons
- No "View Details" friction between discovery and cart
- Review count visible (not review content — the number IS the signal)
- Urgency/scarcity if legitimate: "Only 3 left" or "Sale ends in 4:22:18"
- One-tap add-to-cart with bottom-sheet cart preview (not full page redirect)

**Why it works:** Mobile impulse purchases happen in a 10-30 second window. Every additional scroll, tap, or page load is an opportunity for the interruption (notification, distraction, second thoughts) that kills the impulse.

---

## Pattern: Research-to-Save Funnel

**Use when:** Product is over $150, category is electronics/furniture/appliances, or user is a first-time visitor on mobile.

**Implementation:**
- First viewport: Product image + price + BNPL installment + "Save for Later ♡" (equally prominent as Add to Cart)
- Detailed specs in collapsible sections (not hidden behind "Show More" text links — use accordion with visible section headers)
- Comparison table accessible from PDP (vs specific competitor products)
- "Email me this product" or "Share" functionality visible
- Review section emphasizes detailed reviews with photos, sorted by "Most Helpful"

**Why it works:** The user is not going to buy a $900 item on their phone during a bus ride. But they WILL do the research that determines which item they'll buy on desktop tonight. Optimizing for save/share captures the mobile session's value without fighting the user's actual intent.

---

## Pattern: Trust Escalation for Unknown Brands

**Use when:** Brand has low recognition, limited review history (<100 reviews), or selling in a trust-sensitive category (supplements, skincare, children's products).

**Implementation:**
- Express checkout (Apple Pay/Google Pay) as the FIRST and largest CTA
- Below CTA: Compact trust strip — "Free shipping · 30-day returns · Secure checkout"
- Integrate UGC photos into main product gallery (position 3 or 4 in swipe sequence)
- If <50 reviews: Show exact count honestly. Add "Verified Purchase" badge to each review.
- Display "as featured in" media logos if any exist (even small publications)
- Founder/team photo or "Our Story" link visible (humanizes the brand)
- Satisfaction guarantee badge adjacent to cart CTA

**Why it works:** On desktop, users can see your About page, security badges, reviews, and media mentions simultaneously. On mobile, they see 1-2 at a time. Express checkout outsources trust to Apple/Google. The compact trust strip handles the most common objections in a single line. UGC in the gallery is the fastest path to "people like me bought this and it's real."

---

## Pattern: Session Recovery Prompt

**Use when:** User returns to the site after a previous session where they viewed products or added to cart.

**Implementation:**
- On return visit, show a non-modal prompt (top banner or bottom sheet): "Welcome back! Your cart is waiting" with thumbnail of cart items
- If cart is empty but browsing history exists: "Still thinking about [Product Name]?" with one-tap add-to-cart
- If product has gone on sale since last visit: "Price drop on [Product Name]! Now $X (was $Y)"
- Time the prompt: show within 3 seconds of page load, auto-dismiss after 8 seconds if not interacted with

**Why it works:** Mobile session fragmentation means many "abandonments" are actually interruptions. The user intended to come back. The recovery prompt shortens the re-engagement path from several taps (navigate to category, find product, add to cart) to one tap.

---

## Pattern: Mobile Review Display Optimization

**Use when:** Any product page with reviews.

**Implementation:**
- Above fold: Star rating + count inline with product title area (e.g., "★★★★★ 4.7 (1,284)")
- Tap on rating scrolls to review section (do not open new page)
- Review section header: Rating histogram (compact bar chart showing distribution)
- First visible review: "Most helpful" positive review, truncated to 100-120 characters
- Second visible review: "Most critical" review (3-star or below), same truncation
- Photo review carousel: horizontal scroll of user-submitted images
- Filter chips: "With Photos" · "Verified" · "1-Star" · "5-Star" (single-tap toggles)
- Pagination: "Show 10 more reviews" button (not infinite scroll)

**Why it works:** Mobile review readers are signal-extracting, not story-reading. The histogram tells them "is this product consistently rated well?" in one glance. The most-helpful pair gives them the best bull and bear case. Photo reviews provide tangible proof. The "Most Critical" review builds trust by showing the brand doesn't hide negative feedback — and the specific complaints may not apply to this buyer ("Too small for my 6'4 husband" is irrelevant to a 5'6 buyer).

---

## Pattern: Mobile Checkout Flow

**Use when:** Any mobile checkout experience.

**Implementation:**
- Screen 1: Express checkout buttons (Apple Pay/Google Pay/Shop Pay) as primary option. Below: email field to begin guest flow.
- Screen 2 (if not express): Shipping address with autocomplete, single name field, shipping method with delivery date estimates. Running total visible including shipping.
- Screen 3: Payment with order summary visible. Trust badges adjacent to card fields. BNPL option for orders >$50.
- Progress indicator at top of each screen: "Step X of 3"
- Order total including tax visible from Screen 2 onward — never surprise at payment.

**Why it works:** Each screen has one psychological job: Screen 1 offers the escape hatch (express checkout eliminates everything else). Screen 2 builds commitment through effort investment. Screen 3 is the trust peak — badges and familiar payment logos reduce anxiety at the moment it's highest.

---

## Pattern: Mobile Price Perception Optimization

**Use when:** Products where price is a conversion factor (most e-commerce).

**Implementation:**
- Display current and original prices on the same line, not stacked. Mobile: "$49.99 ~~$79.99~~" not two separate visual blocks
- Show savings as both dollar amount AND percentage: "Save $30 (38% off)" — different users respond to different frames
- BNPL installment price below main price: "or 4 payments of $12.50 with Afterpay"
- For charm pricing ($X.99): Ensure the leading digit is visually dominant. On mobile, "$49.99" should have the "49" larger/bolder than the ".99" — the left-digit effect is what drives perception, and on small screens the decimals can dilute it
- Free shipping threshold: Show progress bar in cart ("$12 away from free shipping!") — this is more effective on mobile than desktop because mobile carts are more likely to be single-item

**Why it works:** Price perception on mobile is shaped by the first number the eye lands on. With compressed layouts, there's less visual context to "justify" a price (no side-by-side comparison, no full feature list visible). Anchoring must be tighter (same line, same visual element) and the savings frame must do more work per pixel.

</patterns>

<anti_patterns>

## Anti-Pattern: Desktop Trust Wall on Mobile
**What:** Stacking 6-8 trust badges vertically on mobile, pushing product info and CTA below the fold.
**Why it fails:** Signals anxiety, not confidence. On mobile, sequence implies priority — a wall of badges before the product says "we're desperate."
**Fix:** 1-line trust strip near CTA. Detailed trust content in expandable sections or at checkout.

---

## Anti-Pattern: Reviews as Full-Page Destination
**What:** Tapping "Reviews" navigates away from the PDP to a separate page.
**Why it fails:** Context-switching on mobile is expensive. Returning to purchase requires re-finding the CTA — introducing a decision point at the worst moment.
**Fix:** Inline scroll-to on same page. "Back to top" floating button returns to CTA.

---

## Anti-Pattern: Aggressive Same-Session Conversion on Every Visit
**What:** Persistent bottom-bar CTAs, exit-intent popups, countdown timers on every mobile session.
**Why it fails:** Most mobile sessions are research. Aggressive pressure trains users your site is pushy and can decrease total cross-device conversion.
**Fix:** Adjust conversion pressure by session behavior — first-visit = research-friendly UX; returning with cart items = conversion-optimized.

---

## Anti-Pattern: Social Proof Notification Spam
**What:** Pop-up notifications every 15-30 seconds ("Someone just bought…" "42 viewing…" "Only 2 left!").
**Why it fails:** Each notification obscures product content. Combining notifications with reviews can REDUCE review effectiveness (Park & McCallister, 2023). Notification blindness after 2-3 instances.
**Fix:** Maximum one per session, timed to decision moment (>30s on PDP), dismissible, never covering CTA or price.

---

## Anti-Pattern: Hiding Total Until Checkout
**What:** Revealing shipping, tax, fees only at payment screen.
**Why it fails:** 48% cite unexpected costs as #1 abandonment reason (Baymard). On mobile, the effort to reach checkout is higher, making the price shock feel like a betrayal of effort.
**Fix:** Show estimated total on cart page. Better: show shipping cost on PDP ("Free shipping" or "$X shipping" adjacent to price).

---

## Anti-Pattern: Forcing Mobile AOV to Match Desktop
**What:** Aggressive upsells, cross-sells, and minimum thresholds on mobile to close the AOV gap.
**Why it fails:** The gap is partially structural (different shopping mode). Heavy upselling adds decision load on a constrained screen and can reduce conversion rate more than it increases AOV.
**Fix:** Accept lower mobile AOV. Optimize for conversion rate and cross-device journey facilitation. If pursuing AOV: lightweight post-add-to-cart suggestions only.

</anti_patterns>

<boundaries>

## When NOT to Apply

- **B2B/complex sales:** Research is B2C-based. B2B has different decision structures (stakeholders, POs, negotiated pricing). Don't apply impulse patterns to B2B mobile.
- **Mobile app vs mobile web:** App users have higher intent, saved payments, and persistent auth. App conversion/AOV significantly higher. Don't apply mobile-web trust fixes to app contexts.
- **High-regulation industries:** Compliance overrides conversion optimization. Don't compress disclosures.
- **Non-Western mobile-first markets:** China, India, SEA have different norms — super-app flows, social commerce, smaller/no AOV gap.
- **Desktop-dominant businesses:** If >60% of conversions are desktop (B2B SaaS, enterprise, some luxury), mobile CRO investment has lower ROI.

## Replication Concerns

- **Mobile AOV data:** No single authoritative source — composite of benchmarks with different methodologies. Directionally accurate, specific numbers should not be cited as exact.
- **Trust badge conversion impact:** Most stats come from vendor case studies or single-site tests. Direction established; magnitude varies enormously.
- **Social proof notifications:** Research is thin and conflicting. Park & McCallister (2023) suggests potential negative interaction effects. Test, don't assume.
- **Cross-device journey:** "90% switch devices" is poorly sourced. Astound Commerce says <10% visit same site multi-device. Real journey is often same-device-different-session.
- **One-click checkout 28.5%:** Single study context (Cornell). Results vary by category, price point, baseline experience.

## Conflicts with Other Domains

- **SEO vs Mobile CRO:** SEO wants extensive content; mobile CRO wants compression. Resolution: first viewport CRO-optimized, SEO content below fold in collapsible sections.
- **Accessibility vs compression:** Trust signal compression can harm accessibility. Resolution: maintain WCAG touch targets, semantic HTML, labeled collapsible sections.
- **Brand vs conversion:** Aggressive urgency/scarcity erodes brand trust. Resolution: only use signals backed by real data.
- **Privacy vs personalization:** Cross-device tracking requires user data. Resolution: first-party data, explicit consent where required.

</boundaries>

<key_data>

| Metric | Value | Source | Year | Confidence |
|--------|-------|--------|------|------------|
| Mobile share of e-commerce traffic | ~75-77% | Statista (29B visits, 2,276 sites) | Q3 2024 | High |
| Mobile share of e-commerce orders | ~57-65% | Statista, Salesforce | 2024 | High |
| Desktop vs mobile conversion rate | ~3.9% vs ~1.8% | Retail Touchpoints | 2025 | High |
| Desktop vs mobile AOV | $122-230 vs $86-149 | Dynamic Yield, OpenSend, Kibo | 2024-2025 | Medium (range is wide) |
| App AOV vs mobile web AOV | ~$217 vs ~$194 | jmango360 | 2024 | Medium (single source) |
| Mobile cart abandonment | ~78-80% vs ~70.2% cross-device avg | SaleCycle/XP2, Baymard (50-study aggregate) | 2025 | Medium-High |
| Apple Pay mobile conversion vs traditional | 58% higher | Envive compilation | 2025 | Medium (vendor-adjacent) |
| Digital wallet share of online transactions | 53% | Worldpay | 2024 | High |
| Situational stimuli effect on impulse buying | ESr=0.477 (strongest factor) | Anoop meta-analysis (75 articles, n=139,545) | 2025 | High |
| Mobile emotional ambivalence → abandonment | Significant mediator | Huang et al. (n=599, two studies) | 2018 | Medium-High (peer-reviewed) |
| Negative review fixation > positive on mobile | Significant | Chen & Samaranayake (Frontiers in Psychology) | 2022 | Medium (peer-reviewed) |
| Multi-device shoppers: purchase rate | 55% vs 6% single-device | Monetate (2B+ sessions) | Q4 2017 | Medium (dated) |
| Users who visit same site multi-device | <10% | Astound Commerce | 2019 | Medium (dated) |
| Checkout steps >5 abandonment increase | 22% | WiserReview | 2025 | Medium |
| Mobile center-bias gaze pattern | 60-70% of screen width | Xu et al. (Nature Communications, n=100+) | 2020 | High (peer-reviewed) |
| First viewport fixation time vs subsequent | 2-3x more | NNGroup eyetracking | 2017-2024 | High |
| Expected reviews per product (age 18-24) | 203 reviews | BrightLocal | 2024 | Medium |
| BNPL AOV increase | 40%+ (vendor-reported) | Multiple BNPL providers | 2024 | Low (vendor data) |
| Product research starting on mobile | ~70% | Multiple sources | 2024-2025 | Medium (methodology unclear) |

</key_data>
