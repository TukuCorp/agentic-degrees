"""6.01 HW2: Heads Up! (light tracker) — completed work file (Python 3).

Reimplemented standalone (ASM-006): the shipped skeleton imported lib601.sf,
lib601.sig, and lib601.ts, none of which is in this repository. The system
functions here use the workspace's own reimplementation at
work/6.01SC/lib/sf.py, and the step response is simulated directly instead of
via lib601.ts.TransducedSignal.

Models built (all return sf.SystemFunction):
    controllerAndSensorModel(k_c)  gain k_c * k_s
    integrator(T)                  T R / (1 - R)
    motorModel(T)                   (T k_m / r_m) R / (1 - (1 - T k_m k_b / r_m) R)
    plantModel(T)                  integrator * motor
    lightTrackerModel(T, k_c)      unity negative feedback around
                                   controllerAndSensorModel * plantModel

Run the analysis (prints system functions, poles, best gain, ranges, and
writes response plots next to this file):
    python hw2Work.py
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from lib import sf  # noqa: E402  (standalone replacement for lib601.sf)

import matplotlib  # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

# Motor / sensor constants (given in the handout).
k_m = 1000.0
k_b = 0.5
k_s = 5.0
r_m = 20.0


def controllerAndSensorModel(k_c):
    """Controller (gain k_c) cascaded with the sensor (gain k_s)."""
    return sf.Gain(k_c * k_s)


def integrator(T):
    """Velocity -> position: Theta_h = (T R / (1 - R)) Omega_h."""
    return sf.SystemFunction(sf.Polynomial([0.0, T]),
                             sf.Polynomial([1.0, -1.0]))


def motorModel(T):
    """Control voltage -> angular velocity, with back-EMF."""
    a = T * k_m / r_m                      # numerator scale
    pole = 1.0 - T * k_m * k_b / r_m       # denominator pole
    return sf.SystemFunction(sf.Polynomial([0.0, a]),
                             sf.Polynomial([1.0, -pole]))


def plantModel(T):
    """Motor cascaded with integrator: Vc -> Theta_h."""
    return integrator(T) * motorModel(T)


def lightTrackerModel(T, k_c):
    """Closed loop: Theta_l -> Theta_h (unity negative feedback)."""
    forward = controllerAndSensorModel(k_c) * plantModel(T)
    return forward.feedback()


def step_response(sf_model, steps=400):
    """Simulate the unit-step response of a system function, from rest."""
    machine = sf_model.stateMachine()
    return machine.transduce([1.0] * steps)


def plot_response(sf_model, steps, filename, title):
    """Plot a unit-step response and save it beside this file."""
    out = step_response(sf_model, steps)
    plt.figure(figsize=(6, 3.5))
    plt.stem(range(steps), out, linefmt="C0-", markerfmt="C0o", basefmt="k-")
    plt.axhline(1.0, color="gray", linestyle="--", linewidth=0.8)
    plt.title(title)
    plt.xlabel("n (sample)")
    plt.ylabel("theta_h[n]")
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)
    plt.tight_layout()
    plt.savefig(path, dpi=110)
    plt.close()
    return path


def characterize(T):
    """Return pole info over a scan of k_c for a fixed timestep T."""
    # closed-loop denominator = 1 - (2 - 25T) R + (1 - 25T + 250 k_c T^2) R^2
    # (derived in solution.md); recompute directly from lightTrackerModel here.
    def mags(k_c):
        poles = lightTrackerModel(T, k_c).poles()
        return sorted(abs(p) for p in poles)

    results = []
    for k_c in [v / 1000.0 for v in range(-10000, 30001, 50)]:
        m = mags(k_c)
        results.append((k_c, max(m), m))
    return results


def best_gain(T, lo=0.0, hi=1.0, steps=40000):
    """Scan k_c in [lo, hi] for the smallest dominant-pole magnitude."""
    best = None
    for i in range(steps + 1):
        k_c = lo + (hi - lo) * i / steps
        m = lightTrackerModel(T, k_c).dominant_pole_magnitude()
        if best is None or m < best[1]:
            best = (k_c, m)
    return best


def main():
    T = 0.005

    print("== System functions (T = %.3f) ==" % T)
    print("controllerAndSensorModel(k_c) =", controllerAndSensorModel(1.0))
    print("  (times k_c; shown for k_c = 1)")
    print("integrator(T)                 =", integrator(T))
    print("motorModel(T)                 =", motorModel(T))
    print("plantModel(T)                 =", plantModel(T))
    print("lightTrackerModel(T, k_c=1)   =", lightTrackerModel(T, 1.0))

    print("\n== Step 10: poles of the light tracker ==")
    for k_c in (0.0, 0.625, 2.0, 20.0, 40.0):
        poles = lightTrackerModel(T, k_c).poles()
        print("k_c = %7.3f  poles = %s" % (k_c, [round(p.real, 4) if abs(p.imag) < 1e-9 else complex(round(p.real, 4), round(p.imag, 4)) for p in poles]))

    print("\n== Step 12: fastest monotonic (real-pole) gain ==")
    # Real poles require k_c <= 0.625; scan that band and also check the
    # complex region so we can state the boundary cleanly.
    best = best_gain(T, 0.0, 0.625)
    print("best k_c (monotonic) = %.5f, dominant pole = %.5f" % best)
    print("poles at best gain   =", [round(p.real, 4) if abs(p.imag) < 1e-9 else complex(round(p.real, 4), round(p.imag, 4)) for p in lightTrackerModel(T, best[0]).poles()])

    print("\n== Step 13: k_c ranges (T = %.3f) ==" % T)
    print("monotonic convergence : 0 < k_c < 0.625 (real poles in (0,1))")
    print("oscillatory convergence: 0.625 < k_c < 20 (complex poles, |p| < 1)")
    print("divergence            : k_c < 0 (monotonic) or k_c > 20 (oscillatory)")

    print("\n== Step 14: effect of T (k_c fixed at 0.625) ==")
    for Tt in (0.001, 0.002, 0.005, 0.01, 0.02):
        poles = lightTrackerModel(Tt, 0.625).poles()
        dom = max(abs(p) for p in poles)
        print("T = %.3f  dominant pole = %.5f" % (Tt, dom))

    print("\n== Plotting ==")
    files = []
    files.append(plot_response(lightTrackerModel(T, 0.625), 80,
                               "resp_best_gain.png", "T=0.005, k_c=0.625 (best, monotonic)"))
    files.append(plot_response(lightTrackerModel(T, 0.3), 80,
                               "resp_monotonic.png", "T=0.005, k_c=0.3 (monotonic)"))
    files.append(plot_response(lightTrackerModel(T, 5.0), 80,
                               "resp_oscillatory.png", "T=0.005, k_c=5 (oscillatory, convergent)"))
    files.append(plot_response(lightTrackerModel(T, 40.0), 80,
                               "resp_divergent.png", "T=0.005, k_c=40 (divergent)"))
    for f in files:
        print("  wrote", f)


if __name__ == "__main__":
    main()
