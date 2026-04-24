# Population model intuition

## One-sentence meaning

A **population model** is a rule for assigning molecules to quantum states.

In spectroscopy, this answers:

```text
How many molecules are in each lower state before light arrives?
```

That matters because an absorption line can only absorb if molecules are already sitting in the transition's lower state.

More precise wording:

```text
distribution model
    -> gives fractions or ratios

population model
    -> gives actual state populations after total density is included
```

In casual spectroscopy language, people often say "population model" for both steps. But your distinction is useful:

```text
distribution = percentage shape across states
population = actual number density in each state
```

The connection is:

$$
n_v = n_\mathrm{total} f_v
$$

where:

| Symbol | Meaning |
| --- | --- |
| $f_v$ | fraction of molecules in state $v$ |
| $n_\mathrm{total}$ | total molecule number density |
| $n_v$ | population density of state $v$ |

---

## Why line existence is not enough

A molecular database can tell us that a transition exists:

```text
state 2 <- state 1
```

This note uses the spectroscopy absorption convention:

```text
upper <- lower
```

So `2 <- 1` means absorption from lower state `1` to upper state `2`.

But the observed absorption also depends on how many molecules occupy `state 1`.

If almost no molecules are in `state 1`, then the line is weak even if the transition is allowed.

If many molecules are in `state 1`, then the line can be strong.

So the database gives the possible transitions, while the population model tells us which transitions are actually populated strongly enough to matter.

---

## Simple CH4 nu3 picture

For the CH4 `nu3` ladder, imagine vibrational levels:

```text
v3 = 0
v3 = 1
v3 = 2
v3 = 3
...
```

The fundamental band is mainly:

```text
v3 = 1 <- v3 = 0
```

The first hot band is:

```text
v3 = 2 <- v3 = 1
```

The second hot band is:

```text
v3 = 3 <- v3 = 2
```

Therefore:

```text
strength of 1 <- 0 depends on population in v3 = 0
strength of 2 <- 1 depends on population in v3 = 1
strength of 3 <- 2 depends on population in v3 = 2
```

The population model tells us the relative sizes of:

```text
N0, N1, N2, N3, ...
```

where `Nv` means the number of molecules in vibrational level `v`.

---

## Local thermodynamic equilibrium (LTE) population model: Boltzmann

In local thermodynamic equilibrium (LTE), the population model is the Boltzmann distribution.

For a rough vibrational ladder:

$$
\frac{N_v}{N_0}
\sim
\exp\left(-\frac{E_v}{k_B T}\right)
$$

Meaning:

```text
one temperature T controls the whole state distribution
```

At low temperature:

```text
N0 is large
N1 is tiny
N2 is much tinier
```

So hot bands are weak.

At high temperature:

```text
N1 and N2 become larger
```

So hot bands become visible.

This is the usual LTE spectroscopy picture.

---

## Non-local thermodynamic equilibrium (non-LTE) population model: Treanor

In a plasma or other non-equilibrium gas, vibration may not share the same temperature as translation.

Then one temperature is not enough.

For the effective CH4 `nu3` model in this repo, Treanor gives:

$$
\ln\left(\frac{N_{v_3}}{N_0}\right)
=
-\frac{\theta_3 v_3}{T_v}
+
\frac{x_e \theta_3 v_3^2}{T_0}
$$

Here:

| Symbol | Meaning |
| --- | --- |
| `T0` | gas/translational temperature |
| `Tv` | vibrational temperature |
| `v3` | CH4 `nu3` vibrational quantum number |
| `N_v3 / N_0` | population of level `v3` relative to ground |

So Treanor answers:

```text
Given T0 and Tv, how many molecules sit in v3 = 0, 1, 2, 3, ... ?
```

It does not directly compute the spectrum. It only gives the state populations.

---

## How this becomes a spectrum

The short chain was:

```text
population model
    -> per-line effective absorber population
    -> per-line intensity / cross section
    -> broadened spectrum
    -> optional retrieval of model parameters from that spectrum
```

Here is what each arrow means.

### Step 1: population model

This step says how molecules are distributed among quantum states.

For CH4 `nu3`, a distribution model gives something like:

```text
f(v3=0), f(v3=1), f(v3=2), f(v3=3)
```

These are fractions or percentages.

Then, after choosing the total CH4 number density:

```text
n(v3=0) = n_total * f(v3=0)
n(v3=1) = n_total * f(v3=1)
n(v3=2) = n_total * f(v3=2)
```

Now we have actual population densities.

So the more explicit first step is:

```text
distribution model + total density -> state population densities
```

### Step 2: per-line effective absorber population

Each spectral line has a lower state and an upper state.

Example:

```text
line A: v3 = 1 <- v3 = 0
line B: v3 = 2 <- v3 = 1
line C: v3 = 3 <- v3 = 2
```

For ordinary intuition, the line strength mostly follows the lower-state population:

```text
1 <- 0 line depends on n(v3=0)
2 <- 1 line depends on n(v3=1)
3 <- 2 line depends on n(v3=2)
```

But the generalized absorption law is slightly more complete. The effective absorber population is:

$$
n_\mathrm{eff}
=
n_l
-
\left(\frac{g_l}{g_u}\right)n_u
$$

This means:

```text
true absorption from lower state
minus stimulated emission from upper state
```

So "per-line effective absorber population" means:

```text
for each transition, compute the net population that actually removes light from the beam
```

### Step 3: per-line intensity / cross section

Once a line has an effective absorber population, we compute how strongly that one line absorbs.

Conceptually:

```text
line strength = transition probability * effective absorber population
```

The transition probability comes from the database:

```text
HITRAN / ExoMol line data
```

The population comes from:

```text
Boltzmann, Treanor, or another state-distribution model
```

This produces a per-line absorption strength or cross section.

In this repo's current CH4 Treanor approximation, we often do this by scaling an LTE line intensity:

$$
I_\mathrm{nonLTE}
=
I_\mathrm{LTE}
\times
\frac{N_\mathrm{Treanor}(v_{3,\mathrm{lower}})}
{N_\mathrm{Boltzmann}(v_{3,\mathrm{lower}})}
$$

That is a shortcut for saying:

```text
change the lower-state population while reusing the existing LTE line machinery
```

### Step 4: broadened spectrum

A line is not a vertical stick in real data. It has a shape.

Broadening turns each line into a peak with finite width:

```text
Doppler broadening -> depends on translational temperature
Lorentz broadening -> depends on pressure and collisions
Voigt profile -> combination of Doppler and Lorentz
```

Then all broadened lines are summed:

```text
spectrum = line 1 profile + line 2 profile + line 3 profile + ...
```

This gives the modeled absorbance spectrum.

### Step 5: optional retrieval

After the forward model exists, we can run the logic backward.

Forward model:

```text
choose T0, Tv, density
    -> compute spectrum
```

Retrieval:

```text
given a spectrum
    -> find T0, Tv, density that best reproduce it
```

This is what connects our modeling work to Sadiek et al. They measured a real spectrum, then fitted a model to infer temperatures and density.

With synthetic data, we can test the retrieval safely:

```text
choose known T0, Tv, density
generate fake spectrum
fit the fake spectrum
check whether the fit recovers the known values
```

---

## Same chain with CH4 hot bands

Suppose Treanor says:

```text
f(v3=1) is much larger than LTE
```

Then:

```text
population/distribution step:
    more molecules are in v3 = 1

per-line effective absorber step:
    2 <- 1 transitions have larger n_l

per-line intensity step:
    2 <- 1 hot-band lines become stronger

broadened spectrum step:
    the first hot band becomes more visible

retrieval step:
    a fitting routine may infer higher Tv
```

---

## Relation to generalized absorption

The generalized absorption law says the net absorber is:

$$
n_\mathrm{eff}
=
n_l
-
\left(\frac{g_l}{g_u}\right)n_u
$$

where:

| Symbol | Meaning |
| --- | --- |
| `n_l` | population density of the lower state |
| `n_u` | population density of the upper state |
| `g_l`, `g_u` | lower/upper state degeneracies |

The population model supplies `n_l` and `n_u`.

In LTE, Boltzmann supplies them.

In non-LTE, Treanor or another non-equilibrium model supplies them.

So:

```text
population model = input
generalized absorption law = how that input affects light attenuation
```

---

## Relation to Sadiek et al.

Sadiek et al. measured NH3 spectra and inferred temperatures by fitting a model.

Conceptually:

```text
measured spectrum
    -> find population model parameters
    -> report T_trans, T_rot, T_vib, density
```

In our CH4 work, we can start from the other direction:

```text
choose population model parameters
    -> generate synthetic spectrum
    -> later fit the spectrum to recover those parameters
```

These are not opposite ideas. They are the forward and inverse versions of the same map.

---

## Practical wording

When writing about this project, use:

```text
Treanor is the population model for the CH4 nu3 ladder.
```

Do not say:

```text
Treanor is the spectrum model.
```

The spectrum model needs more pieces:

```text
population model
line list
line strengths
broadening
Beer-Lambert propagation
```

Treanor is only the first piece.
