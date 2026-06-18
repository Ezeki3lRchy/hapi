# Why the LTE/HITRAN path says "populations never computed explicitly"

This note answers a question about box **(a) 5** in [`ch4_nu3_process_diagram.svg`](ch4_nu3_process_diagram.svg):

> **(a) 5. Populations never computed explicitly**
> *(no* $n(v_3)$ *and no* $n_\mathrm{eff}$ *step in the LTE path)*

The claim is correct but counterintuitive. The short answer: populations **are** being used in the LTE path, but they are **hidden inside the line-intensity rescaling formula**, not computed as a separate variable in code.

## 1. The physics identity that lets LTE collapse the population step

Every absorption line in every workflow obeys the same general form:

$$
\alpha_i(\tilde{\nu}) \;=\; n_{\mathrm{eff},i}\, S_i\, \phi_i(\tilde{\nu}),
\qquad
n_{\mathrm{eff},i} \;=\; n_l \;-\; \frac{g_l}{g_u}\, n_u.
$$

What makes LTE special is that $n_\mathrm{eff}$ factors cleanly into quantities already inside the HITRAN rescaling formula.

Under Boltzmann, the lower-state population density is

$$
n_l \;=\; n_\mathrm{total}\, \frac{g_l}{Q(T)}\, e^{-c_2 E_l / T},
$$

and the upper/lower population ratio satisfies the Boltzmann identity

$$
\frac{n_u}{n_l} \;=\; \frac{g_u}{g_l}\, e^{-c_2 \tilde{\nu} / T}.
$$

Substituting this ratio into the definition of $n_\mathrm{eff}$:

$$
n_{\mathrm{eff},i}
\;=\;
n_l\left[\, 1 \;-\; \frac{g_l}{g_u}\cdot\frac{n_u}{n_l} \right]
\;=\;
n_l\,\bigl[\, 1 \;-\; e^{-c_2 \tilde{\nu} / T}\,\bigr].
$$

That bracket $[1 - e^{-c_2 \tilde{\nu}/T}]$ is **exactly** the stimulated-emission correction that already appears inside HITRAN's intensity rescaling:

$$
S_i(T) \;=\; S_i(T_\mathrm{ref})\,
\frac{Q(T_\mathrm{ref})}{Q(T)}\,
e^{-c_2 E_l (1/T - 1/T_\mathrm{ref})}\,
\frac{1 - e^{-c_2 \tilde{\nu}_i / T}}{1 - e^{-c_2 \tilde{\nu}_i / T_\mathrm{ref}}}.
$$

So

$$
n_\mathrm{total}\, S_i(T) \;\equiv\; n_{\mathrm{eff},i}\, \widetilde{S}_i,
$$

where $\widetilde{S}_i$ is a "pure" line strength that depends only on the transition, not on populations. The two formulations are algebraically identical.

> [!note] Bottom line
> `n_total × S_i(T)` already contains `n_eff,i` as a factor — the population arithmetic is done in closed form inside `S_i(T)`, not by computing `n(v_3)` and `n_eff` as separate variables.

## 2. Why this collapse only works under Boltzmann

The whole trick relies on the Boltzmann identity

$$
\left(\frac{n_u}{n_l}\right)_\mathrm{LTE} \;=\; \frac{g_u}{g_l}\, e^{-c_2 \tilde{\nu} / T}.
$$

If the populations follow any other law (Treanor, two-temperature, inverted, steady-state kinetics), this identity fails:

$$
\left(\frac{n_u}{n_l}\right)_\mathrm{Treanor} \;\neq\; \frac{g_u}{g_l}\, e^{-c_2 \tilde{\nu} / T}.
$$

So you can no longer hide the upper-state correction inside a thermal factor like $(1 - e^{-c_2 \tilde{\nu}/T})$. You are forced to:

1. compute $n(v_3)$ for every relevant vibrational level explicitly;
2. pair lower and upper states transition-by-transition;
3. construct $n_\mathrm{eff} = n_l - (g_l/g_u)\, n_u$ by hand for each line.

Those are exactly **steps (b) 3, (b) 4, (b) 5** on the right side of `ch4_nu3_process_diagram.svg` — the three substeps that the LTE path collapses into the single rescaling formula in **step (a) 3**.

## 3. Where this shows up in code

In [`hapi/hapi.py`](../hapi/hapi.py), functions like

```python
absorptionCoefficient_Voigt(Components, SourceTables, Environment, ...)
```

never have local variables called `n_l`, `n_u`, or `n_eff`. They:

1. read `T` and `P` from `Environment`;
2. look up $S_i(T_\mathrm{ref})$, $E''_i$, $\tilde{\nu}_i$ from the line table;
3. call `partitionSum(T)` to get $Q(T)$;
4. apply the HITRAN rescaling formula above to get $S_i(T)$;
5. multiply by $n_\mathrm{total} = Px/(k_B T)$ at the Beer-Lambert step.

The lower-state population is implicit in the $e^{-c_2 E_l / T}/Q(T)$ factor. The stimulated-emission correction is implicit in the $[1 - e^{-c_2 \tilde{\nu}/T}]$ bracket. Neither is a named quantity in the code path.

In contrast, the Treanor path in [`research/ch4_treanor.py`](../research/ch4_treanor.py) and [`research/nonlte.py`](../research/nonlte.py) **has to** materialize lower-state populations — even in the simpler "ratio scaling" form used in Phase 1 of [`nonlte_absorption_realization_discussion.md`](nonlte_absorption_realization_discussion.md):

$$
I_\mathrm{nonLTE} \;=\; I_\mathrm{LTE}(T_0)\;
\frac{N_\mathrm{Treanor}(v_{3,\,\mathrm{lower}};\,T_v,T_0)}
     {N_\mathrm{Boltzmann}(v_{3,\,\mathrm{lower}};\,T_0)}.
$$

That ratio has the Treanor and Boltzmann lower-state populations appearing as **explicit, named** quantities — precisely the thing the LTE pipeline never needs.

## 4. Summary table

| Quantity | Computed explicitly in LTE? | Computed explicitly in Treanor? |
| --- | --- | --- |
| $n_\mathrm{total}$ | yes | yes |
| $f(v_3) = N_{v_3}/N_0$ (relative distribution) | no — implicit in $e^{-c_2 E_l/T}/Q(T)$ | **yes** — from the Treanor law |
| $n(v_3)$ (absolute per-level density) | no — never named | **yes** — $n_\mathrm{total}\, f(v_3)$ |
| $n_\mathrm{eff} = n_l - (g_l/g_u)n_u$ | no — folded into $[1 - e^{-c_2 \tilde{\nu}/T}]$ | **yes** — per line, by hand |
| Line intensity $S_i(T)$ | yes (HITRAN rescaling) | built via ratio scaling or from Einstein $A$ |

The asymmetry in this table is the reason the LTE column in the figure has one meaningful step plus a "no-op" note, while the Treanor column has three meaningful steps.

## 5. Alternative wordings for the figure box

The current box label is terse. If a more informative label reads better for a paper or slide, the two physics-faithful alternatives are:

| Option | Box title | Subtitle |
| --- | --- | --- |
| A (current) | *Populations never computed explicitly* | (no $n(v_3)$ and no $n_\mathrm{eff}$ step in the LTE path) |
| B | *Populations absorbed into intensity formula* | $n_\mathrm{eff}$ hidden inside HITRAN's $(1 - e^{-c_2 \tilde{\nu}/T})$ factor |
| C | $n_\mathrm{eff}$ *factorizes into* $S(T)$ | Boltzmann gives $n_\mathrm{eff} = n_l\,[1 - e^{-c_2 \tilde{\nu}/T}]$ |

Option A is the cleanest in the figure but assumes the reader knows the physics. Options B and C carry more information but cost some whitespace. The figure can stay at option A while this note carries the full derivation.

## Related notes

- [`ch4_nu3_boltzmann_hitran_process_figure.md`](ch4_nu3_boltzmann_hitran_process_figure.md) — LTE/HITRAN workflow figure and prose
- [`ch4_nu3_treanor_process_figure.md`](ch4_nu3_treanor_process_figure.md) — Treanor non-LTE workflow figure and prose
- [`nonlte_absorption_realization_discussion.md`](nonlte_absorption_realization_discussion.md) — implementation plan and verification strategy
- [`generalized_absorption_non_boltzmann_obsidian.md`](generalized_absorption_non_boltzmann_obsidian.md) — Einstein coefficients, $n_\mathrm{eff}$, generalized Beer-Lambert
