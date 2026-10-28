import json, re, subprocess, sys, os
HERE = os.path.dirname(os.path.abspath(__file__))
for ep in sys.argv[1:]:
    d = os.path.join(HERE, ep)
    html = open(os.path.join(d, "index.html")).read()
    hosts = re.findall(r'id="s\d+" data-composition-id="s\d+" data-composition-src="[^"]+" data-start="([\d.]+)" data-duration="([\d.]+)"', html)
    times = ",".join(f"{float(s) + float(du) * .62:.2f}" for s, du in hosts)
    r = subprocess.run(["npx", "hyperframes", "check", "--json"], cwd=d, capture_output=True, text=True, timeout=600)
    t = r.stdout; j = json.loads(t[t.find("{"):])
    print("==", ep, "ok:", j["ok"])
    for sec in ("lint", "runtime", "layout", "motion", "contrast", "craft", "audio"):
        v = j[sec]
        if v.get("errorCount") or v.get("warningCount"):
            print("  ", sec, "err", v["errorCount"], "warn", v["warningCount"])
            for f in v["findings"][:5]: print("      ", f["code"], "|", f.get("text", f.get("message", ""))[:100], "|", f.get("selector", ""), "| t=", round(f.get("time", 0), 2))
    if os.environ.get("NOSNAP"): continue
    s = subprocess.run(["npx", "hyperframes", "snapshot", "--at", times], cwd=d, capture_output=True, text=True, timeout=600)
    for line in s.stdout.splitlines():
        if "contact-sheet" in line: print("  sheet:", line.strip().split()[0])
