# 6.01 HW2: Heads Up! (light tracker) — solution notes

Source: `mit-ocw-curriculum/electrical-engineering/01-intro-to-eecs-1-6.01SC/other/MIT6_01SCS11_hw2.pdf`
(handout) and `hw2.zip → hw2/hw2Work.py` (skeleton). Code: `hw2Work.py`, built on the workspace's
own `lib/sf.py` (system functions, reimplemented without `lib601.sf` per ASM-006).

## What was built

The five model functions the handout asks for, each returning an `sf.SystemFunction`:

| function | system function H = Y/X | meaning |
|----------|--------------------------|---------|
| `controllerAndSensorModel(k_c)` | `k_c · k_s` | error → control voltage |
| `integrator(T)` | `T·R / (1 − R)` | Ωh → Θh (velocity → position) |
| `motorModel(T)` | `(T·k_m/r_m)·R / (1 − (1 − T·k_m·k_b/r_m)·R)` | Vc → Ωh |
| `plantModel(T)` | `integrator · motor` | Vc → Θh |
| `lightTrackerModel(T, k_c)` | `K·Plant / (1 + K·Plant)`, `K = k_c·k_s` | Θl → Θh (closed loop) |

Constants (given): `k_m = 1000`, `k_b = 0.5`, `k_s = 5`, `r_m = 20`; `T = 0.005` s for the
analysis steps.

## Derivation (Steps 1–11)

**Sensor + controller (Steps 1–2).** `vs = ks·e`, `vc = kc·vs`, so `Vc = kc·ks·E` — a pure gain.
The block diagram is a single gain triangle labelled `kc·ks`.

**Integrator (Steps 3–4).** Position is the running sum of velocity:
`θh[n] = θh[n−1] + T·ωh[n−1]`, i.e. `Θh = R·Θh + T·R·Ωh`, giving `Θh/Ωh = T·R/(1 − R)`.

**Motor (Steps 5–6).** From `αh = km·im`, `vb = kb·ωh`, `im = (vc − vb)/rm`, and the discrete
velocity update `ωh[n] = ωh[n−1] + T·αh[n−1]`:

```
ωh[n] = ωh[n−1]·(1 − T·km·kb/rm) + (T·km/rm)·vc[n−1]
```

so `Ωh/Vc = (T·km/rm)·R / (1 − (1 − T·km·kb/rm)·R)`. With numbers, the motor pole is
`1 − 0.005·1000·0.5/20 = 0.875` and the numerator scale is `0.005·1000/20 = 0.25`.

**Plant (Steps 7–8).** Cascade motor → integrator (commutative at rest):
`Plant = 0.00125·R² / ((1 − R)(1 − 0.875·R))`.

**Closed loop (Steps 9–11).** Unity negative feedback around `K·Plant` with `K = kc·ks = 5·kc`
(Black's formula `H = H1/(1 + H1)`):

```
Θh/Θl = 5·kc·0.00125·R² / (1 − 1.875·R + (0.875 + 0.00625·kc)·R²)
```

**Poles (Step 10).** Substitute `z = 1/R` into the denominator and solve
`z² − 1.875·z + (0.875 + 0.00625·kc) = 0`:

```
poles = (1.875 ± √(0.015625 − 0.025·kc)) / 2
```

## Analysis (Steps 12–14)

**Step 12 — best gain (T = 0.005).** Real (non-oscillatory) poles need the discriminant
`0.015625 − 0.025·kc ≥ 0`, i.e. `kc ≤ 0.625`. The dominant (largest) pole is minimized at the
boundary, where the two poles coincide:

- **best `kc = 0.625`**, double pole **`0.9375`** — critically damped, the fastest possible
  convergence without oscillation. (The complex poles for `kc > 0.625` have magnitude
  `√(0.875 + 0.00625·kc) > 0.9375`, so no faster gain exists at all.)

**Step 13 — kc ranges (T = 0.005).**

| range | behaviour | why |
|-------|-----------|-----|
| `0 < kc < 0.625` | monotonically convergent | two real poles in (0, 1) |
| `0.625 < kc < 20` | oscillatory, convergent | complex-conjugate poles, magnitude < 1 |
| `kc < 0` or `kc > 20` | divergent | dominant pole magnitude > 1 (real for `kc<0`, complex for `kc>20`) |

The `kc > 20` boundary is where the product of the poles reaches 1: `0.875 + 0.00625·kc = 1`,
i.e. `kc = 20`.

**Step 14 — effect of T.** For a fixed gain, larger T moves the poles toward the origin (faster
per-sample convergence, because each sample advances the position further), but the *stability*
range shrinks: the divergence boundary is `kc = 0.1/T`, so a gain that is stable at small T
becomes unstable as T grows. Smaller T moves poles toward 1 (slower per-sample convergence) but
widens the stable-gain range. The critical (oscillation-boundary) gain `0.625` is independent of T.
Confirmed numerically by the script: dominant pole at `kc = 0.625` is `0.9875 / 0.9375 / 0.75` for
`T = 0.001 / 0.005 / 0.02`.

## Verified behaviour

`hw2Work.py` prints the system functions, the poles for sample gains, the best gain `0.625`, the
three ranges, the T-dependence, and writes four unit-step response plots (all reproduced from the
derived system functions, not from a canned answer):

- `resp_best_gain.png` — `T=0.005, kc=0.625` (critically damped rise to 1, no overshoot)
- `resp_monotonic.png` — `kc=0.3` (slow, monotonic)
- `resp_oscillatory.png` — `kc=5` (overshoots, rings, then settles)
- `resp_divergent.png` — `kc=40` (grows without bound)

Run it: `python teach-workspace/work/6.01SC/hw2/hw2Work.py`.

## Check Yourself answers

1. **Units of `km, kb, ks, kc`.** `km` = rad·s⁻²·A⁻¹ (acceleration per amp); `kb` = V·s·rad⁻¹
   (back-EMF per angular velocity); `ks` = V·rad⁻¹ (sensor volts per radian of error); `kc` =
   dimensionless (it multiplies volts to give volts).
2. **`optOverLine` on `f(x) = x² − x`.** Minimizing `f` over `[0, 1]` returns best value `−0.25`
   at `x = 0.5`. (For `h(x) = x⁵ − 7x³ + 6x² + 2`, minimum `−0.88` at `x ≈ 1.66`.)
