---
name: Database Conventions — HITRAN & ExoMol
maturity: draft
last-verified: 2026-04-29
see-also: [[HITRAN_DATABASE_NOTES]], [[EXOMOL_DATABASE_NOTES]], [[hapi_usage]], [[physics/02_line_strength_T]]
---

# Database Conventions — HITRAN & ExoMol

This slice maps the most-used HITRAN columns and ExoMol `.def` fields to the
`research/` functions that consume them. It is deliberately a pointer doc: for
full column-by-column references see `docs/HITRAN_DATABASE_NOTES.md` and
`docs/EXOMOL_DATABASE_NOTES.md`. Do not re-document column layouts here.

---

## §1 Purpose and scope

The two upstream databases use completely different storage models:

- **HITRAN** stores one ready-to-use spectral line per row (`.header` + `.data` pairs).
- **ExoMol** stores states and transitions separately, requiring reconstruction (`.states`, `.trans`, `.pf`, `.def`).

This slice covers only what the `research/` layer actually reads and what each
field feeds into. Column-by-column details live in the two dedicated notes files
linked in the frontmatter.

---

## §2 Most-used fields

### HITRAN (from `.header` / `.data`)

| Field | Physical meaning | Consumed by |
| --- | --- | --- |
| `nu` | Line-center wavenumber (cm⁻¹) | HAPI Voigt kernel; spectral-window filter |
| `sw` | Reference line intensity at 296 K (cm/molecule) | HAPI S(T) rescaling |
| `elower` | Lower-state energy (cm⁻¹) | Boltzmann factor in S(T) |
| `gamma_air` / `gamma_self` | Lorentz HWHM at 296 K, 1 atm | Voigt width calculation |
| `n_air` | Temperature exponent for air broadening | Lorentz width scaling |
| `global_upper_quanta` / `global_lower_quanta` | Vibrational band label (fixed-width text) | Band grouping in `research/hitran.py` |

Full column list with byte positions: `docs/HITRAN_DATABASE_NOTES.md`.

### ExoMol (from `.def` metadata file)

| Field | Physical meaning | Consumed by |
| --- | --- | --- |
| `mass_da` (Isotopologue mass) | Molecular mass in Daltons | Doppler width calculation |
| `nstates` (No. of states) | Number of rows expected in `.states` | Array pre-allocation in `load_state_arrays` |
| `gamma0` (Lorentz half-width) | Default pressure-broadening width (cm⁻¹/bar) | `lorentz_hwhm_cm` fallback |
| `n_exponent` (temperature exponent) | Power-law exponent for Lorentz T-scaling | Same |

Full ExoMol file structure: `docs/EXOMOL_DATABASE_NOTES.md`.

---

## §3 Code map

| Symbol | File | What it does |
| --- | --- | --- |
| `load_table(table_name)` | `research/hitran.py:57` | Reads `.header` JSON + locates `.data`; returns paths dict for HAPI ingestion |
| `load_header_json(header_path)` | `research/hitran.py:625` | Parses the HAPI-format `.header` JSON into a plain dict |
| `load_header_metadata(header_path, ...)` | `research/hitran.py:1063` | Extracts field positions and widths for fixed-width `.data` parsing |
| `parse_def_file(def_path)` | `research/exomol.py:119` | Parses `.def` lines by inline comment; extracts `mass_da`, `nstates`, `gamma0`, `n_exponent` |
| `load_partition_function(pf_path)` | `research/exomol.py:143` | Reads ExoMol `.pf` file into parallel temperature / Q(T) arrays |
| `load_state_arrays(states_path, nstates)` | `research/exomol.py:159` | Streams `.states.bz2`; fills pre-allocated energy and degeneracy arrays indexed by state ID |

---

## §4 Structural difference at a glance

```text
HITRAN row  →  nu, sw, elower, gamma_air, ...    (spectroscopy-ready)
ExoMol row  →  upper_id, lower_id, A             (reconstruction required)
              + .states energies + .pf Q(T)  →  nu0 = E_upper − E_lower
                                              →  S(T) from A, g, Q(T)
```

After this reconstruction, both pipelines converge on the same Voigt-sum →
cross-section → absorbance logic. See `physics/01_absorbance_spine.md`.

---

## §5 Footguns

1. **HITRAN `.data` files are 160-character fixed-width records — never edit
   with any tool that shifts column positions.** The byte offsets in `.header`
   are absolute. Inserting or removing even one character in the wrong column
   corrupts every downstream field extraction. Use the HAPI fetch workflow to
   regenerate; do not hand-edit.

2. **ExoMol `.def` parsing is comment-driven, not positional.** `parse_def_file`
   identifies values by matching the inline comment string (e.g. `"No. of states
   in .states file"`). If the upstream `.def` file uses a slightly different
   comment wording, the field silently goes missing and the function raises
   `RuntimeError` listing what is absent. Check the raw `.def` comment text
   before assuming a parse failure is a code bug.

3. **ExoMol broadening parameters are dataset-wide defaults, not per-line.**
   `gamma0` and `n_exponent` from `.def` apply uniformly to all lines in the
   dataset. HITRAN stores per-line `gamma_air` / `n_air`. For high-accuracy
   work, the ExoMol defaults may need per-species overrides via `--gamma0` /
   `--n-exponent` CLI flags; callers in `research/exomol.py:432–444` accept
   these as optional overrides for that reason.
