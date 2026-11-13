# Matter-Wave / Hologram Test — Report

**Paper:** Mun Seok Lee, "Digital to Wave: LGD In Situ Wave Memory–
Human Wave Integrated Interface–Metaverse Hologram–Wave Affective AI",
Zenodo 21947108, DOI 10.5281/zenodo.21947108, 2026-08-15.
**Module:** `matter_wave.py` (this package).
**Calibration:** `analog_calibration.py` (Observer + Calibrator).
**Date:** 2026-11-13. **Tests:** 10/10 pass (`python -m pytest tests/ -v`).

## Claim under test

Paper §3.3–§3.4: an object's de Broglie matter wave couples to THz
and is stored as a hologram, mapped 1:1 onto the LGD lattice
(a₀ = 0.356 nm). The mapping equation is
W_LGD(i,j,k) = A_O(r_ijk)·exp(i(k_matter·r_ijk + φ_O)) with
r_ijk = a₀(i,j,k) — a phase written onto individual lattice sites.

## Method

Relativistic de Broglie wavelength, λ = h / √(2mℰ + ℰ²/c²), where ℰ
is the kinetic energy — the paper's own formula, correctly stated
there. At the paper's velocities (v/c ~ 1.2 × 10⁻³) the relativistic
correction is ~10⁻⁶, so the non-relativistic λ = h/(mv) agrees to
the same precision; both are computed and compared. Inputs are the
paper's own numbers (CMB peculiar velocity 370 km/s; a₀ = 0.356 nm;
THz band 300 GHz–3 THz) plus standard constants (h, c, k_B, electron
and proton masses). Thermal velocities are v_rms = √(3k_B T/m) at
300 K.

## Measured results

| Mass | Velocity | v (m/s) | λ (m) | λ_THz/λ (1 THz) | λ/a₀ | Phase / site (rad) |
|---|---|---|---|---|---|---|
| electron | CMB 370 km/s | 3.70×10⁵ | 1.97×10⁻⁹ | 1.52×10⁵ | 5.52 | 1.14 |
| electron | thermal 300 K | 1.17×10⁵ | 6.23×10⁻⁹ | 4.81×10⁴ | 17.5 | 0.359 |
| proton | CMB 370 km/s | 3.70×10⁵ | 1.07×10⁻¹² | 2.80×10⁸ | 3.01×10⁻³ | 2.09×10³ |
| proton | thermal 300 K | 2.73×10³ | 1.45×10⁻¹⁰ | 2.06×10⁶ | 0.408 | 15.4 |
| 1 kg | CMB 370 km/s | 3.70×10⁵ | 1.79×10⁻³⁹ | 1.67×10³⁵ | 5.03×10⁻³⁰ | 1.25×10³⁰ |
| 1 kg | thermal 300 K | 1.11×10⁻¹⁰ | 5.94×10⁻²⁴ | 5.04×10¹⁹ | 1.67×10⁻¹⁴ | 3.76×10¹⁴ |
| 70 kg | CMB 370 km/s | 3.70×10⁵ | 2.56×10⁻⁴¹ | 1.17×10³⁷ | 7.19×10⁻³² | 8.74×10³¹ |
| 70 kg | thermal 300 K | 1.33×10⁻¹¹ | 7.10×10⁻²⁵ | 4.22×10²⁰ | 2.00×10⁻¹⁵ | 3.15×10¹⁵ |
| 1000 kg | CMB 370 km/s | 3.70×10⁵ | 1.79×10⁻⁴² | 1.67×10³⁸ | 5.03×10⁻³³ | 1.25×10³³ |
| 1000 kg | thermal 300 K | 3.53×10⁻¹² | 1.88×10⁻²⁵ | 1.59×10²¹ | 5.28×10⁻¹⁶ | 1.19×10¹⁶ |

Headline case (70 kg at 370 km/s): λ = **2.56 × 10⁻⁴¹ m** —
1.17 × 10³⁷ times shorter than the 1 THz wavelength, and the phase
across one lattice spacing is **8.74 × 10³¹ rad**. One matter
wavelength spans 1.39 × 10³¹ lattice sites: the wave cannot address
individual sites, and the phase at neighbouring sites is effectively
random, so no coherent 1:1 mapping is possible.

The mass whose matter wavelength would equal the 1 THz wavelength
(300 µm) is **5.97 × 10⁻³⁶ kg** at 370 km/s (3.93 × 10⁻⁴⁰ kg at
thermal velocity) — about 10⁵ times lighter than an electron, and
~10³⁵ times lighter than 1 kg. No macroscopic object can have a
matter wave that couples to THz.

## Verdict: FAIL

The pass/fail criterion was: FAIL if λ_matter is ≥ 10 orders of
magnitude below λ_THz for every macroscopic mass (≥ 1 kg) at every
paper velocity and every THz frequency. The most generous
macroscopic case (1 kg, thermal, 3 THz) is short by **1.68 × 10¹⁹**
— nine orders above the threshold. The claim is falsified as a
matter-wave storage carrier. This is parameter-independent: it
follows from h, c, the paper's velocity, and the lattice pitch
alone. No choice of field strength, gain, or coupling can change
the de Broglie wavelength of a macroscopic mass.

## Analog calibration

**Module:** `analog_calibration.py`. **Tests:** 10/10 pass (5
original + 5 calibration).

**Design (membrane-arena pattern).** A Yang Observer
(`AnalogObserver`) measures the claim gap — λ_THz/λ, λ/a₀, phase
per lattice site, gap in orders of magnitude — and holds no mutable
state: it changes nothing. A Yin Calibrator (`AnalogCalibrator`)
holds one scalar δ ∈ [−0.05, 0.05], applied as a fractional
velocity adjustment v_cal = v × (1 + δ). `set_delta` clips into
the bound; it never raises and never exceeds it. The harness
sweeps δ over 201 points across its full range and returns the
smallest achievable gap, as measured by the Observer.

**Measured result.** A ±5% velocity calibration moves λ by ∓5%,
i.e. ~0.022 orders of magnitude, while the gap is 19–37 orders.
The best δ is always −0.05 (at the bound), and the improvement is
0.0223 orders in every case:

| Case | Uncalibrated λ_THz/λ | Best-calibrated λ_THz/λ | Best δ | Improvement (orders) |
|---|---|---|---|---|
| 1 kg, thermal, 300 GHz | 1.68 × 10²⁰ | 1.60 × 10²⁰ | −0.05 | 0.0223 |
| 1 kg, thermal, 3 THz (true worst case) | 1.68 × 10¹⁹ | 1.60 × 10¹⁹ | −0.05 | 0.0223 |
| 70 kg, CMB 370 km/s, 1 THz | 1.17 × 10³⁷ | 1.11 × 10³⁷ | −0.05 | 0.0223 |
| 1 kg, thermal, 1 THz | 5.04 × 10¹⁹ | 4.79 × 10¹⁹ | −0.05 | 0.0223 |

**Correction to the frequency label.** The smallest uncalibrated
ratio over all macroscopic cases sits at 3 THz, not 300 GHz: the
ratio scales with the THz wavelength, so the shortest THz
wavelength (3 THz) gives the smallest gap. The 1.68 × 10¹⁹ figure
quoted above as the most generous case is the 3 THz value; at
300 GHz the same mass and velocity give 1.68 × 10²⁰. Both are
≥ 10¹⁸ after the best calibration, so the correction changes no
verdict — it only corrects which frequency is the most generous.
(The label in `matter_wave.py`'s `main()` print and
`worst_case_ratio()` docstring still says 300 GHz; the physics
and the verdict are unaffected.)

**Conclusion.** Bounded calibration cannot save the claim. The
best-calibrated gap for the most generous macroscopic case is
still 1.60 × 10¹⁹ — nine orders above the 10¹⁰ fail threshold.
The FAIL verdict stands, now shown to be robust to any ±5%
velocity calibration.

## Note on the analysis values

The deep-analysis report (`~/workspace/digital-to-wave-2/analysis.md`
§3.4) quoted λ = 2.6 × 10⁻⁴¹ m, λ_THz/λ ≈ 10³⁷, and phase
8.7 × 10³¹ rad for 70 kg at 370 km/s. This module reproduces them:
2.56 × 10⁻⁴¹ m, 1.17 × 10³⁷, 8.74 × 10³¹ rad. The analysis values
are 2-significant-figure roundings; the module's values are the
exact computations, and the tests check them to the stated
precision (see test 1's note on the 2% tolerance for the rounded
reference).

## Honest caveats

1. **This tests the matter wave as described.** The paper's mapping
   writes a matter-wave phase onto individual lattice sites. A
   different hologram mechanism the paper does not specify is not
   tested here.
2. **Subatomic particles are the exception that proves the rule.**
   An electron at 370 km/s has λ = 1.97 nm — larger than the lattice
   pitch (λ/a₀ = 5.52). But an electron's wave cannot carry a
   macroscopic object's hologram, and the paper's claim is about
   objects, not electrons.
3. **Conceptual findings, not computed here.** The CMB "absolute
   frame" is a category error: the CMB rest frame is a convenient
   cosmological frame, not a preferred frame for local physics, and
   no mechanism extracts a phase-coherent local reference from the
   CMB dipole. The Active PLL's stability is asserted, not derived
   (K_D units undefined; no loop analysis, bandwidth, noise, or
   pull-in range). Both are recorded in the deep analysis (§3.1,
   §3.7); this module tests only the wavelength arithmetic.
4. **What is not challenged here:** the relativistic de Broglie
   formula, the velocity–energy relation, and the other textbook
   formulae the paper quotes are correctly stated. The failure is
   in the application — a macroscopic matter wave is ~10³⁷ times
   too short to couple to THz or to address a 0.356 nm lattice.
5. **This is a bound, not an experiment.** It shows the claimed
   mechanism cannot work as described; it does not test any other
   storage mechanism.

## Bottom line

A 70 kg object's matter wave is 2.56 × 10⁻⁴¹ m — 10³⁷ times shorter
than the THz wave it is supposed to couple to, with a phase of
8.7 × 10³¹ rad across a single lattice spacing. Together with the
companion results — the §2 human-wave interface falsified by
dimensional error and impossible intensities, and the THz readout
falsified by the diffraction limit (~10¹⁴–10¹⁷ in readable
capacity) — the core storage/retrieval mechanism of the Digital to
Wave Part II architecture does not hold as a physical system.
