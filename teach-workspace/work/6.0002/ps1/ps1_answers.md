# 6.0002 PS1 — writeup (Problems A.5 and B.2)

Source: `mit-ocw-curriculum/software-engineering/02-computation-data-science-6.0002/other/PS1.zip →
MIT6_0002F16_ProblemSet1.pdf`. Code: `ps1a.py`, `ps1b.py` (completed), `ps1_partition.py`
(provided helper, unchanged).

## Part A.5 — Comparing the cow-transport algorithms

**1. Results from `compare_cow_transport_algorithms` (ps1_cow_data.txt, limit 10).**

| algorithm | trips | wall time |
|-----------|-------|-----------|
| greedy    | 6     | ~0.00 s   |
| brute force | 5   | ~1.4 s    |

The brute-force algorithm runs slower (it enumerates all ~115,975 set partitions of 10 cows and
filters them) but finds the true minimum of 5 trips. Greedy finishes essentially instantly but
returns 6 trips — one worse.

**2. Does the greedy algorithm return the optimal solution? Why / why not?**

No — and this very data proves it. Greedy commits to the two 9-ton cows (`Betsy`, `Henrietta`) in
their own trips first (each needs a whole ship, since nothing ≤ 1 ton remains), then packs
greedily and needs 6 trips total. It cannot reconsider the early decisions. Greedy is optimal only
when the locally-best choice is also globally-best; the cow-transport problem does not have that
property (it is NP-hard in general — bin packing), so greedy is only a fast heuristic here.

**3. Does the brute-force algorithm return the optimal solution? Why / why not?**

Yes. It enumerates *every* way to partition the cows into trips, rejects any partition where a
trip exceeds the limit, and keeps the partition with the fewest trips. Since it inspects the whole
search space, the surviving minimum is exact. The cost is exponential time, which is why it is
only feasible for small inputs (10 cows ≈ 1.4 s here; each additional cow multiplies the work).

## Part B.2 — Golden Eggs (`dp_make_weight`)

**1. Why brute force is difficult with 30 egg weights.**

With unlimited supply of each egg weight, the number of ways to compose a target weight grows
exponentially with the target and the number of distinct weights. Enumerating every multiset that
sums to the target is impractical long before 30 weights — the search tree is far too large.
Dynamic programming avoids it by solving each sub-weight exactly once.

**2. A greedy formulation for the minimum-egg problem.**

- **Objective function:** minimize the number of eggs chosen, `count(eggs)`.
- **Constraints:** the chosen eggs' weights must sum exactly to `target_weight`; each egg weight
  comes from the given set with unlimited supply.
- **Strategy:** repeatedly take the *largest* egg weight that does not exceed the remaining weight
  (a largest-denomination-first greedy, like making change with quarters first).

**3. Is greedy optimal here? Give an example.**

No. Largest-first greedy fails when the denominations are not "canonical" (where each coin divides
the next). Counterexample with weights `(1, 5, 10, 20)` and target `30`: greedy takes `20 + 10 =
30` (2 eggs) — fine. But with weights `(1, 6, 10)` and target `12`: greedy takes `10 + 1 + 1 = 12`
(3 eggs), while the optimum is `6 + 6 = 12` (2 eggs). Greedy overshoots on the first pick and
cannot recover. Dynamic programming, by contrast, is guaranteed optimal because it considers every
last egg choice via the optimal substructure `dp[w] = min(1 + dp[w − e] for e ≤ w)`.
