# matter_wave.py
#
# Matter-wave / hologram test for the object wave claimed in Lee,
# "Digital to Wave: LGD In Situ Wave Memory-Human Wave Integrated
# Interface-Metaverse Hologram-Wave Affective AI"
# (Zenodo 21947108, DOI 10.5281/zenodo.21947108, 2026-08-15).
#
# The paper claims (section 3.3-3.4) that an object's de Broglie
# matter wave couples to THz and is stored as a hologram, mapped 1:1
# onto the LGD lattice (a0 = 0.356 nm). This module applies the
# relativistic de Broglie wavelength -- the paper's own formula,
# correctly stated there -- to the paper's own numbers and computes
# how far the matter wavelength of any macroscopic object sits from
# the THz wavelength and from the lattice pitch.
#
# Method: lambda = h / sqrt(2 m E + E^2 / c^2), where E is the kinetic
# energy. At the paper's velocities the relativistic correction is
# ~1e-6, so the non-relativistic lambda = h / (m v) agrees to the
# same precision; both are computed and compared. The phase across
# one lattice spacing is k * a0 = 2 pi a0 / lambda.
#
# Status: SYNTHETIC computation. A classical-physics bound applied to
# the paper's own numbers. No physical claim, no experiment, no
# medical claim. No new physical law is asserted here.
#
# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (c) 2026 Jean-Francois Brisson (Spark AI NLP)

"""Relativistic de Broglie wavelength of macroscopic objects vs the
THz wavelength and the LGD lattice pitch.

All inputs are the paper's own stated values plus standard physics
constants (h, c, k_B, electron and proton masses). Nothing else is
assumed. The paper's velocity-energy relation and relativistic de
Broglie formula are standard physics, correctly stated in the paper;
the failure is in the application -- a macroscopic matter wave cannot
be a storage carrier at lattice scale.
"""

import math

import numpy as np

# ---------------------------------------------------------------------------
# Inputs: standard physics constants (exact SI definitions where noted)
# ---------------------------------------------------------------------------

PLANCK_H_J_S = 6.62607015e-34  # exact, SI definition
SPEED_OF_LIGHT_M_S = 299792458.0  # exact, SI definition
BOLTZMANN_KB_J_K = 1.380649e-23  # exact, SI definition
ELECTRON_MASS_KG = 9.1093837e-31
PROTON_MASS_KG = 1.67262192e-27
ELECTRONVOLT_J = 1.602176634e-19  # exact, SI definition

# ---------------------------------------------------------------------------
# Inputs: the paper's own stated values (Zenodo 21947108)
# ---------------------------------------------------------------------------

# LGD lattice pitch, paper section 1 (diamond lattice constant).
LATTICE_PITCH_M = 0.356e-9

# CMB peculiar velocity, paper section 3.1-3.2: v ~ 370 km/s.
CMB_VELOCITY_M_S = 370e3

# THz band, paper section 3: 300 GHz - 3 THz.
FREQUENCIES_HZ = (300e9, 1e12, 3e12)

# Temperature for thermal velocities: 300 K (room temperature).
THERMAL_TEMPERATURE_K = 300.0

# Masses reported: electron, proton, and macroscopic masses.
MASSES_KG = {
    "electron": ELECTRON_MASS_KG,
    "proton": PROTON_MASS_KG,
    "1 kg": 1.0,
    "70 kg": 70.0,
    "1000 kg": 1000.0,
}

# Macroscopic masses (the fail criterion applies to these).
MACROSCOPIC_MASSES_KG = (1.0, 70.0, 1000.0)

# Pass/fail threshold: the claim FAILS if the matter wavelength is
# >= 10 orders of magnitude below the THz wavelength, i.e.
# lambda_THz / lambda_matter >= 1e10, for every macroscopic mass at
# every paper velocity and every THz frequency.
FAIL_RATIO_THRESHOLD = 1e10


# ---------------------------------------------------------------------------
# Core computation
# ---------------------------------------------------------------------------

def kinetic_energy_joules(mass_kg, velocity_m_s):
    """Relativistic kinetic energy E = (gamma - 1) m c^2, in joules.

    gamma = 1 / sqrt(1 - (v/c)^2). Computed in the numerically stable
    form E = m v^2 / (s (1 + s)) with s = sqrt(1 - (v/c)^2), so that
    slow velocities do not underflow: at v/c ~ 1e-20 the naive
    (gamma - 1) is exactly 0.0 in double precision, while this form
    returns 1/2 m v^2 to full precision. At the paper's velocities
    (v/c ~ 1.2e-3) this is 1/2 m v^2 to ~1e-6.
    """
    m = float(mass_kg)
    v = float(velocity_m_s)
    if m <= 0.0:
        raise ValueError("mass must be positive")
    if not 0.0 <= abs(v) < SPEED_OF_LIGHT_M_S:
        raise ValueError("velocity must satisfy 0 <= |v| < c")
    beta_sq = (v / SPEED_OF_LIGHT_M_S) ** 2
    s = math.sqrt(1.0 - beta_sq)
    return m * v * v / (s * (1.0 + s))


def de_broglie_wavelength_m(mass_kg, kinetic_energy_j):
    """Relativistic de Broglie wavelength, in metres.

    lambda = h / sqrt(2 m E + E^2 / c^2), the paper's own formula
    (section 3.4), correctly stated there. E is the kinetic energy.
    """
    m = float(mass_kg)
    e = float(kinetic_energy_j)
    if m <= 0.0:
        raise ValueError("mass must be positive")
    if e < 0.0:
        raise ValueError("kinetic energy must be non-negative")
    p = math.sqrt(2.0 * m * e + e ** 2 / SPEED_OF_LIGHT_M_S ** 2)
    return PLANCK_H_J_S / p


def de_broglie_wavelength_from_velocity_m(mass_kg, velocity_m_s):
    """Relativistic de Broglie wavelength for a mass moving at v."""
    e = kinetic_energy_joules(mass_kg, velocity_m_s)
    return de_broglie_wavelength_m(mass_kg, e)


def de_broglie_wavelength_nonrel_m(mass_kg, velocity_m_s):
    """Non-relativistic de Broglie wavelength lambda = h / (m v)."""
    m = float(mass_kg)
    v = float(velocity_m_s)
    if m <= 0.0 or v <= 0.0:
        raise ValueError("mass and velocity must be positive")
    return PLANCK_H_J_S / (m * v)


def thermal_velocity_m_s(mass_kg, temperature_k=THERMAL_TEMPERATURE_K):
    """Root-mean-square thermal velocity v_rms = sqrt(3 k_B T / m)."""
    m = float(mass_kg)
    if m <= 0.0:
        raise ValueError("mass must be positive")
    return math.sqrt(3.0 * BOLTZMANN_KB_J_K * float(temperature_k) / m)


def thz_wavelength_m(freq_hz):
    """Vacuum wavelength (m) of the THz readout wave at freq_hz."""
    return SPEED_OF_LIGHT_M_S / float(freq_hz)


def wavelength_ratio_thz(freq_hz, mass_kg, velocity_m_s):
    """lambda_THz / lambda_matter (dimensionless).

    How many matter wavelengths fit across one THz wavelength. A
    value >> 1 means the matter wave is far too short to couple to
    the THz wave.
    """
    lam = de_broglie_wavelength_from_velocity_m(mass_kg, velocity_m_s)
    return thz_wavelength_m(freq_hz) / lam


def wavelength_ratio_lattice(mass_kg, velocity_m_s):
    """lambda_matter / a0 (dimensionless).

    How many lattice pitches fit across one matter wavelength. A
    value << 1 means one lattice spacing holds many matter
    wavelengths -- the phase across a single site is effectively
    random.
    """
    lam = de_broglie_wavelength_from_velocity_m(mass_kg, velocity_m_s)
    return lam / LATTICE_PITCH_M


def phase_per_lattice_spacing_rad(mass_kg, velocity_m_s):
    """Phase across one lattice spacing, k * a0 = 2 pi a0 / lambda.

    In radians. For macroscopic masses this is astronomically large,
    so the phase at neighbouring lattice sites is effectively random
    -- no coherent 1:1 mapping of a matter wave onto the lattice is
    possible.
    """
    lam = de_broglie_wavelength_from_velocity_m(mass_kg, velocity_m_s)
    return 2.0 * math.pi * LATTICE_PITCH_M / lam


def matter_wavelengths_per_thz(freq_hz, mass_kg, velocity_m_s):
    """Number of matter wavelengths across one THz wavelength.

    Identical to wavelength_ratio_thz; named for the coherence check.
    """
    return wavelength_ratio_thz(freq_hz, mass_kg, velocity_m_s)


def lattice_sites_per_matter_wavelength(mass_kg, velocity_m_s):
    """Number of lattice sites across one matter wavelength, a0 / lambda.

    For macroscopic masses this is astronomically large: a single
    matter wavelength spans ~10^31 lattice sites, so the wave cannot
    address individual sites.
    """
    lam = de_broglie_wavelength_from_velocity_m(mass_kg, velocity_m_s)
    return LATTICE_PITCH_M / lam


def mass_for_wavelength_kg(wavelength_m, velocity_m_s):
    """Mass whose de Broglie wavelength equals wavelength_m at velocity v.

    Non-relativistic inversion m = h / (lambda v). Valid here because
    the resulting mass is tiny (v << c for any such mass at these
    wavelengths). At the paper's 370 km/s this is ~6e-36 kg for a
    1 THz wavelength -- far below the electron mass.
    """
    lam = float(wavelength_m)
    v = float(velocity_m_s)
    if lam <= 0.0 or v <= 0.0:
        raise ValueError("wavelength and velocity must be positive")
    return PLANCK_H_J_S / (lam * v)


def mass_for_wavelength_thermal_kg(wavelength_m, temperature_k=THERMAL_TEMPERATURE_K):
    """Mass whose thermal de Broglie wavelength equals wavelength_m.

    At fixed temperature v_rms = sqrt(3 k_B T / m), so
    lambda = h / sqrt(3 m k_B T) and m = h^2 / (3 k_B T lambda^2).
    """
    lam = float(wavelength_m)
    if lam <= 0.0:
        raise ValueError("wavelength must be positive")
    return (
        PLANCK_H_J_S ** 2
        / (3.0 * BOLTZMANN_KB_J_K * float(temperature_k) * lam ** 2)
    )


# ---------------------------------------------------------------------------
# Verdict and summary
# ---------------------------------------------------------------------------

def worst_case_ratio():
    """The smallest lambda_THz / lambda_matter over all macroscopic
    masses (>= 1 kg), all paper velocities (CMB 370 km/s and thermal
    at 300 K) and all THz frequencies -- i.e. the most generous case
    for the paper. The minimum sits at the smallest mass, the lowest
    velocity and the shortest THz wavelength (1 kg, thermal, 3 THz),
    and it is still ~10^19."""
    ratios = [
        wavelength_ratio_thz(f, m, v)
        for f in FREQUENCIES_HZ
        for m in MACROSCOPIC_MASSES_KG
        for v in (
            CMB_VELOCITY_M_S,
            thermal_velocity_m_s(m),
        )
    ]
    return min(ratios)


def verdict():
    """PASS/FAIL on the paper's matter-wave hologram claim.

    FAIL if lambda_matter is >= 10 orders of magnitude below
    lambda_THz for every macroscopic mass at every paper velocity
    and every THz frequency. Returns "FAIL" or "PASS".
    """
    return "FAIL" if worst_case_ratio() >= FAIL_RATIO_THRESHOLD else "PASS"


def summarize():
    """One row per (mass, velocity) with the full matter-wave chain.

    Returns a list of dicts, one per mass at the CMB velocity and one
    per mass at its thermal velocity, each with the velocity, the de
    Broglie wavelength (relativistic and non-relativistic), the
    ratios to the 1 THz wavelength and to the lattice pitch, the
    phase across one lattice spacing, and the matter wavelengths per
    THz wavelength.
    """
    rows = []
    masses = np.array(
        [MASSES_KG[k] for k in ("electron", "proton", "1 kg", "70 kg", "1000 kg")],
        dtype=float,
    )
    names = ("electron", "proton", "1 kg", "70 kg", "1000 kg")
    for name, m in zip(names, masses):
        m = float(m)
        for label, v in (
            ("CMB 370 km/s", CMB_VELOCITY_M_S),
            ("thermal 300 K", thermal_velocity_m_s(m)),
        ):
            lam = de_broglie_wavelength_from_velocity_m(m, v)
            lam_nr = de_broglie_wavelength_nonrel_m(m, v)
            rows.append(
                {
                    "mass_name": name,
                    "mass_kg": m,
                    "velocity_label": label,
                    "velocity_m_s": v,
                    "lambda_m": lam,
                    "lambda_nonrel_m": lam_nr,
                    "rel_to_nonrel": lam / lam_nr,
                    "lambda_thz_over_lambda_1thz": wavelength_ratio_thz(
                        1e12, m, v
                    ),
                    "lambda_over_a0": wavelength_ratio_lattice(m, v),
                    "phase_per_lattice_rad": phase_per_lattice_spacing_rad(
                        m, v
                    ),
                    "matter_wavelengths_per_thz_1thz": matter_wavelengths_per_thz(
                        1e12, m, v
                    ),
                    "sites_per_matter_wavelength": lattice_sites_per_matter_wavelength(
                        m, v
                    ),
                }
            )
    return rows


def main():
    """Print the matter-wave table and the verdict."""
    print("Matter-wave / hologram test -- Lee, Digital to Wave Part II")
    print("Zenodo 21947108. Paper's own numbers + relativistic de Broglie.")
    print("Claim: an object's matter wave couples to THz and is stored")
    print("1:1 on the LGD lattice (a0 = 0.356 nm).")
    print()
    print(
        f"{'mass':>9} {'velocity':>13} {'v (m/s)':>10} "
        f"{'lambda (m)':>12} {'lam_THz/lam':>12} "
        f"{'lam/a0':>10} {'phase/site':>12}"
    )
    for row in summarize():
        print(
            f"{row['mass_name']:>9} {row['velocity_label']:>13} "
            f"{row['velocity_m_s']:>10.2e} "
            f"{row['lambda_m']:>12.2e} "
            f"{row['lambda_thz_over_lambda_1thz']:>12.2e} "
            f"{row['lambda_over_a0']:>10.2e} "
            f"{row['phase_per_lattice_rad']:>12.2e}"
        )
    print()
    lam_t = thz_wavelength_m(1e12)
    m_eq = mass_for_wavelength_kg(lam_t, CMB_VELOCITY_M_S)
    m_eq_th = mass_for_wavelength_thermal_kg(lam_t)
    print(
        f"Mass whose matter wavelength equals the 1 THz wavelength "
        f"({lam_t*1e6:.0f} um) at 370 km/s: {m_eq:.3e} kg "
        f"(electron mass is {ELECTRON_MASS_KG:.3e} kg)."
    )
    print(
        f"Same, at thermal velocity (300 K): {m_eq_th:.3e} kg."
    )
    print(
        f"Most generous macroscopic case (1 kg, thermal, 3 THz): "
        f"lambda_THz/lambda = {worst_case_ratio():.3e}."
    )
    print()
    print(f"VERDICT: {verdict()} -- the matter wavelength of every "
          f"macroscopic mass is >= 10 orders of magnitude below the "
          f"THz wavelength at every paper velocity.")


if __name__ == "__main__":
    main()
