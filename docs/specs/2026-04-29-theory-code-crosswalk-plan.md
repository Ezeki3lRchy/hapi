# Theory ↔ Code Crosswalk Documentation System — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:subagent-driven-development` (recommended) or `superpowers:executing-plans` to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the 10-doc crosswalk documentation system specified in `docs/specs/2026-04-28-theory-code-crosswalk-design.md`, in the order defined by spec §9, with each doc meeting the acceptance criteria in spec §11a or §11b.

**Architecture:** Three-layer documentation system (Layer A navigation, Layer B topic docs, Layer C existing docstrings). Final layout under `docs/`: 1 master index, 1 pipeline map, 1 HAPI usage doc, 6 physics slices in `docs/physics/`, 1 agent guardrails doc. See spec §4–5.

**Tech Stack:** Markdown only. No code, no test runner, no build system. Editor: VS Code with markdownlint extension; Obsidian for graph view of `[[wikilinks]]` between docs. `git` for version control. `grep`/`find` for source-material discovery in `research/` and existing `docs/`.

---

## Plan overview

| Task | Doc | Approx lines | Dependencies | Side tasks |
|---|---|---|---|---|
| 0 | (pre-flight) | — | — | mkdir physics/, _archive/ |
| 1 | `theory_code_map.md` (skeleton) | ~50 | none | — |
| 2 | `pipeline_map.md` | ~150 | Task 1 done | Archive `NU3_PROGRESSIONS_WORKFLOW.md`, `REPOSITORY_STRUCTURE.md` if overlap (spec §15 Q2/Q3) |
| 3 | `hapi_usage.md` | ~250 | Task 2 done | — |
| 4 | `physics/01_absorbance_spine.md` | ~120 | Task 3 done | SVG inventory (spec §15 Q4) |
| 5 | `physics/02_line_strength_T.md` | ~100 | Task 4 done | SVG inventory |
| 6 | `physics/03_numerical_caveats.md` | ~80 | Task 5 done | SVG inventory |
| 7 | `physics/04_nonlte_treanor.md` | ~150 | Task 6 done | Link only to `TREANOR_DISTRIBUTION_NOTES.md` (spec §15 Q1) |
| 8 | `physics/05_band_jpair_structure.md` | ~80 | Task 7 done | SVG inventory |
| 9 | `physics/06_database_conventions.md` | ~60 | Task 8 done | — |
| 10 | `physics_guardrails.md` + `CLAUDE.md` update | ~100 | Tasks 2–9 done (need source for rules) | Update `CLAUDE.md` "Key Constraints" |
| 11 | `theory_code_map.md` (full re-pass) | +100 | Task 10 done | — |
| 12 | Maturity upgrade pass (after ≥24h delay) | — | All above ≥24h old | Demote any doc whose code references no longer resolve |

**Critical invariant:** The 11 build tasks (1–11) are sequential — do not begin Task N+1 until Task N has been committed. Each task adds one durable artifact. Task 12 is a follow-up gate, not blocking.

**Maturity progression:** Every doc is committed at `maturity: draft`. Task 12 (≥24h delay) re-reads each doc with fresh eyes and graduates to `maturity: verified`. Graduation to `maturity: proven` happens organically when the doc is consulted in anger and is not part of this plan.

---

## File Structure

Files to be created or modified by this plan:

| Path | Created in task | Responsibility |
|---|---|---|
| `docs/_archive/` (directory) | Task 0 | Holds retired legacy docs from §15 Q2/Q3 |
| `docs/physics/` (directory) | Task 0 | Holds the six physics crosswalk slices |
| `docs/theory_code_map.md` | Task 1 (skeleton), 11 (re-pass) | Master index across all crosswalk docs |
| `docs/pipeline_map.md` | Task 2 | Runtime data-flow view, source → artifact |
| `docs/hapi_usage.md` | Task 3 | What HAPI does + how `research/` calls it |
| `docs/physics/01_absorbance_spine.md` | Task 4 | σ(ν), Voigt, Doppler ⊗ Lorentz, Beer-Lambert |
| `docs/physics/02_line_strength_T.md` | Task 5 | S(T), partition functions, intensity thresholds |
| `docs/physics/03_numerical_caveats.md` | Task 6 | wn_step aliasing, HAPI IntensityThreshold semantics, pointwise-max merge |
| `docs/physics/04_nonlte_treanor.md` | Task 7 | Non-LTE / Treanor — links to existing `TREANOR_DISTRIBUTION_NOTES.md` |
| `docs/physics/05_band_jpair_structure.md` | Task 8 | nu3 mode, J-pair grouping, ΔJ branches, selection rules |
| `docs/physics/06_database_conventions.md` | Task 9 | HITRAN/ExoMol column meanings, .def vs .header/.data |
| `docs/physics_guardrails.md` | Task 10 | Bullet list of agent "DO NOT" rules with citations |
| `CLAUDE.md` | Task 10 | Add 1 line under "Key Constraints" pointing to `physics_guardrails.md` |
| `docs/_archive/NU3_PROGRESSIONS_WORKFLOW.md` | Task 2 (conditional) | Archived from `docs/` if overlap is substantial |
| `docs/_archive/REPOSITORY_STRUCTURE.md` | Task 2 (conditional) | Archived from `docs/` if overlap is substantial |

---

## Task 0: Pre-flight setup

**Files:**
- Create: `docs/physics/` (directory)
- Create: `docs/_archive/` (directory)

- [ ] **Step 1: Verify spec is committed**

  Run: `git log --oneline -3 docs/specs/2026-04-28-theory-code-crosswalk-design.md`

  Expected: Shows the commit `401c53b docs: add design spec for theory ↔ code crosswalk system` (or equivalent) as the most recent commit touching the spec.

- [ ] **Step 2: Create the two new directories**

  Run: `mkdir -p docs/physics docs/_archive`

  Expected: No output. Both directories now exist.

- [ ] **Step 3: Verify directories exist**

  Run: `ls -d docs/physics docs/_archive`

  Expected:
  ```
  docs/_archive
  docs/physics
  ```

- [ ] **Step 4: No commit needed**

  Empty directories are not tracked by git. Files committed in subsequent tasks will materialize the directory structure.

---

## Task 1: `theory_code_map.md` (skeleton pass)

**Files:**
- Create: `docs/theory_code_map.md`

**Acceptance criteria (spec §11b):**
- Doc roster table lists all 10 planned crosswalk docs with `draft` maturity and `TBD` last-verified date
- Reverse lookup table is empty (filled in Task 11)
- "If you're about to..." matrix is empty (filled in Task 11)
- Frontmatter present

- [ ] **Step 1: Create the skeleton file**

  Create: `docs/theory_code_map.md` with the following exact content:

  ````markdown
  ---
  name: Theory ↔ Code Crosswalk — Master Index
  maturity: draft
  last-verified: TBD
  see-also: [[pipeline_map]], [[hapi_usage]], [[physics_guardrails]]
  ---

  # Theory ↔ Code Crosswalk — Master Index

  Master index for the theory ↔ code crosswalk documentation system.
  See `docs/specs/2026-04-28-theory-code-crosswalk-design.md` for the
  design rationale and §7 for this doc's required structure.

  ## A. Doc roster

  | Doc | Layer | Maturity | Last verified | Purpose |
  | --- | --- | --- | --- | --- |
  | `pipeline_map.md` | A | draft | TBD | Runtime data flow, source → artifact |
  | `hapi_usage.md` | B | draft | TBD | HAPI parts we use + HAPI quirks |
  | `physics/01_absorbance_spine.md` | B | draft | TBD | σ(ν), Voigt, Beer-Lambert |
  | `physics/02_line_strength_T.md` | B | draft | TBD | S(T), partition functions, intensity thresholds |
  | `physics/03_numerical_caveats.md` | B | draft | TBD | wn_step aliasing, IntensityThreshold, merge rules |
  | `physics/04_nonlte_treanor.md` | B | draft | TBD | Non-LTE / Treanor (links to existing TREANOR notes) |
  | `physics/05_band_jpair_structure.md` | B | draft | TBD | nu3 mode, J-pair grouping, ΔJ branches |
  | `physics/06_database_conventions.md` | B | draft | TBD | HITRAN/ExoMol column meanings |
  | `physics_guardrails.md` | — | draft | TBD | Agent "DO NOT" rules with citations |

  ## B. Reverse lookup

  *Filled in Task 11 of the implementation plan once topic docs exist.*

  ## C. "If you're about to..." matrix

  *Filled in Task 11 of the implementation plan once topic docs exist.*
  ````

- [ ] **Step 2: Verify file**

  Run: `wc -l docs/theory_code_map.md && head -5 docs/theory_code_map.md`

  Expected: ~30 lines; frontmatter visible.

- [ ] **Step 3: Commit**

  ```bash
  git add docs/theory_code_map.md
  git commit -m "docs: add theory_code_map.md skeleton"
  ```

---

## Task 2: `pipeline_map.md`

**Files:**
- Create: `docs/pipeline_map.md`
- Conditionally archive: `docs/NU3_PROGRESSIONS_WORKFLOW.md` → `docs/_archive/`
- Conditionally archive: `docs/REPOSITORY_STRUCTURE.md` → `docs/_archive/`

**Acceptance criteria (spec §11a):**
- All 5 template sections present
- §3 Code map cites ≥3 `research/` modules across the pipeline stages
- §5 Footguns lists ≥1 entry
- Frontmatter: `maturity: draft`, `last-verified: 2026-04-29`, `see-also: [[hapi_usage]], [[physics/03_numerical_caveats]]`
- §15 Q2 and Q3 from spec evaluated and acted on

**Source material to read first (Step 1):**
- `docs/REPOSITORY_STRUCTURE.md` (assess for retirement)
- `docs/NU3_PROGRESSIONS_WORKFLOW.md` (assess for retirement; also extract pipeline-stage info)
- `docs/framework.md` (architecture context)
- `scripts/` directory listing (enumerate the runtime entry points)
- `research/__init__.py`, `research/io.py`, `research/exomol.py`, `research/hitran.py`, `research/combined.py` (top-level docstrings)

- [ ] **Step 1: Read source material**

  ```bash
  ls scripts/
  cat docs/REPOSITORY_STRUCTURE.md
  head -100 docs/NU3_PROGRESSIONS_WORKFLOW.md
  head -50 research/__init__.py research/io.py research/exomol.py research/hitran.py research/combined.py
  ```

  Outcome: a mental map of the 5 runtime stages (Ingest → Build → Extract → Render → Plot) and which `research/` modules own each stage.

- [ ] **Step 2: Search SVG inventory (per spec §15 Q4)**

  Run:
  ```bash
  ls docs/figures/ docs/*.svg 2>/dev/null
  ```

  Outcome: list of existing SVGs (e.g. `docs/exomol_standard_workflow.svg`, `docs/hitran_standard_workflow.svg`). Identify which are pipeline diagrams and link them in §2.

- [ ] **Step 3: Write `pipeline_map.md`**

  Create: `docs/pipeline_map.md` with this skeleton (fill in author-note markers as you write):

  ````markdown
  ---
  name: Pipeline Map — Runtime Data Flow
  maturity: draft
  last-verified: 2026-04-29
  see-also: [[hapi_usage]], [[physics/03_numerical_caveats]], [[theory_code_map]]
  ---

  # Pipeline Map — Runtime Data Flow

  ## 1. Concept summary

  <author note: 1 paragraph describing the runtime data flow at a high level —
  raw HITRAN/ExoMol files enter on the left, final HTML/CSV artifacts exit on
  the right, with 5 stages in between. Name the stages: Ingest, Build,
  Extract, Render, Plot.>

  ## 2. Stage diagram + table

  <author note: ASCII diagram showing the 5 stages. If `docs/exomol_standard_workflow.svg`
  or `docs/hitran_standard_workflow.svg` covers any stage, link them here
  rather than redrawing.>

  | # | Stage | Input | Output | Owner module(s) |
  | --- | --- | --- | --- | --- |
  | 1 | Ingest | HITRAN/ExoMol web | `hitran_db/`, `exomol_db/` | `scripts/download_*.py` |
  | 2 | Build | `exomol_db/` raw | `hitran_exomolCH4_db/` HAPI tables | `scripts/build_exomol_ch4_mm_hitran_db.py` |
  | 3 | Extract | HAPI tables | band-text folders (e.g. `ch4_nu3_progressions/band_line_texts`) | `scripts/extract_*.py` |
  | 4 | Render | band texts + HAPI temp tables | absorbance arrays | `research.absorbance`, `research.combined` |
  | 5 | Plot | absorbance arrays | `artifacts/.../*.html`, `*.csv`, `*.png` | `research.exomol`, `research.hitran`, `research.combined` |

  ## 3. Code map

  | Stage | Module.function | What it does (1 line) |
  | --- | --- | --- |
  | 4 (Render) | `research.absorbance.render_cross_section_from_lines` | Sums Doppler+Lorentz Voigt profiles per line on grid |
  | 4 (Render) | `research.combined.plot_combined_pure_nu3_absorbance_progressions` | Combines ExoMol direct-Voigt + HITRAN HAPI-Voigt via pointwise max |
  | 4 (Render) | `research.combined.plot_combined_exomol_i1_absorbance_progressions` | Routes both ExoMol MM I1 and HITRAN through HAPI temp-table path |
  | 5 (Plot)  | `research.exomol._color_for_index` | Assigns one turbo-colormap color per J-pair trace |
  | 5 (Plot)  | <add at least 1 more from `research.io` / `research.spectra`> | <description> |

  ## 4. Implementation choices and why

  <author note: cover at minimum:
  - Why stages 4 and 5 are split (rendering returns Python objects; plotting
    is optional file output — per `framework.md` design rules).
  - Why the build stage (2) materializes ExoMol-into-HITRAN-style tables
    rather than computing on the fly (HAPI's data model expects table form).
  - Why scripts in `scripts/` are intentionally thin (per `framework.md`).
  - Why some scripts have wrappers around the same `research.*` function
    (e.g. `plot_combined_*` family — one for direct-Voigt, one for MM I1
    HAPI Voigt).>

  ## 5. Footguns

  - If you re-arrange stages 2 and 3, the band-text format breaks because
    Stage 3 reads HAPI table schemas from Stage 2.
  - <add at least one more footgun, e.g. Stage 4 narrow-line aliasing if
    `wn_step > 0.05`; cross-link to `physics/03_numerical_caveats.md` §2.>
  ````

- [ ] **Step 4: Verify acceptance criteria**

  ```bash
  wc -l docs/pipeline_map.md
  grep -c "^|" docs/pipeline_map.md  # should be ≥10 (table rows)
  grep -c "research\." docs/pipeline_map.md  # should be ≥3
  ```

  If §3 has fewer than 3 `research.` references, expand the code map before continuing.

- [ ] **Step 5: Evaluate overlap with `NU3_PROGRESSIONS_WORKFLOW.md` (spec §15 Q2)**

  Re-read `docs/NU3_PROGRESSIONS_WORKFLOW.md`. Decision rule: if `pipeline_map.md` covers the runtime stages and the J-pair-grouping behavior described in NU3 doc §1, §2, and §4 (i.e. if a reader getting the runtime view from `pipeline_map.md` would not lose information), the overlap is substantial.

  If substantial → proceed to Step 6.
  If not substantial → skip Step 6, leave `NU3_PROGRESSIONS_WORKFLOW.md` in place.

- [ ] **Step 6: Archive `NU3_PROGRESSIONS_WORKFLOW.md` (conditional)**

  ```bash
  git mv docs/NU3_PROGRESSIONS_WORKFLOW.md docs/_archive/NU3_PROGRESSIONS_WORKFLOW.md
  ```

  Then prepend this redirect block at the top of the archived file (use Edit tool):

  ```markdown
  > **Archived 2026-04-29.** Superseded by `docs/pipeline_map.md` for the
  > runtime view, `docs/physics/05_band_jpair_structure.md` for J-pair logic,
  > and `docs/physics/03_numerical_caveats.md` for `wn_step` / merge details.
  > Kept here for historical reference to the original Q&A-style review notes.

  ---

  ```

- [ ] **Step 7: Evaluate overlap with `REPOSITORY_STRUCTURE.md` (spec §15 Q3)**

  Decision rule: if `pipeline_map.md` (runtime view) plus `framework.md` (design view) together cover everything `REPOSITORY_STRUCTURE.md` documents, overlap is substantial.

  If substantial → Step 8.
  If not → skip.

- [ ] **Step 8: Archive `REPOSITORY_STRUCTURE.md` (conditional)**

  ```bash
  git mv docs/REPOSITORY_STRUCTURE.md docs/_archive/REPOSITORY_STRUCTURE.md
  ```

  Prepend redirect block at top of the archived file:

  ```markdown
  > **Archived 2026-04-29.** Superseded by `docs/pipeline_map.md` for runtime
  > stages and `docs/framework.md` for package design. Kept for historical
  > reference.

  ---

  ```

- [ ] **Step 9: Commit**

  ```bash
  git add docs/pipeline_map.md docs/_archive/ 2>/dev/null
  git rm --cached docs/NU3_PROGRESSIONS_WORKFLOW.md docs/REPOSITORY_STRUCTURE.md 2>/dev/null || true
  git commit -m "docs: add pipeline_map.md; archive superseded workflow + structure docs"
  ```

  (If neither legacy doc was archived, simplify: `git add docs/pipeline_map.md && git commit -m "docs: add pipeline_map.md"`.)

---

## Task 3: `hapi_usage.md`

**Files:**
- Create: `docs/hapi_usage.md`

**Acceptance criteria (spec §11a):**
- All 5 template sections present
- §3 Code map cites ≥3 `hapi.*` symbols and the `research/` callers that use them
- §5 Footguns lists ≥1 entry (the TIPS T-range constraint is the obvious first)
- Frontmatter: `maturity: draft`, `last-verified: 2026-04-29`, `see-also: [[pipeline_map]], [[physics/02_line_strength_T]], [[physics/03_numerical_caveats]]`

**Source material to read first:**
- `hapi/hapi.py` — search for the public functions listed below (do NOT read the full 54k lines; use `grep -n` to find function definitions)
- `research/absorbance.py`, `research/hitran.py`, `research/combined.py` — find every `hapi.` call site
- `CLAUDE.md` "Key Physics Concepts" and "Key Constraints" sections

- [ ] **Step 1: Enumerate HAPI surface area used by `research/`**

  ```bash
  grep -rn "import hapi\|from hapi" research/
  grep -rn "hapi\." research/ | grep -v "^research/.*:.*#" | sort -u
  ```

  Outcome: list of every HAPI function `research/` actually calls.

- [ ] **Step 2: Locate HAPI function definitions for documentation**

  For each function from Step 1, find its definition in `hapi/hapi.py`:
  ```bash
  grep -n "^def absorptionCoefficient_Voigt\|^def transmittanceSpectrum\|^def partitionSum\|^def fetch\|^def createTable\|^def select" hapi/hapi.py
  ```

  Read the surrounding ~20 lines of each definition to understand the signature and docstring (if any).

- [ ] **Step 3: Write `hapi_usage.md`**

  Create with this skeleton:

  ````markdown
  ---
  name: HAPI Usage
  maturity: draft
  last-verified: 2026-04-29
  see-also: [[pipeline_map]], [[physics/02_line_strength_T]], [[physics/03_numerical_caveats]]
  ---

  # HAPI Usage — What `research/` actually calls and why

  ## 1. Concept summary

  <author note: 1 paragraph: HAPI is the upstream HITRAN spectroscopy
  engine. We treat `hapi/hapi.py` as a black box (CLAUDE.md "Git Remotes").
  This doc is the white-box view of the parts `research/` actually uses,
  and the HAPI quirks `research/` works around.>

  ## 2. HAPI's data model

  <author note: cover:
  - The .header / .data file pair convention.
  - "Tables" in HAPI: in-memory representation, `LOCAL_TABLE_CACHE`.
  - The temp-table-per-J-pair pattern used in `research.combined` and
    `research.hitran` for absorbance rendering.
  - TIPS partition functions: 2017 / 2021 / 2025 versions, T-range 1–2500 K.>

  ## 3. Code map

  | HAPI symbol | Used by (research/ callers) | Purpose in our pipeline |
  | --- | --- | --- |
  | `hapi.fetch` | <find caller> | Download a HITRAN line list to local files |
  | `hapi.absorptionCoefficient_Voigt` | <find caller(s)> | Voigt absorption cross-section per wavenumber grid point |
  | `hapi.transmittanceSpectrum` | <find caller(s)> | Convert cross-section + concentration + path to transmittance |
  | `hapi.partitionSum` | <find caller(s)> | TIPS partition function Q(T) for line-strength T-scaling |
  | `hapi.createTable` / `hapi.select` | <find caller(s)> | SQL-like table operations on local line database |
  | <add others discovered in Step 1> | | |

  ## 4. Implementation choices and why

  <author note: cover:
  - Why `research/` uses HAPI at all rather than implementing Voigt from
    scratch (it's the upstream reference; we'd have to revalidate against
    HITRAN otherwise).
  - The bootstrap pattern: copy .header + .data files into a runtime
    folder before HAPI can use them. Cite `research.hitran.*` source.
  - The temp-table-per-J-pair pattern: for each J pair, build a one-line-
    per-row temp table, call `absorptionCoefficient_Voigt`, dispose. Why
    not call HAPI once for all J pairs together (separate progressions
    need separate filtering and labeling).
  - The dual `IntensityThreshold` choice: 0.0 for ExoMol vs. 1e-23 for
    HITRAN. Cross-link `physics/02_line_strength_T.md` §3 for the reason.>

  ## 5. Footguns

  - `hapi.partitionSum` raises silently outside 1–2500 K (TIPS coverage).
    Always validate `temperature_k` before passing.
  - HAPI's `IntensityThreshold` operates on reference-temperature intensities
    (296 K), not at run temperature. A threshold that works for HITRAN
    erases ExoMol hot bands. See `physics/02_line_strength_T.md` §3.
  - <add at least one more from your Step 1/2 reading.>
  ````

- [ ] **Step 4: Verify acceptance criteria**

  ```bash
  wc -l docs/hapi_usage.md
  grep -c "^| .hapi\." docs/hapi_usage.md  # should be ≥3 HAPI symbols in §3 table
  grep -c "^- " docs/hapi_usage.md         # should be ≥1 footgun bullet in §5
  ```

- [ ] **Step 5: Commit**

  ```bash
  git add docs/hapi_usage.md
  git commit -m "docs: add hapi_usage.md crosswalk"
  ```

---

## Task 4: `physics/01_absorbance_spine.md`

**Files:**
- Create: `docs/physics/01_absorbance_spine.md`

**Acceptance criteria (spec §11a):**
- §3 cites ≥3 `research/` symbols (suggested: `research.absorbance.render_cross_section_from_lines`, `research.absorbance.render_absorbance_on_grid`, `research.spectra.cross_section_to_absorbance`)
- §5 has ≥1 footgun
- Frontmatter: `maturity: draft`, `last-verified: 2026-04-29`, `see-also: [[../pipeline_map]], [[../hapi_usage]], [[02_line_strength_T]], [[03_numerical_caveats]]`

**Source material:**
- `docs/fundamental.md` (existing physics — pointer target for §1)
- `research/absorbance.py`
- `research/spectra.py`
- `CLAUDE.md` "Key Physics Concepts" section

- [ ] **Step 1: Read source**

  ```bash
  cat docs/fundamental.md
  cat research/absorbance.py
  cat research/spectra.py
  ```

- [ ] **Step 2: Search SVG inventory**

  ```bash
  ls docs/figures/ docs/*.svg 2>/dev/null
  ```

  Identify any SVG showing Voigt = Doppler ⊗ Lorentz, or Beer-Lambert geometry.

- [ ] **Step 3: Write `docs/physics/01_absorbance_spine.md`**

  Skeleton:

  ````markdown
  ---
  name: Absorbance spine — σ(ν), Voigt, Beer-Lambert
  maturity: draft
  last-verified: 2026-04-29
  see-also: [[../pipeline_map]], [[../hapi_usage]], [[02_line_strength_T]], [[03_numerical_caveats]]
  ---

  # Absorbance spine — σ(ν), Voigt, Beer-Lambert

  ## 1. Concept summary

  <author note: 1-2 paragraphs OR pointer. Recommended: 1 paragraph saying
  "this slice covers the line-by-line absorbance computation chain. See
  `docs/fundamental.md` §<N> for the derivation; this slice maps each step
  of that derivation to its `research/` implementation."

  Then 1 paragraph naming the chain: line center ν_i + line intensity S_i +
  Voigt profile φ(ν - ν_i) → cross-section σ(ν) = Σ_i S_i · φ(ν - ν_i)
  → absorbance A(ν) = σ(ν) · n · L (Beer-Lambert), where n is number
  density and L is path length.>

  ## 2. Key equations

  - **Cross-section**: σ(ν) = Σ_i S_i · φ_V(ν - ν_i; γ_D, γ_L)
  - **Voigt profile**: φ_V(x; γ_D, γ_L) = ∫ φ_G(x'; γ_D) · φ_L(x - x'; γ_L) dx'
    (i.e. Doppler ⊗ Lorentz convolution)
  - **Doppler width** (HWHM): γ_D(T) = (ν₀/c) · √(2 k_B T ln 2 / m)
  - **Lorentz width** (pressure-broadened, T-scaled): γ_L(P, T) = γ_L(P_ref, T_ref) · (P/P_ref) · (T_ref/T)^n
  - **Beer-Lambert**: A(ν) = σ(ν) · n · L  ;  n = P / (k_B T) for ideal gas
  - **Number density (CH4 partial)**: n_CH4 = x_CH4 · P / (k_B T)

  <SVGs to link if any from Step 2 inventory; otherwise note "Figure gap:
  Voigt = Doppler ⊗ Lorentz visualization not yet drawn" in §5.>

  ## 3. Code map

  | Concept | Module.function | What it does (1 line) |
  | --- | --- | --- |
  | σ(ν) line-by-line sum | `research.absorbance.render_cross_section_from_lines` | Iterates lines, evaluates Voigt at each, sums on grid |
  | Direct Voigt absorbance path | `research.absorbance.render_absorbance_on_grid` | Wraps cross-section + Beer-Lambert in one call |
  | σ(ν) → A(ν) conversion | `research.spectra.cross_section_to_absorbance` | Beer-Lambert: A = σ · n · L |
  | T → A (transmittance route) | `research.spectra.to_absorbance` | A = -ln(T), used after `hapi.transmittanceSpectrum` |
  | Voigt profile (HAPI path) | `hapi.absorptionCoefficient_Voigt` | HAPI's reference Voigt implementation; used by HITRAN render path |

  ## 4. Implementation choices and why

  <author note: cover:
  - Why two render paths exist: direct-Voigt (`render_cross_section_from_lines`)
    and HAPI-temp-table (via `hapi.absorptionCoefficient_Voigt`). The direct
    path is faster for short ExoMol band lists; HAPI is the validated reference.
    Cite `NU3_PROGRESSIONS_WORKFLOW.md` §4 (or `_archive/` location if archived).
  - Why Doppler and Lorentz are not exposed separately: Voigt is what you
    measure; the components are computational, not observational.
  - Why `cross_section_to_absorbance` and `to_absorbance` are separate
    functions (one for σ→A, one for T→A — they are different physical paths).>

  ## 5. Footguns

  - `cross_section_to_absorbance` requires consistent units: σ in cm²/molecule,
    n in molecules/cm³, L in cm, giving dimensionless A. Mixing Torr and atm
    inputs without converting silently breaks Beer-Lambert.
  - The "absorbance from transmittance" path (`A = -ln(T)`) only works when
    T > 0; HAPI's `transmittanceSpectrum` can produce T = 0 for very strong
    lines on coarse grids — `to_absorbance` should guard against this.
    <verify whether it does; flag if it doesn't>
  - <Figure gap, if applicable: e.g. "No diagram of Voigt = Doppler ⊗ Lorentz
    convolution exists in docs/figures/ — consider drawing">
  ````

- [ ] **Step 4: Verify acceptance criteria**

  ```bash
  wc -l docs/physics/01_absorbance_spine.md
  grep -cE "research\." docs/physics/01_absorbance_spine.md  # ≥3
  grep -cE "^- " docs/physics/01_absorbance_spine.md  # ≥1 footgun
  ```

- [ ] **Step 5: Commit**

  ```bash
  git add docs/physics/01_absorbance_spine.md
  git commit -m "docs(physics): add 01_absorbance_spine crosswalk slice"
  ```

---

## Task 5: `physics/02_line_strength_T.md`

**Files:**
- Create: `docs/physics/02_line_strength_T.md`

**Acceptance criteria (spec §11a):**
- §3 cites ≥3 symbols across `research/` and `hapi/` (suggested: `hapi.partitionSum`, `research.combined.plot_combined_exomol_i1_absorbance_progressions` (intensity_threshold parameter), one ExoMol-specific function)
- §5 has ≥1 footgun (the dual-threshold issue is the unavoidable one)
- Frontmatter: `maturity: draft`, `last-verified: 2026-04-29`, `see-also: [[01_absorbance_spine]], [[../hapi_usage]], [[03_numerical_caveats]]`

**Source material:**
- `docs/hot_band_temperature_dependence.md`
- `docs/lte_population_factorization_note.md` (newly added in your local working tree)
- `docs/transition_probability_hitran_exomol_obsidian.md`
- `research/combined.py` (focus on the `intensity_threshold` parameters)
- `CLAUDE.md` "Key Constraints" section about HAPI temperature range and intensity thresholds

- [ ] **Step 1: Read source**

  ```bash
  cat docs/hot_band_temperature_dependence.md
  cat docs/lte_population_factorization_note.md
  grep -n "intensity_threshold\|hitran_intensity_threshold" research/combined.py
  ```

- [ ] **Step 2: Search SVG inventory**

  ```bash
  ls docs/figures/ docs/*.svg 2>/dev/null | grep -i "boltzmann\|temperature\|hot.band\|partition"
  ```

  Identify Boltzmann / temperature-dependence SVGs. (Untracked files in working tree include `docs/ch4_nu3_boltzmann_hitran_process_figure.md` and SVGs.)

- [ ] **Step 3: Write file with this skeleton**

  ````markdown
  ---
  name: Line strength T-dependence — S(T), Q(T), intensity thresholds
  maturity: draft
  last-verified: 2026-04-29
  see-also: [[01_absorbance_spine]], [[../hapi_usage]], [[03_numerical_caveats]]
  ---

  # Line strength T-dependence — S(T), Q(T), intensity thresholds

  ## 1. Concept summary

  <author note: 1 paragraph + pointer. Each line in HITRAN/ExoMol has a
  reference-T intensity (HITRAN: 296 K, ExoMol: variable). At simulation
  temperature T, S(T) = S(T_ref) · [Q(T_ref)/Q(T)] · exp[-c2 E"(1/T - 1/T_ref)]
  · [1 - exp(-c2 ν/T)] / [1 - exp(-c2 ν/T_ref)]. See
  `docs/hot_band_temperature_dependence.md` for derivation.>

  ## 2. Key equations

  - **S(T) scaling**: <full equation as above>
  - **Partition function ratio**: Q(T_ref) / Q(T) — supplied by HAPI's TIPS tables
  - **Boltzmann factor**: exp[-c2 E"(1/T - 1/T_ref)] where c2 = hc/k_B
  - **Stimulated emission correction**: [1 - exp(-c2 ν/T)] / [1 - exp(-c2 ν/T_ref)]

  <link relevant SVGs from Step 2 inventory>

  ## 3. Code map

  | Concept | Module.function | What it does (1 line) |
  | --- | --- | --- |
  | Q(T) lookup | `hapi.partitionSum` | TIPS-2025 partition function, valid 1–2500 K |
  | S(T) calculation | (HAPI internal, called by `hapi.absorptionCoefficient_Voigt`) | Applied automatically when temp ≠ reference T |
  | ExoMol intensity threshold knob | `research.combined.plot_combined_exomol_i1_absorbance_progressions` (param `intensity_threshold`) | Filters ExoMol lines below threshold (default 0.0) |
  | HITRAN intensity threshold knob | same function (param `hitran_intensity_threshold`) | Filters HITRAN lines below threshold (default 1e-23) |
  | <add ExoMol-specific T handling> | `research.exomol.<func>` | <description> |

  ## 4. Implementation choices and why

  <author note: cover:
  - Why ExoMol uses `intensity_threshold=0.0` and HITRAN uses 1e-23. The
    physical reason: ExoMol exports hot-band intensities at 296 K reference
    where they look ~1e-26 cm/molecule, well below HITRAN's typical 1e-23
    cutoff. Filtering ExoMol with HITRAN's threshold erases hot bands
    entirely — they only become visible at run temperature. Cite the
    artifact comparison from `_archive/NU3_PROGRESSIONS_WORKFLOW.md` §11
    (or original location if not archived).
  - Why HAPI's TIPS T-range limits are fixed at 1–2500 K (TIPS-2025 coverage).
    Above 2500 K HAPI may error or extrapolate silently — never raise
    `temperature_k` past 2500 without re-evaluating.
  - Why ExoMol tables are pre-exported at a fixed reference T (296 K in our
    case) rather than computed at run-T (efficiency for large line lists).>

  ## 5. Footguns

  - **DO NOT** change either intensity threshold default without re-reading
    this slice §3 and §4. The defaults encode physics, not laziness.
  - **DO NOT** raise `temperature_k > 2500` — HAPI's TIPS partition functions
    are undefined and may error silently. See CLAUDE.md "Key Constraints".
  - <add one more, e.g. "ExoMol exported intensities are at the export
    reference T (typically 296 K), not at the run T — confirm before
    interpreting strength tables">
  ````

- [ ] **Step 4: Verify acceptance criteria**

  ```bash
  grep -cE "research\.|hapi\." docs/physics/02_line_strength_T.md  # ≥3
  grep -cE "^- " docs/physics/02_line_strength_T.md  # ≥1
  ```

- [ ] **Step 5: Commit**

  ```bash
  git add docs/physics/02_line_strength_T.md
  git commit -m "docs(physics): add 02_line_strength_T crosswalk slice"
  ```

---

## Task 6: `physics/03_numerical_caveats.md`

**Files:**
- Create: `docs/physics/03_numerical_caveats.md`

**Acceptance criteria (spec §11a):**
- §3 cites ≥3 symbols (suggested: grid construction in `research.spectra`, merge logic in `research.combined`, HAPI's `IntensityThreshold` parameter)
- §5 has ≥1 footgun (the wn_step aliasing example with concrete numbers from the J 2->3 experiments is the canonical one)
- Frontmatter: `maturity: draft`, `last-verified: 2026-04-29`, `see-also: [[01_absorbance_spine]], [[02_line_strength_T]], [[../hapi_usage]]`

**Source material:**
- `_archive/NU3_PROGRESSIONS_WORKFLOW.md` (or original if not archived) — §10 has the J 2->3 wn_step experiment numbers
- `research/combined.py` — the merge rule (pointwise max)
- `research/spectra.py` — grid construction

- [ ] **Step 1: Read source**

  ```bash
  # Find archived or live workflow doc
  ls docs/_archive/NU3_PROGRESSIONS_WORKFLOW.md docs/NU3_PROGRESSIONS_WORKFLOW.md 2>/dev/null
  # Read merge logic
  grep -n "merge\|pointwise\|maximum\|np.maximum" research/combined.py
  # Read grid logic
  grep -n "build_grid\|wn_step" research/spectra.py
  ```

- [ ] **Step 2: Write file with this skeleton**

  ````markdown
  ---
  name: Numerical caveats — wn_step aliasing, IntensityThreshold, merge rules
  maturity: draft
  last-verified: 2026-04-29
  see-also: [[01_absorbance_spine]], [[02_line_strength_T]], [[../hapi_usage]]
  ---

  # Numerical caveats — wn_step aliasing, IntensityThreshold, merge rules

  ## 1. Concept summary

  <author note: 1 paragraph: this slice documents the numerical-method
  pitfalls that bite without warning. Three big ones: grid sampling
  (`wn_step`), HAPI's `IntensityThreshold` semantics (already cross-linked
  in slice 02), and the pointwise-max merge rule for combined ExoMol+HITRAN.>

  ## 2. Key numerical concerns

  - **Voigt grid sampling.** Narrow lines (γ_V ~ 0.001–0.01 cm⁻¹) require
    `wn_step ≤ γ_V / 5` to capture the peak. Empirical: at `wn_step = 0.1`
    a J 2->3 peak that is 8.2e-2 at `wn_step = 0.01` collapses to 8.9e-7
    — six orders of magnitude error. (Source: archived workflow doc §10.)
  - **`IntensityThreshold`** filters reference-T intensities, not run-T —
    cross-link `[[02_line_strength_T]]` §3.
  - **Merge rule for combined sources** (`research.combined`): pointwise
    max of ExoMol and HITRAN absorbance contributions per J pair.

  ## 3. Code map

  | Concept | Module.function | What it does (1 line) |
  | --- | --- | --- |
  | Grid construction | `research.spectra.build_grid` | Constructs wavenumber grid from wn_min, wn_max, wn_step |
  | Pointwise-max merge | (within `research.combined.plot_combined_pure_nu3_absorbance_progressions`) | `np.maximum(exomol_abs, hitran_abs)` per grid point |
  | HAPI intensity filter | `hapi.absorptionCoefficient_Voigt` (param `IntensityThreshold`) | Drops lines with reference-T intensity below threshold |

  ## 4. Implementation choices and why

  <author note: cover:
  - Why pointwise-max (not sum, not weighted average) for the merge.
    Either-source-wins recovery — if one dataset misses a line, the other
    can still contribute. Sum would double-count where both sources have
    the same line.
  - Why this rule applies only to absorbance, not transmittance. Pointwise
    max of transmittance would be physically wrong (transmittance is
    multiplicative).
  - Why grids use uniform wn_step rather than adaptive sampling. HAPI
    expects uniform; refactoring to adaptive would require re-validating
    all artifacts.>

  ## 5. Footguns

  - **DO NOT** use `wn_step > 0.05` for narrow-line absorbance. At
    `wn_step = 0.1` the peak collapses by ~6 orders of magnitude. See §2.
  - **DO NOT** change the merge rule from `np.maximum` to anything else
    without justification. The rule encodes either-source-wins recovery
    for J pairs missing from one source.
  - **DO NOT** apply pointwise-max to transmittance (T) — only to
    absorbance (A). Pointwise max of T is physically wrong.
  ````

- [ ] **Step 3: Verify and commit**

  ```bash
  grep -cE "research\.|hapi\." docs/physics/03_numerical_caveats.md  # ≥3
  grep -cE "^- \*\*DO NOT\*\*" docs/physics/03_numerical_caveats.md  # ≥1
  git add docs/physics/03_numerical_caveats.md
  git commit -m "docs(physics): add 03_numerical_caveats crosswalk slice"
  ```

---

## Task 7: `physics/04_nonlte_treanor.md`

**Files:**
- Create: `docs/physics/04_nonlte_treanor.md`

**Acceptance criteria (spec §11a + §15 Q1):**
- §1 is a pointer to `docs/TREANOR_DISTRIBUTION_NOTES.md` (link only, do not absorb)
- §3 cites ≥3 symbols (must include `research/treanor*` and the non-LTE plot script if it exists)
- §5 has ≥1 footgun
- Frontmatter: `maturity: draft`, `last-verified: 2026-04-29`, `see-also: [[02_line_strength_T]], [[../pipeline_map]]`

**Source material:**
- `docs/TREANOR_DISTRIBUTION_NOTES.md` (DO NOT modify; this slice points at it)
- `docs/nonlte_absorption_realization_discussion.md`
- `docs/population_model_intuition_obsidian.md`
- `research/treanor*` (find module name with `ls research/`)
- `scripts/plot_ch4_nu3_nonlte_absorbance.py`
- `scripts/plot_ch4_nu3_treanor_populations.py`

- [ ] **Step 1: Locate source modules and scripts**

  ```bash
  ls research/treanor* research/nonlte* research/non_lte* 2>/dev/null
  ls scripts/*nonlte* scripts/*treanor* 2>/dev/null
  ```

  Note the actual module/file names — the spec assumes their existence based on commit history but the names may vary.

- [ ] **Step 2: Read source**

  ```bash
  cat docs/TREANOR_DISTRIBUTION_NOTES.md
  cat docs/nonlte_absorption_realization_discussion.md
  cat $(ls research/treanor* research/nonlte* research/non_lte* 2>/dev/null)
  ```

- [ ] **Step 3: Search SVG inventory**

  ```bash
  ls docs/figures/ docs/*.svg docs/*treanor*.md 2>/dev/null
  ```

  Likely matches in the working tree: `docs/ch4_nu3_treanor_process_figure.md`, `docs/ch4_nu3_process_diagram.svg`.

- [ ] **Step 4: Write file with this skeleton**

  ````markdown
  ---
  name: Non-LTE / Treanor distribution — code map
  maturity: draft
  last-verified: 2026-04-29
  see-also: [[02_line_strength_T]], [[../pipeline_map]]
  ---

  # Non-LTE / Treanor distribution — code map

  ## 1. Concept summary

  This slice does NOT re-derive the Treanor distribution or the non-LTE
  absorbance physics. The canonical derivation lives in
  [`docs/TREANOR_DISTRIBUTION_NOTES.md`](../TREANOR_DISTRIBUTION_NOTES.md)
  and the realization discussion in
  [`docs/nonlte_absorption_realization_discussion.md`](../nonlte_absorption_realization_discussion.md).

  This slice exists only to map the concepts in those docs to the
  `research/` and `scripts/` modules that implement them, and to flag
  the implementation choices and footguns specific to the code.

  ## 2. Key concepts (pointers)

  <author note: 4-6 bullets with name + 1-line pointer back to the
  canonical doc:>

  - **Treanor distribution**: vibrational population P_v / P_0 = exp(-v · θ_v / T_v + v(v-1) · χ_e θ_v / T_g) — see TREANOR_NOTES §<N>
  - **Two-temperature decoupling**: T_v ≠ T_g — see population_model §<N>
  - **Hot-band intensity at non-LTE**: <pointer>
  - **Vibrational-rotational coupling**: <pointer>

  <Link relevant SVG: `docs/ch4_nu3_treanor_process_figure.md`,
  `docs/ch4_nu3_process_diagram.svg` if applicable.>

  ## 3. Code map

  | Concept | Module.function | What it does (1 line) |
  | --- | --- | --- |
  | Treanor population calculation | `research.<treanor module>.<func>` | Computes P_v / P_0 from T_v, T_g, θ_v, χ_e |
  | Non-LTE intensity scaling | `research.<exomol or treanor>.<func>` | Re-weights line intensities by Treanor population ratio |
  | Validation plot | `scripts/plot_ch4_nu3_treanor_populations.py` | Plots P_v vs v at given T_v / T_g |
  | Non-LTE absorbance plot | `scripts/plot_ch4_nu3_nonlte_absorbance.py` | Renders absorbance with non-LTE intensities |

  ## 4. Implementation choices and why

  <author note: cover:
  - Why Treanor and not Boltzmann (the active research direction — populations
    deviate from LTE in the operating regime). Cross-link TREANOR_NOTES §<N>.
  - Why the `research/` Treanor module is separate from `research.absorbance`
    (separation of concerns: population model is independent of the absorbance
    chain that consumes it).
  - Why two scripts exist (population validation + absorbance application) —
    they answer different questions.>

  ## 5. Footguns

  - **DO NOT** mix LTE-style intensity tables with Treanor-weighted line
    selections in the same artifact — the result is physically meaningless.
  - **DO NOT** use Treanor populations outside the validity regime
    (anharmonicity expansion only converges for low-to-moderate v at
    moderate T_v). Cross-link TREANOR_NOTES §<N> for limits.
  - <add one more from your reading>
  ````

- [ ] **Step 5: Verify and commit**

  ```bash
  grep -cE "research\." docs/physics/04_nonlte_treanor.md  # ≥3
  grep -cE "^- \*\*DO NOT\*\*|^- " docs/physics/04_nonlte_treanor.md  # ≥1
  git add docs/physics/04_nonlte_treanor.md
  git commit -m "docs(physics): add 04_nonlte_treanor crosswalk slice"
  ```

---

## Task 8: `physics/05_band_jpair_structure.md`

**Files:**
- Create: `docs/physics/05_band_jpair_structure.md`

**Acceptance criteria:**
- §3 cites ≥3 symbols (suggested: `research.exomol._collect_sorted_progression_groups`, `research.hitran._parse_band_text_groups`, one from `research.bands`)
- §5 has ≥1 footgun
- Frontmatter: `maturity: draft`, `last-verified: 2026-04-29`, `see-also: [[../pipeline_map]], [[01_absorbance_spine]]`

- [ ] **Step 1: Read source**

  ```bash
  grep -n "_collect_sorted_progression_groups\|_parse_band_text_groups\|J_PAIR\|delta_j\|deltaJ" research/exomol.py research/hitran.py research/bands.py
  cat research/bands.py | head -100
  ```

- [ ] **Step 2: Write file**

  ````markdown
  ---
  name: Band / J-pair structure — vibrational labels, ΔJ branches
  maturity: draft
  last-verified: 2026-04-29
  see-also: [[../pipeline_map]], [[01_absorbance_spine]]
  ---

  # Band / J-pair structure — vibrational labels, ΔJ branches

  ## 1. Concept summary

  <author note: 1 paragraph: vibrational mode labels (e.g. nu3 0->1 is the
  fundamental, 1->2 is the first hot band). J-pair = (lower J, upper J);
  ΔJ = upper - lower ∈ {-1, 0, +1} for dipole-allowed transitions.
  Branch labels: P (ΔJ=-1), Q (ΔJ=0), R (ΔJ=+1).>

  ## 2. Key structure

  - **Vibrational labels**: `nu3 0->1`, `nu3 1->2`, etc.
  - **J-pair**: ordered pair `(J_lower, J_upper)`, e.g. `J 2->3`
  - **ΔJ branches**: P (`ΔJ = -1`), Q (`ΔJ = 0`), R (`ΔJ = +1`)
  - **Color convention** (from CLAUDE.md PNG section): blue=P, orange=Q, green=R

  <link any SVG showing band structure / J-pair logic if found>

  ## 3. Code map

  | Concept | Module.function | What it does (1 line) |
  | --- | --- | --- |
  | ExoMol J-pair grouping | `research.exomol._collect_sorted_progression_groups` | Groups rows by (J_lower, J_upper) within a progression |
  | HITRAN J-pair grouping | `research.hitran._parse_band_text_groups` | Same for HITRAN band-text format |
  | Band label formatting | `research.bands.format_band_label` (verify name) | Builds human-readable band label from quantum numbers |
  | Color per J-pair index | `research.exomol._color_for_index` (also in `research.hitran`) | Maps trace index to turbo colormap entry |

  ## 4. Implementation choices and why

  <author note: cover:
  - Why ΔJ branch is computed at plot time rather than stored on each row
    (it's a derived quantity from J_lower / J_upper, no need to materialize).
  - Why color is per-J-pair-index rather than per-ΔJ — the overlay panel
    shows J-pair color sweep through turbo, while the dedicated ΔJ panels
    use solid branch colors. See CLAUDE.md "PNG Plot Convention".
  - Why one .txt file = one band export, with J-pair grouping done at
    plot time only.>

  ## 5. Footguns

  - <add ≥1 footgun, e.g. "Forced J-pair labels (DEFAULT_FORCED_ABSORBANCE_J_PAIRS) override the top-N selection — labels can appear without prominent peaks. See archived NU3_PROGRESSIONS_WORKFLOW.md §5">
  ````

- [ ] **Step 3: Verify and commit**

  ```bash
  grep -cE "research\." docs/physics/05_band_jpair_structure.md  # ≥3
  grep -cE "^- " docs/physics/05_band_jpair_structure.md  # ≥1
  git add docs/physics/05_band_jpair_structure.md
  git commit -m "docs(physics): add 05_band_jpair_structure crosswalk slice"
  ```

---

## Task 9: `physics/06_database_conventions.md`

**Files:**
- Create: `docs/physics/06_database_conventions.md`

**Acceptance criteria:**
- §3 cites ≥3 symbols (load functions in `research.hitran` and `research.exomol`, plus the bootstrap pattern call)
- §5 has ≥1 footgun
- Frontmatter: `maturity: draft`, `last-verified: 2026-04-29`, `see-also: [[../hapi_usage]], [[../pipeline_map]]`

- [ ] **Step 1: Read source**

  ```bash
  cat docs/HITRAN_DATABASE_NOTES.md
  cat docs/EXOMOL_DATABASE_NOTES.md
  grep -n "load\|read\|.header\|.data\|.def" research/hitran.py research/exomol.py | head -30
  ```

- [ ] **Step 2: Write file**

  ````markdown
  ---
  name: Database conventions — HITRAN columns, ExoMol .def, fixed-width formats
  maturity: draft
  last-verified: 2026-04-29
  see-also: [[../hapi_usage]], [[../pipeline_map]]
  ---

  # Database conventions — HITRAN columns, ExoMol .def, fixed-width formats

  ## 1. Concept summary

  <author note: 1 paragraph: this slice is largely a pointer doc. HITRAN's
  160-column fixed-width format and ExoMol's .def + .states + .trans
  format are documented by the upstream organizations. This slice maps
  the most-used columns to their physical meaning and to the `research/`
  load functions that consume them. See `docs/HITRAN_DATABASE_NOTES.md`
  and `docs/EXOMOL_DATABASE_NOTES.md` for our local workflow notes.>

  ## 2. Key columns and conventions

  - **HITRAN .par columns** (most-used subset): ν (cm⁻¹), S (cm⁻¹/(molecule·cm⁻²)), γ_air, γ_self, E", n_air, δ_air, plus quantum-number strings.
  - **ExoMol .def** fields used by us: molecular mass, default Lorentz width γ_0, T-exponent n.
  - **HITRAN-style fixed-width band texts** (our derived format): exact same column layout as HITRAN .par, used for the temp-table-per-J-pair pattern (see `[[../hapi_usage]]` §2).

  ## 3. Code map

  | Concept | Module.function | What it does (1 line) |
  | --- | --- | --- |
  | HITRAN table load | `research.hitran.<load_table or similar>` | Loads .header + .data into HAPI's table cache |
  | ExoMol .def parse | `research.exomol.<parse_def or similar>` | Reads molecular mass, γ_0, n exponent |
  | HAPI bootstrap pattern | `research.hitran.<bootstrap function>` | Copies .header + .data to runtime folder for HAPI |

  ## 4. Implementation choices and why

  <author note: cover why we materialize ExoMol-as-HITRAN tables rather
  than calling ExoMol formats directly (HAPI only knows HITRAN format).>

  ## 5. Footguns

  - HITRAN .par files are fixed-width 160 chars — never edit them with
    column-shifting tools (some text editors auto-trim trailing whitespace).
  - <add ≥1 more, e.g. "ExoMol .def molecular mass is in atomic mass units, not kg">
  ````

- [ ] **Step 3: Verify and commit**

  ```bash
  grep -cE "research\." docs/physics/06_database_conventions.md  # ≥3
  grep -cE "^- " docs/physics/06_database_conventions.md  # ≥1
  git add docs/physics/06_database_conventions.md
  git commit -m "docs(physics): add 06_database_conventions crosswalk slice"
  ```

---

## Task 10: `physics_guardrails.md` + `CLAUDE.md` integration

**Files:**
- Create: `docs/physics_guardrails.md`
- Modify: `CLAUDE.md` (add 1 line under "Key Constraints")

**Acceptance criteria (spec §11b):**
- ≥10 hard rules
- Every rule cites a doc section (`physics/0*` slice, `CLAUDE.md`, `[[hapi_usage]]`, etc.)
- `CLAUDE.md` "Key Constraints" updated with pointer
- Frontmatter present

- [ ] **Step 1: Distill rules from §5 (Footguns) of all topic docs**

  Run:
  ```bash
  grep -A 1 "## 5. Footguns" docs/pipeline_map.md docs/hapi_usage.md docs/physics/0*.md | grep -E "DO NOT|don't"
  ```

  Outcome: list of footgun bullets across all 9 topic docs. The strongest 10–15 become guardrail rules.

- [ ] **Step 2: Write `physics_guardrails.md`**

  ````markdown
  ---
  name: Physics-impacting guardrails for AI agents
  maturity: draft
  last-verified: 2026-04-29
  see-also: [[theory_code_map]]
  ---

  # Physics-impacting guardrails for AI agents

  Read this file before any change to `research/`, `scripts/`, or any
  default in any plot/render function. Every rule below cites the doc
  that justifies it. Do not weaken or remove a rule without updating
  the cited doc.

  ## Hard "do not" rules

  - **DO NOT** modify `hapi/hapi.py`. Tracks upstream hitranonline/hapi.
    See `CLAUDE.md` "Git Remotes".
  - **DO NOT** change `intensity_threshold` defaults `(ExoMol=0.0,
    HITRAN=1e-23)`. Encodes hot-band reference-T physics. See
    `physics/02_line_strength_T.md` §3.
  - **DO NOT** use `wn_step > 0.05` for narrow-line absorbance. At
    step=0.1 a narrow J-pair peak collapses by ~6 orders of magnitude.
    See `physics/03_numerical_caveats.md` §2.
  - **DO NOT** raise `temperature_k` above 2500 K. TIPS-2025 partition
    functions are undefined; HAPI errors silently in some paths. See
    `CLAUDE.md` "Key Constraints" and `physics/02_line_strength_T.md` §4.
  - **DO NOT** change the merge rule in `research.combined` from
    pointwise max to anything else. Encodes either-source-wins recovery.
    See `physics/03_numerical_caveats.md` §3.
  - **DO NOT** apply pointwise-max to transmittance — only to absorbance.
    See `physics/03_numerical_caveats.md` §3.
  - **DO NOT** mix LTE intensity tables with Treanor-weighted line
    selections in the same artifact. See `physics/04_nonlte_treanor.md` §5.
  - **DO NOT** treat ExoMol exported intensities as run-T values — they
    are at the export reference T (typically 296 K). See
    `physics/02_line_strength_T.md` §5.
  - **DO NOT** edit HITRAN .par files with column-shifting tools — they
    are 160-char fixed-width. See `physics/06_database_conventions.md` §5.
  - **DO NOT** assume Treanor populations are valid outside the
    low-to-moderate v / moderate T_v regime. See
    `physics/04_nonlte_treanor.md` §5.

  ## Naming + reference rules

  - **DO NOT** rename functions in `research/` without updating
    `docs/pipeline_map.md`, `docs/hapi_usage.md`, and any
    `docs/physics/0*.md` doc that cites them, in the same commit.
    (Spec §10 Maintenance Rule 2.)

  ## Workflow rules

  - **BEFORE** any change to a default value in `scripts/*.py`, read
    `physics_guardrails.md` (this file) first, then the linked
    physics slice.
  - **BEFORE** adding a new molecule species, read `pipeline_map.md`
    stages 1–2, `hapi_usage.md` data-model section, and
    `physics/06_database_conventions.md`.
  ````

- [ ] **Step 3: Update `CLAUDE.md` with pointer**

  Use Edit tool. Find the existing "## Key Constraints" section in
  `CLAUDE.md` (around line 80–100 currently) and add this bullet at the
  top of its bullet list:

  ```markdown
  - **Physics guardrails**: Before changing any default, threshold, or
    algorithm choice in `research/` or `scripts/`, read
    `docs/physics_guardrails.md`. Every guardrail rule cites the
    `docs/physics/` slice that justifies it.
  ```

- [ ] **Step 4: Verify acceptance criteria**

  ```bash
  grep -c "^- \*\*DO NOT\*\*" docs/physics_guardrails.md  # ≥10
  grep -c "physics/0\|CLAUDE.md\|hapi_usage" docs/physics_guardrails.md  # every rule cited
  grep "Physics guardrails" CLAUDE.md  # CLAUDE.md updated
  ```

- [ ] **Step 5: Commit**

  ```bash
  git add docs/physics_guardrails.md CLAUDE.md
  git commit -m "docs: add physics_guardrails.md and link from CLAUDE.md"
  ```

---

## Task 11: `theory_code_map.md` (full re-pass)

**Files:**
- Modify: `docs/theory_code_map.md` (replace skeleton with full content)

**Acceptance criteria (spec §11b):**
- Doc roster table updated with current maturity for all 10 docs (still `draft` until Task 12 upgrades)
- Reverse lookup table covers every `research/` module that appears in any topic doc's §3
- "If you're about to..." matrix has ≥6 rows

- [ ] **Step 1: Build reverse lookup data**

  ```bash
  for doc in docs/pipeline_map.md docs/hapi_usage.md docs/physics/0*.md; do
    echo "=== $doc ==="
    grep -oE "research\.[a-zA-Z_]+(\.[a-zA-Z_]+)?" "$doc" | sort -u
  done
  ```

  Outcome: per-doc list of `research/` modules referenced. Build the inverse mapping (per-module list of docs that reference it).

- [ ] **Step 2: Replace `theory_code_map.md` content**

  Use Edit tool to replace the existing skeleton with full content. Use this template:

  ````markdown
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

  | `research/` module | Referenced by |
  | --- | --- |
  | `research.absorbance` | <fill from Step 1 output> |
  | `research.spectra` | <fill from Step 1 output> |
  | `research.combined` | <fill from Step 1 output> |
  | `research.exomol` | <fill from Step 1 output> |
  | `research.hitran` | <fill from Step 1 output> |
  | `research.bands` | <fill from Step 1 output> |
  | `research.io` | <fill from Step 1 output> |
  | `research.<treanor module>` | <fill from Step 1 output> |

  ## C. "If you're about to..." matrix

  | Task | Read first |
  | --- | --- |
  | Refactor merge logic in `research.combined` | `pipeline_map` (stages 4–5), `physics/03_numerical_caveats` |
  | Add a new molecule species | `pipeline_map` (stages 1–2), `hapi_usage` (data model), `physics/06_database_conventions` |
  | Change a default value in any `scripts/*.py` | `physics_guardrails` first, then linked slice |
  | Add a new ExoMol band-text source | `pipeline_map` (stages 2–3), `hapi_usage` (HAPI bootstrap), `physics/02_line_strength_T` |
  | Modify the Voigt rendering path | `physics/01_absorbance_spine`, `hapi_usage` (Voigt section) |
  | Touch any non-LTE / Treanor code | `physics/04_nonlte_treanor`, `TREANOR_DISTRIBUTION_NOTES.md` (canonical derivation) |
  | Change `wn_step` or grid construction | `physics/03_numerical_caveats` §2 |
  | Add a new `scripts/*.py` plotting wrapper | `pipeline_map` (stage 5), `framework.md` (script-thinness rule) |
  ````

- [ ] **Step 3: Verify acceptance criteria**

  ```bash
  grep -c "^| .research\." docs/theory_code_map.md  # ≥1 row in §B for every module
  grep -c "^| .[A-Z]" docs/theory_code_map.md  # ≥6 rows in §C
  ```

- [ ] **Step 4: Commit**

  ```bash
  git add docs/theory_code_map.md
  git commit -m "docs: fill in theory_code_map.md (reverse lookup + matrix)"
  ```

---

## Task 12: Maturity upgrade pass (after ≥24h delay)

**Trigger:** Earliest 24 hours after Task 11 commit. The fresh-eyes gate (spec §11a item 4) requires elapsed time, not just elapsed work.

**For each topic doc** (`pipeline_map.md`, `hapi_usage.md`, `physics/0*.md`):

- [ ] **Step 1: Re-read with fresh eyes**

  Read the doc end-to-end. Note any sentence that reads opaquely on second reading, any §3 entry that no longer matches current code, any §5 footgun that turned out to be wrong.

- [ ] **Step 2: Verify code references still resolve**

  For each `research.X.Y` mention in §3:
  ```bash
  grep -rn "def Y\|class Y" research/X.py
  ```
  If the symbol is missing → spec §10 Rule 1 triggered; fix the reference or demote the doc.

- [ ] **Step 3: Apply maturity upgrade**

  If §1-§2 pass without substantive issues:
  - Use Edit tool to change frontmatter `maturity: draft` → `maturity: verified`
  - Update `last-verified: 2026-04-XX` to today's date

  If issues found:
  - Fix inline
  - Keep as `maturity: draft` until next pass

- [ ] **Step 4: Update `theory_code_map.md` doc roster**

  Edit the §A table to reflect new maturity tags.

- [ ] **Step 5: Commit the upgrade pass**

  ```bash
  git add docs/pipeline_map.md docs/hapi_usage.md docs/physics/0*.md docs/theory_code_map.md
  git commit -m "docs: upgrade crosswalk docs to verified after fresh-eyes review"
  ```

---

## Self-Review (post-plan, pre-execution)

This section is the writing-plans skill's required self-review. Filled in here before handoff:

**1. Spec coverage:** Every spec section maps to plan content:
  - Spec §4 (3-layer architecture) → Plan File Structure section + per-task layer attribution
  - Spec §5 (file structure) → Task 0 + per-task file paths
  - Spec §6 (5-section template) → Per-task skeleton in Tasks 2–9
  - Spec §7 (master index) → Tasks 1 + 11
  - Spec §8 (guardrails doc) → Task 10
  - Spec §9 (build order) → Tasks 1–11 in stated order
  - Spec §10 Rule 1 (coarse references) → Task 12 Step 2 verification
  - Spec §10 Rule 2 (same-commit rename) → Task 10 guardrails rule + CLAUDE.md update
  - Spec §10 Rule 3 (quarterly review) → Not in plan; operational rule, not build task
  - Spec §11a (topic-doc lifecycle) → Per-task acceptance criteria + Task 12
  - Spec §11b (scaffolding-doc lifecycle) → Tasks 1, 10, 11 acceptance criteria
  - Spec §15 Q1 (link only to TREANOR) → Task 7
  - Spec §15 Q2 (archive NU3 doc) → Task 2 Steps 5–6
  - Spec §15 Q3 (archive REPOSITORY_STRUCTURE) → Task 2 Steps 7–8
  - Spec §15 Q4 (SVG inventory) → Per-task SVG search step in Tasks 2, 4, 5, 7

**2. Placeholder scan:** No "TBD", "TODO", "implement later", "fill in details" in the plan instructions themselves. Author-note markers (`<author note: ...>`) are intentional content describing what each section's prose should cover — they are not unfilled placeholder bugs but execution guidance for a doc-writing plan.

**3. Type consistency:** Naming consistent throughout: doc filenames match between Tasks 1 (skeleton) and 11 (re-pass); the §15 Q4 SVG search is consistently called out in physics tasks; the maturity tag values (`draft`, `verified`, `proven`) are spelled the same way everywhere; `research/` symbol names cited in plan match what spec §11a requires (≥3 per doc).

---

## Execution Handoff

Plan complete and saved to `docs/specs/2026-04-29-theory-code-crosswalk-plan.md`. Two execution options:

**1. Subagent-Driven (recommended)** — Dispatch a fresh subagent per task, review between tasks, fast iteration. Best for the doc-heavy nature of this work because each topic doc is largely independent — parallel subagent dispatch is genuinely valuable here.

**2. Inline Execution** — Execute tasks in this session using `superpowers:executing-plans`, batch execution with checkpoints. Best if you want to write the docs yourself and use Claude only for verification + commit at each task boundary.

**Which approach?**
