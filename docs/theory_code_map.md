---
name: Theory ↔ Code Crosswalk — Master Index
maturity: draft
last-verified: 2026-04-29
see-also: [[pipeline_map]], [[hapi_usage]], [[physics_guardrails]]
---

# Theory ↔ Code Crosswalk — Master Index

Master index for the theory ↔ code crosswalk documentation system.
See `docs/specs/2026-04-28-theory-code-crosswalk-design.md` for the
design rationale.

Read this page first. From here, navigate to the right doc via:
- **§A** — what docs exist and how mature they are
- **§B** — which crosswalk docs reference a given `research/` module
- **§C** — what to read before doing a specific task

## A. Doc roster

| Doc | Layer | Maturity | Last verified | Purpose |
| --- | --- | --- | --- | --- |
| `pipeline_map.md` | A | draft | 2026-04-29 | Runtime data flow, source → artifact |
| `hapi_usage.md` | B | draft | 2026-04-29 | HAPI parts we use + HAPI quirks |
| `physics/01_absorbance_spine.md` | B | draft | 2026-04-29 | σ(ν), Voigt, Beer-Lambert |
| `physics/02_line_strength_T.md` | B | draft | 2026-04-29 | S(T), partition functions, intensity thresholds |
| `physics/03_numerical_caveats.md` | B | draft | 2026-04-29 | wn_step aliasing, IntensityThreshold, merge rules |
| `physics/04_nonlte_treanor.md` | B | draft | 2026-04-29 | Non-LTE / Treanor (links to TREANOR notes) |
| `physics/05_band_jpair_structure.md` | B | draft | 2026-04-29 | nu3 mode, J-pair grouping, ΔJ branches |
| `physics/06_database_conventions.md` | B | draft | 2026-04-29 | HITRAN/ExoMol column meanings |
| `physics_guardrails.md` | — | draft | 2026-04-29 | Agent "DO NOT" rules with citations |
| `theory_code_map.md` (this) | A | draft | 2026-04-29 | This index |

## B. Reverse lookup

Built from §3 Code Map sections of each topic doc. Each row lists the
`research/` module (or sub-module) and every topic doc whose §3 cites it.
The `hapi.*` symbols are upstream HAPI and not listed here; see
`hapi_usage.md` for those.

| `research/` module | Referenced by |
| --- | --- |
| `research.absorbance` | `pipeline_map` (stages 4–5), `hapi_usage` §3, `physics/01_absorbance_spine` §3 |
| `research.spectra` | `physics/01_absorbance_spine` §3 (`cross_section_to_absorbance`, `to_absorbance`, `voigt_profile_cm`), `physics/03_numerical_caveats` §3 (`build_grid`) |
| `research.combined` | `pipeline_map` §3, `hapi_usage` §3 (`_render_hapi_absorbance_from_raw_lines`), `physics/02_line_strength_T` §3 (intensity threshold params), `physics/03_numerical_caveats` §3 (pointwise-max merge) |
| `research.exomol` | `pipeline_map` §3 (`_color_for_index`), `physics/02_line_strength_T` §3 (`load_partition_function`, `interpolate_partition_function`, `lte_line_intensity_cm_per_molecule`, `collect_nu3_transitions_by_jpair`), `physics/04_nonlte_treanor` §3 (`collect_nu3_transitions_by_jpair`), `physics/05_band_jpair_structure` §3 (`_collect_sorted_progression_groups`, `_color_for_index`, `_format_jpair_label`) |
| `research.hitran` | `pipeline_map` §3, `hapi_usage` §3 (multiple functions), `physics/05_band_jpair_structure` §3 (`_parse_band_text_groups`, `_color_for_index`), `physics/06_database_conventions` §3 (`load_table`, `load_header_json`, `load_header_metadata`) |
| `research.bands` | `physics/05_band_jpair_structure` §3 (`format_band_label`) |
| `research.io` | `pipeline_map` §3 (`write_rows_csv`) |
| `research.treanor` | `physics/04_nonlte_treanor` §3 (`treanor`, `treanor_minimum`) |
| `research.ch4_treanor` | `physics/04_nonlte_treanor` §3 (`treanor_nu3`, `boltzmann_nu3`, `nonlte_intensity_scale_factor`) |
| `research.nonlte` | `physics/04_nonlte_treanor` §3 (`collect_nu3_transitions_nonlte`) |

## C. "If you're about to..." matrix

| Task | Read first |
| --- | --- |
| Change `intensity_threshold` or `hitran_intensity_threshold` defaults | `physics_guardrails` (hard rules), `physics/02_line_strength_T` §3–4 |
| Refactor merge logic in `research.combined` | `pipeline_map` (stages 4–5), `physics/03_numerical_caveats` §2–4 |
| Change `wn_step` or grid construction | `physics/03_numerical_caveats` §2 (the J 2→3 benchmark), `physics/01_absorbance_spine` §2 |
| Modify the Voigt rendering path | `physics/01_absorbance_spine` §3–4 (two-path design), `hapi_usage` §3–4 |
| Add or modify ExoMol band-text source | `pipeline_map` (stages 2–3), `hapi_usage` §2–3 (bootstrap pattern), `physics/02_line_strength_T` §4 |
| Touch any non-LTE / Treanor code | `physics/04_nonlte_treanor` §3–5, `docs/TREANOR_DISTRIBUTION_NOTES.md` (canonical derivation) |
| Set `temperature_k` above current value | `physics/02_line_strength_T` §2 (TIPS range), `physics_guardrails` (2500 K hard rule) |
| Add a new molecule or database source | `pipeline_map` (stages 1–2), `hapi_usage` §2 (data model), `physics/06_database_conventions` §2–3 |
| Rename or remove a public function in `research/` | `physics_guardrails` (rename rule), then grep `docs/physics/` for the old name |
| Add a new `scripts/*.py` plotting wrapper | `pipeline_map` (stage 5), `CLAUDE.md` §Architecture (script-thinness rule) |
