# test_matter_wave.py
#
# Tests for matter_wave.py (matter-wave / hologram test of the object
# wave claimed in Lee, Digital to Wave Part II, Zenodo 21947108).
#
# Exactly 5 tests:
#   1. De Broglie wavelength reproduces the known electron value
#      (1 eV -> ~1.23 nm) and the paper's 70 kg / 370 km/s value
#      (2.6e-41 m) within 1%.
#   2. Scaling: lambda ~ 1/m at fixed velocity, lambda ~ 1/sqrt(m)
#      at fixed kinetic energy (and at fixed temperature, where the
#      thermal velocity itself goes as 1/sqrt(m)); the relativistic
#      form reduces to the non-relativistic form at low velocity.
#      (Note: the 1/sqrt(m) scaling holds at fixed kinetic energy,
#      not at fixed velocity -- at fixed velocity lambda = h/(m v)
#      scales as 1/m. Both correct scalings are tested here.)
#   3. Phase across one lattice spacing equals 2 pi a0 / lambda.
#   4. Claim ratio lambda_THz/lambda_matter > 1e10 for every
#      macroscopic mass (>= 1 kg) at every paper velocity and every
#      THz frequency (the fail criterion: a passing test 4 means the
#      claim FAILS by >= 10 orders of magnitude).
#   5. The mass at which lambda_matter = lambda_THz (1 THz) is below
#      1e-20 kg, far below any macroscopic mass -- the computed value
#      is stated (5.97e-36 kg at 370 km/s; 3.93e-40 kg thermal).
#
# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (c) 2026 Jean-Francois Brisson (Spark AI NLP)

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import matter_wave as mw


def test_1_de_broglie_reproduces_known_values():
    """Electron at 1 eV -> ~1.23 nm; 70 kg at 370 km/s -> 2.6e-41 m."""
    # Electron at 1 eV kinetic energy (textbook value ~1.23 nm).
    lam_e = mw.de_broglie_wavelength_m(
        mw.ELECTRON_MASS_KG, mw.ELECTRONVOLT_J
    )
    assert math.isclose(lam_e, 1.23e-9, rel_tol=0.01), lam_e
    # Paper's headline case: 70 kg at the CMB velocity 370 km/s.
    # The analysis quotes 2.6e-41 m (2 significant figures); the exact
    # computed value is 2.558e-41 m, which rounds to 2.6e-41 m. The
    # 2% tolerance reflects the 2-significant-figure reference, not
    # an arithmetic difference.
    lam_70 = mw.de_broglie_wavelength_from_velocity_m(
        70.0, mw.CMB_VELOCITY_M_S
    )
    assert math.isclose(lam_70, 2.6e-41, rel_tol=0.02), lam_70
    assert math.isclose(lam_70, 2.558e-41, rel_tol=0.01), lam_70
    # Same value from the non-relativistic form (v/c ~ 1.2e-3).
    lam_70_nr = mw.de_broglie_wavelength_nonrel_m(70.0, mw.CMB_VELOCITY_M_S)
    assert math.isclose(lam_70_nr, 2.6e-41, rel_tol=0.02), lam_70_nr


def test_2_scaling_and_low_velocity_limit():
    """lambda ~ 1/m at fixed velocity; ~ 1/sqrt(m) at fixed energy;
    relativistic form -> non-relativistic form as v/c -> 0."""
    # At fixed velocity, lambda = h/(m v): doubling the mass halves
    # the wavelength.
    lam_1 = mw.de_broglie_wavelength_nonrel_m(1.0, 1000.0)
    lam_2 = mw.de_broglie_wavelength_nonrel_m(2.0, 1000.0)
    assert math.isclose(lam_2, lam_1 / 2.0, rel_tol=1e-12), (lam_1, lam_2)
    # At fixed kinetic energy, lambda = h/sqrt(2 m E): doubling the
    # mass divides the wavelength by sqrt(2).
    e = 1.0e-18
    lam_e1 = mw.de_broglie_wavelength_m(1.0, e)
    lam_e2 = mw.de_broglie_wavelength_m(2.0, e)
    assert math.isclose(lam_e2, lam_e1 / math.sqrt(2.0), rel_tol=1e-12), (
        lam_e1,
        lam_e2,
    )
    # At fixed temperature the thermal velocity goes as 1/sqrt(m), so
    # the thermal wavelength also goes as 1/sqrt(m).
    lam_t1 = mw.de_broglie_wavelength_nonrel_m(
        1.0, mw.thermal_velocity_m_s(1.0)
    )
    lam_t2 = mw.de_broglie_wavelength_nonrel_m(
        2.0, mw.thermal_velocity_m_s(2.0)
    )
    assert math.isclose(lam_t2, lam_t1 / math.sqrt(2.0), rel_tol=1e-12), (
        lam_t1,
        lam_t2,
    )
    # Relativistic form reduces to non-relativistic at low velocity:
    # at 370 km/s (v/c ~ 1.2e-3) the two agree to ~1e-6.
    for m, v in ((70.0, mw.CMB_VELOCITY_M_S), (1.0, 1000.0)):
        lam_r = mw.de_broglie_wavelength_from_velocity_m(m, v)
        lam_n = mw.de_broglie_wavelength_nonrel_m(m, v)
        assert math.isclose(lam_r, lam_n, rel_tol=1e-5), (m, v, lam_r, lam_n)


def test_3_phase_per_lattice_spacing_is_two_pi_a0_over_lambda():
    """Phase across one lattice spacing = 2 pi a0 / lambda."""
    for m, v in (
        (70.0, mw.CMB_VELOCITY_M_S),
        (1.0, mw.CMB_VELOCITY_M_S),
        (mw.PROTON_MASS_KG, mw.thermal_velocity_m_s(mw.PROTON_MASS_KG)),
    ):
        lam = mw.de_broglie_wavelength_from_velocity_m(m, v)
        phase = mw.phase_per_lattice_spacing_rad(m, v)
        assert math.isclose(
            phase, 2.0 * math.pi * mw.LATTICE_PITCH_M / lam, rel_tol=1e-12
        ), (m, v, phase)
    # Spot value from the analysis: 70 kg at 370 km/s -> 8.7e31 rad.
    assert math.isclose(
        mw.phase_per_lattice_spacing_rad(70.0, mw.CMB_VELOCITY_M_S),
        8.7e31,
        rel_tol=0.01,
    )


def test_4_claim_ratio_exceeds_1e10_everywhere():
    """lambda_THz/lambda_matter > 1e10 for every macroscopic mass
    (>= 1 kg) at every paper velocity and every THz frequency.

    This IS the fail criterion. A passing test means the matter
    wavelength of every macroscopic object is more than ten orders
    of magnitude below the THz wavelength in every case, including
    the most generous one (1 kg, thermal, 300 GHz). The verdict is
    FAIL.
    """
    for f in mw.FREQUENCIES_HZ:
        for m in mw.MACROSCOPIC_MASSES_KG:
            for v in (mw.CMB_VELOCITY_M_S, mw.thermal_velocity_m_s(m)):
                ratio = mw.wavelength_ratio_thz(f, m, v)
                assert ratio > 1e10, (f, m, v, ratio)
    # Spot ratios from the analysis:
    # 70 kg at 370 km/s, 1 THz -> ~1.17e37.
    assert math.isclose(
        mw.wavelength_ratio_thz(1e12, 70.0, mw.CMB_VELOCITY_M_S),
        1.17e37,
        rel_tol=0.01,
    )
    # Most generous macroscopic case (1 kg, thermal, 300 GHz) is
    # still ~1.68e20 -- ten orders above the threshold.
    assert mw.worst_case_ratio() > 1e10
    # The module's own verdict must be FAIL.
    assert mw.verdict() == "FAIL"


def test_5_mass_for_thz_wavelength_is_subatomic():
    """The mass whose matter wavelength equals the 1 THz wavelength
    is below 1e-20 kg -- far below any macroscopic mass, and far
    below even the electron mass."""
    lam_t = mw.thz_wavelength_m(1e12)
    # At the paper's 370 km/s: computed value 5.97e-36 kg.
    m_eq = mw.mass_for_wavelength_kg(lam_t, mw.CMB_VELOCITY_M_S)
    assert m_eq < 1e-20, m_eq
    assert math.isclose(m_eq, 5.97e-36, rel_tol=0.01), m_eq
    assert m_eq < mw.ELECTRON_MASS_KG, m_eq
    # At thermal velocity (300 K): even smaller, 3.93e-40 kg.
    m_eq_th = mw.mass_for_wavelength_thermal_kg(lam_t)
    assert m_eq_th < 1e-20, m_eq_th
    assert math.isclose(m_eq_th, 3.93e-40, rel_tol=0.01), m_eq_th
    # Consistency: a mass that light at 370 km/s really has a
    # 300 um de Broglie wavelength. Tolerance 1e-5: mass_for_wavelength
    # inverts the non-relativistic form, while this check uses the
    # relativistic form, and the two differ by ~7.6e-7 at 370 km/s.
    lam_check = mw.de_broglie_wavelength_from_velocity_m(
        m_eq, mw.CMB_VELOCITY_M_S
    )
    assert math.isclose(lam_check, lam_t, rel_tol=1e-5), lam_check
