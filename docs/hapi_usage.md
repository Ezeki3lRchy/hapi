---
name: HAPI Usage
maturity: draft
last-verified: 2026-04-29
see-also: [[pipeline_map]], [[physics/02_line_strength_T]], [[physics/03_numerical_caveats]]
---

# HAPI Usage — What `research/` actually calls and why

## 1. Concept summary

HAPI (`hapi/hapi.py`) is the upstream HITRAN Application Programming Interface, a single ~54 k-line
spectroscopy engine maintained at `hitranonline/hapi`. Per the repo's `CLAUDE.md` "Git Remotes"
section, that file tracks upstream and must not be modified for research work. This document is the
white-box view: which parts of HAPI `research/` actually calls, how those calls are wired together,
and the HAPI quirks that `research/` deliberately works around. Readers who want the physical
derivations behind the numbers should consult `docs/physics/01_absorbance_spine.md` (cross-section
and Beer-Lambert) and `docs/physics/02_line_strength_T.md` (temperature-dependent line strength).

## 2. HAPI's data model

**File-backed tables.** HAPI persists each line list as a pair of files: `<table>.header` (JSON
metadata: column order, format strings, default values, row count) and `<table>.data` (fixed-width
ASCII, one line per spectral line). These files live under the directory passed to `hapi.db_begin`.

**`LOCAL_TABLE_CACHE`.** When `db_begin(path)` is called it invokes `databaseBegin`, which sets a
process-global variable `VARIABLES['BACKEND_DATABASE_NAME']` to `path` and then calls `loadCache()`,
which reads every `.header` + `.data` pair in that directory into the module-level dict
`LOCAL_TABLE_CACHE`. All subsequent `createTable`, `select`, `addRowObject`, and
`absorptionCoefficient_Voigt` calls operate on this in-memory dict. Because `LOCAL_TABLE_CACHE` is
module-level global state, calling `db_begin` a second time with a different path silently replaces
the previous cache — there is no isolation between sessions.

**Temp-table-per-J-pair pattern.** `research.hitran` and `research.combined` never pass the full
line list to `absorptionCoefficient_Voigt`. Instead, for each (J_lower, J_upper) pair they:
1. Call `hapi.createTable` to create an empty table with the correct schema.
2. Parse each raw fixed-width line with `hapi.getRowObjectFromString`, then insert it with
   `hapi.addRowObject`.
3. Manually set `LOCAL_TABLE_CACHE[temp_table]["header"]["number_of_rows"]` to the actual row count
   (HAPI does not update this automatically when rows are added programmatically).
4. Call `absorptionCoefficient_Voigt` on that single-J-pair table.
5. Call `hapi.dropTable` in a `finally` block to release the in-memory table.

This pattern keeps each J-pair's absorbance trace independent so it can be colored and labeled
separately in the output plots.

**TIPS partition functions.** HAPI bundles TIPS-2011, TIPS-2017, TIPS-2021, and TIPS-2025. The
`partitionSum` function defaults to TIPS-2025. All versions cover only 1–2500 K; see §5 for the
failure mode.

## 3. Code map

| HAPI symbol | Used by (`research/` callers) | Purpose in our pipeline |
| --- | --- | --- |
| `hapi.db_begin` | `research.hitran.fetch_tables`, `research.hitran.render_absorbance`, `research.hitran._prepare_runtime_db_from_band_texts`, `research.combined` | Sets the active database directory and loads `.header`+`.data` pairs into `LOCAL_TABLE_CACHE` |
| `hapi.fetch` | `research.hitran.fetch_tables` | Downloads a HITRAN line list from HITRANonline and saves it as a `.header`+`.data` pair under the active db directory |
| `hapi.storage2cache` | `research.hitran._prepare_runtime_db_from_band_texts` | Explicitly loads a single on-disk table into `LOCAL_TABLE_CACHE` after `db_begin` |
| `hapi.select` | `research.hitran.render_absorbance` | SQL-style filter: copies rows matching quantum-label conditions from the source table into a named destination table |
| `hapi.createTable` | `research.hitran._register_source_schema_from_header`, `research.hitran._build_temp_table_from_lines` | Creates an empty in-memory table with the column schema from a RowObjectDefault list |
| `hapi.getDefaultRowObject` | `research.hitran._build_temp_table_from_lines` | Returns the RowObjectDefault (schema) of an existing table, used to create a temp table with the same schema |
| `hapi.getRowObjectFromString` | `research.hitran._build_temp_table_from_lines`, `research.combined` | Parses a single fixed-width ASCII line into a list of `(field_name, value, format)` tuples |
| `hapi.addRowObject` | `research.hitran._build_temp_table_from_lines` | Appends a parsed RowObject into an in-memory table |
| `hapi.absorptionCoefficient_Voigt` | `research.hitran.render_absorbance`, `research.hitran.plot_band_text_absorbance_progressions`, `research.combined._render_hapi_absorbance_from_raw_lines` | Computes the Voigt absorption coefficient (cm⁻¹) on a wavenumber grid; applies temperature, pressure, mole fraction, diluent, and intensity threshold |
| `hapi.transmittanceSpectrum` | `research.hitran.render_absorbance`, `research.hitran.plot_band_text_absorbance_progressions`, `research.combined._render_hapi_absorbance_from_raw_lines` | Converts absorption coefficient to transmittance using Beer-Lambert: `T = exp(-coeff * l)` |
| `hapi.dropTable` | `research.hitran` (multiple), `research.combined` | Removes an in-memory table from `LOCAL_TABLE_CACHE`; called in `finally` blocks to clean up temp tables |
| `hapi.length` | `research.hitran.render_absorbance` | Returns row count of a table; used to detect empty filtered tables before calling `absorptionCoefficient_Voigt` |
| `hapi.LOCAL_TABLE_CACHE` | `research.hitran._register_source_schema_from_header`, `research.hitran._build_temp_table_from_lines` | Accessed directly to patch in header metadata and row counts that HAPI does not set automatically |

## 4. Implementation choices and why

**Why `research/` uses HAPI at all.** HAPI is the reference implementation for HITRAN spectroscopy.
Re-implementing `absorptionCoefficient_Voigt` from scratch would require validating the result
against HITRAN's own output — using HAPI means we inherit that validation by construction. The
direct-Voigt path in `research.absorbance` (pure Python, no HAPI) exists only for ExoMol lines
where HAPI's fixed-width ASCII schema does not apply.

**The bootstrap pattern.** HAPI's `db_begin` populates `LOCAL_TABLE_CACHE` from whatever files
exist on disk at that moment. `research.hitran._prepare_runtime_db` copies the source `.header` and
`.data` files into a fresh runtime directory under `artifacts/_runtime_hitran_db/` before calling
`db_begin`. This isolation prevents the runtime temp tables from polluting the canonical
`hitran_db/` directory and ensures a clean cache state for each run.

**Why temp tables are built row-by-row rather than with `hapi.select`.** The band-text files under
`ch4_nu3_progressions/` are not full HAPI tables on disk — they are pre-filtered text files
containing only the lines for a specific vibrational band. There is no on-disk HAPI table to
`select` from. `_build_temp_table_from_lines` manufactures an in-memory HAPI table from those lines
so that `absorptionCoefficient_Voigt` can process them using its standard code path.

**Why `number_of_rows` is patched manually.** `hapi.addRowObject` appends data to the in-memory
column arrays but does not increment `header["number_of_rows"]`. HAPI reads that field to size its
internal wavenumber grid before computing the absorption coefficient. If the field is left at 0 the
function raises an error or produces an empty result. `research.hitran._build_temp_table_from_lines`
sets it explicitly after all rows are inserted.

**The dual `IntensityThreshold` choice.** `absorptionCoefficient_Voigt` is called with
`IntensityThreshold=intensity_threshold`. For HITRAN lines the default is `1e-23 cm/molec`; for
ExoMol lines the default is `0.0`. This is intentional: ExoMol hot-band reference-temperature
intensities (~1e-26 cm/molec) are well below HITRAN's typical threshold. Applying a 1e-23 threshold
to ExoMol data would silently erase most hot-band contributions. See
`docs/physics/02_line_strength_T.md` §3 for the physics behind intensity thresholds.

**`HITRAN_units=False`.** Every call to `absorptionCoefficient_Voigt` in `research/` passes
`HITRAN_units=False`. This returns the absorption coefficient in cm⁻¹ rather than cm²/molecule,
which is required for the subsequent `transmittanceSpectrum` call to produce correct transmittance
values (the HAPI docstring explicitly states this requirement).

## 5. Footguns

- **`hapi.partitionSum` is silent outside 1–2500 K.** The TIPS tables underlying `partitionSum`
  cover 1–2500 K. Temperatures outside this range do not raise a clear error — the interpolation
  silently extrapolates, producing physically wrong partition sums and therefore wrong line
  intensities. Always validate `case.temperature_k` is in [1, 2500] before calling any HAPI
  function that accepts temperature.

- **`hapi.db_begin` is process-global and not re-entrant.** Calling `db_begin` replaces
  `LOCAL_TABLE_CACHE` for the entire process. If two code paths call `db_begin` with different
  directories in an interleaved fashion (e.g. HITRAN render and ExoMol build in the same process),
  the second call wipes the first session's tables. `research/` avoids this by completing one full
  render pipeline (db_begin → build temp tables → render → dropTable) before returning control.
  Do not call `db_begin` inside a loop that is itself inside another `db_begin` session.

- **`IntensityThreshold` filters on reference-temperature (296 K) intensities, not run-temperature
  intensities.** HAPI applies the threshold to the stored `sw` column, which is the line intensity
  at the HITRAN reference temperature of 296 K. At high run temperatures (e.g. 600 K) some lines
  that are below the threshold at 296 K become significant — and some lines that are above the
  threshold at 296 K become negligible. A threshold chosen by inspecting 296 K spectra may be
  wrong at 600 K. See `docs/physics/02_line_strength_T.md` §3.

- **`hapi.select` with `Output=True` (the default) prints to stdout.** The `select` function
  defaults to `Output=True`, which prints a table of matched rows to standard output. Every call in
  `research.hitran.render_absorbance` passes `Output=False` explicitly. Omitting this flag during
  development produces large console dumps that are easy to mistake for progress reporting.

- **Temp-table name collisions across parallel calls.** The temp table name is derived from
  `source_table`, `progression_slug`, `lower_j`, and `upper_j`. If two concurrent calls share the
  same source table and J-pair, the second `dropTable` in a `finally` block will delete the first
  call's table while it is still in use. `research/` is single-threaded; do not parallelize the
  per-J-pair render loop without adding table-name uniquification (e.g. a UUID suffix).
