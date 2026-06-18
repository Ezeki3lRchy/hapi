# Non-local thermodynamic equilibrium (non-LTE) absorption realization discussion

This note responds to three planning questions around
[`generalized_absorption_non_boltzmann_obsidian.md`](generalized_absorption_non_boltzmann_obsidian.md):
how to realize the generalized absorption law in this repo, how Treanor should enter, and how to verify the result. It also maps the idea to Sadiek et al. 2024 on dual-comb spectroscopy of non-thermal ammonia formation.

## 1. The mental map

The cleanest map is:

```text
state distribution model + total density
    -> state population densities
    -> per-line effective absorber population
    -> per-line intensity / cross section
    -> broadened spectrum
    -> optional retrieval of model parameters from that spectrum
```

This is easy to misunderstand because "population model" is often used loosely. More precisely:

```text
distribution = fractions or ratios across states
population = actual number density in each state
```

The conversion is:

$$
n_i = n_\mathrm{total} f_i
$$

where $f_i$ is the fraction in state $i$, $n_\mathrm{total}$ is the total molecule number density, and $n_i$ is the population density of state $i$.

### Reading the map

#### 1. State distribution model + total density

This step decides how molecules are shared across quantum states.

For CH4 `nu3`, a distribution model gives relative amounts such as:

```text
f(v3=0), f(v3=1), f(v3=2), f(v3=3)
```

Boltzmann gives these fractions using one temperature. Treanor gives these fractions using `T0` and `Tv` for the effective `nu3` ladder.

By itself, this is only a percentage map. To get actual populations, multiply by total CH4 density:

```text
n(v3=0) = n_total * f(v3=0)
n(v3=1) = n_total * f(v3=1)
n(v3=2) = n_total * f(v3=2)
```

#### 2. Per-line effective absorber population

Each spectral line has a lower state and an upper state:

```text
line A: upper state <- lower state
```

This note uses the spectroscopy absorption convention:

```text
upper <- lower
```

So `2 <- 1` means absorption from lower state `1` to upper state `2`.

For a CH4 hot band:

```text
v3 = 2 <- v3 = 1
```

the line can absorb only if molecules occupy the lower state `v3 = 1`.

If we ignored stimulated emission, we could stop here and say:

```text
absorber population for this line = lower-state population
```

For the `v3 = 2 <- v3 = 1` hot band, that would mean:

```text
absorber population = n(v3=1)
```

But this is incomplete when the upper state is also populated.

The generalized absorption law says the net absorber for one line is:

$$
n_\mathrm{eff}
=
n_l
-
\left(\frac{g_l}{g_u}\right)n_u
$$

This is why the phrase says **effective** absorber population.

It is not simply:

```text
n_l
```

It is:

```text
lower-state absorption ability
minus
upper-state stimulated-emission ability
```

For the same hot-band example:

```text
transition: v3 = 2 <- v3 = 1

n_l = population density in v3 = 1
n_u = population density in v3 = 2

n_eff = n(v3=1) - degeneracy_correction * n(v3=2)
```

Here:

```text
degeneracy_correction = g_l / g_u
```

It is normally a **positive** number, because degeneracies count how many quantum states share the same energy label. A degeneracy is a count, so it is not negative.

The negative sign in `n_eff` does not come from the degeneracy correction. It comes from the physics of stimulated emission:

```text
n_eff = lower-state absorption term - upper-state stimulated-emission term
```

So:

```text
degeneracy_correction > 0
stimulated-emission term is subtracted
```

If the upper-state population is large enough, the whole `n_eff` can become negative:

```text
n_eff < 0
```

That does not mean the degeneracy correction is negative. It means stimulated emission is stronger than absorption for that line, so the medium gives gain instead of absorption.

So this step asks:

```text
for this particular line, how much population actually removes light from the probe beam?
```

The first term is true absorption from the lower state. The second term is stimulated emission from the upper state, which gives photons back to the beam.

### Why it is per-line

It is **per-line** because every spectral line can have a different pair of states.

Example:

```text
line A: v3 = 1 <- v3 = 0
    n_eff,A = n(v3=0) - degeneracy_correction_A * n(v3=1)

line B: v3 = 2 <- v3 = 1
    n_eff,B = n(v3=1) - degeneracy_correction_B * n(v3=2)

line C: v3 = 3 <- v3 = 2
    n_eff,C = n(v3=2) - degeneracy_correction_C * n(v3=3)
```

The same gas has one overall state distribution, but each transition reads a different lower/upper pair from that distribution.

### What the sign means

If:

```text
n_eff > 0
```

the line absorbs light.

If:

```text
n_eff = 0
```

true absorption and stimulated emission cancel for that line.

If:

```text
n_eff < 0
```

the line gives net gain instead of absorption. This is population inversion.

==For most ordinary infrared absorption cases, `n_eff` is positive.== The generalized formula matters because non-local thermodynamic equilibrium (non-LTE) populations can make the upper-state correction less negligible, especially for excited-state hot bands or inverted distributions.

#### 3. Per-line intensity / cross section

Now combine:

```text
transition probability from HITRAN/ExoMol
+ effective absorber population from the distribution model
= strength of this one spectral line
```

This produces a per-line intensity or cross section. In the current CH4 Treanor implementation, we do a simpler ratio-scaling version based on local thermodynamic equilibrium (LTE) line intensity:

$$
I_\mathrm{nonLTE}
=
I_\mathrm{LTE}
\times
\frac{N_\mathrm{Treanor}(v_{3,\mathrm{lower}})}
{N_\mathrm{Boltzmann}(v_{3,\mathrm{lower}})}
$$

That means:

```text
reuse the LTE line machinery, but replace the LTE lower-state distribution with the Treanor lower-state distribution
```

#### 4. Broadened spectrum

A line intensity is still only a stick line. Real spectra have line shapes.

Broadening turns each line into a finite-width feature:

```text
Doppler broadening: depends on translational temperature
Lorentz broadening: depends on pressure/collisions
Voigt profile: Doppler + Lorentz
```

Then all lines are summed:

```text
broadened spectrum = sum of all broadened line contributions
```

This gives the modeled absorbance/transmission spectrum.

#### 5. Optional retrieval

Once the forward model exists, we can fit it backward.

Forward model:

```text
choose T0, Tv, density
    -> compute spectrum
```

Retrieval:

```text
given a spectrum
    -> find T0, Tv, density that reproduce it
```

This is why synthetic spectra are useful: we choose the true parameters first, generate the spectrum, and then test whether the retrieval can recover the known truth.

Sadiek et al. travel mostly from right to left:

```text
measured NH3 transmission spectrum
    -> fit spectral model
    -> infer T_trans, T_rot, T_vib, and NH3 density
```

Our current work should first travel left to right:

```text
chosen CH4 population law
    -> synthetic non-LTE CH4 spectrum
    -> known truth: T0, Tv, density, path length
```

Then, after the forward model is trustworthy, we can also do retrieval:

```text
synthetic or measured spectrum
    -> fit forward model
    -> recover T0, Tv, and density
```

So the paper is not doing the opposite thing in a contradictory way. It uses a forward absorption model inside a fit. The experiment provides the spectrum; the model parameters are adjusted until the modeled spectrum matches. In this repo, we can build the same kind of forward model first, but with synthetic data where the true parameters are known.

## 2. What the generalized absorption law changes

The existing note shows that for a transition from lower state 1 to upper state 2,

$$
\kappa_\nu
=
\sigma_{12}(\nu)
\left[
n_1 - \left(\frac{g_1}{g_2}\right)n_2
\right].
$$

The bracket is the important part. LTE line intensity formulas hide this bracket inside the usual thermal stimulated-emission factor:

$$
1-\exp(-h\nu/kT).
$$

For non-Boltzmann populations, that thermal replacement is no longer generally valid. The implementation target should therefore be:

```text
do not assume population ratio from one thermal T
compute the lower and upper state populations from the chosen population model
use n_eff = n_lower - (g_lower / g_upper) n_upper for net absorption
```

There are two implementation levels:

| Level | What it does | Why use it first |
| --- | --- | --- |
| Ratio scaling | Multiply existing LTE intensities by a non-LTE lower-state population ratio | Small diff, already partly implemented for CH4 nu3 Treanor |
| Full generalized line strength | Recompute each line from Einstein A, degeneracies, lower and upper populations, and stimulated emission explicitly | More faithful to the markdown derivation |

The current repo already has the ratio-scaling path:

- [`research/ch4_treanor.py`](../research/ch4_treanor.py)
- [`research/nonlte.py`](../research/nonlte.py)
- [`scripts/validate_ch4_nu3_treanor_equilibrium.py`](../scripts/validate_ch4_nu3_treanor_equilibrium.py)

That is a good Phase 1. The generalized absorption note points toward a Phase 2 where `n_eff` is represented explicitly.

## 3. Plan to realize it

### Phase 1: make the current CH4 nu3 Treanor forward model explicit

Goal: produce spectra where CH4 nu3 hot-band intensities are controlled by a gas/translational temperature `T0` and a vibrational temperature `Tv`.

Use the existing approximation:

$$
I_\mathrm{nonLTE}
=
I_\mathrm{LTE}(T_0)
\times
\frac{N_\mathrm{Treanor}(v_{3,\mathrm{lower}}; T_v,T_0)}
{N_\mathrm{Boltzmann}(v_{3,\mathrm{lower}}; T_0)}.
$$

This changes the lower-state population but keeps the rest of the LTE machinery: partition function handling, line positions, broadening, and absorbance conversion.

Deliverable:

- one script that renders LTE vs non-LTE CH4 nu3 spectra for several `Tv` values at fixed `T0`
- one report table with per-band integrated absorbance ratios: `1<-0`, `2<-1`, `3<-2`, `4<-3`
- one figure showing that hot bands grow relative to the fundamental as `Tv` increases

### Phase 2: expose the generalized `n_eff` formulation

Goal: move from "scale LTE intensity by lower-state population" to "compute net absorber population per transition."

For each transition:

```text
lower state population: n_l
upper state population: n_u
degeneracies: g_l, g_u
effective absorber density: n_eff = n_l - (g_l / g_u) n_u
line contribution: kappa_nu = sigma_lu(nu) * n_eff
```

This is closer to the derivation in
[`generalized_absorption_non_boltzmann_obsidian.md`](generalized_absorption_non_boltzmann_obsidian.md), especially when upper-state populations become non-negligible.

Deliverable:

- a small population-model interface, probably function-based rather than class-based:

```python
def population_fraction(state, model_params) -> float:
    ...
```

- a line-strength function that can be tested on one transition before being used in a full spectrum
- an LTE recovery check showing that the explicit `n_eff` formula matches the standard HITRAN/ExoMol LTE intensity formula within expected tolerance

### Phase 3: retrieval from synthetic spectra

Goal: use generated spectra to infer the temperatures, like Sadiek et al. did with measured NH3 spectra.

For synthetic CH4:

```text
choose truth: T0, Tv, density, pressure, path length
generate spectrum
add optional noise
fit T0, Tv, density
compare fitted values to truth
```

This is where the map becomes clear: the forward model and inverse model are the same physics used in opposite directions.

## 4. How to use Treanor

Treanor should not be treated as "the spectrum model." It is only the population model.

For this repo, the practical CH4 version is:

```text
Treanor supplies N_v3 / N_0 along the restricted ladder (0,0,v3,0)
ExoMol/HITRAN supplies line positions, A coefficients/intensities, degeneracies, and state labels
Voigt broadening supplies line shape
Beer-Lambert converts cross section to absorbance/transmission
```

Treanor answers:

```text
How many molecules are in v3 = 0, 1, 2, 3, ... relative to v3 = 0?
```

It does not answer by itself:

```text
Where are the spectral lines?
How wide are they?
Which transitions are allowed?
What is the total CH4 density?
What is the pressure broadening?
```

Those remain line-list and gas-condition responsibilities.

### Treanor parameters

| Parameter | Meaning in this repo |
| --- | --- |
| `T0` | gas/translational temperature; also used for Doppler width, number density, and pressure broadening temperature scaling |
| `Tv` | vibrational temperature shaping the CH4 nu3 population ladder |
| `v3_lower` | lower-state quantum number that selects which Treanor population ratio applies |

If `Tv = T0`, the model must reduce to LTE. If it does not, the implementation is wrong or the normalization conventions are inconsistent.

### Important limitation

For CH4, Treanor is only an effective single-mode approximation here. It should be described as:

```text
CH4 nu3-only non-LTE toy/forward model
```

not:

```text
full methane non-LTE state population model
```

That distinction matters because methane has multiple vibrational modes, degeneracies, symmetry structure, Fermi resonance, and mode coupling.

## 5. How to verify after realizing it

Verification should be staged.

### A. Physics identity checks

| Check | Expected result |
| --- | --- |
| `Tv = T0` | non-LTE intensities equal LTE intensities |
| `v3_lower = 0` | scale factor is 1 for the fundamental lower state |
| higher `Tv` at fixed `T0` | hot bands increase relative to LTE |
| very low `Tv` | hot bands shrink |
| explicit `n_eff` under LTE populations | recovers the usual stimulated-emission factor |

The existing command already covers the most important identity:

```bash
python scripts/validate_ch4_nu3_treanor_equilibrium.py
```

### B. Spectrum-level checks

For generated spectra:

| Check | Expected result |
| --- | --- |
| same line grid and same broadening between LTE/non-LTE cases | only intensities change unless `T0` changes |
| integrated absorbance per progression | monotonic or explainable trend with `Tv` |
| no negative absorption unless population inversion is intentionally reached | negative `n_eff` means gain, not ordinary absorption |
| pressure/path/density scaling | absorbance scales linearly with pressure, mole fraction, and path length in optically thin cases |

### C. Retrieval checks

Start with synthetic spectra before using real data.

| Synthetic test | Pass condition |
| --- | --- |
| noiseless spectrum | fit recovers `T0`, `Tv`, density nearly exactly |
| noisy spectrum | fit recovers truth within uncertainty |
| wrong model fit | residuals show structured errors, especially across hot bands |
| LTE fit to non-LTE spectrum | one-temperature fit cannot match all bands consistently |

The last check is the bridge to Sadiek et al. Their NH3 paper shows why broadband fitting matters: if different bands imply different densities under one assumed temperature, that is evidence that the population model is wrong or incomplete.

## 6. Relation to Sadiek et al. 2024

Sadiek et al. measured broadband NH3 transmission in an N2-H2 plasma and fit a spectral model to retrieve separate translational, rotational, and vibrational temperatures plus NH3 number density. Their model includes:

- Voigt line shapes
- HITRAN transition data
- a two-zone path model: non-thermal reactor region plus thermal region
- separate fitted temperatures for different degrees of freedom
- uncertainty propagation through Monte Carlo draws of reference data and physical inputs

The important conceptual lesson is not "they used data, we use modeling." The lesson is:

```text
temperature is not directly measured
temperature is inferred by asking which population model best explains the spectrum
```

For us:

```text
modeling data = controlled fake experiment
real spectrum = real experiment
same retrieval logic can apply to both
```

The clearer research story is:

1. Build a forward model for CH4 nu3 non-LTE absorption.
2. Verify that it reduces to LTE.
3. Generate synthetic spectra with known `T0` and `Tv`.
4. Fit those spectra to prove that `T0` and `Tv` are identifiable.
5. Only then apply the method to experimental spectra, if available.

## 7. Recommended next markdown/code split

Keep the current derivation note as the theory note:

- `generalized_absorption_non_boltzmann_obsidian.md`: Einstein coefficients, `n_eff`, generalized Beer-Lambert law

Use this note as the planning bridge:

- `nonlte_absorption_realization_discussion.md`: implementation plan, Treanor usage, verification, Sadiek map

If implementation proceeds, add one more workflow note:

- `CH4_NU3_NONLTE_RETRIEVAL_WORKFLOW.md`: concrete commands, artifact names, fit parameters, and pass/fail checks

That three-note split keeps the map readable:

```text
theory -> realization plan -> executable workflow
```
