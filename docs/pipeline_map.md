---
name: Pipeline Map — Runtime Data Flow
maturity: draft
last-verified: 2026-04-29
see-also: [[hapi_usage]], [[physics/03_numerical_caveats]], [[theory_code_map]]
---

# Pipeline Map — Runtime Data Flow

## 1. Concept summary

Raw HITRAN and ExoMol line-list files enter the pipeline on the left and
finished HTML plots, PNG figures, CSV J-pair tables, and Markdown reports
exit on the right. In between, the runtime passes through five sequential
stages: **Ingest** (download raw data from web sources), **Build** (reshape
ExoMol data into HAPI-compatible table form), **Extract** (pull per-band and
per-J-pair line rows into structured text files), **Render** (compute
absorbance arrays from those line rows using Voigt broadening), and **Plot**
(assemble Plotly HTML and Matplotlib PNG figures and write CSV/report
artifacts). Stages 1–3 are run once and their outputs are durable on disk.
Stages 4–5 are run on demand for each simulation case and produce the
`artifacts/` tree.

## 2. Stage diagram + table

```
┌────────────┐   ┌────────────┐   ┌────────────┐   ┌────────────┐   ┌────────────┐
│  1. Ingest │──▶│  2. Build  │──▶│ 3. Extract │──▶│  4. Render │──▶│  5. Plot   │
│  (web DL)  │   │  (tables)  │   │ (band txts)│   │ (absorbance│   │ (HTML/PNG/ │
│            │   │            │   │            │   │  arrays)   │   │  CSV)      │
└────────────┘   └────────────┘   └────────────┘   └────────────┘   └────────────┘
     │                 │                 │                 │                │
  hitran_db/      hitran_exomol      ch4_nu3_         numpy arrays    artifacts/
  exomol_db/      CH4_db/           progressions/    (in memory)     *.html *.png
                  (HAPI tables)     exomol_ch4_mm_                   *.csv report
                                    *_band_texts/
```

The two existing SVG diagrams show the per-source variant of this pipeline in
detail:

- [`docs/exomol_standard_workflow.svg`](exomol_standard_workflow.svg) — full
  ExoMol workflow from `.def` + `.trans.bz2` download through band-text
  extraction and absorbance plotting.
- [`docs/hitran_standard_workflow.svg`](hitran_standard_workflow.svg) — full
  HITRAN workflow from `hapi.fetch()` through HAPI-Voigt rendering and HTML
  output.

| # | Stage | Input | Output | Owner module(s) |
| --- | --- | --- | --- | --- |
| 1 | Ingest | HITRAN/ExoMol web APIs | `hitran_db/`, `exomol_db/` | `scripts/download_hitran_ch4.py`, `scripts/download_exomol_ch4_mm.py` |
| 2 | Build | `exomol_db/` raw `.trans.bz2` + `.def` | `hitran_exomolCH4_db/` HAPI-style tables | `scripts/build_exomol_ch4_mm_hitran_db.py` |
| 3 | Extract | HAPI tables | band-text folders (`ch4_nu3_progressions/band_line_texts`, `exomol_ch4_mm_*_band_texts/`) | `scripts/extract_ch4_nu3_band_texts.py`, `scripts/extract_exomol_ch4_mm_pure_nu3_band_texts.py` |
| 4 | Render | band-text files + HAPI temp tables | absorbance arrays (`np.ndarray`) in memory | `research.absorbance`, `research.combined` |
| 5 | Plot | absorbance arrays + J-pair metadata | `artifacts/.../*.html`, `*.png`, `*.csv`, `report.md` | `research.exomol`, `research.hitran`, `research.combined`, `research.io` |

## 3. Code map

| Stage | Module.function | What it does (1 line) |
| --- | --- | --- |
| 4 (Render) | `research.absorbance.render_cross_section_from_lines` | Sums Doppler+Lorentz Voigt profiles per line on a wavenumber grid |
| 4 (Render) | `research.absorbance.render_absorbance_on_grid` | Applies `cross_section_to_absorbance` to convert the summed cross-section to absorbance using gas-case conditions |
| 4 (Render) | `research.combined.plot_combined_pure_nu3_absorbance_progressions` | Combines ExoMol direct-Voigt + HITRAN HAPI-Voigt via pointwise maximum per J pair |
| 4 (Render) | `research.combined.plot_combined_exomol_i1_absorbance_progressions` | Routes both ExoMol MM I1 and HITRAN through HAPI temp-table path with independent intensity thresholds |
| 5 (Plot) | `research.exomol._color_for_index` | Assigns one turbo-colormap color per J-pair trace from a per-figure index |
| 5 (Plot) | `research.io.write_rows_csv` | Writes per-J-pair summary rows to a CSV file at a caller-specified path |

## 4. Implementation choices and why

**Stages 4 and 5 are separate** because the design rule in `framework.md` is
"return Python objects first; saving files should be explicit and optional."
The Render stage returns `np.ndarray` absorbance arrays and metadata
dataclasses. The Plot stage receives those objects and decides whether and
where to write HTML, PNG, CSV, and Markdown. This separation means a caller
can compute absorbance for comparison purposes without incurring any file I/O.

**Stage 2 materializes ExoMol data into HAPI-style tables** rather than
computing cross-sections directly from the raw ExoMol `.trans.bz2` files,
because HAPI's `absorptionCoefficient_Voigt()` expects its line data in the
HAPI internal-table format (`.header` + `.data` file pairs plus a bootstrapped
in-memory schema). Feeding ExoMol lines through the same path reuses the
validated HAPI Voigt engine and ensures identical broadening parameters are
applied to both data sources.

**Scripts in `scripts/` are intentionally thin.** Per `framework.md`, scripts
parse CLI arguments, build config objects (`GasCase`, `SpectralWindow`,
`DatasetPaths`), and call one or two `research.*` functions. All scientific
logic lives in `research/`. This makes the research package importable and
testable without the CLI layer.

**Two combined scripts exist for the same logical task** because they use
different ExoMol sources with different Voigt rendering paths.
`plot_combined_pure_nu3_absorbance_progressions` reads ExoMol sorted pure-nu3
band texts and uses `render_absorbance_on_grid` (a direct Voigt sum), while
`plot_combined_exomol_i1_absorbance_progressions` reads ExoMol MM I1
HITRAN-style band texts and routes them through the same HAPI temp-table path
as HITRAN. The two paths differ in how line intensities are filtered (see §5)
and in the intermediate intermediate on-disk format they expect as input.

## 5. Footguns

- **Re-ordering stages 2 and 3 breaks the band-text format.** Stage 3
  (`extract_*.py` scripts) reads line rows out of HAPI tables that were
  created in Stage 2. The band-text `.txt` files carry HITRAN-style fixed-width
  column layouts that depend on the table schema bootstrapped in Stage 2. If you
  try to run Stage 3 against the raw `exomol_db/` files directly, the column
  offsets will not match and the extract scripts will silently produce empty or
  garbled band texts.

- **Using a single `IntensityThreshold` for both ExoMol and HITRAN in the
  combined I1 path silently zeroes hot-band contributions.** ExoMol MM I1
  hot-band lines (nu3 1→2, 2→3, 3→4) have reference-temperature intensities
  around 1e-26 to 1e-25 cm/molecule. HAPI's `IntensityThreshold` filter
  operates on these reference-temperature values before any temperature
  scaling. Applying the HITRAN default threshold of 1e-23 to the ExoMol
  source removes every hot-band line before the cross-section is computed,
  producing zero absorbance even at 600 K where those bands are physically
  significant. The fix is two independent thresholds:
  `--intensity-threshold 0.0` for ExoMol and `--hitran-intensity-threshold
  1e-23` for HITRAN (the defaults in
  `research.combined.plot_combined_exomol_i1_absorbance_progressions`). See
  also [[physics/03_numerical_caveats]] §2 for the `wn_step` aliasing variant
  of this class of silent-zero error.

- **`wn_step` coarser than ~0.05 cm⁻¹ aliases narrow lines to near-zero.**
  At `wn_step = 0.1 cm⁻¹` a single narrow J-pair peak can drop by several
  orders of magnitude compared with `wn_step = 0.01 cm⁻¹` because the grid
  may not land within the Voigt HWHM of the line center. This affects both
  the HITRAN HAPI-Voigt path and the ExoMol direct-Voigt path. Cross-link:
  [[physics/03_numerical_caveats]] §2.
