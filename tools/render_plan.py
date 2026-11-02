"""Render one post video from a plan JSON.

Usage: python3 tools/render_plan.py plans/2026-11-08_example.json
Plan format:
{
  "id": "2026-11-08_three_numbers",          # output: posts/<id>.mp4
  "music": "upbeat" | "chill" | "tense" | "playful",
  "scenes": [                                 # same scene kinds as tools/compose.py
    {"kind": "card",  "title": "...", "sub": "...", "dur": 3.0},
    {"kind": "shot",  "img": "shots/x.jpg", "crop": [x0,y0,x1,y1], "title": "...", "caption": "...", "dur": 4.0},
    {"kind": "stats", "title": "...", "rows": [["Label","$1","good|bad|amber|ink"]], "caption": "...", "dur": 4.2},
    {"kind": "end",   "title": "...", "cta": "...", "sub": "...", "dur": 3.4}
  ]
}
Paths are relative to the repo root. Run from the repo root.
"""
import json, os, subprocess, sys, shutil
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from compose import KIND
from music import track, SR
from scipy.io import wavfile

ENC = ["-c:v", "libx264", "-preset", "medium", "-crf", "19", "-pix_fmt", "yuv420p", "-r", "30", "-profile:v", "high"]


def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode:
        sys.exit("ffmpeg failed: " + " ".join(cmd) + "\n" + r.stderr[-2000:])


def render(plan_path):
    plan = json.load(open(plan_path))
    vid = plan["id"]
    work = os.path.join("build", vid)
    shutil.rmtree(work, ignore_errors=True); os.makedirs(work); os.makedirs("posts", exist_ok=True)
    scenes = plan["scenes"]
    parts = []
    for i, sc in enumerate(scenes):
        if sc.get("crop"): sc["crop"] = tuple(sc["crop"])
        if sc["kind"] == "stats": sc["rows"] = [tuple(r) for r in sc["rows"]]
        png = os.path.join(work, f"{i:02d}.png")
        KIND[sc["kind"]](sc).save(png)
        D = float(sc["dur"])
        vf = (f"loop=-1:1,trim=duration={D},setpts=PTS-STARTPTS,"
              f"scale=w='trunc(1080*(1+0.035*t/{D})/2)*2':h=-2:eval=frame:flags=bicubic,crop=1080:1920,format=yuv420p")
        if i == 0: vf += ",fade=t=in:st=0:d=0.3"
        if i == len(scenes) - 1: vf += f",fade=t=out:st={D - 0.45}:d=0.45"
        tmp, fin = os.path.join(work, f"{i:02d}.tmp.mp4"), os.path.join(work, f"{i:02d}.mp4")
        run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", "30", "-i", png, "-vf", vf] + ENC + [tmp])
        os.replace(tmp, fin); parts.append(fin)
    lst = os.path.join(work, "list.txt")
    open(lst, "w").write("".join(f"file '{os.path.basename(p)}'\n" for p in parts))
    vonly = os.path.join(work, "v.mp4")
    run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", vonly])
    total = sum(float(s["dur"]) for s in scenes)
    wav = os.path.join(work, "music.wav")
    wavfile.write(wav, SR, track(plan.get("music", "upbeat"), total))
    tmp = os.path.join("posts", vid + ".tmp.mp4")
    run(["ffmpeg", "-y", "-loglevel", "error", "-i", vonly, "-i", wav, "-map", "0:v", "-map", "1:a", "-c:v", "copy",
         "-af", "loudnorm=I=-14:TP=-1.5:LRA=11", "-c:a", "aac", "-b:a", "192k", "-ar", "44100", "-shortest",
         "-movflags", "+faststart", tmp])
    out = os.path.join("posts", vid + ".mp4")
    os.replace(tmp, out)
    # cover frame for checking
    first = os.path.join(work, "00.png")
    print(json.dumps({"video": out, "seconds": round(total, 2), "first_frame": first}))


if __name__ == "__main__":
    for p in sys.argv[1:]:
        render(p)
