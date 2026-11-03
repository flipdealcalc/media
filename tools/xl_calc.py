"""Run a deal through one of the Deal Ledger spreadsheets and read back the real numbers.

Usage (from repo root):
  python3 tools/xl_calc.py BRRRR_Calculator "BRRRR Calculator" '{"Purchase price": 95000, "Monthly rent": 1900}' [--shot NAME]
  python3 tools/xl_calc.py Rental_Deal_Calculator "Rental Calculator" '{"Purchase price": 140000, "Monthly rent": 1500}'

Inputs are matched by the label in column A of that sheet (the value goes in column B, yellow cells only).
Prints every label/value pair on the sheet (inputs, working numbers and results) as JSON.
--shot NAME also saves shots/NAME_results.jpg: a picture of the results side of the sheet.
ONLY use numbers printed here in captions and on-screen text.
Needs LibreOffice; recalculation uses /mnt/skills/public/xlsx/scripts/recalc.py when present.
"""
import json, os, shutil, subprocess, sys, tempfile
import openpyxl

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RECALC = "/mnt/skills/public/xlsx/scripts/recalc.py"


def run(book, sheet, inputs, shot=None):
    src = os.path.join(os.environ.get("SPREADSHEETS_DIR", os.path.join(ROOT, "spreadsheets")), book + ".xlsx")
    tmpd = tempfile.mkdtemp()
    tmp = os.path.join(tmpd, book + ".xlsx")
    shutil.copy(src, tmp)
    wb = openpyxl.load_workbook(tmp)
    ws = wb[sheet]
    found = set()
    for r in range(1, ws.max_row + 1):
        lab = ws.cell(row=r, column=1).value
        if isinstance(lab, str) and lab.strip() in inputs:
            c = ws.cell(row=r, column=2)
            if c.protection.locked:
                sys.exit(f"'{lab}' is not an input cell")
            c.value = inputs[lab.strip()]; found.add(lab.strip())
    missing = set(inputs) - found
    if missing: sys.exit(f"labels not found on {sheet}: {sorted(missing)}")
    wb.save(tmp)
    if os.path.exists(RECALC):
        subprocess.run(["python3", RECALC, tmp, "120"], check=True, capture_output=True)
    else:
        sys.exit("recalc script not found: install LibreOffice and a recalculation step")
    v = openpyxl.load_workbook(tmp, data_only=True)[sheet]
    out = {}
    for r in range(1, v.max_row + 1):
        for lc, vc in ((1, 2), (5, 6)):
            lab, val = v.cell(row=r, column=lc).value, v.cell(row=r, column=vc).value
            if isinstance(lab, str) and val is not None and lab.strip():
                out[lab.strip()] = round(val, 4) if isinstance(val, float) else val
    if shot:
        vis = [w.title for w in openpyxl.load_workbook(tmp).worksheets if w.sheet_state == 'visible']
        vis_idx = vis.index(sheet)
        subprocess.run(["soffice", "--headless", "--convert-to", "html", "--outdir", tmpd, tmp], check=True, capture_output=True)
        html = os.path.join(tmpd, book + ".html")
        js = f"""const {{chromium}}=require('playwright');(async()=>{{const b=await chromium.launch();const p=await b.newPage({{viewport:{{width:1600,height:1000}},deviceScaleFactor:2}});
await p.goto('file://{html}');await p.addStyleTag({{content:'body{{background:#fff;font-family:Arial}} td{{padding:2px 6px}}'}});
const t=await p.$$('table');let idx={vis_idx};
await t[Math.min(idx,t.length-1)].screenshot({{path:'{tmpd}/sheet.png'}});await b.close();}})();"""
        open(os.path.join(tmpd, "s.js"), "w").write(js)
        subprocess.run(["node", os.path.join(tmpd, "s.js")], check=True, capture_output=True)
        from PIL import Image
        im = Image.open(os.path.join(tmpd, "sheet.png")).convert("RGB")
        # results live on the right half of calculator sheets
        im = im.crop((int(im.width * 0.585), 0, im.width, min(im.height, int(im.width * 0.9))))
        os.makedirs(os.path.join(ROOT, "shots"), exist_ok=True)
        p = os.path.join(ROOT, "shots", f"{shot}_results.jpg"); im.save(p, quality=92); out["_shot"] = p
    return out


if __name__ == "__main__":
    book, sheet, inputs = sys.argv[1], sys.argv[2], json.loads(sys.argv[3])
    shot = sys.argv[sys.argv.index("--shot") + 1] if "--shot" in sys.argv else None
    print(json.dumps(run(book, sheet, inputs, shot), indent=1, default=str))
