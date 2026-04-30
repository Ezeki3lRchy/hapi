---
name: Absorbance spine — σ(ν), Voigt, Beer-Lambert
maturity: draft
last-verified: 2026-04-29
see-also: [[../pipeline_map]], [[../hapi_usage]], [[02_line_strength_T]], [[03_numerical_caveats]]
---

# Absorbance spine — σ(ν), Voigt, Beer-Lambert

## 1. Concept summary

This slice covers the line-by-line absorbance computation chain: how individual
spectral lines are broadened, summed into a cross-section, and converted to
absorbance. See `docs/fundamental.md` for the full derivation and worked
examples; this slice maps each step of that derivation to its `research/`
implementation and records the footguns that derivation does not warn about.

The chain has four links. First, each line in the database contributes a center
ν_i and an intensity S_i. Second, thermal and pressure effects broaden that
line into a Voigt profile φ_V(ν − ν_i; γ_D, γ_L), where γ_D is the
Doppler (Gaussian) half-width and γ_L is the Lorentz (collisional) half-width.
Third, all broadened contributions are summed on a wavenumber grid to give
the cross-section σ(ν) = Σ_i S_i · φ_V(ν − ν_i). Fourth, Beer-Lambert scaling
converts σ(ν) to absorbance A(ν) = σ(ν) · n · L, where n is the absorber
number density and L is the path length.

## 2. Key equations

- **Cross-section**: σ(ν) = Σ_i S_i · φ_V(ν − ν_i; γ_D, γ_L)
- **Voigt profile**: φ_V(x; γ_D, γ_L) = ∫ φ_G(x′; γ_D) · φ_L(x − x′; γ_L) dx′
  (Doppler ⊗ Lorentz convolution; computed via the Faddeeva function `wofz`)
- **Doppler HWHM**: γ_D(T) = (ν₀/c) · √(2 k_B T ln 2 / m)
  — proportional to wavenumber; grows with temperature; independent of pressure
- **Lorentz HWHM**: γ_L(P, T) = γ₀ · (P / P_ref) · (T_ref / T)^n
  — grows with pressure; shrinks at higher temperature (exponent n ≈ 0.5–0.75)
- **Beer-Lambert**: A(ν) = σ(ν) · n · L
- **Number density (partial)**: n = x_mol · P / (k_B T)   [ideal gas]
  — x_mol is mole fraction; P in Pa after unit conversion

No SVG in `docs/figures/` shows the Voigt = Doppler ⊗ Lorentz convolution; see
the Figure gap entry in §5.

The workflow SVGs (`docs/exomol_standard_workflow.svg`,
`docs/hitran_standard_workflow.svg`, `docs/ch4_nu3_process_diagram.svg`) show
pipeline stages but do not illustrate line-profile geometry.

## 3. Code map

| Concept | Module.function | What it does (1 line) |
| --- | --- | --- |
| σ(ν) line-by-line sum | `research.absorbance.render_cross_section_from_lines` | Iterates lines, evaluates Voigt at each center, accumulates on grid |
| Direct Voigt absorbance path | `research.absorbance.render_absorbance_on_grid` | Calls `render_cross_section_from_lines` then `cross_section_to_absorbance` |
| σ(ν) → A(ν) conversion | `research.spectra.cross_section_to_absorbance` | Beer-Lambert: A = σ · n_CH4 · L; n from `number_density_cm3` |
| T(ν) → A(ν) conversion | `research.spectra.to_absorbance` | A = −ln(clip(T, 1e-300)); used after `hapi.absorptionCoefficient_Voigt` |
| Voigt profile (HAPI path) | `hapi.absorptionCoefficient_Voigt` | HAPI's reference Voigt implementation; used by the HITRAN render path |

Both `render_cross_section_from_lines` and `render_absorbance_on_grid` live in
`research/absorbance.py`. The Voigt kernel itself is in
`research.spectra.voigt_profile_cm` (wraps `scipy.special.wofz`).

## 4. Implementation choices and why

**Two render paths exist, not one.** The direct-Voigt path
(`render_cross_section_from_lines` → `cross_section_to_absorbance`) is used for
ExoMol pure-nu3 band texts. It is faster for short line lists and does not
require HAPI table plumbing. The HAPI-temp-table path
(`hapi.absorptionCoefficient_Voigt` → `to_absorbance`) is used for HITRAN lines
and for ExoMol MM I1 band texts because HAPI is the validated reference
implementation for HITRAN-style fields. The combined workflow takes the
pointwise maximum of the two arrays. See `docs/pipeline_map.md` §4 and
`docs/_archive/NU3_PROGRESSIONS_WORKFLOW.md` §4 for the rationale recorded
at the time this split was introduced.

**Doppler and Lorentz widths are not exposed separately** in the public API. The
Voigt profile is what a spectrometer measures; the Gaussian and Lorentzian
components are a computational decomposition, not physical observables. Callers
specify T, P, γ₀, and n_exponent; `render_cross_section_from_lines` derives
both half-widths internally.

**`cross_section_to_absorbance` and `to_absorbance` are different functions
for different physical paths.** `cross_section_to_absorbance` applies
Beer-Lambert to a σ(ν) array (ExoMol direct path). `to_absorbance` inverts a
transmittance array via A = −ln(T) (HAPI Voigt path, which returns
transmittance). Mixing them would double-count Beer-Lambert scaling or produce
nonsensical absorbance values. They are kept as separate named functions
precisely to make the two paths explicit.

**The `line_cutoff` parameter in `render_cross_section_from_lines`** clips the
per-line evaluation window to `max(line_cutoff, 25 × max(γ_D, γ_L))`. This
keeps the loop fast for narrow lines without silently truncating wide lines. The
effective window is always at least 25 half-widths wide on each side.

## 5. Footguns

- **Unit mismatch in Beer-Lambert.** `cross_section_to_absorbance` expects
  σ in cm²/molecule, n in molecules/cm³, and L in cm, giving dimensionless A.
  If pressure is passed in Torr (the native repo unit), the conversion to Pa is
  inside `number_density_cm3` — do not convert again before calling
  `cross_section_to_absorbance`. Passing atm instead of Torr silently scales
  n by ~133, producing absorbance values ~133× too large.

- **T=0 in `to_absorbance` is guarded, but barely.** `to_absorbance` clips
  transmittance to 1×10⁻³⁰⁰ before taking the log, so T=0 does not cause
  a domain error — it produces A ≈ 690. If HAPI returns T=0 on a coarse grid
  (strong line, wide wn_step), the absorbance will be finite but wrong. Cross-
  reference `docs/physics/03_numerical_caveats.md` §2 for the wn_step aliasing
  footgun that is the root cause.

- **Figure gap: no Voigt = Doppler ⊗ Lorentz diagram.** No SVG in `docs/figures/`
  or `docs/` shows the convolution geometry. A diagram plotting φ_G, φ_L, and
  φ_V side-by-side for typical CH4 nu3 conditions (T=600 K, P=3 Torr) would
  clarify why γ_D dominates at low pressure. Consider adding to `docs/figures/`.
