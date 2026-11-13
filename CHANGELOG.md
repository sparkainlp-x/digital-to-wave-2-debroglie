# Changelog

All notable changes to this project are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and the project uses
[Semantic Versioning](https://semver.org/).

## [Unreleased]

## [0.2.0] - 2026-11-13

### Results (SYNTHETIC; no physical, biological or safety claim)

- **Verdict still FAIL, now robust to calibration.** A bounded
  analog calibration (Observer + Calibrator, δ ∈ [−0.05, 0.05] as
  a fractional velocity adjustment) moves the claim gap by only
  0.0223 orders of magnitude, while the gap is 19–37 orders. The
  best-calibrated gap for the most generous macroscopic case
  (1 kg, thermal, 3 THz) is 1.60 × 10¹⁹ at δ = −0.05 — nine
  orders above the 10¹⁰ fail threshold. For the 300 GHz case the
  best-calibrated gap is 1.60 × 10²⁰.
- **Correction:** the smallest uncalibrated ratio over all
  macroscopic cases sits at 3 THz, not 300 GHz (the ratio scales
  with the THz wavelength). The 1.68 × 10¹⁹ figure is the 3 THz
  value; at 300 GHz the same mass and velocity give 1.68 × 10²⁰.
  No verdict changes; only the frequency label is corrected.

### Added

- `analog_calibration.py`: `AnalogObserver` (read-only gap
  measurement), `AnalogCalibrator` (one clipped scalar in
  [-0.05, 0.05]), `calibrate()` and `calibration_table()`
  harness, `verdict_after_calibration()`.
- `tests/test_analog_calibration.py`: exactly 5 tests, 5/5 pass
  (full suite now 10/10).
- `reports/matter-wave.md`: new "Analog calibration" section with
  the best-calibrated gaps and the frequency-label correction.

## [0.1.0] - 2026-11-13

### Results (SYNTHETIC; no physical, biological or safety claim)

- **Verdict: FAIL.** The paper's matter-wave hologram claim — an
  object's de Broglie wave couples to THz and is stored 1:1 on the
  LGD lattice (a₀ = 0.356 nm) — is falsified by the relativistic de
  Broglie wavelength. For 70 kg at the paper's CMB velocity
  (370 km/s): λ = 2.56 × 10⁻⁴¹ m, 1.17 × 10³⁷ times shorter than
  the 1 THz wavelength, with a phase of 8.74 × 10³¹ rad across one
  lattice spacing. Even the most generous macroscopic case (1 kg,
  thermal, 300 GHz) is short by 1.68 × 10¹⁹. The mass whose matter
  wavelength would equal the 1 THz wavelength is 5.97 × 10⁻³⁶ kg
  (3.93 × 10⁻⁴⁰ kg thermal) — ~10⁵ times lighter than an electron.

### Added

- `matter_wave.py`: relativistic de Broglie wavelength (paper's own
  formula), thermal velocities, ratios to the THz wavelength and to
  the lattice pitch, phase per lattice spacing, mass-for-wavelength
  inversion, verdict.
- `tests/test_matter_wave.py`: exactly 5 tests, 5/5 pass.
- `reports/matter-wave.md`: one-page report with the numbers, the
  verdict, and the honest caveats.
- `pyproject.toml`, `VERSION`, `CHANGELOG.md`, `CITATION.cff`,
  `.zenodo.json`, `NOTICE`, `MODULES.sha256`, `.gitignore`.
