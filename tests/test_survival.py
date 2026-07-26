"""Unit tests for the Turnbull NPMLE implementation in src/survival.py.

Each case has a known analytic answer, so a wrong implementation fails
loudly rather than producing a plausible-looking curve.
"""
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))), "src"))

from survival import turnbull  # noqa: E402


def mass_at(support, left, right):
    return sum(p for q, r, p in support
               if abs(q - left) < 1e-9 and abs(r - right) < 1e-9)


class TurnbullTests(unittest.TestCase):

    def test_mass_sums_to_one(self):
        iv = [(0.0, 10.0), (5.0, 20.0), (10.0, 30.0), (0.0, 5.0)]
        s = turnbull(iv)
        self.assertAlmostEqual(sum(p for _, _, p in s), 1.0, places=4)

    def test_disjoint_intervals_split_evenly(self):
        """Two subjects in non-overlapping intervals: each support interval
        must carry exactly half the mass."""
        s = turnbull([(0.0, 1.0), (1.0, 2.0)])
        self.assertEqual(len(s), 2)
        for _, _, p in s:
            self.assertAlmostEqual(p, 0.5, places=4)

    def test_identical_intervals_single_support(self):
        s = turnbull([(0.0, 5.0)] * 7)
        self.assertEqual(len(s), 1)
        self.assertAlmostEqual(s[0][2], 1.0, places=4)

    def test_nested_interval_mass_goes_to_inner(self):
        """A wide interval containing a narrow one: the NPMLE puts all mass on
        the narrow (identifiable) support region."""
        s = turnbull([(0.0, 10.0), (4.0, 5.0)])
        inner = mass_at(s, 4.0, 5.0)
        self.assertAlmostEqual(inner, 1.0, places=3)

    def test_right_censoring_holds_mass_beyond_last_event(self):
        """One event in (0,1], one subject censored at 5: survival after the
        event must not fall to zero."""
        s = turnbull([(0.0, 1.0), (5.0, None)])
        early = mass_at(s, 0.0, 1.0)
        self.assertLess(early, 1.0)
        self.assertGreater(early, 0.0)

    def test_all_censored_gives_no_identified_deaths(self):
        s = turnbull([(1.0, None), (2.0, None)])
        finite = sum(p for _, r, p in s if r != float("inf"))
        self.assertAlmostEqual(finite, 0.0, places=4)

    def test_survival_is_monotone_nonincreasing(self):
        iv = [(0.0, 3.0), (1.0, 4.0), (2.0, 9.0), (0.0, 1.0), (6.0, None)]
        s = turnbull(iv)
        cum = 0.0
        prev = 1.0
        for _, _, p in s:
            cum += p
            surv = 1 - cum
            self.assertLessEqual(surv, prev + 1e-9)
            prev = surv

    def test_exact_times_reduce_to_empirical_cdf(self):
        """Degenerate intervals (t, t+eps] behave like exact observations:
        four distinct times => four equal masses of 1/4."""
        eps = 1e-6
        iv = [(float(t), float(t) + eps) for t in (1, 2, 3, 4)]
        s = turnbull(iv)
        self.assertEqual(len(s), 4)
        for _, _, p in s:
            self.assertAlmostEqual(p, 0.25, places=3)


if __name__ == "__main__":
    unittest.main(verbosity=2)
