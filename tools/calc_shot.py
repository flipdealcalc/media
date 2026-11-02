"""Run a deal through the web calculator and save screenshots + the real numbers.

Usage (from repo root):
  python3 tools/calc_shot.py NAME --asking 120000 --sqft 1100 --arv 199000 [--level average] [--address "3 bed ranch"] [--extra id=value ...]

Saves (all JPEG, phone-sized unless noted):
  shots/NAME_deal.jpg      deal inputs (asking, sqft, ARV)
  shots/NAME_rehab.jpg     rehab section
  shots/NAME_hold.jpg      holding costs
  shots/NAME_sell.jpg      selling costs
  shots/NAME_offer.jpg     max offer panel
  shots/NAME_profit.jpg    profit + worst case panel
  shots/NAME_bar.jpg       where the ARV goes
  shots/NAME_verdict.jpg   GO / PASS verdict card
  shots/NAME_loans.jpg     desktop: cash out of pocket, 3 loans
  shots/NAME_cases.jpg     desktop: best / expected / worst case by loan
and prints every number as JSON. ONLY use numbers printed here in captions and on-screen text.
Useful crops: deal shots look best with "crop": [0, 285, 992, 1404].
"""
import argparse, json, os
from playwright.sync_api import sync_playwright

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
URL = "file://" + os.path.join(ROOT, "calculator", "index.html")

ap = argparse.ArgumentParser()
ap.add_argument("name"); ap.add_argument("--asking", type=float, required=True)
ap.add_argument("--sqft", type=float, required=True); ap.add_argument("--arv", type=float, required=True)
ap.add_argument("--level", default="average", choices=["light", "average", "heavy", "veryheavy", "custom"])
ap.add_argument("--address", default="Example deal")
ap.add_argument("--extra", nargs="*", default=[], help="more input ids, e.g. months=8 contingency=15")
a = ap.parse_args()
os.makedirs(os.path.join(ROOT, "shots"), exist_ok=True)


def path(part):
    return os.path.join(ROOT, "shots", f"{a.name}_{part}.jpg")


def setup(p):
    p.goto(URL); p.evaluate("localStorage.clear()"); p.reload(); p.click("#btnExample")
    p.fill("#address", a.address); p.fill("#asking", str(int(a.asking))); p.fill("#sqft", str(int(a.sqft)))
    p.fill("#arv", str(int(a.arv))); p.select_option("#rehabLevel", a.level)
    for kv in a.extra:
        k, v = kv.split("=", 1); p.fill("#" + k, v)
    p.wait_for_timeout(200)


with sync_playwright() as pw:
    b = pw.chromium.launch()
    m = b.new_page(viewport={"width": 390, "height": 844}, device_scale_factor=2.77)
    setup(m)
    m.evaluate("var c=document.querySelector('#checklist'); if(c) c.style.display='none'")
    shots = {"deal": "fieldset:nth-of-type(1)", "rehab": "fieldset:nth-of-type(2)", "hold": "fieldset:nth-of-type(3)",
             "sell": "fieldset:nth-of-type(4)", "verdict": "#verdict", "offer": ".results .panel:nth-of-type(3)",
             "profit": ".results .panel:nth-of-type(4)", "bar": ".results .panel:nth-of-type(5)"}
    for k, sel in shots.items():
        m.locator(sel).first.screenshot(path=path(k), type="jpeg", quality=92)
    nums = m.evaluate("""()=>({mao_true:r_mao1.textContent, mao_70:r_mao2.textContent, max_offer:r_offer.textContent,
      room_vs_asking:r_room.textContent, profit_at_asking:r_profit.textContent, profit_pct_arv:r_pct.textContent,
      worst_case:r_worst.textContent, verdict:vTag.textContent, verdict_line:vHead.textContent,
      rehab_budget:o_rehab.textContent, holding:o_hold.textContent, selling:o_sell.textContent, acquisition:o_acq.textContent})""")
    d = b.new_page(viewport={"width": 1280, "height": 900}, device_scale_factor=2)
    setup(d)
    d.locator("#lc_t1").screenshot(path=path("loans"), type="jpeg", quality=92)
    d.locator("#lc_t6").screenshot(path=path("cases"), type="jpeg", quality=92)
    rows = lambda t: d.evaluate(f"()=>[...document.querySelectorAll('#{t} tr')].map(r=>[...r.children].map(c=>c.textContent.trim()))")
    nums["loan_table_cash"] = rows("lc_t1")
    nums["loan_table_sell_cases"] = rows("lc_t6")
    nums["inputs"] = {"asking": a.asking, "sqft": a.sqft, "arv": a.arv, "level": a.level, "extra": a.extra}
    b.close()
json.dump(nums, open(os.path.join(ROOT, "shots", f"{a.name}_numbers.json"), "w"), indent=1)
print(json.dumps({k: v for k, v in nums.items() if not k.startswith("loan_table")}, indent=1))
