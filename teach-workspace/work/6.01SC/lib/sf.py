"""System-function module, reimplemented without lib601.sf.

An LTI system is represented by its system function H = N(R) / D(R), where N
and D are polynomials in the delay operator R. This module implements the PCAP
system of 6.01 chapter 5: primitives (gain, delay), composition (cascade,
parallel/sum, negative feedback), and the analysis operations — the difference
equation, the poles, and a state machine that runs the response.

Contract (mirrors lib601.sf / the plan PHASE-02 signatures):
    Gain(k)            -> SystemFunction with H = k
    R (Delay)          -> SystemFunction with H = R
    H1 * H2            -> cascade
    H1 + H2            -> parallel (sum)
    H.feedback()       -> unity negative feedback  H / (1 + H)
    H.differenceEquation() -> DifferenceEquation (dCoeffs, cCoeffs)
    H.poles()          -> list of poles (roots of D in z = 1/R)
    H.stateMachine()   -> an SM with .transduce(inputs)

Difference-equation convention (chapter 5, section 5.4.2):
    y[n] = c0 y[n-1] + ... + c{k-1} y[n-k]
         + d0 x[n]   + ... + d_j x[n-j]
so dCoeffs = numerator coefficients (b0, b1, ...) and
   cCoeffs = negated denominator coefficients (-a1, -a2, ...) after a0 = 1.

Uses numpy only for polynomial root-finding in poles(); everything else is
standard library. Run hw2Work.py to see it exercised end to end.
"""

import sys

try:
    import numpy as np
except ImportError:  # pragma: no cover - poles() then raises a clear error
    np = None

from lib.sm import SM


class Polynomial:
    """A polynomial in R with ascending coefficients: coeffs[i] = coeff of R^i."""

    def __init__(self, coeffs):
        self.coeffs = [float(c) for c in coeffs]
        self._trim()

    def _trim(self):
        while len(self.coeffs) > 1 and self.coeffs[-1] == 0:
            self.coeffs.pop()

    def degree(self):
        return len(self.coeffs) - 1

    def __add__(self, other):
        n = max(len(self.coeffs), len(other.coeffs))
        return Polynomial([
            (self.coeffs[i] if i < len(self.coeffs) else 0.0)
            + (other.coeffs[i] if i < len(other.coeffs) else 0.0)
            for i in range(n)
        ])

    def __mul__(self, other):
        out = [0.0] * (len(self.coeffs) + len(other.coeffs) - 1)
        for i, a in enumerate(self.coeffs):
            for j, b in enumerate(other.coeffs):
                out[i + j] += a * b
        return Polynomial(out)

    def __neg__(self):
        return Polynomial([-c for c in self.coeffs])

    def __rmul__(self, scalar):
        # scalar * polynomial
        return Polynomial([scalar * c for c in self.coeffs])

    def __repr__(self):
        return "Polynomial(" + repr(self.coeffs) + ")"


def _as_poly(value):
    if isinstance(value, Polynomial):
        return value
    return Polynomial([value])


class SystemFunction:
    """H = N(R) / D(R). The denominator is normalized so D's constant term is 1."""

    def __init__(self, num, den=None):
        self.num = _as_poly(num)
        self.den = _as_poly(den) if den is not None else Polynomial([1.0])
        self._normalize()

    def _normalize(self):
        if self.den.coeffs[0] == 0:
            raise ValueError("denominator constant term must be non-zero")
        if self.den.coeffs[0] != 1.0:
            scale = self.den.coeffs[0]
            self.den = Polynomial([c / scale for c in self.den.coeffs])
            self.num = Polynomial([c / scale for c in self.num.coeffs])

    def __mul__(self, other):
        # cascade: H = H1 * H2
        return SystemFunction(self.num * other.num, self.den * other.den)

    def __add__(self, other):
        # parallel (sum): H = H1 + H2
        num = self.num * other.den + other.num * self.den
        den = self.den * other.den
        return SystemFunction(num, den)

    def feedback(self):
        # unity negative feedback: H / (1 + H)
        return SystemFunction(self.num, self.den + self.num)

    def differenceEquation(self):
        """Return a DifferenceEquation (dCoeffs, cCoeffs) for this system."""
        return DifferenceEquation(list(self.num.coeffs),
                                  [-c for c in self.den.coeffs[1:]])

    def poles(self):
        """Roots of the denominator polynomial in z = 1/R.

        The denominator is a0 + a1 R + ... + ak R^k (a0 = 1); substituting
        z = 1/R and multiplying by z^k gives a0 z^k + a1 z^{k-1} + ... + ak = 0,
        whose roots are the poles. numpy.roots takes descending coefficients,
        which is exactly self.den.coeffs. A constant denominator has no poles.
        """
        if np is None:
            raise ImportError("poles() needs numpy; activate the workspace venv")
        if self.den.degree() == 0:
            return []
        return [complex(r) for r in np.roots(np.array(self.den.coeffs, dtype=float))]

    def dominant_pole_magnitude(self):
        poles = self.poles()
        return max((abs(p) for p in poles), default=0.0)

    def stateMachine(self):
        return self.differenceEquation().stateMachine()

    def __repr__(self):
        return "SystemFunction(N=" + repr(self.num) + ", D=" + repr(self.den) + ")"


class DifferenceEquation:
    """y[n] = c0 y[n-1] + ... + d0 x[n] + ... as (dCoeffs, cCoeffs)."""

    def __init__(self, d_coeffs, c_coeffs):
        self.dCoeffs = [float(c) for c in d_coeffs]
        self.cCoeffs = [float(c) for c in c_coeffs]

    def stateMachine(self):
        return LTIStateMachine(self.dCoeffs, self.cCoeffs)

    def __repr__(self):
        return "DifferenceEquation(dCoeffs=%r, cCoeffs=%r)" % (
            self.dCoeffs, self.cCoeffs)


class LTIStateMachine(SM):
    """State machine realizing an LTI difference equation (chapter 5 LTISM).

    State = (list of j previous inputs, list of k previous outputs), both
    initialized to zero ("at rest").
    """

    def __init__(self, d_coeffs, c_coeffs):
        self.dCoeffs = [float(c) for c in d_coeffs]
        self.cCoeffs = [float(c) for c in c_coeffs]
        self.j = len(self.dCoeffs) - 1
        self.k = len(self.cCoeffs)

    def start_state(self):
        return ([0.0] * self.j, [0.0] * self.k)

    def get_next_values(self, state, inp):
        inputs, outputs = state
        inputs = [inp] + inputs
        current = _dot(inputs, self.dCoeffs) + _dot(outputs, self.cCoeffs)
        next_inputs = inputs[:-1]
        next_outputs = ([current] + outputs)[:-1]
        return ((next_inputs, next_outputs), current)


def _dot(a, b):
    return sum(x * y for x, y in zip(a, b))


def Gain(k):
    return SystemFunction(Polynomial([k]))


# The unit delay operator R as a system function.
R = SystemFunction(Polynomial([0.0, 1.0]))
