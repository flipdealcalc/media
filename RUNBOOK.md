# Weekly posting runbook (for the Sunday scheduled task)

This repo holds everything needed to make and schedule one week of Flip Deal Calculator posts on Instagram and TikTok through Metricool, with no human review. Owner: Ian (ian@kcmhvac.com). Posting is fully hands-off by his choice, so the rules below matter.

## Accounts
- Metricool brand id: **7803252**, timezone America/Indianapolis. Networks: instagram (@flipdealcalc, Business), tiktok (@flipdealcalc, General account: no clickable bio link until verified or 1,000 followers).
- Store: https://flipdealcalc.gumroad.com/l/flip ($39 spreadsheet), https://flipdealcalc.gumroad.com/l/free (free web calculator).
- Discount codes: INSTA, TIKTOK, FBGROUP ($5 off). LAUNCH ($10 off) ended Nov 8, 2026, so don't mention it after that.
- Video URLs for Metricool: `https://raw.githubusercontent.com/flipdealcalc/media/main/<path>` (see "Media URLs" below for the tested format).

## Each Sunday
1. `git pull`. Read `log/` to see what has already been posted. Don't repeat a topic from the last 4 weeks.
2. Pull last week's numbers: Metricool analytics for instagram and tiktok (views, reach, follows, comments). Note which topics did best.
3. Pick 7 topics for Mon–Sun. Favor what performed best. Topic bank:
   - Run a deal: a new asking / sqft / ARV / rehab level → verdict (vary price points: $60K–$250K, Midwest-typical)
   - A loan comparison on a new deal (hard money vs conventional vs HELOC)
   - The worst-case stress test on a new deal
   - A rehab-level explainer (light / average / heavy / very heavy, with what each includes)
   - Common mistakes: ARV from the average instead of the low comp, forgetting holding costs, no contingency, using the 70% rule on small houses
   - "Would you buy this?" teardown (end with "comment your answer")
   - Spreadsheet feature tour (use shots/ from the real spreadsheet; at most 1 in 7 posts is a direct sales post)
4. For every deal number: run `python3 tools/calc_shot.py NAME --asking A --sqft S --arv R --level L`. Use ONLY the numbers it prints. Never type a number you did not get from the calculator or from a previous plan in this repo.
5. Write `plans/YYYY-MM-DD_slug.json` for each day (format in `tools/render_plan.py`), 18–28 seconds, 5–7 scenes, ending with an `end` scene: cta "Free calculator · link in bio".
6. Render: `python3 tools/render_plan.py plans/<each>.json`. Open a few frames from `build/<id>/` and check that text fits and doesn't overlap. Fix and re-render if needed.
7. Write `log/week_YYYY-MM-DD.json` (same shape as week_2026-11-02.json) with Instagram and TikTok captions.
   - Instagram: hook line, 1–3 short lines with the numbers, CTA "Comment CALC and I'll DM you the free calculator." (or "Link in bio" for the spreadsheet), 4–5 hashtags.
   - TikTok: one or two sentences plus "Free calculator link is on my IG @flipdealcalc" (until the TikTok bio link exists), 3–4 hashtags.
8. Commit and push (posts/, plans/, shots/, log/). Wait ~1 minute, then check each raw URL returns 200.
9. Schedule in Metricool at 10:00 America/Indianapolis, one post per network per day:
   - Instagram: `instagramData.type = "REEL"`, `showReelOnFeed: true`, `isAiGenerated: false`.
   - TikTok: `tiktokData.title` (required, short hook), `privacyOption = "PUBLIC_TO_EVERYONE"`, `commercialContentOwnBrand: true`, `isAigc: false`.
   - `autoPublish: true`. Save each returned post id/plannerUrl into the week log and push again.
10. Send Ian a short report: what was posted last week and how it did (views, follows, comments, link clicks if available), what's scheduled this week, and anything he should do (for example, reply to deal comments).

## Hard rules (no human reviews these posts)
- No promises of profit or income. No "guaranteed", "passive income", "get rich" language.
- No fake reviews, testimonials, buyer counts or sales claims.
- No real person's name or a full street address. Real listings can be described ("925 sq ft ranch listed at $194,900") but not identified.
- Every post shows "Estimates only. Not financial advice." on the end card (the end scene does this automatically).
- If a render fails, a number looks wrong, or Metricool rejects a post, skip that day rather than post something broken, and say so in the report.
- Don't change prices, discount codes, the Gumroad store or account settings.

## Media URLs
Tested 2026-11-01: `https://raw.githubusercontent.com/flipdealcalc/media/main/posts/<file>.mp4` works. Metricool copies the file to its own storage when the post is created, so the push must land before scheduling. If it ever fails, try `https://github.com/flipdealcalc/media/raw/main/<path>`.
