# spooky_stability.py
#
# Spooky stability layer for the matter-wave / hologram test of
# Lee, "Digital to Wave: LGD In Situ Wave Memory-Human Wave
# Integrated Interface-Metaverse Hologram-Wave Affective AI"
# (Zenodo 21947108, DOI 10.5281/zenodo.21947108, 2026-08-15).
#
# The uncalibrated test (matter_wave.py) falsified the paper's §3
# claim: a macroscopic object's de Broglie wavelength is ~10^37
# times shorter than the THz wavelength, and even the most generous
# macroscopic case (1 kg, thermal, 3 THz) is short by 1.68 x 10^19.
# The analog calibration layer (analog_calibration.py) showed the
# FAIL is robust to any bounded +/-5% velocity calibration (it buys
# exactly 0.0223 orders). This layer asks a third robustness
# question, measured the Omega-Genesis way: is the FAIL stable
# under random input noise?
#
# The "spooky" concept comes from Omega-Genesis (Untitled7, the
# only measured run in the Colab notebooks: 10M iterations, seed
# 42). There, spooky correlation = mean pairwise |dot| over 5
# noisy copies of the same 32-dim state, and it measured 0.9005
# (CCI 0.8862, empathy 0.5503, self-knowing 0.0, zero bubbles).
# Spooky measures self-similarity under small noise, not
# entanglement. Here the "state" is the vector of log10(lambda_THz
# / lambda) across the module's 10 standard cases at 1 THz, and a
# "noisy copy" is that state recomputed after perturbing each
# case's (mass, velocity) by independent relative Gaussian noise.
#
# IMPORTANT: the spooky value here is NOT comparable to the
# Omega-Genesis 0.9005. Same concept (self-similarity under noise),
# different state, different noise. The Omega-Genesis state is a
# 32-dim membrane state under 20% erasure stress; this state is a
# 10-dim vector of log-gaps under relative Gaussian input noise.
# The numbers answer different questions and must not be compared.
#
# Status: SYNTHETIC computation. A classical-physics bound applied
# to the paper's own numbers. No physical claim, no experiment, no
# medical claim. No new physical law is asserted here.
#
# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (c) 2026 Jean-Francois Brisson (Spark AI NLP)

"""Spooky stability of the matter-wave test, Omega-Genesis style.

The state is the vector of log10(lambda_THz / lambda) across the
module's 10 standard cases (electron, proton, 1 kg, 70 kg,
1000 kg at the CMB velocity and at thermal velocity, 300 K), all
at 1 THz. A noisy copy perturbs each case's (mass, velocity) by
independent relative Gaussian noise with standard deviation
noise_sigma (default 0.01). The spooky correlation is the mean
pairwise |dot| (cosine similarity) between n_copies noisy state
vectors, each normalized to unit length -- the Omega-Genesis
definition, adapted to this scalar-output test.

The result: the log-gap vector is extremely stable under input
noise (spooky > 0.999 at sigma = 0.01), because the gap ratio is
a smooth, near-linear function of velocity and mass. The verdict
is stable too: 5/5 copies still FAIL at sigma = 0.01 and at
sigma = 0.05. The FAIL is robust to input noise, measured the
Omega-Genesis way.
"""

import math

import numpy as np

import matter_wave as mw

# ---------------------------------------------------------------------------
# Defaults (Omega-Genesis: 5 noisy copies, seed 42)
# ---------------------------------------------------------------------------

DEFAULT_NOISE_SIGMA = 0.01
DEFAULT_N_COPIES = 5
DEFAULT_SEED = 42

# THz frequency for the state vector: 1 THz (the module's table
# frequency). All 10 standard cases are evaluated at 1 THz.
STATE_FREQUENCY_HZ = 1e12

# The verdict threshold, same as matter_wave.FAIL_RATIO_THRESHOLD.
FAIL_RATIO_THRESHOLD = mw.FAIL_RATIO_THRESHOLD


# ---------------------------------------------------------------------------
# The state: log10(lambda_THz / lambda) across the 10 standard cases
# ---------------------------------------------------------------------------

def standard_cases():
    """The module's 10 standard cases, as (mass_name, mass_kg,
    velocity_label, velocity_m_s).

    The same masses and velocities the module already reports
    (electron, proton, 1 kg, 70 kg, 1000 kg at the CMB velocity
    and at thermal velocity, 300 K), all evaluated at 1 THz.
    """
    cases = []
    for name in ("electron", "proton", "1 kg", "70 kg", "1000 kg"):
        m = mw.MASSES_KG[name]
        cases.append((name, m, "CMB 370 km/s", mw.CMB_VELOCITY_M_S))
        cases.append(
            (name, m, "thermal 300 K", mw.thermal_velocity_m_s(m))
        )
    return cases


def _log_gap(mass_kg, velocity_m_s, frequency_hz=STATE_FREQUENCY_HZ):
    """log10(lambda_THz / lambda) for one (mass, velocity)."""
    return math.log10(
        mw.wavelength_ratio_thz(frequency_hz, mass_kg, velocity_m_s)
    )


def base_state_vector():
    """The unperturbed state: log10(lambda_THz / lambda) at 1 THz
    for the 10 standard cases, as a numpy array of shape (10,)."""
    return np.array(
        [
            _log_gap(m, v)
            for _, m, _, v in standard_cases()
        ],
        dtype=float,
    )


def _positive_factor(rng, sigma):
    """One relative-Gaussian factor 1 + eps, eps ~ N(0, sigma^2),
    redrawn until positive.

    A mass or velocity factor must stay positive for the
    de Broglie computation (matter_wave raises on non-positive
    mass or on |v| >= c). At sigma <= 0.05 a non-positive draw is
    effectively impossible (P < 1e-100); at sigma = 0.5 it is a
    ~2% tail event per draw, and redrawing keeps the perturbation
    Gaussian conditional on staying in the valid domain.
    """
    while True:
        factor = 1.0 + float(rng.normal(0.0, sigma))
        if factor > 0.0:
            return factor


def _noisy_log_gap_vectors(noise_sigma=DEFAULT_NOISE_SIGMA,
                           n_copies=DEFAULT_N_COPIES,
                           seed=DEFAULT_SEED):
    """Raw (unnormalized) noisy log-gap vectors, one per copy.

    For each copy, every case's (mass, velocity) is perturbed by
    independent relative Gaussian noise with standard deviation
    noise_sigma, and the log-gap vector is recomputed at 1 THz.
    The RNG is seeded identically on every call, so the same
    (noise_sigma, n_copies, seed) always returns the same vectors,
    and the same seed draws the same underlying standard normals
    at any sigma (scaled by sigma). Returns a list of n_copies
    numpy arrays, each of shape (10,).
    """
    rng = np.random.default_rng(seed)
    vectors = []
    for _ in range(n_copies):
        perturbed = []
        for _, m, _, v in standard_cases():
            m_noisy = m * _positive_factor(rng, noise_sigma)
            v_noisy = v * _positive_factor(rng, noise_sigma)
            perturbed.append((m_noisy, v_noisy))
        vectors.append(
            np.array(
                [_log_gap(m, v) for m, v in perturbed],
                dtype=float,
            )
        )
    return vectors


def noisy_state_vectors(noise_sigma=DEFAULT_NOISE_SIGMA,
                        n_copies=DEFAULT_N_COPIES,
                        seed=DEFAULT_SEED):
    """Noisy state vectors, each normalized to unit length.

    Same draws as _noisy_log_gap_vectors; each raw log-gap vector
    is divided by its L2 norm. Returns a list of n_copies numpy
    arrays, each of shape (10,) with unit norm.
    """
    vectors = []
    for raw in _noisy_log_gap_vectors(noise_sigma, n_copies, seed):
        norm = float(np.linalg.norm(raw))
        vectors.append(raw / norm)
    return vectors


# ---------------------------------------------------------------------------
# Spooky correlation (Omega-Genesis definition)
# ---------------------------------------------------------------------------

def spooky_correlation(noise_sigma=DEFAULT_NOISE_SIGMA,
                       n_copies=DEFAULT_N_COPIES,
                       seed=DEFAULT_SEED):
    """Mean pairwise |dot| over n_copies noisy state vectors.

    The Omega-Genesis spooky definition: mean pairwise |dot|
    (cosine similarity, since the vectors are unit-normalized)
    between the noisy copies. Returns a float in [0, 1]. A value
    near 1 means the state is almost unchanged by the noise --
    the log-gap vector is self-similar under small input noise.
    """
    vectors = noisy_state_vectors(noise_sigma, n_copies, seed)
    dots = []
    for i in range(len(vectors)):
        for j in range(i + 1, len(vectors)):
            dots.append(abs(float(np.dot(vectors[i], vectors[j]))))
    return float(sum(dots) / len(dots))


def min_pairwise_abs_dot(noise_sigma=DEFAULT_NOISE_SIGMA,
                         n_copies=DEFAULT_N_COPIES,
                         seed=DEFAULT_SEED):
    """Smallest pairwise |dot| among the noisy state vectors.

    The weakest link of the spooky correlation: if even the least
    similar pair is still > 0.99, every pair is highly correlated.
    """
    vectors = noisy_state_vectors(noise_sigma, n_copies, seed)
    worst = None
    for i in range(len(vectors)):
        for j in range(i + 1, len(vectors)):
            d = abs(float(np.dot(vectors[i], vectors[j])))
            if worst is None or d < worst:
                worst = d
    return float(worst)


# ---------------------------------------------------------------------------
# Verdict stability under input noise
# ---------------------------------------------------------------------------

def verdict_stability(noise_sigma=DEFAULT_NOISE_SIGMA,
                      n_copies=DEFAULT_N_COPIES,
                      seed=DEFAULT_SEED):
    """Fraction of noisy copies whose verdict is still FAIL.

    For each noisy copy, the worst-case ratio is the minimum
    lambda_THz / lambda over the MACROSCOPIC noisy cases
    (1 kg, 70 kg, 1000 kg at both velocities, at 1 THz) --
    mirroring matter_wave.verdict(), whose FAIL criterion applies
    to macroscopic masses only. The electron and proton are in
    the spooky state vector but are not the claim's subject, so
    they are excluded from the verdict. FAIL if the worst-case
    ratio is >= 1e10.

    Returns a dict with the fraction of copies still FAIL, the
    list of worst-case ratios (one per copy), and n_copies.
    """
    macroscopic_idx = [
        i
        for i, (name, _, _, _) in enumerate(standard_cases())
        if name in ("1 kg", "70 kg", "1000 kg")
    ]
    worst_ratios = []
    for raw in _noisy_log_gap_vectors(noise_sigma, n_copies, seed):
        worst_log = min(float(raw[i]) for i in macroscopic_idx)
        worst_ratios.append(10.0 ** worst_log)
    n_fail = sum(1 for r in worst_ratios if r >= FAIL_RATIO_THRESHOLD)
    return {
        "fraction_fail": n_fail / len(worst_ratios),
        "n_fail": n_fail,
        "n_copies": len(worst_ratios),
        "worst_case_ratios": worst_ratios,
    }


def max_relative_spread(noise_sigma=DEFAULT_NOISE_SIGMA,
                        n_copies=DEFAULT_N_COPIES,
                        seed=DEFAULT_SEED):
    """Largest relative spread of the (linear) gap ratio across
    copies, over the 10 standard cases.

    For each case, (max - min) / mean of lambda_THz / lambda
    across the n_copies; returns the maximum over cases, as a
    fraction (0.02 = 2%). A small spread means the gap barely
    moves under the noise.
    """
    vectors = _noisy_log_gap_vectors(noise_sigma, n_copies, seed)
    ratios = np.array([[10.0 ** x for x in v] for v in vectors])
    spreads = (ratios.max(axis=0) - ratios.min(axis=0)) / ratios.mean(axis=0)
    return float(spreads.max())


def main():
    """Print the spooky correlation, the verdict stability, and
    the max relative spread of the gap across copies."""
    print("Spooky stability -- Lee, Digital to Wave Part II")
    print("Omega-Genesis spooky: mean pairwise |dot| over 5 noisy")
    print("copies of the log-gap state vector (10 standard cases")
    print("at 1 THz), each (mass, velocity) perturbed by relative")
    print("Gaussian noise, sigma = 0.01 (seed 42).")
    print()
    spooky = spooky_correlation()
    print(f"Spooky correlation (sigma = 0.01): {spooky:.9f}")
    print(f"  min pairwise |dot|: "
          f"{min_pairwise_abs_dot():.9f}")
    print(f"  spooky at sigma = 0.05: "
          f"{spooky_correlation(noise_sigma=0.05):.9f}")
    print(f"  spooky at sigma = 0.50: "
          f"{spooky_correlation(noise_sigma=0.50):.9f}")
    print()
    for sigma in (0.01, 0.05):
        stab = verdict_stability(noise_sigma=sigma)
        print(
            f"Verdict stability (sigma = {sigma}): "
            f"{stab['n_fail']}/{stab['n_copies']} FAIL "
            f"(worst ratios "
            f"{min(stab['worst_case_ratios']):.2e} - "
            f"{max(stab['worst_case_ratios']):.2e})"
        )
    print()
    print(
        f"Max relative spread of the gap across copies "
        f"(sigma = 0.01): {100.0 * max_relative_spread():.2f}%"
    )
    print()
    print(f"VERDICT: {mw.verdict()} -- the FAIL is stable under "
          f"input noise, measured the Omega-Genesis way.")


if __name__ == "__main__":
    main()
