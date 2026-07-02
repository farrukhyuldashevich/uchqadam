# UchQadam — Product Requirements Document

**Version:** v1.0 (working draft)
**Period:** July 1 – August 31, 2026 (60 days)
**Owner:** Farrukh Rasulov
**Status:** Pre-launch, store + neighborhood locked in

---

## 1. One-line summary

A 60-day, single-store, single-neighborhood experiment to validate whether residents within ~500m of one Tashkent convenience store will use a digital channel (Telegram) to order everyday goods and pay for delivery.

## 2. North star question

**"Given a frictionless digital ordering channel, will people in this neighborhood order from this store often enough that the behavior is real, repeatable, and worth scaling?"**

Everything in this PRD ladders up to producing a defensible answer — yes, no, or a specific list of conditions — by **August 31, 2026**.

## 3. Why this matters / strategic context

This is *not* a quick-commerce play. Speed is not the value proposition. Convenience is. Tashkent summer heat (40°C+), the universality of Telegram, the prevalence of cash/local-transfer payments, and the cultural habit of messaging local stores directly all suggest that demand may already exist informally. The experiment is to convert that latent behavior into a measurable, repeatable funnel — without spending money or building anything the validation does not require.

Negative result is acceptable and useful. A clean "no" in 60 days is more valuable than a hopeful "maybe" in 6 months.

## 4. Users & merchant

**Customers.** Residents within ~500m of the partner store. Primary segment: working-age adults (~25–45) who already use Telegram daily and are time-constrained, heat-averse, or both. Secondary: older household-purchase decision-makers who may use Telegram only for messaging today.

**Merchant.** One convenience store, already identified and committed (as of June 29, 2026). The store's existing inventory defines the initial catalog. The merchant must agree to: (a) provide a product list with prices, (b) accept orders pushed to them via a private Telegram channel, (c) prepare orders within a target window, (d) hand off to a delivery person.

**Delivery.** Founder + 1–2 paid helpers, on foot or by bike. No dedicated fleet, no contracts.

## 5. Scope

**In scope (Month 1 + 2):**

- Concierge ordering (manual, Telegram DM + Google Sheets)
- Traditional Telegram commerce bot (catalog, cart, checkout, COD)
- Merchant order-notification channel
- Basic order tracking, daily metrics dashboard
- Customer acquisition through mahalla Telegram chats, physical flyers, word of mouth
- Cash on delivery; opt-in Click/Payme by end of Month 2 if COD friction is the dominant blocker
- Lightweight retention loop (re-engagement messages, simple bundles)

**Out of scope:**

- Native mobile app (Android/iOS)
- Standalone web app / PWA
- AI conversational ordering (deferred — revisit only if catalog UX is proven to be the bottleneck after ≥100 orders)
- Multi-store onboarding
- Automated dispatch, routing optimization, ETA prediction
- Loyalty programs beyond a single referral mechanic
- Investor materials
- Anything that requires paid infrastructure beyond ~$10/month

## 6. Success criteria

Two layers — a **floor** (means we have a real signal) and a **stretch** (the optimistic but plausible target).

### Month 1 (July) — Launch & initial iteration

| Metric | Floor | Stretch |
|---|---|---|
| Unique orderers | 30 | 100 |
| Total orders | 50 | 150 |
| Repeat orderers (≥2 orders) | 1+ | 15+ |
| Days from concierge launch to bot live | ≤21 | ≤14 |
| Catalog SKUs live | 30 | 60 |
| Median delivery time | ≤30 min | ≤15 min |

### Month 2 (August) — Growth & metrics

| Metric | Floor | Stretch |
|---|---|---|
| Weekly active orderers (last week of Aug) | 50 | 150 |
| Repeat rate (% of users with ≥2 orders) | 25% | 50% |
| Average order value (AOV) | 25,000 sum | 60,000 sum |
| Orders attributable to a measurable acquisition channel | ≥60% | ≥80% |
| Cancellation / no-show rate | <15% | <5% |
| Digital payment share (if Click/Payme launched) | n/a | ≥30% |

### Decision gate at end of August

- **Continue & scale to second store** if: ≥50 weekly active orderers AND ≥25% repeat rate AND store-level economics aren't negative at unit level (delivery fee covers helper payment + small contribution to time).
- **Continue with fixes** if: weekly actives ≥30 but repeat <25% — investigate whether the bottleneck is selection, price, delivery, or trust.
- **Stop or restructure** if: <20 weekly actives by end of August despite executing acquisition push. The signal is the absence of demand, not the absence of effort.

## 7. Timeline — week by week

The plan is intentionally front-loaded. July is intensive so August has the runway to push acquisition and metrics hard.

### Month 1 — July

**Week 1 (July 1–7) — Concierge live**
- Day 1–2: Final catalog with merchant (start with 10–15 high-velocity SKUs: water, bread, milk, eggs, snacks, ice cream, household basics)
- Day 1: Create the public-facing Telegram presence (channel + DM contact) with name, hours, delivery radius map, price list
- Day 2: Set up Google Sheets backbone — `catalog`, `orders`, `customers`, `daily_metrics` tabs
- Day 3: Soft launch to personal network within radius (5–10 people). Take orders manually via DM. Deliver yourself.
- Day 4–7: Iterate on catalog (add what people asked for), order intake (refine the message template), and the merchant handoff. Target: 10 orders by end of week.
- **Week 1 success:** ≥5 orders, 0 critical failures (wrong items, missed deliveries).

**Week 2 (July 8–14) — Expand & observe**
- Expand catalog to 30+ SKUs based on Week 1 demand patterns
- Recruit 1–2 paid delivery helpers (per-order pay)
- Post first announcements in 2–3 mahalla Telegram chats
- Add structured intake template: customers send orders in a known format that's faster to process
- Begin daily metric logging (a 60-second end-of-day routine)
- **Week 2 success:** ≥20 orders, ≥15 unique customers, ≥1 repeat customer.

**Week 3 (July 15–21) — Build the bot in parallel**
- Continue concierge in foreground; build bot in background
- Stack: aiogram (Python) on a free Railway/Render tier OR run on a laptop initially
- Google Sheets stays as the data layer (merchant edits catalog from their phone)
- Bot features (minimum viable): browse catalog with photos + prices, add to cart, place order with name/address/phone, COD only
- Merchant notification = private Telegram group; bot posts each order with Accept/Reject buttons
- **Week 3 success:** Bot functionally complete in staging by Friday; merchant has tested placing a fake order and accepting it.

**Week 4 (July 22–31) — Migrate & soft launch**
- Mon–Tue: bot in production; concierge still available as fallback for 1 week
- Wed: announce the bot in the same 2–3 mahalla chats + push to existing concierge customers via DM
- Goal: migrate the existing customer base + onboard new ones
- Build a basic metrics view: daily order count, unique customers, repeat rate, AOV, cancellation rate (Google Sheets pivot or a simple Looker Studio dashboard pointing at the sheet)
- **Month 1 close (July 31):** Run a personal retro. What surprised you? What is the strongest signal? What is the strongest negative signal? Document in a one-page learning log.

### Month 2 — August

**Week 5 (Aug 1–7) — Acquisition experiments**
- Test 3 acquisition channels in parallel, each with a trackable identifier:
  1. Mahalla Telegram chat posts (organic + scheduled)
  2. Physical flyer drop in the radius (QR → bot start link with a UTM-like param)
  3. Referral incentive: existing customer who refers a new one gets ~5,000 sum off their next order
- Track first-order conversion per channel
- **Week 5 success:** ≥30 new unique orderers added; you can name your highest-converting channel.

**Week 6 (Aug 8–14) — Reduce the friction that matters**
- Diagnose the dominant order-blocker from observed data + light customer DMs:
  - If it's payment friction: integrate Click or Payme card-on-file
  - If it's catalog navigation: add a "popular this week" quick-buy section
  - If it's trust / first-order anxiety: add a visible review/testimonial loop in the channel
- Avoid building all three "just in case." Pick the one with evidence behind it.
- **Week 6 success:** Identified friction is measurably lower the following week.

**Week 7 (Aug 15–21) — Retention & order frequency**
- Implement a low-touch retention loop: customers who haven't ordered in 7 days get one (and only one) re-engagement message featuring a relevant SKU or small incentive
- Test order bundling: pre-built bundles ("breakfast pack," "ice cream night") at a small discount vs. à la carte
- Test peak-hour push: a short message in the channel during high-heat hours (~14:00–17:00) reminding people you exist
- **Week 7 success:** Repeat rate improves week-over-week; ≥1 bundle pattern shows pickup.

**Week 8 (Aug 22–31) — Compile, decide, document**
- Hold the experiment steady — no new features unless something is breaking
- Build the end-of-experiment report: orders, customers, cohorts, AOV trend, repeat curve, channel-level CAC (proxied by time spent), merchant feedback, customer DMs that stood out
- Make the explicit go/no-go decision against the criteria in §6
- Document the playbook: what worked, what didn't, what to keep, what to throw away
- **August 31 close:** A decision is on paper. If "go," the Month 3 plan is sketched. If "no-go," the lessons are extracted so the next experiment is sharper.

## 8. MVP architecture

Deliberately minimal. Everything either free or near-free.

| Layer | Choice | Why |
|---|---|---|
| Customer interface | Telegram (DM in Week 1, bot from Week 3–4) | Zero install, already universal |
| Bot framework | aiogram (Python) — backup: grammY (Node.js) | Free, well-documented, mature |
| Hosting | Railway free tier, fallback to laptop in Week 1–2 | Free, deploys from Git |
| "Database" (Weeks 1–6) | Google Sheets via Sheets API | Merchant edits catalog from phone, orders append as rows, no admin panel to build |
| Database (Week 7+ if needed) | SQLite or Supabase free tier | Only if Sheets actually breaks under load |
| Merchant interface | Private Telegram group with bot order-posts + buttons | No dashboard to build |
| Payments | COD only initially; Click/Payme added in Week 6 *if* warranted | Validate demand before payment integration paperwork |
| Photos | Founder's phone | Don't pay for stock |
| Metrics | Google Sheets formulas → Looker Studio (free) for visuals | Free, looks professional |
| Comms with customers | Telegram only | Same channel customers already prefer |

## 9. User flow

**Customer first order (target ≤4 taps from link tap to order placed):**
1. Sees post in mahalla chat OR scans flyer QR → opens bot link
2. Presses **Start** → sees welcome + radius map + "Browse menu" button
3. Browses categories → adds items to cart → taps **Checkout**
4. Enters name + apartment/landmark + phone → confirms COD → submits

**Behind the scenes:**
5. Bot posts order to merchant group with all line items + customer contact + delivery instructions
6. Merchant taps **Accept** → bot DMs customer the confirmation + ETA
7. Merchant packs order → notifies delivery person
8. Delivery person picks up → delivers → collects cash → marks order complete in the group

**Repeat order:** customer messages the bot, last cart is suggested as a quick reorder, ~2 taps to a completed order.

## 10. Risks & mitigations

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| No demand — zero or trickle of orders in Weeks 1–2 | Medium | High | This is the question being tested. Pre-commit to the kill-switch at end of August. Don't keep building if Week 2 ends with <5 orders. |
| Merchant flakiness (slow prep, inventory gaps, walks away) | Medium | High | Weekly 15-min check-in; written agreement on basics; have a backup store on a watchlist by Week 3 |
| Delivery helper unreliable | Medium | Medium | Always have a backup; founder personally delivers when needed (also a great way to talk to customers) |
| Cash handling errors / disputes | Low | Medium | Day-end reconciliation; small float; written log per order |
| Bot bugs that look like ghost orders | Medium | Medium | Manual fallback always on — if bot breaks, point users back to DM in Week 1–4; in Aug, have a written kill-switch + manual mode |
| Founder burnout — July is intentionally intensive | Medium | High | Block one full day off per week; the experiment is 60 days, not 60 sprints. |
| Over-engineering temptation (AI ordering, native app, multi-store) | High | Medium | This PRD is the answer when the temptation hits — read §5 again |
| Demand exists but unit economics don't work | Low | High | Track per-order time + helper cost from Week 2. Even a "yes" answer needs viable math. |

## 11. What's deliberately NOT in this PRD

- A startup pitch deck
- Investor-grade financial model
- Multi-city scaling plan
- App design mockups
- A brand identity exercise
- AI conversational ordering (Option 3B) — revisit *only* if there are ≥100 orders AND there's evidence catalog navigation is the bottleneck

If you find yourself building any of the above before August 31, stop and ask whether it's serving the north star question.

## 12. Post-experiment roadmap (sketch only)

Only relevant if the August 31 decision is "go." Not a commitment.

- **September:** Tighten the loop on the existing store. Improve unit economics. Decide explicitly whether to deepen single-store penetration or onboard store #2.
- **Q4:** If onboarding store #2, treat it as a second experiment, not a copy-paste. Different store, possibly different micro-neighborhood, fresh acquisition test.
- **Later:** PWA companion for richer browsing (only when catalog complexity demands it). Native app only when there are multiple stores AND push notifications / location services would meaningfully change retention. Telegram-first remains the durable model — in CIS markets, this isn't a stepping stone, it's a primary channel.

## 13. Founder operating rhythm

- **Daily (60 seconds, end of day):** Log orders, unique customers, any incidents, one observation
- **Weekly (30 minutes, Sunday evening):** Review the week against the Month's success criteria. Decide one experiment to run next week. Write a 3-line journal entry.
- **End of Month 1 (July 31):** One-page retro. What surprised you? What's the strongest signal? Confirm or revise Month 2 plan.
- **End of Month 2 (August 31):** End-of-experiment report + go/no-go decision against §6 criteria.

---

*This PRD is a working document. Update it as reality teaches you things. The version dated 2026-06-29 is your reference for what you committed to before the experiment started — keep an honest log of where reality diverged.*
