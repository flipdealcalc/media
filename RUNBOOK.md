# Weekly posting runbook (for the Sunday scheduled task)

This repo holds everything needed to make and schedule one week of **Deal Ledger** posts on Instagram, TikTok and Facebook through Metricool, with no human review. Owner: Ian (ian@kcmhvac.com). Posting is fully hands-off by his choice, so the rules below matter.

## Brand and accounts
- Brand: **Deal Ledger**: spreadsheets for flips, rentals and BRRRRs. "Analyze the deal. Then run it."
- Metricool brand id: **7803252**, timezone America/Indianapolis. Call `getBrandSettings` first: `networksData` lists the networks actually connected and their current handles. Only schedule to networks listed there. Handles: Instagram **@dealledgerhq**, TikTok **@dealledgerhq**, Facebook Page **Deal Ledger** (renamed 2026-11-03 from flipdealcalc). Metricool may keep showing the old names for a while; the connections still post to the renamed accounts. Never use @flipdealcalc in captions.
- TikTok is a General account (no clickable bio link until verified or 1,000 followers): TikTok captions point to the Instagram handle for the link.
- Store (Gumroad): **https://dealledgerhq.gumroad.com** (username changed from flipdealcalc on 2026-11-04; flipdealcalc.gumroad.com links no longer work, never use them).
  - Live (checked 2026-11-04): /l/flip (Flip Deal Calculator, $39), /l/free (free web flip calculator), /l/rental (Rental Deal Calculator, $29), /l/brrrr (BRRRR Calculator, $29), /l/flip-tracker (Flip Project Tracker, $39), /l/rental-tracker (Rental Portfolio Tracker, $49)
  - Also live: /l/deal-pipeline (Deal Pipeline, $19), /l/investor-toolkit (Investor Toolkit bundle, all 7, $129). Portfolio Dashboard ($19): check `log/store_links.json` for its URL. If a link isn't listed there, don't link that product; say "link in bio" on Instagram or skip the link.
  - Before promoting any product link, fetch it and make sure it loads.
- Discount codes: INSTA, TIKTOK, FBGROUP ($5 off). LAUNCH ended Nov 8, 2026, so don't mention it.
- Video URLs for Metricool: `https://raw.githubusercontent.com/flipdealcalc/media/main/<path>`.

## Tools in this repo
- `tools/calc_shot.py`: runs a flip through the free web calculator; phone-sized screenshots + numbers.
- `tools/xl_calc.py`: runs a deal through any Deal Ledger spreadsheet (BRRRR, Rental, Flip calculators and the trackers) and prints every number; `--shot NAME` saves a picture of the results.
  - The spreadsheets are the paid products, so they are **never** committed to this public repo (`spreadsheets/` is git-ignored). They live in the private repo **flipdealcalc/Deal-Ledger-Private**. Attach it with add_repo (access read), clone it to /home/claude/private, and run xl_calc with `SPREADSHEETS_DIR=/home/claude/private/spreadsheets`.
  - If the private repo can't be reached, skip rental/BRRRR deal posts that week and use flip topics (calc_shot.py) or tips instead. Say so in the report.
  - BRRRR: `SPREADSHEETS_DIR=/home/claude/private/spreadsheets python3 tools/xl_calc.py BRRRR_Calculator "BRRRR Calculator" '{"Purchase price": 90000, "After-repair value (ARV)": 180000, "Rehab budget": 35000, "Monthly rent": 1650}' --shot brrrr_1108`
  - Rental: `SPREADSHEETS_DIR=/home/claude/private/spreadsheets python3 tools/xl_calc.py Rental_Deal_Calculator "Rental Calculator" '{"Purchase price": 140000, "Monthly rent": 1500}' --shot rental_1109`
- `tools/render_plan.py`: turns a plan JSON into a finished 9:16 video with original music. Brand pill reads "DEAL LEDGER".
- `shots/`: screenshots of the real spreadsheets and calculators.

## Each Sunday
1. `git pull`. Read `log/` to see what has already been posted. Don't repeat a topic from the last 4 weeks.
2. `getBrandSettings`, then last week's Metricool analytics for each connected network (views, reach, follows, comments). Note which topics did best.
3. Pick 7 topics for Mon–Sun. Rotate across the whole line, roughly: 2 flip, 2 rental or BRRRR, 1 tracking/organization, 1 "would you buy this?", 1 tip or mistake. Favor what performed best. At most 1 in 7 posts is a direct sales post (bundle or a product tour). Topic bank:
   - Run a flip: asking / sqft / ARV / rehab level → max offer, profit, worst case, verdict
   - Run a BRRRR: cash in, cash back at refi, cash left in, max price for all cash back, what a low appraisal does
   - Run a rental: cash flow, cash-on-cash, DSCR, 1% rule, why "cash flow" on a listing is usually wrong (missing vacancy, capex, management)
   - Loan comparison: hard money vs conventional vs HELOC on one deal
   - Tracking: Schedule E categories (interest vs principal, repairs vs capital improvements), lien waivers on every draw, budget vs actual on a flip, lease renewals 60 days out
   - Common mistakes: ARV from the average comp, no contingency, forgetting holding costs, using the 70% rule on small houses, BRRRR without checking seasoning
   - "Would you buy this?" teardown (end with "comment your answer")
   - Tool tour (sales post): one tool at a time, or the Investor Toolkit bundle
4. Numbers: use ONLY numbers printed by `calc_shot.py` or `xl_calc.py` (or a previous plan in this repo). Never type a number you didn't get from a tool. Midwest-typical deals: $60K–$300K.
5. Write `plans/YYYY-MM-DD_slug.json` for each day (format in `tools/render_plan.py`), 18–28 seconds, 5–7 scenes, ending with an `end` scene: cta "Free calculator · link in bio" (or "Toolkit · link in bio" for a sales post).
6. Render: `python3 tools/render_plan.py plans/<each>.json`. Open a few frames from `build/<id>/` and check that text fits and doesn't overlap. Fix and re-render if needed.
7. Write `log/week_YYYY-MM-DD.json` (same shape as week_2026-11-02.json) with captions per network:
   - Instagram: hook line, 1–3 short lines with the numbers, CTA "Comment CALC and I'll DM you the free calculator." (or "Link in bio"), 4–5 hashtags.
   - Facebook: same as Instagram but a full link instead of "link in bio" (for example https://dealledgerhq.gumroad.com/l/free), 2–3 hashtags.
   - TikTok: one or two sentences plus "Link is on my IG @dealledgerhq", 3–4 hashtags. Needs `tiktokData.title` (short hook).
8. Commit and push (posts/, plans/, shots/, log/). Wait ~1 minute.
9. Schedule in Metricool at 10:00 America/Indianapolis, one post per connected network per day (separate posts so each gets its own caption):
   - Instagram: `instagramData.type = "REEL"`, `showReelOnFeed: true`, `isAiGenerated: false`.
   - Facebook: `facebookData.type = "REEL"`.
   - TikTok: `tiktokData.title`, `privacyOption = "PUBLIC_TO_EVERYONE"`, `commercialContentOwnBrand: true`, `isAigc: false`.
   - `autoPublish: true`. Save each returned post id into the week log and push again.
10. Send Ian a short report: last week's results per network and the top post, this week's 7 topics, and anything he should do (reply to deal comments, a failed post, a product link that isn't live).

## Product spotlights (6 PM slot)
- A second daily slot at **18:00** is used for product spotlight Reels (one product per day, all three networks). Nov 5–10, 2026 are scheduled: see `log/spotlights_2026-11-05.json`. The weekly 10:00 posts stay as they are.
- Portfolio Dashboard has no spotlight yet: on 2026-11-04 its page (/l/portfolio) still showed the Rental Portfolio Tracker's name and $49 price. Before giving it a spotlight, fetch the page and confirm it says Portfolio Dashboard and $19.
- After Nov 10, keep at most 2 product spotlights per week at 18:00, rotating products, and only for links in `log/store_links.json` that load.

## Hard rules (no human reviews these posts)
- No promises of profit or income. No "guaranteed", "passive income", "get rich" language.
- No fake reviews, testimonials, buyer counts or sales claims.
- No real person's name or a full street address. Real listings can be described ("925 sq ft ranch listed at $194,900") but not identified.
- No tax advice: tracking posts explain categories and say "ask your CPA" for anything beyond that.
- Every post shows "Estimates only. Not financial advice." on the end card (the end scene does this automatically).
- If a render fails, a number looks wrong, or Metricool rejects a post, skip it rather than post something broken, and say so in the report.
- Don't change prices, discount codes, the Gumroad store or account settings.
- Never commit a paid spreadsheet (.xlsx), a buyer file, or anything from the private repo into this public repo. Screenshots of results are fine.

## Media URLs
Tested 2026-11-01: `https://raw.githubusercontent.com/flipdealcalc/media/main/posts/<file>.mp4` works. Metricool copies the file to its own storage when the post is created, so the push must land before scheduling. If it ever fails, try `https://github.com/flipdealcalc/media/raw/main/<path>`.
