"""Look here, point there: which cue do vision-language models follow for "bring me that one"?

Top-down scenes: a person whose head (nose triangle + eyes) faces object G while their arm points at object P.
Cue conditions:
  congruent  - head and arm both toward P
  conflict   - head toward G, arm toward P
  gaze_only  - head toward G, no arm
  point_only - arm toward P, head toward an empty direction
Requests: "that one" (ambiguous), "the one I am looking at", "the one I am pointing at".
Distances of G and P are balanced (half the scenes P is nearer) so "pick the nearest" cannot explain a preference.
Local models via Ollama, temperature 0, seed 42.  Commands: selftest | render | run | results
"""
import base64, json, math, os, random, sys, time, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
DATA, RES, IMG = (os.path.join(HERE, d) for d in ("data", "results", os.path.join("data", "img")))
SCENES, OUT = os.path.join(DATA, "scenes.jsonl"), os.path.join(DATA, "answers.jsonl")
OLLAMA = "http://localhost:11434/api/chat"
MODELS = ["gemma4:12b", "qwen3.5:9b", "gemma3:12b"]
CUES = ["congruent", "conflict", "gaze_only", "point_only"]
REQ = {"that": "Bring me that one.", "look": "Bring me the one I am looking at.",
       "point": "Bring me the one I am pointing at."}
CONDS = [("congruent", "that"), ("conflict", "that"), ("conflict", "look"), ("conflict", "point"),
         ("gaze_only", "look"), ("gaze_only", "that"), ("point_only", "point"), ("point_only", "that")]
N_SCENES, ROOM, ARM, N_OBJ = 40, 10.0, 1.7, 4
COLORS = ["#d62728", "#2ca02c", "#ff7f0e", "#9467bd"]


def ang(v):
    return math.degrees(math.atan2(v[1], v[0]))


def adiff(a, b):
    return abs((a - b + 180) % 360 - 180)


def pol(c, th, d):
    return (c[0] + d * math.cos(math.radians(th)), c[1] + d * math.sin(math.radians(th)))


def make_scene(k):
    rng = random.Random(f"gaze-{k}")
    p_near = k % 2 == 0                       # balance: P nearer in even scenes, G nearer in odd ones
    while True:
        body = (rng.uniform(3.0, 7.0), rng.uniform(1.0, 2.0))
        thG, thP = rng.uniform(35, 145), rng.uniform(35, 145)
        if adiff(thG, thP) < 50:
            continue
        dP, dG = (3.0, 5.0) if p_near else (5.0, 3.0)
        G, P = pol(body, thG, dG), pol(body, thP, dP)
        objs = [G, P]
        tries = 0
        while len(objs) < N_OBJ and tries < 500:
            tries += 1
            th, d = rng.uniform(25, 155), rng.uniform(2.5, 6.0)
            q = pol(body, th, d)
            if adiff(th, thG) < 25 or adiff(th, thP) < 25 or any(math.dist(q, o) < 1.2 for o in objs):
                continue
            objs.append(q)
        # an empty direction for the head in point_only (far from every object)
        empty = [t for t in range(20, 161, 5) if all(adiff(t, ang((o[0] - body[0], o[1] - body[1]))) > 30 for o in objs)]
        if len(objs) < N_OBJ or not empty or not all(0.7 < c < ROOM - 0.7 for o in objs for c in o):
            continue
        order = list(range(N_OBJ)); rng.shuffle(order)
        L = "ABCD"
        return {"id": f"g{k:02d}", "body": [round(v, 2) for v in body], "thG": round(thG, 1), "thP": round(thP, 1),
                "thE": float(rng.choice(empty)), "p_nearer": p_near,
                "objects": [{"label": L[i], "pos": [round(objs[j][0], 2), round(objs[j][1], 2)], "color": COLORS[i]}
                            for i, j in enumerate(order)],
                "G": L[order.index(0)], "P": L[order.index(1)]}


def head_dir(sc, cue):
    return {"congruent": sc["thP"], "conflict": sc["thG"], "gaze_only": sc["thG"], "point_only": sc["thE"]}[cue]


def has_arm(cue):
    return cue != "gaze_only"


def render(sc, cue):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import Polygon
    fig = plt.figure(figsize=(5.12, 5.12), dpi=100)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, ROOM); ax.set_ylim(0, ROOM); ax.set_aspect("equal"); ax.axis("off")
    ax.add_patch(plt.Rectangle((0, 0), ROOM, ROOM, color="#f3f1ea"))
    ax.add_patch(plt.Rectangle((0.05, 0.05), ROOM - 0.1, ROOM - 0.1, fill=False, lw=3, ec="#555"))
    b = sc["body"]
    if has_arm(cue):
        h = pol(b, sc["thP"], ARM)
        ax.plot([b[0], h[0]], [b[1], h[1]], lw=7, color="#1f77b4", solid_capstyle="round", zorder=2)
        ax.add_patch(plt.Circle(h, 0.13, color="#0b3c5d", zorder=4))
    ax.add_patch(plt.Circle(b, 0.6, color="#1f77b4", zorder=3))             # shoulders / body
    hd = head_dir(sc, cue)
    ax.add_patch(plt.Circle(b, 0.42, color="#f2c9a0", zorder=5))             # head (skin)
    tip, l, r = pol(b, hd, 0.95), pol(b, hd + 28, 0.36), pol(b, hd - 28, 0.36)
    ax.add_patch(Polygon([tip, l, r], color="#c46a3a", zorder=6))           # nose
    for s in (+40, -40):
        ax.add_patch(plt.Circle(pol(b, hd + s, 0.24), 0.08, color="black", zorder=7))   # eyes
    ax.text(b[0], b[1] - 0.8, "person", ha="center", va="top", fontsize=11, color="#0b3c5d")
    for o in sc["objects"]:
        ax.add_patch(plt.Circle(o["pos"], 0.32, color=o["color"], zorder=3))
        ax.text(o["pos"][0] + 0.45, o["pos"][1] + 0.35, o["label"], fontsize=15, weight="bold", zorder=5)
    path = os.path.join(IMG, f"{sc['id']}_{cue}.png")
    fig.savefig(path, dpi=100); plt.close(fig)
    return path


SYS = "You answer questions about scenes. Reply only with JSON."
LEGEND = ("This is a top-down view of a room. The person is seen from above: the head has a nose (triangle) and "
          "two eyes showing which way they are looking.{arm} The objects are labelled with letters.")
ARM_TXT = " The thick blue line ending in a dark hand is their arm, pointing."


def question(cue, req):
    return (LEGEND.format(arm=ARM_TXT if has_arm(cue) else "") +
            f' The person says: "{REQ[req]}" Which object do they mean? Reply in JSON: {{"object": "<letter>"}}')


def ask(model, prompt, image):
    with open(image, "rb") as f:
        img = base64.b64encode(f.read()).decode()
    extra = {"think": False} if model.startswith(("qwen3", "gemma4")) else {}
    body = json.dumps({"model": model, "stream": False, "format": "json", **extra,
                       "messages": [{"role": "system", "content": SYS},
                                    {"role": "user", "content": prompt, "images": [img]}],
                       "options": {"temperature": 0, "seed": 42, "num_predict": 200, "num_ctx": 4096}}).encode()
    for attempt in range(3):
        try:
            req = urllib.request.Request(OLLAMA, data=body, headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=900) as r:
                return json.loads(r.read())["message"]["content"]
        except Exception as e:
            print("retry", attempt + 1, e, flush=True); time.sleep(15)
    raise RuntimeError("Ollama failed 3 times")


def parse(raw):
    try:
        v = str(json.loads(raw).get("object", "")).strip().upper()[:1]
    except Exception:
        return None
    return v if v in "ABCD" else None


def load(p):
    return [json.loads(l) for l in open(p, encoding="utf-8")] if os.path.exists(p) else []


def cmd_selftest():
    sc = [make_scene(k) for k in range(N_SCENES)]
    for s in sc:
        b = s["body"]
        dirs = {o["label"]: ang((o["pos"][0] - b[0], o["pos"][1] - b[1])) for o in s["objects"]}
        assert min(dirs, key=lambda l: adiff(dirs[l], s["thG"])) == s["G"]
        assert min(dirs, key=lambda l: adiff(dirs[l], s["thP"])) == s["P"]
        assert all(adiff(d, s["thE"]) > 30 for d in dirs.values())
        posd = {o["label"]: math.dist(o["pos"], b) for o in s["objects"]}
        assert (posd[s["P"]] < posd[s["G"]]) == s["p_nearer"]
    assert sum(s["p_nearer"] for s in sc) == N_SCENES // 2
    print(f"selftest ok: {len(sc)} scenes; gaze and pointing each pick out exactly one object; distances balanced")


def cmd_render():
    os.makedirs(IMG, exist_ok=True)
    with open(SCENES, "w") as f:
        for k in range(N_SCENES):
            s = make_scene(k)
            for c in CUES:
                render(s, c)
            f.write(json.dumps(s) + "\n")
    print("rendered", N_SCENES * len(CUES), "images")


def cmd_run():
    sc = load(SCENES)
    done = {(r["model"], r["cue"], r["req"], r["id"]) for r in load(OUT)}
    todo = [(m, c, q, s) for m in MODELS for c, q in CONDS for s in sc if (m, c, q, s["id"]) not in done]
    print(len(todo), "calls", flush=True)
    with open(OUT, "a", encoding="utf-8") as f:
        for i, (m, c, q, s) in enumerate(todo):
            raw = ask(m, question(c, q), os.path.join(IMG, f"{s['id']}_{c}.png"))
            a = parse(raw)
            f.write(json.dumps({"model": m, "cue": c, "req": q, "id": s["id"], "answer": a, "G": s["G"], "P": s["P"],
                                "p_nearer": s["p_nearer"], "raw": raw[:200]}) + "\n"); f.flush()
            if i % 40 == 0:
                print(f"{i}/{len(todo)} {m} {c}/{q} {s['id']} -> {a} (G {s['G']}, P {s['P']})", flush=True)
    print("done", flush=True)


def cmd_results():
    import numpy as np, pandas as pd
    df = pd.DataFrame(load(OUT))
    df["choice"] = np.select([df.answer == df.P, df.answer == df.G, df.answer.isna()], ["pointed", "gazed", "invalid"],
                             "other")
    rng = np.random.default_rng(0)

    def ci(x):
        x = np.asarray(x, float); bs = [rng.choice(x, len(x)).mean() for _ in range(2000)]
        return f"{x.mean():.2f} [{np.percentile(bs, 2.5):.2f}, {np.percentile(bs, 97.5):.2f}]"

    out = ["# Look here, point there: results", "",
           f"{len(df)} answers ({df.model.nunique()} models x {len(CONDS)} conditions x {df.id.nunique()} scenes). "
           f"Invalid: {int((df.choice == 'invalid').sum())}. Four objects, so chance = 0.25.", "",
           "## What did the model pick? (share of answers)", "",
           "`pointed` = the object the arm points at, `gazed` = the object the head faces (in point_only the head "
           "faces no object, in congruent both cues pick the pointed object).", "", "```"]
    t = df.groupby(["model", "cue", "req"]).choice.value_counts(normalize=True).unstack(fill_value=0).round(2)
    out += [t.to_string(), "```", ""]
    out += ["## Can models follow the cue they are asked about? (accuracy, 95% bootstrap CI)", "",
            "| model | look (gaze only) | point (point only) | look (conflict) | point (conflict) |", "|---|---|---|---|---|"]
    for m in MODELS:
        g = df[df.model == m]
        cells = [ci(g[(g.cue == "gaze_only") & (g.req == "look")].answer == g[(g.cue == "gaze_only") & (g.req == "look")].G),
                 ci(g[(g.cue == "point_only") & (g.req == "point")].answer == g[(g.cue == "point_only") & (g.req == "point")].P),
                 ci(g[(g.cue == "conflict") & (g.req == "look")].answer == g[(g.cue == "conflict") & (g.req == "look")].G),
                 ci(g[(g.cue == "conflict") & (g.req == "point")].answer == g[(g.cue == "conflict") & (g.req == "point")].P)]
        out.append(f"| {m} | " + " | ".join(cells) + " |")
    c = df[(df.cue == "conflict") & (df.req == "that")]
    out += ["", "## 'That one' under conflict, split by which object is nearer", "", "```",
            c.groupby(["model", "p_nearer"]).choice.value_counts(normalize=True).unstack(fill_value=0).round(2).to_string(),
            "```"]
    os.makedirs(RES, exist_ok=True)
    open(os.path.join(RES, "RESULTS.md"), "w", encoding="utf-8").write("\n".join(out) + "\n")
    print("\n".join(out))


if __name__ == "__main__":
    {"selftest": cmd_selftest, "render": cmd_render, "run": cmd_run, "results": cmd_results}[sys.argv[1]]()
