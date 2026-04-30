---
name: Non-LTE / Treanor distribution — code map
maturity: draft
last-verified: 2026-04-29
see-also: [[02_line_strength_T]], [[../pipeline_map]]
---

# Non-LTE / Treanor distribution — code map

## 1. Concept summary

This slice does NOT re-derive the Treanor distribution or the non-LTE
absorbance physics. The canonical derivation and physical motivation live in
[`docs/TREANOR_DISTRIBUTION_NOTES.md`](../TREANOR_DISTRIBUTION_NOTES.md).
The CH4 ν₃ realization discussion — how Treanor enters the absorption chain,
the generalized effective-absorber formula, and the verification plan — lives in
[`docs/nonlte_absorption_realization_discussion.md`](../nonlte_absorption_realization_discussion.md).
The two-temperature population model intuition lives in
[`docs/population_model_intuition_obsidian.md`](../population_model_intuition_obsidian.md).

This slice exists only to map the concepts in those docs to the `research/`
modules and `scripts/` that implement them, and to record the implementation
choices and footguns specific to the code.

## 2. Key concepts (pointers)

- **Treanor distribution** — two-temperature vibrational population model for
  anharmonic oscillators; formula and physical derivation in
  `docs/TREANOR_DISTRIBUTION_NOTES.md` §"The formula" (Fridman Eq. 3-37).
- **Treanor minimum v\*** — the quantum number at which population inversion
  begins when T_v ≫ T_0; formula and CO/CH4 ν₃ tables in
  `TREANOR_DISTRIBUTION_NOTES.md` §"The Treanor minimum".
- **Two-temperature decoupling (T_v ≠ T_0)** — physical meaning of the two
  temperatures and what they do not mean; see `TREANOR_DISTRIBUTION_NOTES.md`
  §"What the two temperatures do not mean" and
  `docs/population_model_intuition_obsidian.md` §"Non-LTE population model".
- **CH4 ν₃ effective single-mode approximation** — treating the (0,0,v₃,0)
  ladder as an isolated anharmonic oscillator; limitations listed in
  `TREANOR_DISTRIBUTION_NOTES.md` §"Main limitations for CH₄".
- **Ratio-scaling approach** — I_nonLTE = I_LTE × N_Treanor(v₃_lower) /
  N_Boltzmann(v₃_lower); rationale and Phase 2 generalized-n_eff path in
  `docs/nonlte_absorption_realization_discussion.md` §2–3.
- **Process diagram** — step-by-step flow from (T_0, T_v, P, x, L) to
  non-LTE absorbance spectrum: see
  [`docs/ch4_nu3_treanor_process_figure.md`](../ch4_nu3_treanor_process_figure.md)
  and the accompanying SVG
  [`docs/ch4_nu3_process_diagram.svg`](../ch4_nu3_process_diagram.svg).

## 3. Code map

| Concept | Module.function | What it does (1 line) |
| --- | --- | --- |
| Diatomic Treanor population | `research.treanor.treanor` | Returns N_v / N_0 for a diatomic oscillator at (T_v, T_0) — reference/teaching module for CO and N₂ |
| Diatomic Treanor minimum | `research.treanor.treanor_minimum` | Continuous v* = T_0 / (2 x_e T_v) — Fridman Eq. (3-38) |
| CH4 ν₃ Treanor population | `research.ch4_treanor.treanor_nu3` | N_v3 / N_0 along the (0,0,v₃,0) ladder at (T_v, T_0) |
| CH4 ν₃ Boltzmann population | `research.ch4_treanor.boltzmann_nu3` | Compact v² Boltzmann used for equilibrium identity check |
| Non-LTE intensity scale factor | `research.ch4_treanor.nonlte_intensity_scale_factor` | Per-transition multiplier: treanor_nu3(v₃_lower) / boltzmann_nu3(v₃_lower) |
| High-level non-LTE workflow | `research.nonlte.collect_nu3_transitions_nonlte` | Wraps ExoMol line collection and applies Treanor scale factor to each transition group |
| Population validation plot | `scripts/plot_ch4_nu3_treanor_populations.py` | Plots ln(N_v3 / N_0) vs v₃ for multiple T_v at fixed T_0; compares Treanor vs Boltzmann |
| Non-LTE absorbance plot | `scripts/plot_ch4_nu3_nonlte_absorbance.py` | Renders LTE vs non-LTE CH4 ν₃ absorbance side-by-side; imports `nonlte_intensity_scale_factor` directly |
| Equilibrium identity check | `scripts/validate_ch4_nu3_treanor_equilibrium.py` | Verifies that setting T_v = T_0 makes all scale factors equal 1.0 |

The diatomic module (`research/treanor.py`) is the reference implementation for
CO and N₂. The CH4-specific module (`research/ch4_treanor.py`) uses the same
Treanor formula but with CH4 ν₃ constants (ω₃ = 3019 cm⁻¹, ω₃x₃₃ = 62.2 cm⁻¹,
Herzberg 1945). The high-level integration (`research/nonlte.py`) calls
`research.ch4_treanor.nonlte_intensity_scale_factor` on each J-pair group
returned by `research.exomol.collect_nu3_transitions_by_jpair`.

## 4. Implementation choices and why

**Treanor is the population model, not the spectrum model.** The Treanor modules
supply N_v3 / N_0 along the CH4 ν₃ ladder. Line positions, A-coefficients,
selection rules, broadening, and Beer-Lambert propagation all remain with the
ExoMol/HITRAN line-list machinery and the absorbance chain in `research/absorbance.py`.
This separation means the population model can be changed (Boltzmann ↔ Treanor ↔
other) without touching the Voigt integration or Beer-Lambert steps. See
`docs/nonlte_absorption_realization_discussion.md` §4.

**Ratio scaling rather than full generalized n_eff.** The current implementation
multiplies LTE line intensities by treanor_nu3(v₃_lower) / boltzmann_nu3(v₃_lower).
This reuses the LTE partition-function machinery and avoids recomputing Einstein
A-coefficients explicitly. It is accurate when the upper-state stimulated-emission
correction is small. The generalized n_eff = n_lower − (g_lower / g_upper) n_upper
formulation (Phase 2) is documented in `nonlte_absorption_realization_discussion.md`
§3 for future implementation.

**Equilibrium identity is enforced by construction.** `boltzmann_nu3` uses the
same compact v² energy form as `treanor_nu3`, so the ratio is exactly 1.0 when
T_v = T_0 at every v₃. This is verified by
`scripts/validate_ch4_nu3_treanor_equilibrium.py`. If a different Boltzmann form
(full anharmonic E_v = hc [ω v − ω x_e v(v+1)]) were used, the ratio would not
be exactly 1.0 at equilibrium due to the v-linear mismatch documented in
`TREANOR_DISTRIBUTION_NOTES.md` §"The formula" (Why this is the same as Fridman
Eq. 3-37).

**Two scripts, not one, because they answer different questions.** The population
plot (`plot_ch4_nu3_treanor_populations.py`) validates that the Treanor curve
shape and inversion point match the theory. The absorbance plot
(`plot_ch4_nu3_nonlte_absorbance.py`) validates that the non-LTE intensity
scaling propagates correctly through the full spectrum pipeline. Merging them
would obscure which step introduces any discrepancy.

**`research/treanor.py` is a teaching module.** It is parameterized for diatomic
molecules (CO, N₂) and is not used in the CH4 ν₃ absorbance pipeline. It
remains in the repo as a self-contained reference that reproduces Fridman Fig. 3.3.
The CH4-specific logic lives entirely in `research/ch4_treanor.py`.

## 5. Footguns

- **DO NOT** mix LTE-intensity line tables with Treanor-weighted line selections
  in the same artifact. The ratio-scaling approach assumes that I_LTE is computed
  at T_0 (not at some other reference temperature) before the scale factor is
  applied. If the ExoMol export was done at a different reference temperature,
  the scale factor cancels the wrong Boltzmann weight and the result is
  physically meaningless.

- **DO NOT** use Treanor populations outside the validity regime without
  checking the Treanor minimum. The anharmonicity expansion (compact v²
  form) is accurate for low-to-moderate v₃. At high v₃ and extreme T_v,
  higher-order anharmonic terms matter and the population inversion may be
  unphysical. See `TREANOR_DISTRIBUTION_NOTES.md` §"The Treanor minimum" for
  the v* table at CH4 ν₃ conditions.

- **DO NOT** describe Treanor as "the spectrum model" or "the non-LTE
  spectrum." Treanor supplies population fractions only. The spectrum requires
  additionally: a line list, transition strengths, broadening parameters, and
  Beer-Lambert propagation. See `docs/population_model_intuition_obsidian.md`
  §"Practical wording".

- **DO NOT** apply this module to CH4 hot-band populations outside the
  (0,0,v₃,0) ladder without review. Other methane modes, combination bands,
  and Fermi-resonance partners are outside the scope of this single-mode
  approximation. The current ExoMol line lists in this repo typically contain
  transitions up to v₃ ≤ 4; the Treanor minimum at T_v = 3000 K, T_0 = 600 K
  is v* ≈ 4.9, so population inversion is only barely captured by the available
  data range. See `TREANOR_DISTRIBUTION_NOTES.md` §"Data range" limitation.

- **Equilibrium identity check is the first verification gate.** Before using
  any modified Treanor or Boltzmann function in a spectrum, run
  `scripts/validate_ch4_nu3_treanor_equilibrium.py`. If it does not report all
  scale factors = 1.0 at T_v = T_0, the normalization convention is broken.
  See `nonlte_absorption_realization_discussion.md` §5 verification table.
