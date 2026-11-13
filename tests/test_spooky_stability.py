# test_spooky_stability.py
#
# Tests for spooky_stability.py (Omega-Genesis spooky correlation
# applied to the matter-wave test of Lee, Digital to Wave Part II,
# Zenodo 21947108).
#
# Exactly 5 tests:
#   1. Spooky correlation is in [0, 1] and > 0.99 for sigma = 0.01.
#   2. Spooky decreases as noise grows: spooky at sigma = 0.5 is
#      strictly less than spooky at sigma = 0.01 (same seed).
#   3. Verdict stable in all copies (5/5 FAIL) at sigma = 0.01 and
#      at sigma = 0.05.
#   4. Spooky is reproducible with a fixed seed: same seed gives
#      an identical value; a different seed gives a value that
#      differs by < 0.01.
#   5. The noisy state vectors are distinct (not identical to each
#      other) yet highly correlated: min pairwise |dot| > 0.99 at
#      sigma = 0.01.
#
# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (c) 2026 Jean-Francois Brisson (Spark AI NLP)

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np

import matter_wave as mw
import spooky_stability as ss


def test_1_spooky_in_unit_interval_and_above_0_99():
    """Spooky correlation is in [0, 1] and > 0.99 at sigma = 0.01.

    Measured: 0.99999995. The log-gap vector is almost unchanged
    by 1% input noise, because the gap ratio is a smooth,
    near-linear function of velocity and mass.
    """
    spooky = ss.spooky_correlation()
    assert 0.0 <= spooky <= 1.0, spooky
    assert spooky > 0.99, spooky
    # Spot value: 0.99999995 to the stated precision.
    assert math.isclose(spooky, 0.99999995, rel_tol=1e-6), spooky
    # The base state itself is a 10-vector of log-gaps spanning
    # ~4.7 to ~38.2 orders, all positive.
    base = ss.base_state_vector()
    assert base.shape == (10,), base.shape
    assert np.all(base > 0.0), base
    assert math.isclose(float(base[5]), 19.7027, rel_tol=1e-3), base
    # The 1 kg thermal case at 1 THz is the macroscopic worst
    # case in the state: 10**19.70 = 5.04e19.
    assert math.isclose(10.0 ** float(base[5]), 5.04e19, rel_tol=0.01)


def test_2_spooky_decreases_as_noise_grows():
    """Spooky at sigma = 0.5 is strictly less than at sigma = 0.01.

    Same seed for both, so the underlying standard normals are
    identical and the sigma = 0.5 perturbation is exactly 50x
    the sigma = 0.01 perturbation component-wise: the state
    deviates further, so the correlation must drop.
    """
    spooky_small = ss.spooky_correlation(noise_sigma=0.01, seed=42)
    spooky_large = ss.spooky_correlation(noise_sigma=0.50, seed=42)
    assert spooky_large < spooky_small, (spooky_large, spooky_small)
    # Spot values: 0.99999995 at sigma = 0.01, 0.99964289 at
    # sigma = 0.50. Even at 50% input noise the correlation stays
    # above 0.999 -- the gap vector is dominated by its spread
    # (~4.7 to ~38.2 orders), not by the noise.
    assert math.isclose(spooky_small, 0.99999995, rel_tol=1e-6)
    assert math.isclose(spooky_large, 0.99964289, rel_tol=1e-6)
    # Monotone in between: sigma = 0.05 sits strictly between.
    spooky_mid = ss.spooky_correlation(noise_sigma=0.05, seed=42)
    assert spooky_large < spooky_mid < spooky_small, (
        spooky_large,
        spooky_mid,
        spooky_small,
    )


def test_3_verdict_stable_in_all_copies():
    """Verdict stable 5/5 FAIL at sigma = 0.01 and at sigma = 0.05.

    The worst-case ratio is the minimum over the macroscopic
    noisy cases (1 kg, 70 kg, 1000 kg at both velocities, 1 THz).
    At sigma = 0.01 the worst ratios span 4.92e19-5.13e19; at
    sigma = 0.05 they span 4.45e19-5.47e19 -- all >= 1e10 by
    nine orders.
    """
    for sigma in (0.01, 0.05):
        stab = ss.verdict_stability(noise_sigma=sigma)
        assert stab["fraction_fail"] == 1.0, (sigma, stab)
        assert stab["n_fail"] == 5, (sigma, stab)
        assert stab["n_copies"] == 5, (sigma, stab)
        assert len(stab["worst_case_ratios"]) == 5
        for ratio in stab["worst_case_ratios"]:
            assert ratio >= 1e10, (sigma, ratio)
        # The worst ratios stay within ~10% of the unperturbed
        # 1 kg thermal value (5.04e19) at either sigma.
        assert min(stab["worst_case_ratios"]) > 4.0e19, stab
        assert max(stab["worst_case_ratios"]) < 6.0e19, stab
    # The module's own verdict is FAIL, and the noisy verdicts
    # agree with it.
    assert mw.verdict() == "FAIL"


def test_4_spooky_reproducible_with_fixed_seed():
    """Same seed gives an identical value; a different seed
    differs by < 0.01."""
    spooky_a = ss.spooky_correlation(seed=42)
    spooky_b = ss.spooky_correlation(seed=42)
    assert spooky_a == spooky_b, (spooky_a, spooky_b)
    # A different seed draws different noise, but at sigma = 0.01
    # the correlation is pinned near 1, so any seed lands within
    # 0.01 of any other.
    for other_seed in (7, 123, 20261113):
        spooky_other = ss.spooky_correlation(seed=other_seed)
        assert abs(spooky_other - spooky_a) < 0.01, (
            other_seed,
            spooky_other,
            spooky_a,
        )
    # The noisy state vectors are reproducible too: same seed,
    # identical vectors.
    vecs_a = ss.noisy_state_vectors(seed=42)
    vecs_b = ss.noisy_state_vectors(seed=42)
    assert len(vecs_a) == len(vecs_b) == 5
    for va, vb in zip(vecs_a, vecs_b):
        assert np.array_equal(va, vb)


def test_5_noisy_vectors_distinct_yet_highly_correlated():
    """The noisy state vectors are distinct but highly
    correlated: min pairwise |dot| > 0.99 at sigma = 0.01.

    Distinctness: the noise is real -- the copies are not
    copies of each other. Correlation: the noise barely moves
    the state, so every pair is almost perfectly aligned.
    """
    vectors = ss.noisy_state_vectors(noise_sigma=0.01, seed=42)
    assert len(vectors) == 5
    # Each vector is unit-normalized.
    for v in vectors:
        assert math.isclose(float(np.linalg.norm(v)), 1.0, rel_tol=1e-12)
    # Distinct: not all identical. The first two copies differ,
    # and at least one component moves by more than 1e-6 across
    # copies (the noise is real, not rounded away).
    assert not np.array_equal(vectors[0], vectors[1])
    stacked = np.array(vectors)
    # At least one component moves by more than 1e-6 across
    # copies: the noise is real, not rounded away.
    assert float((stacked.max(axis=0) - stacked.min(axis=0)).max()) > 1e-6
    # Highly correlated: every pairwise |dot| > 0.99.
    assert ss.min_pairwise_abs_dot(noise_sigma=0.01) > 0.99
    # Spot value: min pairwise |dot| is 0.99999992.
    assert math.isclose(
        ss.min_pairwise_abs_dot(noise_sigma=0.01),
        0.99999992,
        rel_tol=1e-6,
    )
    # And the mean is the spooky correlation itself.
    assert math.isclose(
        ss.spooky_correlation(noise_sigma=0.01),
        0.99999995,
        rel_tol=1e-6,
    )
