# Digital to Wave Part II — Matter-Wave / Hologram Test

A short, runnable test of the object matter wave claimed in Lee,
"Digital to Wave: LGD In Situ Wave Memory–Human Wave Integrated
Interface–Metaverse Hologram–Wave Affective AI"
(Zenodo 21947108, DOI 10.5281/zenodo.21947108, 2026-08-15).

## The claim under test

The paper claims (§3.3–§3.4) that an object's de Broglie matter wave
couples to THz and is stored as a hologram, mapped 1:1 onto the LGD
lattice (a₀ = 0.356 nm).

## The test

Apply the relativistic de Broglie wavelength — the paper's own
formula, correctly stated there — to the paper's own numbers. For a
70 kg mass at the paper's CMB peculiar velocity (370 km/s),
λ = 2.56 × 10⁻⁴¹ m: about 10³⁷ times shorter than the THz wavelength
(300 µm at 1 THz), and the phase across one lattice spacing is
8.7 × 10³¹ rad — effectively random. No macroscopic object can have
a matter wave that couples to THz or addresses individual lattice
sites.

## Verdict

**FAIL.** The matter wavelength of every macroscopic mass (≥ 1 kg)
is ≥ 10 orders of magnitude below the THz wavelength at every paper
velocity (CMB 370 km/s and thermal at 300 K) and every THz frequency
(300 GHz–3 THz). Even the most generous macroscopic case (1 kg,
thermal, 3 THz) is short by 1.68 × 10¹⁹. The mass whose matter
wavelength would equal the 1 THz wavelength is 5.97 × 10⁻³⁶ kg —
about 10⁵ times lighter than an electron. This is
parameter-independent: it follows from h, c, the paper's velocity,
and the lattice pitch alone.

## Analog calibration

An Observer agent (read-only) and a Calibrator agent (one clipped
scalar δ ∈ [−0.05, 0.05], applied as a fractional velocity
adjustment) test whether a bounded calibration could save the
claim. It cannot: a ±5% velocity calibration moves the gap by only
0.022 orders of magnitude, while the gap is 19–37 orders. The
best-calibrated gap for the most generous macroscopic case (1 kg,
thermal, 3 THz) is still 1.60 × 10¹⁹, at δ = −0.05. The FAIL
verdict stands, robust to calibration. See
`reports/matter-wave.md` ("Analog calibration") and
`analog_calibration.py`.

## Spooky stability

The Omega-Genesis "spooky" concept — mean pairwise |dot| over 5
noisy copies of a state — applied to this test: the state is the
vector of log10(λ_THz/λ) across the 10 standard cases at 1 THz,
and each noisy copy perturbs every (mass, velocity) by relative
Gaussian noise (σ = 0.01, seed 42). Measured spooky correlation
**0.99999995**, and the verdict is stable **5/5 FAIL** at σ = 0.01
and σ = 0.05. The FAIL is robust to input noise. The value is
NOT comparable to the Omega-Genesis 0.9005 — same concept,
different state, different noise. See `reports/matter-wave.md`
("Spooky stability") and `spooky_stability.py`.

## Run it

```sh
python matter_wave.py   # prints the table and the verdict
python analog_calibration.py   # prints the calibration table
python spooky_stability.py   # prints spooky + verdict stability
python -m pytest tests/ -v     # 15 tests, all must pass
```

## Layout

- `matter_wave.py` — the module (stdlib + NumPy only).
- `analog_calibration.py` — Observer (read-only) + Calibrator
  (one clipped scalar δ ∈ [−0.05, 0.05]) + calibration harness.
- `spooky_stability.py` — Omega-Genesis spooky correlation over
  noisy log-gap state vectors + verdict stability.
- `tests/test_matter_wave.py` — exactly 5 tests.
- `tests/test_analog_calibration.py` — exactly 5 tests.
- `tests/test_spooky_stability.py` — exactly 5 tests.
- `reports/matter-wave.md` — one-page report with the numbers, the
  verdict, the calibration results, the spooky stability, and the
  honest caveats.
- `pyproject.toml` — package metadata (version 0.3.0, AGPL-3.0-only).
- `VERSION` — 0.3.0. `CHANGELOG.md` — release notes.
- `CITATION.cff`, `.zenodo.json`, `NOTICE` — citation and attribution
  metadata (DOI pending: no Zenodo record yet).
- `MODULES.sha256` — SHA-256 checksums of the module, tests and report.
- `LICENSE` — GNU Affero General Public License v3 (AGPL-3.0-only).

## Credits

- **Mun Seok Lee** — author of the Part II paper under test
  ("Digital to Wave: LGD In Situ Wave Memory–Human Wave Integrated
  Interface–Metaverse Hologram–Wave Affective AI", Zenodo 21947108).
  The claims, equations and numbers tested here are his; the test,
  the computation and the verdict are not his and he has not reviewed
  or endorsed this software.
- **Jean-François Brisson (Spark AI NLP)** — author of this test
  module, the deep analysis behind it, and the FAIL verdict.
- **Omega-Genesis (Untitled7, Colab notebooks)** — source of the
  "spooky" concept applied in `spooky_stability.py`: mean pairwise
  |dot| over 5 noisy copies of a state (measured 0.9005 there).
  The concept is reused; the value is not comparable (different
  state, different noise).
- **Companion work:** `sparkainlp-x/digital-to-wave-2-thz-validity`,
  which validity-checked the §2 human-wave-interface equations
  (dimensional error, impossible intensities, χ⁽²⁾ = 0 in bulk water),
  and `sparkainlp-x/digital-to-wave-2-diffraction`, which falsified
  the THz readout by the Abbe diffraction limit (readable capacity
  short by ~10¹⁴–10¹⁷). This module covers the §3 matter-wave /
  hologram gap those repos left open.

## Status and limits

SYNTHETIC computation. A classical-physics bound applied to the
paper's own numbers. No physical claim, no experiment, no medical
claim. This tests the matter wave as a storage carrier as the paper
describes it; it does not test any other hologram mechanism the paper
does not specify. The CMB "absolute frame" category error and the
PLL's undefined K_D are recorded as conceptual findings in the
report, not computed here.

## License

AGPL-3.0-only. Copyright (c) 2026 Jean-Francois Brisson (Spark AI NLP).
