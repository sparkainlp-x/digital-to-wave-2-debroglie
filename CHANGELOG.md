# Changelog

All notable changes to this project are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and the project uses
[Semantic Versioning](https://semver.org/).

## [Unreleased]

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
