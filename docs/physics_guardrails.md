---
name: Physics Guardrails — Agent "DO NOT" Rules
maturity: draft
last-verified: 2026-04-29
see-also: [[theory_code_map]], [[pipeline_map]], [[hapi_usage]], [[physics/01_absorbance_spine]], [[physics/02_line_strength_T]], [[physics/03_numerical_caveats]], [[physics/04_nonlte_treanor]], [[physics/05_band_jpair_structure]], [[physics/06_database_conventions]]
---

# Physics Guardrails — Agent "DO NOT" Rules

A flat, citation-rich checklist for agentic workers. Every rule below is
harvested from the §5 Footguns sections of the topic docs in `docs/physics/`
or from `CLAUDE.md`. No rule appears here without a citation. Before changing
any default, threshold, or algorithm choice in `research/` or `scripts/`,
verify that your change does not violate a rule in this file.

---

## Hard rules

- **DO NOT** modify `hapi/hapi.py` for research work — it tracks the upstream
  `hitranonline/hapi` repo; all custom logic belongs in `research/` and
  `scripts/`; see `CLAUDE.md` §Git Remotes.

- **DO NOT** change `intensity_threshold` from 0.0 for ExoMol lines — applying
  any positive threshold filters hot-band lines at reference temperature (296 K)
  before T-scaling can amplify them, silently erasing all hot-band progressions
  while leaving the fundamental band present and appearing valid; see
  `physics/02_line_strength_T.md` §3 and §4.

- **DO NOT** change `hitran_intensity_threshold` from 1e-23 for HITRAN lines
  without verifying that newly included weak lines have been validated — raising
  the threshold silently drops physically significant weak lines at high
  temperature; see `physics/02_line_strength_T.md` §5.

- **DO NOT** set `temperature_k > 2500` — HAPI's TIPS-2025 partition functions
  are tabulated only on [1 K, 2500 K]; exceeding this range produces a silent
  wrong answer or a runtime exception; see `physics/02_line_strength_T.md` §2
  and `CLAUDE.md` §Key Constraints.

- **DO NOT** use `wn_step > 0.05 cm⁻¹` for narrow-line absorbance work — CH4
  nu3 Voigt half-widths are ~0.001–0.01 cm⁻¹; a grid ten times coarser than
  the line width aliases the peak by multiple orders of magnitude with no error
  raised (benchmark: `wn_step = 0.1` collapses an 8.2e-2 peak to 8.9e-7); see
  `physics/03_numerical_caveats.md` §2.

- **DO NOT** change the merge rule in `research.combined` from `np.maximum` to
  `+` or any other operator — the pointwise-max rule encodes either-source-wins
  recovery for J pairs missing from one source, and summation would double-count
  lines present in both databases; see `physics/03_numerical_caveats.md` §4.

- **DO NOT** apply pointwise-max to transmittance — only to absorbance — because
  `max(T_exomol, T_hitran)` selects the weaker attenuation rather than the
  stronger one, underestimating total absorption wherever both sources overlap;
  see `physics/03_numerical_caveats.md` §2 and §4.

- **DO NOT** mix LTE-intensity line tables with Treanor-weighted line selections
  in the same artifact — the ratio-scaling approach assumes I_LTE is computed at
  T_0 before the scale factor is applied; a different reference temperature makes
  the scale factor cancel the wrong Boltzmann weight and the result is physically
  meaningless; see `physics/04_nonlte_treanor.md` §5.

- **DO NOT** edit HITRAN `.data` files with any tool that shifts column positions
  — `.data` files are 160-character fixed-width records and the byte offsets in
  the companion `.header` JSON are absolute; inserting or removing even one
  character corrupts every downstream field extraction; see
  `physics/06_database_conventions.md` §5.

- **DO NOT** rename or remove public functions in `research/` without updating
  all doc cross-references in the same commit — the crosswalk docs in
  `docs/physics/` cite module.function paths by name and will silently become
  wrong otherwise; see `docs/specs/2026-04-29-theory-code-crosswalk-plan.md`
  §Task 10 Rule 2 and `docs/theory_code_map.md`.

- **DO NOT** call `hapi.db_begin` a second time inside a loop that is itself
  inside another `hapi.db_begin` session — `LOCAL_TABLE_CACHE` is process-global
  and the second call silently wipes the first session's tables; see
  `hapi_usage.md` §5.

- **DO NOT** pass pressure in atm (instead of Torr) to `cross_section_to_absorbance`
  — the conversion to Pa is inside `number_density_cm3`; converting again before
  calling the function silently scales number density by ~133, producing absorbance
  values ~133× too large; see `physics/01_absorbance_spine.md` §5.

- **DO NOT** use `hapi.select` without passing `Output=False` — the default
  `Output=True` prints the entire matched table to stdout, which is easy to
  mistake for progress reporting and produces unreadable console output during
  J-pair loops; see `hapi_usage.md` §5.

- **DO NOT** apply the Treanor module (`research/ch4_treanor.py`) to CH4
  hot-band populations outside the `(0,0,v₃,0)` ladder — other methane modes,
  combination bands, and Fermi-resonance partners are outside the scope of the
  single-mode approximation; see `physics/04_nonlte_treanor.md` §5.

---

## How to use this file

1. Before touching a threshold, default, or algorithm: search this file for the
   affected parameter name.
2. Follow the citation to the topic doc for the full physical explanation.
3. If a proposed change conflicts with a rule, document the justification in the
   commit message and update the relevant topic doc's §4 Implementation choices.
4. If a new footgun is discovered, add it here with a citation and update the
   relevant `docs/physics/` slice's §5 Footguns section in the same commit.
