# test_analog_calibration.py
#
# Tests for analog_calibration.py (Observer + Calibrator layer on the
# matter-wave test of Lee, Digital to Wave Part II, Zenodo 21947108).
#
# Exactly 5 tests:
#   1. The Observer measures the same gap as the module's direct
#      computation: lambda_THz/lambda matches within 1e-9 relative.
#   2. The Observer is read-only: two identical calls give identical
#      results, and observing does not change any module value.
#   3. The Calibrator clips: set_delta(0.5) -> 0.05,
#      set_delta(-2.0) -> -0.05, set_delta(0.03) -> 0.03.
#   4. The Calibrator cannot close the gap: the best-calibrated
#      lambda_THz/lambda for 1 kg, thermal, 300 GHz is still >= 1e18,
#      and the best delta is at a bound with an improvement < 0.1
#      orders of magnitude.
#   5. delta = 0 reproduces the uncalibrated gap exactly.
#
# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (c) 2026 Jean-Francois Brisson (Spark AI NLP)

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import analog_calibration as ac
import matter_wave as mw


def test_1_observer_matches_direct_computation():
    """The Observer's lambda_THz/lambda matches the module's direct
    computation within 1e-9 relative, for every standard case."""
    observer = ac.AnalogObserver()
    for name in ("electron", "proton", "1 kg", "70 kg", "1000 kg"):
        m = mw.MASSES_KG[name]
        for v in (mw.CMB_VELOCITY_M_S, mw.thermal_velocity_m_s(m)):
            for f in mw.FREQUENCIES_HZ:
                obs = observer.observe(m, v, f)
                direct = mw.wavelength_ratio_thz(f, m, v)
                assert math.isclose(
                    obs.lambda_thz_over_lambda, direct, rel_tol=1e-9
                ), (name, v, f, obs.lambda_thz_over_lambda, direct)
                # The other three gap quantities match too.
                assert math.isclose(
                    obs.lambda_over_a0,
                    mw.wavelength_ratio_lattice(m, v),
                    rel_tol=1e-9,
                )
                assert math.isclose(
                    obs.phase_per_lattice_rad,
                    mw.phase_per_lattice_spacing_rad(m, v),
                    rel_tol=1e-9,
                )
                assert math.isclose(
                    obs.gap_orders, math.log10(direct), rel_tol=1e-9
                )


def test_2_observer_is_read_only():
    """Two identical calls give identical results, and observing
    does not change any module value."""
    observer = ac.AnalogObserver()
    # The observer holds no mutable state.
    assert vars(observer) == {}, vars(observer)
    # Module values before observing.
    worst_before = mw.worst_case_ratio()
    lam_before = mw.de_broglie_wavelength_from_velocity_m(
        70.0, mw.CMB_VELOCITY_M_S
    )
    ratio_before = mw.wavelength_ratio_thz(
        1e12, 70.0, mw.CMB_VELOCITY_M_S
    )
    # Observe repeatedly, including the same case twice.
    obs1 = observer.observe(70.0, mw.CMB_VELOCITY_M_S, 1e12)
    obs2 = observer.observe(70.0, mw.CMB_VELOCITY_M_S, 1e12)
    observer.observe(1.0, mw.thermal_velocity_m_s(1.0), 300e9)
    # Identical calls give identical results.
    assert obs1 == obs2
    # Observing changed no module value.
    assert mw.worst_case_ratio() == worst_before
    assert (
        mw.de_broglie_wavelength_from_velocity_m(
            70.0, mw.CMB_VELOCITY_M_S
        )
        == lam_before
    )
    assert (
        mw.wavelength_ratio_thz(1e12, 70.0, mw.CMB_VELOCITY_M_S)
        == ratio_before
    )
    # And the observer still holds no state afterwards.
    assert vars(observer) == {}, vars(observer)


def test_3_calibrator_clips_to_pm_0_05():
    """set_delta clips into [-0.05, 0.05]: never raises, never
    exceeds the bound."""
    cal = ac.AnalogCalibrator()
    assert cal.set_delta(0.5) == 0.05
    assert cal.delta == 0.05
    assert cal.set_delta(-2.0) == -0.05
    assert cal.delta == -0.05
    assert cal.set_delta(0.03) == 0.03
    assert cal.delta == 0.03
    # Exact bounds are held, not just approached.
    assert cal.set_delta(0.05) == 0.05
    assert cal.set_delta(-0.05) == -0.05
    # Zero is a no-op: the calibrated velocity is the raw velocity.
    cal.set_delta(0.0)
    assert cal.calibrated_velocity(1000.0) == 1000.0
    # A +5% delta raises the velocity by exactly 5%.
    cal.set_delta(0.05)
    assert math.isclose(cal.calibrated_velocity(1000.0), 1050.0, rel_tol=0.0)
    # A -5% delta lowers it by exactly 5%.
    cal.set_delta(-0.05)
    assert math.isclose(cal.calibrated_velocity(1000.0), 950.0, rel_tol=0.0)


def test_4_calibrator_cannot_close_the_gap():
    """Best-calibrated lambda_THz/lambda for 1 kg, thermal, 300 GHz
    is still >= 1e18, and the best delta is at a bound with an
    improvement < 0.1 orders of magnitude."""
    result = ac.calibrate(
        1.0, mw.thermal_velocity_m_s(1.0), 300e9
    )
    # Still >= 1e18 after the best bounded calibration.
    assert result["best_ratio"] >= 1e18, result["best_ratio"]
    # The best delta sits at a bound (the ratio scales as (1+delta),
    # so the minimum is at delta = -0.05).
    assert result["best_delta"] == -0.05, result["best_delta"]
    # The improvement is ~0.02 orders -- far under 0.1.
    assert result["improvement_orders"] < 0.1, result["improvement_orders"]
    assert math.isclose(
        result["improvement_orders"], 0.0223, rel_tol=0.01
    ), result["improvement_orders"]
    # Spot value: uncalibrated 1.68e20, best-calibrated 1.60e20.
    assert math.isclose(
        result["uncalibrated_ratio"], 1.68e20, rel_tol=0.01
    ), result["uncalibrated_ratio"]
    assert math.isclose(
        result["best_ratio"], 1.60e20, rel_tol=0.01
    ), result["best_ratio"]
    # The true worst case (3 THz) is even tighter and still fails.
    worst = ac.worst_case_calibrated()
    assert worst["best_ratio"] >= 1e18, worst["best_ratio"]
    assert math.isclose(worst["best_ratio"], 1.60e19, rel_tol=0.01), (
        worst["best_ratio"],
    )
    # The verdict after calibration is still FAIL.
    assert ac.verdict_after_calibration() == "FAIL"


def test_5_delta_zero_reproduces_uncalibrated_gap_exactly():
    """delta = 0 reproduces the uncalibrated gap exactly: the
    calibrate() uncalibrated ratio equals the module's direct
    computation, and a calibrator held at delta = 0 changes nothing."""
    for m, v, f in (
        (70.0, mw.CMB_VELOCITY_M_S, 1e12),
        (1.0, mw.thermal_velocity_m_s(1.0), 300e9),
        (mw.ELECTRON_MASS_KG, mw.CMB_VELOCITY_M_S, 3e12),
    ):
        result = ac.calibrate(m, v, f)
        direct = mw.wavelength_ratio_thz(f, m, v)
        assert result["uncalibrated_ratio"] == direct, (
            m,
            v,
            f,
            result["uncalibrated_ratio"],
            direct,
        )
        # A calibrator at delta = 0 leaves the velocity unchanged,
        # so its best_gap floor is the uncalibrated ratio and its
        # sweep can only improve on it (by moving delta negative).
        cal = ac.AnalogCalibrator(delta=0.0)
        assert cal.delta == 0.0
        assert cal.calibrated_velocity(v) == v
        best_ratio, best_delta = cal.best_gap(m, v, f)
        assert best_ratio == result["best_ratio"]
        assert best_delta == result["best_delta"]
        assert best_ratio <= result["uncalibrated_ratio"]
