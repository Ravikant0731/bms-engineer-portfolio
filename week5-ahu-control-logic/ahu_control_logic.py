"""
Week 5: AHU control logic simulation
PI cooling valve, fan-proof interlock, STOPPED/STARTING/RUNNING/FAULT sequence,
3 alarms (FAN_FAIL, HIGH_TEMP, FILTER_DIRTY), CSV interval trend every 10 s scan.
"""
import csv
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

SCAN = 10                      # s, controller scan = trend interval
SIM_END = 6000                 # s
SETPOINT = 24.0                # C
KP, KI = 20.0, 4.0             # KI in %/(C*min)  -> Ti = Kp/Ki = 5 min
PROOF_TIMEOUT = 30             # s, no fan proof -> FAULT
HIGH_ON, HIGH_OFF = 27.0, 26.5 # C, alarm limit and clear (hysteresis)
HIGH_DELAY = 300               # s (5 min)
HIGH_INHIBIT = 600             # s (10 min after start)
FILTER_LIMIT = 250             # Pa

# Fault injection (the "test case")
HW_FAULT = (1800, 3000)        # fan cannot be proven in this window
OPERATOR_RESET_AT = 3600       # operator clears fault after repair


class Room:
    def __init__(self, temp=29.0, outside=32.0):
        self.temp, self.outside = temp, outside

    def step(self, valve_pct, fan_running, dt):
        heat_gain = 0.0006 * (self.outside - self.temp) + 0.0005   # envelope + internal load
        cooling = 0.0001 * valve_pct if fan_running else 0.0       # no airflow = no cooling
        self.temp += (heat_gain - cooling) * dt


room = Room()
state, fan_cmd = "STOPPED", False
integral, state_timer, start_time = 0.0, 0, None
fan_fail = high_temp = filter_dirty = False
high_timer = 0
log, events = [], []


def change(t, new):
    global state
    events.append((t, f"{state} -> {new}"))
    state = new


for t in range(0, SIM_END, SCAN):
    hw_fault = HW_FAULT[0] <= t < HW_FAULT[1]
    fan_proof = fan_cmd and not hw_fault
    reset_cmd = (t == OPERATOR_RESET_AT)

    # ---- sequence ----
    if state == "STOPPED":
        if t >= 10:                                  # auto start request
            fan_cmd, start_time, state_timer = True, t, 0
            change(t, "STARTING")
    elif state == "STARTING":
        state_timer += SCAN
        if fan_proof:
            change(t, "RUNNING")
        elif state_timer >= PROOF_TIMEOUT:
            fan_cmd, fan_fail, integral = False, True, 0.0
            change(t, "FAULT")
    elif state == "RUNNING":
        if not fan_proof:
            fan_cmd, fan_fail, integral = False, True, 0.0
            change(t, "FAULT")
    elif state == "FAULT":
        if reset_cmd and not hw_fault:               # fault must be cleared first
            fan_fail = False
            change(t, "STOPPED")

    # ---- PI loop (only while RUNNING) ----
    if state == "RUNNING":
        err = room.temp - SETPOINT                   # cooling: hot = positive = open valve
        cand = integral + KI * err * (SCAN / 60.0)
        out = KP * err + cand
        if 0.0 < out < 100.0 or (out >= 100.0 and err < 0) or (out <= 0.0 and err > 0):
            integral = max(0.0, min(100.0, cand))    # anti-windup: integrate only if not saturated
        pi_out = max(0.0, min(100.0, KP * err + integral))
    else:
        pi_out, integral = 0.0, 0.0

    # ---- interlock: fan proven AND running, else valve forced 0 ----
    valve = pi_out if (fan_cmd and fan_proof and state == "RUNNING") else 0.0

    room.step(valve, fan_proof, SCAN)

    # ---- alarms ----
    inhibited = fan_cmd and start_time is not None and (t - start_time) < HIGH_INHIBIT
    if room.temp > HIGH_ON and not inhibited:
        high_timer += SCAN
        if high_timer >= HIGH_DELAY and not high_temp:
            high_temp = True
            events.append((t, "HIGH_TEMP alarm raised"))
    else:
        high_timer = 0
    if high_temp and room.temp < HIGH_OFF:
        high_temp = False
        events.append((t, "HIGH_TEMP alarm cleared"))

    filter_dp = 150 + 0.02 * t                       # filter loading up slowly
    if filter_dp > FILTER_LIMIT and not filter_dirty:
        filter_dirty = True
        events.append((t, "FILTER_DIRTY alarm raised"))

    log.append([t, state, round(room.temp, 2), round(valve, 1), int(fan_cmd), int(fan_proof),
                round(filter_dp, 1), int(fan_fail), int(high_temp), int(filter_dirty)])

# ---- trend CSV ----
with open("trend_log.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["time_s", "state", "zone_temp_C", "valve_pct", "fan_cmd", "fan_proof",
                "filter_dp_Pa", "FAN_FAIL", "HIGH_TEMP", "FILTER_DIRTY"])
    w.writerows(log)

# ---- chart ----
T = [r[0] for r in log]
fig, ax = plt.subplots(4, 1, figsize=(10, 9), sharex=True)
ax[0].plot(T, [r[2] for r in log], label="Zone temp")
ax[0].axhline(SETPOINT, color="g", ls="--", label="Setpoint 24 C")
ax[0].axhline(HIGH_ON, color="r", ls=":", label="HIGH_TEMP 27 C")
ax[0].set_ylabel("Temp (C)"); ax[0].legend(loc="upper right", fontsize=8)
ax[1].plot(T, [r[3] for r in log], color="orange"); ax[1].set_ylabel("Valve (%)")
ax[2].step(T, [r[5] for r in log], color="purple", where="post"); ax[2].set_ylabel("Fan proof")
ax[3].step(T, [r[7] for r in log], color="red", label="FAN_FAIL", where="post")
ax[3].step(T, [r[8] + 2 for r in log], color="goldenrod", label="HIGH_TEMP", where="post")
ax[3].step(T, [r[9] + 4 for r in log], color="blue", label="FILTER_DIRTY", where="post")
ax[3].set_yticks([]); ax[3].set_ylabel("Alarms"); ax[3].set_xlabel("Time (s)")
ax[3].legend(loc="upper left", fontsize=8)
fig.suptitle("AHU Control Logic: PI loop, interlock, sequence, alarms")
plt.tight_layout()
plt.savefig("screenshots/ahu-control-logic.png", dpi=120)

# ---- summary ----
print("=== EVENTS ===")
for t, e in events:
    print(f"t={t:5d}s  {e}")
print()
print("Setpoint               :", SETPOINT, "C")
print("Temp at t=1790 (before fault):", [r[2] for r in log if r[0] == 1790][0], "C")
print("Max temp during fault  :", max(r[2] for r in log if HW_FAULT[0] <= r[0] < OPERATOR_RESET_AT + 600), "C")
print("Valve during FAULT     :", set(r[3] for r in log if r[1] == "FAULT"), "%")
print("Final temp             :", log[-1][2], "C")
print("Saved trend_log.csv and screenshots/ahu-control-logic.png")
