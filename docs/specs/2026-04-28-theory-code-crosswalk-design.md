# Theory ↔ Code Crosswalk Documentation System

**Status:** design draft, awaiting implementation
**Date:** 2026-04-28
**Repo:** `/Volumes/T7/GitHub/hapi`
**Owner:** solo researcher (single-user repo)
**Trigger:** "I feel a little lost about the framework for this project. I packaged the whole process so I know the detail, but not fully know it and sometimes I will forget. For agent coding, they also need some doc to bound their action."

This document specifies a documentation system for the `hapi` spectroscopy research workspace. The system's primary purpose is to bridge the existing physics docs (`docs/fundamental.md`, `docs/hot_band_*.md`, etc.) with the existing implementation packages (`research/`, the way `research/` calls into `hapi/`), so that the gap between "knowing the physics" and "remembering which line of code does it" stops costing time.

This is a system *for one person* (with AI agents acting on their behalf). It deliberately strips out the team-collaboration apparatus described in current "Harness Engineering" writeups (multi-contributor knowledge repos, role-based permissions, conflict resolution) and keeps only the parts that compound for solo work: knowledge typing, maturity tracking, decay, and progressive indexing.

---

## 1. Problem statement

The repo currently has three kinds of docs that work in isolation but do not connect:

1. **Physics docs** (`docs/fundamental.md`, `docs/framework.md` (the physics framework parts), `docs/hot_band_temperature_dependence.md`, `docs/transition_probability_hitran_exomol_obsidian.md`, etc.) — these describe physics concepts and equations.
2. **Architecture docs** (`docs/framework.md` package-design portion, `docs/REPOSITORY_STRUCTURE.md`) — these describe Python module responsibilities.
3. **Workflow / behavior docs** (`docs/NU3_PROGRESSIONS_WORKFLOW.md`, `docs/EXOMOL_DATABASE_NOTES.md`, `docs/HITRAN_DATABASE_NOTES.md`) — these describe what specific scripts do.

What is missing:

- **Bidirectional crosswalk between physics and code.** "Where does Voigt get implemented?" requires `grep`. "Why does this function take an `n_exponent` argument?" requires reading multiple files.
- **Top-down runtime view.** No single page shows the data flow from raw HITRAN/ExoMol files to final HTML/CSV artifacts. The 41 scripts in `scripts/` provide many entry points but no single map.
- **HAPI usage map.** `hapi/hapi.py` is treated as a black box (per `CLAUDE.md`'s "do not modify" rule), but the user does not yet have a focused doc that explains the parts of HAPI `research/` actually relies on, and the HAPI quirks `research/` works around.
- **Agent-facing physics guardrails.** `CLAUDE.md` has a "Key Constraints" section, but the constraints are buried among other content and do not cite specific physics docs justifying each rule. Agents asked to refactor freely change physics-driven defaults because nothing tells them not to.

The cost of these gaps is concrete:

- The user re-derives implementation choices (e.g. why `intensity_threshold` defaults differ between ExoMol and HITRAN) when revisiting the codebase after weeks away.
- Agents asked to clean up `research/` propose changes that are physically meaningful (not stylistic) and the user has to catch them in review.
- The "framework feeling lost" is structural, not knowledge-shortage: the knowledge exists across docs and source, but is not indexed in a way that allows fast lookup.

## 2. Goals

**Primary goals (must be achieved by the system).**

1. *Physics → code lookup.* Any concept named in a physics doc can be traced to its implementing function in `research/` or `hapi/` in under a minute, without grep.
2. *Code → physics lookup.* Any function in `research/` can be traced to the physics concept it implements and the equation it computes, without leaving `docs/`.
3. *Pipeline visibility.* The full runtime data flow from raw HITRAN/ExoMol input to plotted output is visible on a single page.
4. *Agent guardrails.* An agent reading `physics_guardrails.md` can identify which `research/` defaults encode physics (and must not be casually changed) versus which are stylistic (and can be).

**Secondary goals (the system should naturally serve these but they are not gating).**

1. *Memory aid.* The system slows the rate at which the user forgets their own implementation choices.
2. *Agent context efficiency.* An agent asked about "non-LTE" should be able to load only the relevant ~150-line slice doc, not the full physics literature.

## 3. Non-goals

The system explicitly does NOT do these things, even though related needs exist:

- *Re-derive physics.* All physics derivations remain in the existing physics docs. Crosswalk docs link to them and do not duplicate.
- *Re-document `hapi/hapi.py` line-by-line.* `hapi/hapi.py` is ~54k lines and tracks upstream. The HAPI usage doc covers what `research/` calls plus the HAPI gotchas that bite, not the full module.
- *Per-script docs.* Scripts in `scripts/` are intentionally thin wrappers (per `docs/framework.md` design rules). Per-script documentation would duplicate `research/` docs and would rot when scripts move.
- *Replace HITRAN / ExoMol official documentation.* The database conventions slice links to the canonical sources; it does not republish them.
- *Build a team-collaboration knowledge system.* No multi-user roles, no contribution log, no conflict resolution. This repo has one author.

## 4. System overview — three-layer architecture

```text
┌────────────────────────────────────────────────────────────────────┐
│ Layer A — NAVIGATION                                                │
│   docs/pipeline_map.md          "where am I in the system?"        │
│   docs/theory_code_map.md       "what doc should I read?"          │
├────────────────────────────────────────────────────────────────────┤
│ Layer B — TOPIC DOCS                                                │
│   docs/hapi_usage.md            "what HAPI does + how we use it"   │
│   docs/physics/01-06_*.md       "physics concept ↔ code mapping"   │
├────────────────────────────────────────────────────────────────────┤
│ Layer C — CODE ANNOTATIONS (existing, not new)                      │
│   research/*.py docstrings      "what this function does"          │
└────────────────────────────────────────────────────────────────────┘

Plus one cross-cutting agent-facing doc:
   docs/physics_guardrails.md     "DO NOT change X because Y"
```

The three-layer structure mirrors the article's "three-tier progressive index" (catalog → topic clusters → entries), scaled for solo use:

- **Layer A** is the catalog: small docs that fit in a single screen, optimized for navigation, loaded by the user (or agent) first.
- **Layer B** is the topic cluster: focused docs that fit in 100–300 lines each, loaded only when the topic is in scope.
- **Layer C** is already implemented as docstrings + source code. The new system does not regenerate Layer C; it indexes into it.

## 5. File structure

Final layout under `docs/`:

```text
docs/
├── theory_code_map.md           ← master index (Layer A)
├── pipeline_map.md              ← runtime data flow (Layer A)
├── hapi_usage.md                ← HAPI usage (Layer B)
├── physics/                     ← physics crosswalk docs (Layer B)
│   ├── 01_absorbance_spine.md
│   ├── 02_line_strength_T.md
│   ├── 03_numerical_caveats.md
│   ├── 04_nonlte_treanor.md
│   ├── 05_band_jpair_structure.md
│   └── 06_database_conventions.md
└── physics_guardrails.md        ← agent-facing rules
```

**Naming conventions:**

- All lowercase with underscores. Matches the dominant pattern in current `docs/` (`hot_band_temperature_dependence.md`, `lte_population_factorization_note.md`, etc.).
- Topic docs in `physics/` carry numeric prefixes (`01_`, `02_`, ...) for sort order; the prefix corresponds to build order, not importance ranking.
- Cross-cutting / master docs (`theory_code_map.md`, `pipeline_map.md`, `hapi_usage.md`, `physics_guardrails.md`) have no numeric prefix.
- The agent-facing rules doc is named `physics_guardrails.md` rather than `AGENTS_PHYSICS_GUARDRAILS.md` to avoid visual collision with the existing 7× `AGENTS.md` files (`AGENTS.md`, `hapi/AGENTS.md`, etc.) and to match the lowercase style of `docs/`.

## 6. Per-doc template

Every **topic doc** — `pipeline_map.md`, `hapi_usage.md`, and the six `physics/0*_*.md` slices — must conform to the following 5-section structure. The shape is uniform so that a reader (human or agent) always knows where to find what.

The two **scaffolding docs** (`theory_code_map.md` and `physics_guardrails.md`) do *not* use this template; their structures are defined in §7 and §8 respectively. They are intentionally different shapes (an index of indices, and a flat list of rules) because their jobs are navigation and constraint-stating, not content delivery.

```markdown
# <Title>

> **Maturity:** draft | verified | proven
> **Last verified:** YYYY-MM-DD
> **See also:** [[other_doc]], [[other_doc]]

## 1. Concept summary (or pointer)

<For physics docs: 1–3 paragraphs describing the concept. If a derivation
already exists elsewhere in docs/, write 1 paragraph here that says
"this slice covers <X>; see <existing doc> for derivation" and proceed.>

<For pipeline_map.md: 1 paragraph describing the runtime data flow at a
high level.>

<For hapi_usage.md: 1 paragraph describing HAPI's role in the system.>

## 2. Key equations / data model / diagram

<For physics docs: LaTeX equations or links to existing SVGs in
docs/figures/ and docs/*.svg. The author MUST search the existing
SVG inventory and link relevant figures rather than duplicating or
omitting them (per §15 Q4). When a figure that would help does not
yet exist, flag it in §5 (Footguns) as a "Figure gap" — do not block
slice completion on figure creation.>

<For pipeline_map.md: stage diagram (ASCII or SVG link) + stage table.>

<For hapi_usage.md: HAPI's data model — what is a "table", what is a
.header/.data pair, what is the in-memory representation.>

## 3. Code map

<Required table mapping the formal content from §2 to specific code
locations in research/ (and hapi/ where applicable). Format:>

| Concept / step / construct | Module.function | What it does (1 line) |
| --- | --- | --- |
| <example> | research.absorbance.render_cross_section_from_lines | Sums Voigt profiles per line on grid |

## 4. Implementation choices and why

<Narrative section, agent-facing. Justifies non-obvious defaults, flags
physics-driven constants, calls out implementation choices that look
arbitrary but encode physical or numerical constraints.>

<Example: "intensity_threshold defaults to 0.0 for ExoMol because
hot-band reference-T intensities (~1e-26 cm/molecule) fall below HITRAN's
typical 1e-23 threshold. Filtering ExoMol with HITRAN's threshold erases
hot bands entirely.">

## 5. Footguns

<Bullet list. Each bullet is a 'if you change X, Y will break, because Z'
statement. These bullets are the source material for physics_guardrails.md.>

- <example> If you raise wn_step above 0.05 for narrow J-pair features,
  the peak height drops by orders of magnitude due to grid aliasing
  (verified at wn_step=0.1 in artifacts/.../step0p1_nu3_0to1).
```

**Template enforcement rules:**

- All five sections must be present in every doc, in the listed order.
- A section may contain only a pointer to another doc (e.g. §1 may say "see `docs/fundamental.md` §3 for derivation"), but the section header must be present so that internal anchors (`#1-concept-summary`) work consistently.
- The maturity, last-verified date, and see-also fields in the frontmatter quote-block are required.
- §3 (Code map) must cite at least three concrete `research/` (or `hapi/`) symbols. A doc with fewer than three code-map entries is not yet `verified` (see §11).

## 7. Master index design — `theory_code_map.md`

The master index is the single page a user (or agent) reads first. Target size: ~150 lines.

**Required subsections:**

### A. Doc roster

A table listing every Layer A and Layer B doc, with current state. Format:

| Doc | Layer | Maturity | Last verified | 1-line purpose |
| --- | --- | --- | --- | --- |
| `pipeline_map.md` | A | proven | 2026-04-28 | Runtime data flow, source → artifact |
| `hapi_usage.md` | B | verified | 2026-04-28 | HAPI parts we use + HAPI quirks |
| `physics/01_absorbance_spine.md` | B | proven | 2026-04-28 | σ(ν), Voigt, Beer-Lambert |
| ... | | | | |

### B. Reverse lookup

A table indexed by `research/` module, listing the crosswalk docs that reference it. Lets the user start from "I'm in `research.combined`" and get a 3-doc reading list without scanning every crosswalk doc. Format:

| `research/` module | Referenced by |
| --- | --- |
| `research.absorbance` | `physics/01`, `physics/03`, `pipeline_map` (stage 4) |
| `research.combined` | `pipeline_map` (stages 3–5), `physics/03`, `physics/02` |
| ... | ... |

### C. "If you're about to..." matrix

Approximately 6–10 task-shaped rows, each pointing to the docs that should be read first. Format:

| If you're about to... | Read first |
| --- | --- |
| Refactor merge logic in `research.combined` | `pipeline_map` (stages 3–5), `physics/03_numerical_caveats` |
| Add a new molecule species to the workflow | `pipeline_map` (stages 1–2), `hapi_usage` (table model), `physics/06_database_conventions` |
| Change a default value in any `scripts/*.py` | `physics_guardrails.md` first, then linked slice |
| Add a new ExoMol band-text source | `pipeline_map` (stages 2–3), `hapi_usage` (HAPI bootstrap pattern), `physics/02_line_strength_T` |
| ... | ... |

The "if you're about to..." matrix is the most actionable section. It is what an agent should consult before any non-trivial change.

## 8. Guardrails doc design — `physics_guardrails.md`

Target size: ~100 lines. Format: bullet list of 10–15 hard rules in the form `DO NOT <action> — <consequence>; see <doc § anchor>`.

**Sample content (final wording assigned during build phase):**

```markdown
# Physics-impacting guardrails for AI agents

Read this file before any change to `research/`, `scripts/`, or any
default in any plot/render function. Every rule below cites the doc
that justifies it. Do not weaken or remove a rule without updating
the cited doc.

## Hard "do not" rules

- DO NOT modify `hapi/hapi.py`. Tracks upstream hitranonline/hapi.
  See `CLAUDE.md` §"Git Remotes".
- DO NOT change `intensity_threshold` defaults `(ExoMol=0.0,
  HITRAN=1e-23)`. Encodes hot-band reference-T physics; ExoMol
  hot-band lines have intensities ~1e-26 at 296 K which would be
  filtered by HITRAN's threshold. See `physics/02_line_strength_T.md` §3.
- DO NOT use `wn_step > 0.05` for narrow-line absorbance.
  At step=0.1 a J 2->3 peak that is 8.2e-2 at step=0.01 collapses to
  8.9e-7 — six orders of magnitude error. See
  `physics/03_numerical_caveats.md` §2.
- DO NOT raise `temperature_k` above 2500 K. TIPS2025 partition
  functions are undefined above this; HAPI errors silently in some
  paths. See `CLAUDE.md` §"Key Constraints" and
  `physics/02_line_strength_T.md` §4.
- DO NOT change the merge rule in `research.combined` from pointwise
  max to anything else without justification. The merge rule encodes
  "either-source-wins" recovery for J-pairs missing from one source.
  See `physics/03_numerical_caveats.md` §3 and
  `docs/NU3_PROGRESSIONS_WORKFLOW.md` §11.
- ... (10–15 such rules total)

## Naming + reference rules

- DO NOT rename functions in `research/` without updating
  `pipeline_map.md`, `hapi_usage.md`, and any `physics/` doc that
  cites them, in the same commit.
```

**Integration with `CLAUDE.md`:** Add a single new line under `CLAUDE.md` "Key Constraints" pointing agents at `physics_guardrails.md` before any physics-impacting change. Example:

```markdown
- **Physics guardrails**: Before changing any default, threshold, or
  algorithm choice in research/ or scripts/, read
  docs/physics_guardrails.md.
```

## 9. Build order with rationale

Build the system in this exact order. Each numbered item must be complete (all 5 template sections filled, see §11) before the next begins. The order is chosen to maximize navigational return per line written.

| # | Doc | Why this position |
| --- | --- | --- |
| 1 | `theory_code_map.md` (skeleton only) | Reserve the index spot. List all empty children with `draft` maturity and "TBD" last-verified date. Skeleton only; the full reverse lookup and "if you're about to..." matrix are filled in the re-pass at step 11. |
| 2 | `pipeline_map.md` | Smallest doc, highest navigational return. Once the user can see the whole flow on one page, the "lost" feeling drops fastest. This doc also defines vocabulary (stage names) used throughout the rest of the system. **Side-task during this step:** evaluate overlap with `docs/NU3_PROGRESSIONS_WORKFLOW.md` and `docs/REPOSITORY_STRUCTURE.md`; if substantial, archive each to `docs/_archive/` with a redirect line at the top (per §15 decisions Q2 and Q3). |
| 3 | `hapi_usage.md` | The pipeline already shows where HAPI is called; now document what HAPI does at each call site. Order matters: writing HAPI doc before pipeline doc means choosing between describing HAPI's full surface area vs. only what's used — the pipeline doc's stage list answers that question. |
| 4 | `physics/01_absorbance_spine.md` | The spine. Every other physics slice references `σ(ν) = Σ S_i φ(ν)`, Voigt = Doppler ⊗ Lorentz, and Beer-Lambert. Build it first so subsequent slices can link to it instead of restating it. |
| 5 | `physics/02_line_strength_T.md` | Where most "physically meaningful defaults" in `research/` live. High value because it explains the documented `intensity_threshold` choice and the 296 K reference temperature. |
| 6 | `physics/03_numerical_caveats.md` | Highest consultation rate of all six physics slices. The `wn_step` aliasing, `IntensityThreshold` semantics, pointwise-max merge rule are exactly the things the user forgets first and an agent gets wrong first. |
| 7 | `physics/04_nonlte_treanor.md` | Active research direction (recent commits show iterative work on Treanor populations and non-LTE intensity integration). Write while the derivations are still fresh in the user's head; the cost of forgetting this slice is highest. |
| 8 | `physics/05_band_jpair_structure.md` | Mostly lookup. The J-pair logic is so structural in the code that the code itself is largely self-documenting, so this slice is shorter and lower-priority. |
| 9 | `physics/06_database_conventions.md` | Mostly lookup. HITRAN and ExoMol maintain canonical docs; this slice is mostly links + a small "what each column means in our context" summary. |
| 10 | `physics_guardrails.md` | Distilled from the §5 (Footguns) sections of #2–9. Cannot be written until the source slices exist. |
| 11 | `theory_code_map.md` (full re-pass) | Now has real children. Fill in the doc roster with maturity tags, the reverse lookup, and the "if you're about to..." matrix. |

**Rough effort estimate:** 4–6 focused writing sessions for the full first pass. `pipeline_map.md` and `hapi_usage.md` are the largest single docs (~150 + ~250 lines respectively). The six physics slices average ~100 lines each.

## 10. Maintenance discipline

Three rules. Each is short enough to remember, narrow enough to enforce.

**Rule 1 — Coarse references over fine.** When citing code in §3 (Code map) or §4 (Implementation choices), use the coarsest reference that disambiguates:

- ✓ `research.combined`
- ✓ `research.combined.plot_combined_pure_nu3_absorbance_progressions` (when needed for clarity)
- ✗ `research/combined.py:line 234`

Line numbers rot fastest. Function names rot more slowly. Module names rot the slowest.

**Rule 2 — Same-commit rename rule.** Any rename of a function or module in `research/` requires a search-and-replace across `docs/pipeline_map.md`, `docs/hapi_usage.md`, and all `docs/physics/*.md` *in the same commit* as the rename. This rule lives in both `CLAUDE.md` (so the user remembers it) and `physics_guardrails.md` (so agents enforce it).

**Rule 3 — Quarterly maturity review.** Every 3 months (or at the start of any major refactor), scan all crosswalk docs:

- For each doc, confirm at least one §3 (Code map) reference still resolves in current source. If not → demote to `draft`.
- For each doc, confirm the last-verified date is within the last 6 months. If not → demote one rung (`proven` → `verified`, `verified` → `draft`).
- For each `proven` doc not consulted in the last 12 months → demote to `verified`.

This implements the article's "decay" concept on a solo-friendly cadence. The decay is manual rather than automatic because (a) tooling for automatic decay is not currently in this repo, and (b) for one author the manual pass is fast (~30 minutes for 10 docs).

## 11. Acceptance criteria — per-doc lifecycle

Each doc carries one of three maturity tags in its frontmatter: `draft` → `verified` → `proven`. Criteria differ slightly between topic docs (5-section template, see §6) and scaffolding docs (`theory_code_map.md`, `physics_guardrails.md`).

### 11a. Topic docs (`pipeline_map.md`, `hapi_usage.md`, `physics/0*_*.md`)

**Graduates from `draft` to `verified` when all four gates pass:**

1. All 5 template sections are present and non-empty (or contain a deliberate "see X" pointer with reasoning).
2. §3 Code map cites at least 3 concrete symbols in `research/` (or `hapi/` for the HAPI doc).
3. §5 Footguns lists at least 1 entry (zero footguns suggests the doc has not yet been written from real-use experience).
4. The author has re-read the doc once after a delay of at least 24 hours since first writing (the "fresh eyes" check). This catches sentences that read clearly while writing but become opaque when re-read.

**Graduates from `verified` to `proven` when:**

- It has been *consulted in anger* at least once. "In anger" means: the user used it before a real refactor, the user pointed an agent at it as constraint context, or the user re-read it because they'd actually forgotten the concept and the doc successfully reminded them. Reading a doc to proofread it does not count.

**Demotes downward via:**

- The Rule 3 quarterly review (see §10).
- A discovered §3 Code map entry that no longer resolves in current source.
- A footgun in §5 that turns out to be wrong (was based on a misunderstanding) — demote and rewrite.

### 11b. Scaffolding docs (`theory_code_map.md`, `physics_guardrails.md`)

These do not have §3 / §5 sections, so their gates are different.

**`theory_code_map.md` graduates from `draft` to `verified` when:**

- Doc roster table (§A) lists every existing topic doc with its current maturity tag.
- Reverse lookup table (§B) covers every `research/` module that appears in any topic doc's §3 Code map.
- "If you're about to..." matrix (§C) has at least 6 task rows.

It graduates to `proven` when the user has used the matrix at least once to navigate to a relevant doc before starting work (i.e. the index has earned its keep navigationally).

**`physics_guardrails.md` graduates from `draft` to `verified` when:**

- Lists at least 10 hard rules.
- Every rule cites a specific doc section as justification (typically a `physics/0*` slice or `CLAUDE.md` "Key Constraints"; external sources like HITRAN/ExoMol official docs are also acceptable when the constraint comes from upstream).
- `CLAUDE.md` "Key Constraints" section has been updated to point agents at this file.

It graduates to `proven` when an agent has been observed (via session transcript) following a rule it would otherwise have violated — i.e. the guardrails have prevented at least one real mistake.

## 12. Risks and mitigations

| Risk | Mitigation |
| --- | --- |
| Write-only doom: the system gets started, never gets finished, and partial docs mislead more than no docs | Lean variant α (10 docs, ~1270 lines total) chosen specifically to fit a 4–6 session budget. Numeric prefixes (`01_`, `02_`...) give visible progress. Build order front-loads the highest-leverage docs (`pipeline_map.md` first) so even a half-finished system has value. |
| Doc-vs-code rot: code changes, references silently become wrong | Maintenance Rule 1 (coarse references) reduces rot rate. Rule 2 (same-commit rename) catches rot at the source. Rule 3 (quarterly review) catches what slips through. |
| Agent ignores `physics_guardrails.md` | Add explicit pointer in `CLAUDE.md` "Key Constraints". Each guardrail rule cites the long-form doc, so an agent that follows the link gets the reasoning, not just the rule. |
| Template too rigid for some content (e.g. database conventions has no equations) | Template explicitly allows "pointer-only" sections. §2 of `physics/06_database_conventions.md` will be 1 sentence + a link to HITRAN/ExoMol official docs. |
| Slice (iv) Non-LTE / Treanor depends on actively-evolving research | This is why slice (iv) is built early (build order #7, before the lower-priority slices) — write while the derivations are fresh, demote to `draft` if research direction changes. |
| The Obsidian vault in `docs/` may interact unexpectedly with new subfolder `docs/physics/` | Obsidian supports nested folders natively. The `[[wikilink]]` syntax used in template frontmatter works across folders. |

## 13. Mapping to "Harness Engineering" article concepts

The article that motivated this discussion describes a team-oriented knowledge architecture with five storage layers, five knowledge types, three maturity levels, and decay mechanisms. This system uses those ideas selectively. What was kept and what was dropped:

| Article concept | Kept? | How it appears in this system |
| --- | --- | --- |
| Layer 0-P (personal preferences) | Kept implicitly | Lives in the user's `~/.claude/CLAUDE.md`, outside this repo. |
| Layer 0-T (team conventions) | Adapted | Becomes `CLAUDE.md` and the existing `AGENTS.md` chain. Not duplicated by this system. |
| Layer 1 (cross-project tech knowledge) | Deferred | If a future repo of the user's needs to share knowledge with this one, the relevant slices can be lifted out. Not designed for now. |
| Layer 2 (domain/biz knowledge) | Kept and adapted | This is what `docs/physics/*.md` and `docs/fundamental.md` cover. |
| Layer 3 (project-specific knowledge) | Kept | This is what `pipeline_map.md` and `hapi_usage.md` cover. |
| Five knowledge types (model/decision/guideline/pitfall/process) | Kept implicitly | Each topic doc's §1 is `model`, §3 + §4 contain `decision`, §5 contains `pitfall`. Not enforced via metadata. |
| Three maturity levels (draft / verified / proven) | Kept | Used in every doc's frontmatter. See §11. |
| Auto-decay mechanism | Adapted | Manual quarterly review (Rule 3) instead of automated decay. Solo-scale. |
| Three contributor roles | Dropped | One-person repo. |
| Independent Git knowledge repo | Dropped | Knowledge stays in this repo's `docs/` because it is project-specific and the `hapi` workspace is currently the only repo of this kind. |
| Cross-device remote control / WeChat handoff | Dropped | Out of scope; different audience. |
| Three-tier progressive index (catalog / topic / entry) | **Kept** | The Layer A / Layer B / Layer C structure is exactly this pattern. |
| Knowledge reference tracking with auto-update of `last_referenced` | Dropped | No tooling for this; manual maturity tags are the substitute. |

Net assessment: the article describes ~12 concepts; this system kept 6 of them (the ones that work for one person), adapted 2, and dropped 4. The dropped concepts are the team-oriented ones; the kept concepts are the structural / cognitive ones.

## 14. Out of scope (explicit list)

For clarity, these things are *not* part of this system, even though related needs exist:

- A separate per-stage docs subfolder (`docs/pipeline/01_*.md`, `docs/pipeline/02_*.md`, ...). The lean variant α chose a single `pipeline_map.md` instead. If the single doc grows past ~400 lines, a future migration to the subfolder structure is upward-compatible.
- A separate per-HAPI-topic docs subfolder. Same reasoning as above.
- Automatic doc generation from code annotations. Code annotations (Layer C) and crosswalk docs (Layers A/B) coexist; one is not generated from the other.
- A search index, full-text search frontend, or doc rendering server. Markdown + Obsidian + `grep` are sufficient.
- An agent that auto-updates crosswalk docs when code changes. Future work; not designed now.
- Migration of existing physics docs into the new structure. The new system *links to* `docs/fundamental.md`, `docs/hot_band_*.md`, etc. without modifying them.

## 15. Resolved questions

All four open questions resolved during spec review on 2026-04-28.

1. **`physics/04_nonlte_treanor.md` and `docs/TREANOR_DISTRIBUTION_NOTES.md` — link or absorb?**
   **Decision: link only.** Crosswalk slice points at the existing TREANOR notes for derivations and adds only the code-mapping content. Keeps one canonical Treanor derivation, avoids duplication, makes the TREANOR notes the primary source of truth for the physics.

2. **Keep, retire, or rewrite `docs/NU3_PROGRESSIONS_WORKFLOW.md`?**
   **Decision: retire if overlap is substantial.** During step 2 of the build (writing `pipeline_map.md`), evaluate overlap. If `pipeline_map.md` covers the same runtime-behavior content (it should, given its scope), retire `NU3_PROGRESSIONS_WORKFLOW.md` — move it to a `docs/_archive/` subfolder rather than deleting, so the original Q&A-style review notes remain available but stop being a primary reference. Add a redirect line at the top of the archived doc pointing readers to `pipeline_map.md`.

3. **Keep, retire, or restructure `docs/REPOSITORY_STRUCTURE.md`?**
   **Decision: retire if overlap is substantial.** Same overlap-evaluation step as Q2, applied during step 2 (`pipeline_map.md`) and step 11 (`theory_code_map.md` re-pass). `REPOSITORY_STRUCTURE.md` is already partially stale (lists the cleanup as incomplete) and is partially superseded by `framework.md`. If `pipeline_map.md` + `theory_code_map.md` together cover the "what lives where" question, archive `REPOSITORY_STRUCTURE.md` to `docs/_archive/` with a redirect.

4. **Inventory the SVGs in `docs/figures/` and `docs/*.svg` and tag them in crosswalk docs?**
   **Decision: yes.** Each physics slice's §2 "Key equations / data model / diagram" must search the existing SVG inventory for relevant figures and link them rather than duplicating or omitting. When a slice would benefit from a figure that does not yet exist, flag it in that slice's §5 (Footguns) or in a new "Figure gaps" subsection — defer drawing to a follow-up pass, do not block slice completion on figure creation.

These decisions are now load-bearing constraints for the build phase and should be carried into the implementation plan.

---

## Appendix — Summary of decisions made during brainstorming

For traceability, the design decisions made interactively (in order):

1. **Trigger.** User wants to understand framework + remember it + bound agent action. Not implementing the article wholesale.
2. **Most painful gap.** Theory ↔ implementation crosswalk (A), not pipeline navigation (B) or guardrails (C). [Later updated to include B and C.]
3. **Scope of "theory".** All six slices: absorbance spine, line-strength T-dependence, J-pair structure, non-LTE/Treanor, database conventions, numerical caveats. User chose "all".
4. **Doc structure.** Approach A — topic-per-doc with master index, vs. monolithic doc or code-only annotations.
5. **Lean vs. full variant.** Variant α (lean): single `pipeline_map.md` and single `hapi_usage.md` rather than per-stage / per-topic subfolders. Reduces total to ~10 docs / ~1270 lines / 4–6 sessions.
6. **Build order.** Pipeline first (A), then HAPI (B-hapi), then physics slices (B-physics) in the order: spine, T-dependence, numerical caveats, non-LTE, J-pair, database conventions.
7. **File naming.** Lowercase-underscore. Renamed `AGENTS_PHYSICS_GUARDRAILS.md` → `physics_guardrails.md` to avoid collision with existing `AGENTS.md` chain.
8. **Spec location.** `docs/specs/2026-04-28-theory-code-crosswalk-design.md` (not `docs/superpowers/specs/`, which is the brainstorming skill default).

---

*End of design specification.*
