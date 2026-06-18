---
name: Numerical caveats — wn_step aliasing, IntensityThreshold, merge rules
maturity: draft
last-verified: 2026-04-29
see-also: [[01_absorbance_spine]], [[02_line_strength_T]], [[../hapi_usage]]
---

# Numerical caveats — wn_step aliasing, IntensityThreshold, merge rules

## 1. Concept summary

Three numerical pitfalls bite without warning in this pipeline. First: the
wavenumber grid step `wn_step` must be fine enough to sample the Voigt peak;
too coarse a grid aliases narrow lines into near-zero values with no error
raised. Second: HAPI's `IntensityThreshold` filters on reference-temperature
intensities (not run-temperature intensities), making it physically incorrect
to apply a HITRAN-tuned threshold to ExoMol hot-band lines — this is covered
in [[02_line_strength_T]] §3 and cross-referenced here for completeness.
Third: the pointwise-max merge rule in `research.combined` combines ExoMol
and HITRAN absorbance contributions correctly only if both are absorbance
values; applying the rule to transmittance is physically wrong.

## 2. Key numerical concerns

- **Voigt grid sampling.** CH4 nu3 lines have Voigt half-widths γ_V on the
  order of 0.001–0.01 cm⁻¹ at typical lab conditions. The sampling rule
  `wn_step ≤ γ_V / 5` must be satisfied to recover the true peak. Empirical
  benchmark on the J 2→3 transition (T = 600 K, P = 3 Torr, x = 0.008,
  L = 100 cm):

  | `wn_step` (cm⁻¹) | HITRAN-only `peak_absorbance` |
  |---|---|
  | 0.01 | 8.196447e-02 |
  | 0.1 | 8.879971e-07 |

  Six orders of magnitude difference — a factor of ~92 000× — between
  `wn_step = 0.01` and `wn_step = 0.1`. Neither run raises an error.
  (Source: `docs/_archive/NU3_PROGRESSIONS_WORKFLOW.md` §10.)

- **`IntensityThreshold` filters reference-T, not run-T.** HAPI's
  `IntensityThreshold` parameter in `hapi.absorptionCoefficient_Voigt` drops
  lines whose reference-temperature intensity falls below the threshold before
  any T-scaling is applied. A threshold calibrated for HITRAN (1e-23 cm/mol)
  erases ExoMol hot-band lines whose reference-T intensities are ~1e-26 to
  1e-25 cm/mol. See [[02_line_strength_T]] §3 for the full physical
  explanation.

- **Pointwise-max merge applies to absorbance, not transmittance.** The
  combined ExoMol + HITRAN workflow merges both source contributions using
  `np.maximum(exomol_absorbance, hitran_absorbance)` per grid point. This is
  physically correct only for absorbance (A = −ln T, additive in the
  optically thin limit). Taking `max(T_exomol, T_hitran)` for transmittance
  values would be wrong: transmittance is multiplicative and taking the
  maximum would underestimate total absorption.

## 3. Code map

| Concept | Module.symbol | What it does (1 line) |
|---|---|---|
| Grid construction | `research.spectra.build_grid` | Returns `np.arange(wn_min, wn_max + 0.5*wn_step, wn_step)` as float64 uniform grid |
| Pointwise-max merge | `research.combined` — `np.maximum(exomol_absorbance, hitran_absorbance)` at lines 796, 1321 | Either-source-wins recovery per J pair, operates on absorbance arrays |
| HAPI intensity filter | `hapi.absorptionCoefficient_Voigt` param `IntensityThreshold` | Drops lines whose reference-T intensity is below threshold before T-scaling |

## 4. Implementation choices and why

**Why pointwise-max (not sum, not average) for the merge.** If only one
source contains a given J pair, its contribution is the full curve; the other
source contributes zero. Pointwise max reduces to the single source in that
case. Where both sources have the same line, summing would double-count;
averaging would underestimate. Max gives "either source wins" recovery: if one
dataset has a stronger or more complete representation of a J pair, it
dominates without suppressing the other dataset's contribution when it is
uniquely present.

**Why the merge rule operates on absorbance and not transmittance.** Absorbance
is proportional to number density and path length (Beer-Lambert: A = σ·n·L).
Taking the max of two independent absorbance estimates is a conservative
upper-bound estimate consistent with "whichever source has the better line
data wins." Transmittance is multiplicative (T = exp(−A)); the max of two
transmittances would imply the weaker of two attenuation effects, which is
physically backwards.

**Why uniform `wn_step` rather than adaptive sampling.** HAPI's
`absorptionCoefficient_Voigt` expects a uniform wavenumber grid specified by
`wn_step`. Switching to adaptive sampling would require either bypassing HAPI
or revalidating all existing artifacts. The current constraint is: choose
`wn_step` conservatively at the start of a run and hold it fixed.

**Why grids are built once per run.** `research.spectra.build_grid` creates
a single shared grid for the whole spectral window. All J-pair curves share
this grid, making absorbance arrays directly addable or comparable without
interpolation. Mixing grids across runs (different `wn_step`) produces
artifacts — see §2 above.

## 5. Footguns

- **DO NOT** use `wn_step > 0.05 cm⁻¹` for narrow-line absorbance work
  because CH4 nu3 Voigt half-widths are ~0.001–0.01 cm⁻¹ and a grid ten
  times coarser than the line width aliases the peak by multiple orders of
  magnitude with no error raised. Use `wn_step ≤ 0.01 cm⁻¹` for quantitative
  work. (See §2 benchmark: `wn_step = 0.1` collapses a 8.2e-2 peak to 8.9e-7.)
- **DO NOT** change the merge rule from `np.maximum` to `+` or any other
  operator without physically justifying the change because the pointwise-max
  rule encodes either-source-wins recovery for J pairs missing from one source,
  and summation would double-count lines present in both databases.
- **DO NOT** apply pointwise-max to transmittance (T) — only to absorbance (A)
  — because pointwise max of transmittances would select the weaker attenuation
  rather than the stronger one, underestimating total absorption wherever both
  sources overlap.
