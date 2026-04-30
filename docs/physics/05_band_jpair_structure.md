---
name: Band / J-pair structure — vibrational labels, ΔJ branches
maturity: draft
last-verified: 2026-04-29
see-also: [[../pipeline_map]], [[01_absorbance_spine]]
---

# Band / J-pair structure — vibrational labels, ΔJ branches

## 1. Concept summary

Each spectral line in a molecular band is characterized by two orthogonal quantum
numbers: the **vibrational** mode label (which vibrational state transition) and the
**rotational** J quantum number (which rotational level within that vibrational state).

**Vibrational labels** identify which vibrational transition a line belongs to. For the
nu3 mode of CH4, `nu3 0->1` is the fundamental band (ground state to first excited
state) and `nu3 1->2` is the first hot band (first excited to second excited). Hot bands
are weaker at 296 K but grow rapidly with temperature; they dominate the ExoMol spectrum
at combustion temperatures. The vibrational labels in this codebase use the HITRAN
quantum number notation `(v1 v2 v3 v4)`, where the nu3 quanta is the third component.

**J-pair structure** describes the rotational character of each line. A J-pair is an
ordered pair `(J_lower, J_upper)` giving the rotational quantum number of the lower
and upper energy levels. The selection rule for electric-dipole transitions restricts
`ΔJ = J_upper - J_lower ∈ {-1, 0, +1}`. These three values define the three rotational
branches: **P branch** (ΔJ = -1), **Q branch** (ΔJ = 0), and **R branch** (ΔJ = +1).
In the 4-panel PNG figures produced by this codebase, each branch occupies one subplot
and the fourth subplot overlays all branches together.

## 2. Key structure

- **Vibrational band label**: string of the form `"(0 0 0 0) -> (0 0 1 0)"` produced by
  `research.bands.format_band_label`; the nu3 quantum number is position 2 (zero-indexed)
- **J-pair**: ordered pair `(J_lower, J_upper)`, e.g. J-pair `(2, 3)` → `J 3<-2` in
  plot labels (upper J first, matching HITRAN spectroscopic notation)
- **ΔJ branches**: P (`ΔJ = -1`), Q (`ΔJ = 0`), R (`ΔJ = +1`)
- **Color convention** (PNG subplots, per CLAUDE.md "PNG Plot Convention"):
  - ΔJ = -1 (P branch): blue — `matplotlib.cm.tab10(0)`
  - ΔJ = 0 (Q branch): orange — `matplotlib.cm.tab10(1)`
  - ΔJ = +1 (R branch): green — `matplotlib.cm.tab10(2)`
- **Overlay panel color**: per-J-pair-index sweep through the `turbo` colormap via
  `research.exomol._color_for_index` / `research.hitran._color_for_index`

## 3. Code map

| Concept | Module.function | What it does (1 line) |
| --- | --- | --- |
| ExoMol J-pair grouping | `research.exomol._collect_sorted_progression_groups` | Reads sorted pure-nu3 `.txt` files, groups rows by `(J_lower, J_upper)` within each vibrational progression |
| HITRAN J-pair grouping | `research.hitran._parse_band_text_groups` | Reads MM I1 HITRAN-style band-text `.txt` files, groups rows by `(J_lower, J_upper)` within each vibrational band |
| Band label formatting | `research.bands.format_band_label` | Returns `"{lower} -> {upper}"` from cleaned quantum-number strings |
| J-pair label format | `research.exomol._format_jpair_label` (also `research.hitran`) | Returns `"J {upper_j}<-{lower_j}"` — upper J listed first |
| Per-J-pair overlay color | `research.exomol._color_for_index` / `research.hitran._color_for_index` | Maps trace index to turbo colormap hex; used in the "All ΔJ overlaid" panel |

## 4. Implementation choices and why

ΔJ is not stored on each data row; it is derived at plot time from `J_upper - J_lower`.
This keeps the stored data minimal and avoids redundancy — the pair `(J_lower, J_upper)`
already encodes everything. The computation is trivial and performed inside
`_collect_sorted_progression_groups` and `_parse_band_text_groups` when building the
`delta_j` field on each trace dict.

The color scheme is split between two rendering contexts deliberately. The three ΔJ
subplots use fixed branch colors (`_DIRECT_DELTA_J_COLORS` / `_DELTA_J_COLORS`,
backed by `tab10`) so that blue always means P, orange always means Q, and green always
means R regardless of how many J pairs are present. The overlay panel uses a per-J-pair
index color from the `turbo` colormap via `_color_for_index(index, total)`, which spreads
colors across the visible spectrum to distinguish individual J-pair traces when all
branches are plotted together.

One `.txt` file corresponds to one vibrational band export. J-pair grouping is done
entirely at plot time, not at export time, so the raw files can be re-analyzed with
different filters without re-running the HITRAN/ExoMol queries.

## 5. Footguns

- **Forced J-pair labels can appear without prominent peaks.**
  `DEFAULT_FORCED_ABSORBANCE_J_PAIRS = ((2, 3), (3, 4))` in `research/exomol.py`
  overrides the top-N label selection: J-pairs `(2, 3)` and `(3, 4)` always receive
  on-figure labels even when their peaks are not among the strongest. At low temperatures
  or narrow windows, these J pairs may have negligible absorbance, producing floating
  labels with no visible peak beneath them. To suppress this, pass an empty
  `forced_j_pairs=()` to the render function, or reduce the default in `exomol.py:55`.
  See `docs/_archive/NU3_PROGRESSIONS_WORKFLOW.md` §5 for the original description of
  this issue.

- **Branch color is context-dependent.** The `tab10`-based branch colors (blue/orange/
  green) apply only to the three dedicated ΔJ subplots. The overlay panel uses `turbo`
  per-index colors. Code that reads a trace's `"color"` field and assumes it is a branch
  color will be wrong for overlay traces — the color is a J-pair index color there.

- **`format_band_label` does not validate quantum number format.** It calls
  `clean_quanta_label` which replaces blank/whitespace with `"000"` but otherwise passes
  the string through. Malformed quantum strings (e.g. from misaligned HITRAN fixed-width
  columns) produce label strings that silently look valid in plots but do not match any
  expected band.
