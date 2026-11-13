# analog_calibration.py
#
# Analog calibration layer for the matter-wave / hologram test of
# Lee, "Digital to Wave: LGD In Situ Wave Memory-Human Wave
# Integrated Interface-Metaverse Hologram-Wave Affective AI"
# (Zenodo 21947108, DOI 10.5281/zenodo.21947108, 2026-08-15).
#
# The uncalibrated test (matter_wave.py) falsified the paper's §3
# claim: a macroscopic object's de Broglie wavelength is ~10^37
# times shorter than the THz wavelength, and even the most generous
# macroscopic case (1 kg, thermal, 3 THz) is short by 1.68 x 10^19.
# This layer asks whether a bounded analog calibration could save
# the claim. It cannot, and the layer exists to show that honestly.
#
# Design (the membrane-arena pattern):
#   - Yang Observer (AnalogObserver): read-only. It measures the
#     claim gap -- lambda_THz / lambda, lambda / a0, phase per
#     lattice site, gap in orders of magnitude -- and returns it.
#     It holds no mutable state and modifies nothing.
#   - Yin Calibrator (AnalogCalibrator): one clipped scalar delta in
#     [-0.05, 0.05], applied as a fractional velocity adjustment,
#     v_cal = v * (1 + delta). A +/-5% velocity calibration moves
#     lambda by -/+5%, i.e. ~0.02 orders of magnitude, while the
#     gap is 19-37 orders. Calibration cannot close the gap.
#
# Status: SYNTHETIC computation. A classical-physics bound applied
# to the paper's own numbers. No physical claim, no experiment, no
# medical claim. No new physical law is asserted here.
#
# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (c) 2026 Jean-Francois Brisson (Spark AI NLP)

"""Analog calibration layer for the matter-wave test.

An Observer agent (read-only) measures the claim gap for a given
(mass, velocity, frequency); a Calibrator agent (one clipped scalar
delta in [-0.05, 0.05]) applies a fractional velocity adjustment and
searches its full clipped range for the smallest achievable gap.
The result: bounded calibration moves the gap by ~0.02 orders of
magnitude while the gap is 19-37 orders, so the FAIL verdict stands,
now shown to be robust to calibration.
"""

import math
from dataclasses import dataclass

import numpy as np

import matter_wave as mw

# ---------------------------------------------------------------------------
# Calibrator bound (membrane-arena Yin bound): one clipped scalar.
# ---------------------------------------------------------------------------

DELTA_MIN = -0.05
DELTA_MAX = 0.05

# Grid points for the calibrator sweep over its full clipped range.
DELTA_GRID_POINTS = 201


# ---------------------------------------------------------------------------
# Observer agent (Yang): read-only measurement of the claim gap
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class GapObservation:
    """A read-only measurement of the claim gap.

    Frozen: an observation cannot be edited after it is made. All
    values are pure functions of (mass_kg, velocity_m_s,
    frequency_hz) through matter_wave.py; nothing here is stored or
    accumulated between calls.
    """

    mass_kg: float
    velocity_m_s: float
    frequency_hz: float
    lambda_m: float
    lambda_thz_over_lambda: float
    lambda_over_a0: float
    phase_per_lattice_rad: float
    gap_orders: float  # log10(lambda_THz / lambda)


class AnalogObserver:
    """Yang Observer: measures the claim gap, changes nothing.

    The observer holds no mutable state: it has no attributes, and
    every method is a pure function of its arguments. Calling
    observe() twice with the same inputs returns identical results,
    and observing never changes any value in matter_wave.py.
    """

    def observe(self, mass_kg, velocity_m_s, frequency_hz):
        """Measure the claim gap for one (mass, velocity, frequency).

        Returns a GapObservation with the de Broglie wavelength, the
        ratio to the THz wavelength, the ratio to the lattice pitch,
        the phase across one lattice spacing, and the gap in orders
        of magnitude (log10 of lambda_THz / lambda).
        """
        m = float(mass_kg)
        v = float(velocity_m_s)
        f = float(frequency_hz)
        lam = mw.de_broglie_wavelength_from_velocity_m(m, v)
        ratio = mw.wavelength_ratio_thz(f, m, v)
        return GapObservation(
            mass_kg=m,
            velocity_m_s=v,
            frequency_hz=f,
            lambda_m=lam,
            lambda_thz_over_lambda=ratio,
            lambda_over_a0=mw.wavelength_ratio_lattice(m, v),
            phase_per_lattice_rad=mw.phase_per_lattice_spacing_rad(m, v),
            gap_orders=math.log10(ratio),
        )


# ---------------------------------------------------------------------------
# Calibrator agent (Yin): one clipped scalar
# ---------------------------------------------------------------------------

class AnalogCalibrator:
    """Yin Calibrator: a single scalar delta in [-0.05, 0.05].

    delta is applied as a fractional velocity adjustment,
    v_cal = v * (1 + delta). set_delta() clips into the bound: it
    never raises and never lets delta exceed [-0.05, 0.05]. The
    bound is the membrane-arena Yin bound; it is not widened here.
    """

    def __init__(self, delta=0.0):
        self._delta = 0.0
        self.set_delta(delta)

    @property
    def delta(self):
        """The current calibration scalar, always in [-0.05, 0.05]."""
        return self._delta

    def set_delta(self, value):
        """Set delta, clipped into [-0.05, 0.05].

        Never raises, never exceeds the bound. Returns the clipped
        value actually held.
        """
        x = float(value)
        if x < DELTA_MIN:
            x = DELTA_MIN
        elif x > DELTA_MAX:
            x = DELTA_MAX
        self._delta = x
        return self._delta

    def calibrated_velocity(self, velocity_m_s):
        """v_cal = v * (1 + delta)."""
        return float(velocity_m_s) * (1.0 + self._delta)

    def best_gap(self, mass_kg, velocity_m_s, frequency_hz, observer=None):
        """Smallest achievable lambda_THz / lambda over the full
        clipped delta range, as measured by an AnalogObserver.

        Sweeps delta over DELTA_GRID_POINTS evenly spaced points in
        [-0.05, 0.05] and returns (best_ratio, best_delta). The
        sweep does not change the calibrator's held delta. Because
        lambda ~ 1/v, the ratio scales as (1 + delta), so the best
        (smallest) ratio sits at the delta = -0.05 bound -- the
        improvement is a factor 0.95, i.e. ~0.02 orders of magnitude.
        """
        obs = observer if observer is not None else AnalogObserver()
        grid = np.linspace(DELTA_MIN, DELTA_MAX, DELTA_GRID_POINTS)
        best_ratio = None
        best_delta = None
        for d in grid:
            v_cal = float(velocity_m_s) * (1.0 + float(d))
            ratio = obs.observe(mass_kg, v_cal, frequency_hz).lambda_thz_over_lambda
            if best_ratio is None or ratio < best_ratio:
                best_ratio = ratio
                best_delta = float(d)
        return best_ratio, best_delta


# ---------------------------------------------------------------------------
# Calibration harness
# ---------------------------------------------------------------------------

def calibrate(mass_kg, velocity_m_s, frequency_hz):
    """Calibrate one (mass, velocity, frequency) case.

    Returns a dict with the uncalibrated gap (delta = 0), the
    best-calibrated gap (delta swept over its full clipped range),
    the delta achieving it, and the improvement in orders of
    magnitude. The uncalibrated gap is the observer's measurement
    at delta = 0, i.e. the module's own direct computation.
    """
    observer = AnalogObserver()
    calibrator = AnalogCalibrator()
    uncal = observer.observe(mass_kg, velocity_m_s, frequency_hz)
    best_ratio, best_delta = calibrator.best_gap(
        mass_kg, velocity_m_s, frequency_hz, observer=observer
    )
    return {
        "mass_kg": float(mass_kg),
        "velocity_m_s": float(velocity_m_s),
        "frequency_hz": float(frequency_hz),
        "uncalibrated_ratio": uncal.lambda_thz_over_lambda,
        "uncalibrated_gap_orders": uncal.gap_orders,
        "best_ratio": best_ratio,
        "best_delta": best_delta,
        "best_gap_orders": math.log10(best_ratio),
        "improvement_orders": uncal.gap_orders - math.log10(best_ratio),
    }


def calibration_table():
    """Best-calibrated gaps for the module's standard cases.

    The same masses and velocities the module already reports
    (electron, proton, 1 kg, 70 kg, 1000 kg at the CMB velocity and
    at thermal velocity, 300 K), at 1 THz, plus the frequency
    extremes for the most generous macroscopic case (1 kg, thermal):
    300 GHz and 3 THz. The true smallest uncalibrated ratio over
    all macroscopic cases sits at 3 THz (1.68e19); the 300 GHz case
    for the same mass and velocity is 1.68e20. Both are reported
    here so the table does not depend on which one is called the
    most generous.
    """
    rows = []
    names = ("electron", "proton", "1 kg", "70 kg", "1000 kg")
    for name in names:
        m = mw.MASSES_KG[name]
        for label, v in (
            ("CMB 370 km/s", mw.CMB_VELOCITY_M_S),
            ("thermal 300 K", mw.thermal_velocity_m_s(m)),
        ):
            row = calibrate(m, v, 1e12)
            row["mass_name"] = name
            row["velocity_label"] = label
            rows.append(row)
    # Frequency extremes for the most generous macroscopic case.
    m = 1.0
    v = mw.thermal_velocity_m_s(m)
    for f in (300e9, 3e12):
        row = calibrate(m, v, f)
        row["mass_name"] = "1 kg"
        row["velocity_label"] = "thermal 300 K"
        rows.append(row)
    return rows


def worst_case_calibrated():
    """Best-calibrated gap for the true worst macroscopic case.

    The smallest uncalibrated ratio over all macroscopic masses,
    paper velocities and THz frequencies sits at 1 kg, thermal
    velocity, 3 THz. Returns its calibrate() result.
    """
    return calibrate(
        1.0, mw.thermal_velocity_m_s(1.0), 3e12
    )


def verdict_after_calibration():
    """PASS/FAIL after the best bounded calibration.

    FAIL if even the best-calibrated ratio for the true worst
    macroscopic case is still >= 1e10. It is ~1.6e19, so FAIL.
    """
    return (
        "FAIL"
        if worst_case_calibrated()["best_ratio"] >= mw.FAIL_RATIO_THRESHOLD
        else "PASS"
    )


def main():
    """Print the calibration table and the verdict."""
    print("Analog calibration -- Lee, Digital to Wave Part II")
    print("Observer (Yang, read-only) + Calibrator (Yin, delta in")
    print("[-0.05, 0.05], fractional velocity adjustment).")
    print()
    print(
        f"{'mass':>9} {'velocity':>13} {'freq':>7} "
        f"{'uncal ratio':>12} {'best ratio':>12} "
        f"{'best d':>7} {'impr (ord)':>10}"
    )
    for row in calibration_table():
        print(
            f"{row['mass_name']:>9} {row['velocity_label']:>13} "
            f"{row['frequency_hz']/1e12:>6.2f}T "
            f"{row['uncalibrated_ratio']:>12.2e} "
            f"{row['best_ratio']:>12.2e} "
            f"{row['best_delta']:>7.3f} "
            f"{row['improvement_orders']:>10.4f}"
        )
    print()
    worst = worst_case_calibrated()
    print(
        f"Most generous macroscopic case after best calibration "
        f"(1 kg, thermal, 3 THz): lambda_THz/lambda = "
        f"{worst['best_ratio']:.3e} at delta = {worst['best_delta']:.2f}."
    )
    print(
        f"Calibration moved the gap by "
        f"{worst['improvement_orders']:.4f} orders of magnitude; "
        f"the gap is {worst['best_gap_orders']:.2f} orders."
    )
    print()
    print(f"VERDICT: {verdict_after_calibration()} -- bounded "
          f"calibration cannot save the claim.")


if __name__ == "__main__":
    main()
