---
name: Line strength T-dependence — S(T), Q(T), intensity thresholds
maturity: draft
last-verified: 2026-04-29
see-also: [[01_absorbance_spine]], [[../hapi_usage]], [[03_numerical_caveats]]
---

# Line strength T-dependence — S(T), Q(T), intensity thresholds

## 1. Concept summary

Every line in a HITRAN or ExoMol database is stored with a reference-temperature
intensity S(T_ref). For HITRAN, T_ref = 296 K. For ExoMol MM I1 as exported into
our pipeline, the reference is also 296 K. At simulation temperature T, HAPI
rescales each line through the standard four-factor formula before computing
the Voigt cross-section. For the full derivation of why the population
arithmetic collapses into this formula under LTE, see
[`docs/lte_population_factorization_note.md`](../lte_population_factorization_note.md).
For the quantitative temperature dependence of hot bands and the Boltzmann
population table, see
[`docs/hot_band_temperature_dependence.md`](../hot_band_temperature_dependence.md).

The key consequence for this codebase is asymmetric: at 296 K, hot-band lines
(lower state v3 ≥ 1) have S(T_ref) values of order 1e-26 cm/molecule — ten
to a hundred times smaller than the weakest HITRAN fundamental lines. Those
same lines can be 1e-4 or stronger at 1000 K after the Boltzmann factor is
applied. A threshold set on reference-temperature intensities therefore has a
completely different physical meaning for hot-band ExoMol lines than it does
for ground-state HITRAN lines.

## 2. Key equations

**S(T) scaling** (HITRAN/HAPI standard):

```
S(T) = S(T_ref) · [Q(T_ref) / Q(T)]
                · exp[-c2 · E" · (1/T − 1/T_ref)]
                · [1 − exp(−c2 · ν0 / T)] / [1 − exp(−c2 · ν0 / T_ref)]
```

where:
- `S(T_ref)` — line intensity from database, at reference temperature (296 K)
- `Q(T)` — total internal partition function at temperature T (TIPS-2025)
- `E"` — lower-state energy in cm⁻¹
- `ν0` — line center in cm⁻¹
- `c2 = hc/k_B ≈ 1.4388 cm·K`

Each factor's physical role:

| Factor | Physical role | Effect on hot bands |
| --- | --- | --- |
| `Q(T_ref) / Q(T)` | Partition function ratio | Always ≤ 1 for T > T_ref. Population spreads across more states at high T. |
| `exp[−c2 E" (1/T − 1/T_ref)]` | Lower-state Boltzmann population | For hot bands E" ≥ 3000 cm⁻¹ — this factor grows enormously with T. |
| `[1 − exp(−c2 ν0/T)] / [1 − exp(−c2 ν0/T_ref)]` | Stimulated-emission correction | Near 1 for ν3 transitions at all relevant temperatures. Minor effect. |

**Partition function**: Q(T) is provided by HAPI's TIPS-2025 tables, valid for
1 K ≤ T ≤ 2500 K. Outside this range HAPI may raise or extrapolate silently.

**ExoMol partition function** (direct-Voigt path only): `research.exomol` loads
the ExoMol `.pf` file and linearly interpolates Q(T) via
`research.exomol.load_partition_function` + `research.exomol.interpolate_partition_function`.
The `research.exomol.lte_line_intensity_cm_per_molecule` function applies the
same four-factor scaling for ExoMol lines rendered through the direct-Voigt path.

**Intensity threshold semantics**: HAPI's `IntensityThreshold` parameter is
compared against `S(T_ref)`, the stored reference-temperature value, before any
T-scaling is applied. Lines below the threshold are dropped from the computation
permanently — the run-temperature amplification is never applied to them.

## 3. Code map

| Concept | Module.function | What it does (1 line) |
| --- | --- | --- |
| Q(T) for HITRAN/HAPI path | `hapi.partitionSum` | TIPS-2025 partition function, valid 1–2500 K; called internally by `hapi.absorptionCoefficient_Voigt` |
| S(T) rescaling (HITRAN path) | HAPI internal, invoked by `hapi.absorptionCoefficient_Voigt` | Applies the four-factor formula automatically whenever T ≠ T_ref |
| ExoMol intensity threshold knob | `research.combined.plot_combined_exomol_i1_absorbance_progressions` param `intensity_threshold` | Filters ExoMol MM I1 lines by S(T_ref); default 0.0 (no filtering) |
| HITRAN intensity threshold knob | same function, param `hitran_intensity_threshold` | Filters HITRAN lines by S(T_ref); default 1e-23 cm/molecule |
| Q(T) for ExoMol direct-Voigt path | `research.exomol.load_partition_function` + `research.exomol.interpolate_partition_function` | Load ExoMol .pf file; interpolate Q at run temperature |
| S(T) rescaling (ExoMol direct-Voigt path) | `research.exomol.lte_line_intensity_cm_per_molecule` | Applies four-factor formula to ExoMol line data using ExoMol Q(T) |
| ExoMol threshold (direct-Voigt path) | `research.exomol.collect_nu3_transitions_by_jpair` param `intensity_threshold` | Filters ExoMol lines by computed S(T); default 0.0 |

The two threshold parameters of `plot_combined_exomol_i1_absorbance_progressions`
are the most cited example of physics-encoded defaults in this codebase. Their
source values in `research/combined.py` are:

```python
intensity_threshold: float = 0.0        # line 1112 — ExoMol MM I1
hitran_intensity_threshold: float = 1.0e-23  # line 1113 — HITRAN
```

## 4. Implementation choices and why

**Why ExoMol uses `intensity_threshold = 0.0` and HITRAN uses `hitran_intensity_threshold = 1e-23`**

The defaults encode physics, not code quality preference.

ExoMol exports hot-band transitions (v3: 1→2, 2→3, 3→4) with S(T_ref) values
around 1e-26 cm/molecule at T_ref = 296 K. This is because the Boltzmann
population of v3 = 1 at 296 K is only 4.2 × 10⁻⁷ — fewer than one in a million
molecules occupies the first hot-band lower state at room temperature. The
stored intensity honestly reflects this near-zero population.

At T = 1000 K the same line has a Boltzmann factor of 1.3 × 10⁻², roughly
30 000 times larger. After HAPI's four-factor rescaling, S(1000 K) ~ 1e-22 or
stronger — fully above the HITRAN threshold. But because the threshold is
applied to S(T_ref) before T-scaling, those lines would be silently discarded
if `intensity_threshold = 1e-23` were applied to ExoMol data. The result is an
absorbance spectrum that is physically correct for the fundamental band but
completely missing every hot band, with no error message.

Setting `intensity_threshold = 0.0` for ExoMol prevents this silent erasure.
HITRAN's `hitran_intensity_threshold = 1e-23` is appropriate for HITRAN because
HITRAN's CH4 database does not include hot-band transitions at all — its weakest
lines are fundamental or combination bands that have non-negligible S(296 K).

**Why HAPI's TIPS T-range is capped at 2500 K**

TIPS-2025 (Total Internal Partition Sums, 2025 edition) tabulates Q(T) for
molecules from 1 K to 2500 K. Outside this range the HAPI implementation may
raise a runtime error or extrapolate without warning. All run configurations in
this repo use `temperature_k ≤ 2500`. See CLAUDE.md "Key Constraints" for the
enforcement note.

**Why ExoMol tables are exported at a fixed reference temperature**

ExoMol's MM I1 line list is large (~10⁸ transitions). Rather than compute LTE
intensities at run time for the entire list, the build step (Stage 2 in
[`docs/pipeline_map.md`](../pipeline_map.md)) exports lines pre-filtered and
pre-formatted into HITRAN-style band texts at T_ref = 296 K. HAPI then applies
the standard rescaling formula at render time. This means the threshold knob
operates on 296 K intensities — exactly the situation described above for hot
bands.

## 5. Footguns

- **DO NOT change `intensity_threshold` from 0.0 for ExoMol without re-reading
  §3 and §4 of this slice.** Applying any positive threshold to ExoMol hot-band
  lines filters them out at reference temperature before T-scaling can amplify
  them. The resulting spectrum appears physically valid (fundamental band is
  present) but silently erases all hot-band progressions. This rule is quoted
  verbatim in `docs/physics_guardrails.md`.

- **DO NOT change `hitran_intensity_threshold` from 1e-23 for HITRAN without
  verifying that newly included weak lines have been validated.** Lowering the
  threshold includes lines that HITRAN itself considers marginal; raising it
  may silently drop physically significant weak lines depending on the
  temperature and gas case.

- **DO NOT set `temperature_k > 2500`** — HAPI's TIPS-2025 partition functions
  are only defined on [1 K, 2500 K]. Exceeding this range may produce a silent
  wrong answer or a runtime exception. See CLAUDE.md "HAPI temperature range".

- **ExoMol exported intensities are at T_ref = 296 K, not at run temperature.**
  Do not interpret the stored S values in band-text files as the strengths you
  will observe at simulation T. The four-factor rescaling can change them by
  many orders of magnitude — upward for hot bands, downward for the fundamental
  at high T.
