"""
Week 6: BMS dashboard generator.
Reads the Week 5 trend log and writes a self-contained HTML dashboard
(status tiles, alarm panel, trend charts, event log) for a chosen snapshot time.
Usage: python3 bms_dashboard.py [snapshot_seconds] [output.html]
"""
import csv
import sys

SRC = "trend_log.csv"
SETPOINT, HIGH_LIMIT = 24.0, 27.0
snap = int(sys.argv[1]) if len(sys.argv) > 1 else 2400
out = sys.argv[2] if len(sys.argv) > 2 else "dashboard.html"

rows = []
for r in csv.DictReader(open(SRC)):
    rows.append({"t": int(r["time_s"]), "state": r["state"], "temp": float(r["zone_temp_C"]),
                 "valve": float(r["valve_pct"]), "proof": int(r["fan_proof"]),
                 "dp": float(r["filter_dp_Pa"]), "FAN_FAIL": int(r["FAN_FAIL"]),
                 "HIGH_TEMP": int(r["HIGH_TEMP"]), "FILTER_DIRTY": int(r["FILTER_DIRTY"])})
now = min(rows, key=lambda r: abs(r["t"] - snap))

ALARMS = [("FAN_FAIL", 1, "#b3261e"), ("HIGH_TEMP", 2, "#b8860b"), ("FILTER_DIRTY", 3, "#1a4fa0")]
STATE_COLOR = {"STOPPED": "#555", "STARTING": "#b8860b", "RUNNING": "#2e7d32", "FAULT": "#b3261e"}


def mmss(t):
    return f"{t // 60:02d}:{t % 60:02d}"


def events():
    ev, prev = [], None
    for r in rows:
        if prev:
            if r["state"] != prev["state"]:
                ev.append((r["t"], f"State {prev['state']} -> {r['state']}", "#333"))
            for name, _, col in ALARMS:
                if r[name] != prev[name]:
                    ev.append((r["t"], f"{name} {'RAISED' if r[name] else 'CLEARED'}", col))
        prev = r
    return ev


def chart(key, lo, hi, color, refs):
    w, h, pad = 900, 200, 36
    x = lambda t: pad + (w - 2 * pad) * t / rows[-1]["t"]
    y = lambda v: h - pad / 2 - (h - pad) * (v - lo) / (hi - lo)
    s = [f'<svg viewBox="0 0 {w} {h}" width="100%">']
    for a, b in fault_spans():
        s.append(f'<rect x="{x(a):.0f}" y="8" width="{x(b) - x(a):.0f}" height="{h - 26}" fill="#b3261e" opacity="0.10"/>')
    for v, c, lab in refs:
        s.append(f'<line x1="{pad}" x2="{w - pad}" y1="{y(v):.0f}" y2="{y(v):.0f}" stroke="{c}" stroke-dasharray="5 4"/>'
                 f'<text x="{w - pad}" y="{y(v) - 3:.0f}" text-anchor="end" font-size="11" fill="{c}">{lab}</text>')
    pts = " ".join(f"{x(r['t']):.1f},{y(r[key]):.1f}" for r in rows)
    s.append(f'<polyline fill="none" stroke="{color}" stroke-width="2" points="{pts}"/>')
    s.append(f'<line x1="{x(now["t"]):.0f}" x2="{x(now["t"]):.0f}" y1="8" y2="{h - 18}" stroke="#111" stroke-width="1.5"/>')
    s.append(f'<text x="{pad - 6}" y="{y(hi) + 4:.0f}" text-anchor="end" font-size="11">{hi:g}</text>'
             f'<text x="{pad - 6}" y="{y(lo) + 4:.0f}" text-anchor="end" font-size="11">{lo:g}</text></svg>')
    return "".join(s)


def fault_spans():
    spans, start = [], None
    for r in rows:
        if r["state"] == "FAULT" and start is None:
            start = r["t"]
        if r["state"] != "FAULT" and start is not None:
            spans.append((start, r["t"])); start = None
    return spans


def tile(label, value, sub="", color="#111"):
    return (f'<div class="tile"><div class="lab">{label}</div>'
            f'<div class="val" style="color:{color}">{value}</div><div class="sub">{sub}</div></div>')


active = [(n, p, c) for n, p, c in ALARMS if now[n]]
temp_col = "#b3261e" if now["temp"] > HIGH_LIMIT else "#111"
tiles = "".join([
    tile("Unit state", now["state"], "AHU-1", STATE_COLOR[now["state"]]),
    tile("Zone temperature", f"{now['temp']:.1f} &deg;C", f"setpoint {SETPOINT:g} &deg;C", temp_col),
    tile("Cooling valve", f"{now['valve']:.0f} %", "AO 0-100%"),
    tile("Fan run proof", "PROVEN" if now["proof"] else "NO PROOF", "status input",
         "#2e7d32" if now["proof"] else "#b3261e"),
    tile("Filter dP", f"{now['dp']:.0f} Pa", "alarm above 250 Pa"),
])
alarm_html = "".join(f'<div class="al" style="border-left:6px solid {c}"><b style="color:{c}">{n}</b> priority {p}</div>'
                     for n, p, c in sorted(active, key=lambda a: a[1])) or '<div class="ok">No active alarms</div>'
log_html = "".join(f'<tr><td>{mmss(t)}</td><td style="color:{c}">{m}</td></tr>' for t, m, c in events())

page = f"""<!doctype html><html><head><meta charset="utf-8"><title>AHU-1 Dashboard</title>
<style>body{{font-family:Arial,sans-serif;margin:24px;background:#f4f5f7;color:#111}}
h1{{margin:0 0 4px}}.sub{{color:#666;font-size:13px}}.grid{{display:grid;grid-template-columns:repeat(5,1fr);gap:12px;margin:16px 0}}
.tile,.card{{background:#fff;border-radius:8px;padding:14px;box-shadow:0 1px 3px #0002}}.lab{{font-size:12px;color:#666}}
.val{{font-size:26px;font-weight:bold;margin:4px 0}}.al{{background:#fff4f3;padding:8px 10px;margin:6px 0}}
.ok{{color:#2e7d32;font-weight:bold}}table{{border-collapse:collapse;width:100%}}td{{padding:4px 8px;border-bottom:1px solid #eee;font-size:14px}}
.row{{display:grid;grid-template-columns:2fr 1fr;gap:12px}}h3{{margin:0 0 8px;font-size:15px}}</style></head><body>
<h1>AHU-1 Dashboard</h1><div class="sub">Snapshot at {mmss(now['t'])} (t={now['t']} s) &middot; source: Week 5 trend log, 10 s interval</div>
<div class="grid">{tiles}</div>
<div class="row"><div class="card"><h3>Zone temperature trend (shaded = FAULT, line = snapshot)</h3>
{chart('temp', 22, 31, '#1565c0', [(SETPOINT, '#2e7d32', 'setpoint 24'), (HIGH_LIMIT, '#b3261e', 'HIGH_TEMP 27')])}
<h3>Cooling valve trend (%)</h3>{chart('valve', 0, 100, '#e65100', [])}</div>
<div><div class="card"><h3>Active alarms</h3>{alarm_html}</div><br>
<div class="card"><h3>Event log</h3><table>{log_html}</table></div></div></div></body></html>"""
open(out, "w").write(page)
print(f"Snapshot t={now['t']} s: state={now['state']} temp={now['temp']} valve={now['valve']} "
      f"active={[n for n, _, _ in active] or 'none'}")
print("Wrote", out)
