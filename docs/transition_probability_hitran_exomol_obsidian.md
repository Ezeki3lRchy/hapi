# Transition probability from HITRAN and ExoMol

## One-sentence meaning

The **transition probability** tells how intrinsically likely a molecule is to make a specific quantum transition when radiation interacts with it.

It is the database-side answer to:

```text
If a molecule is already in the lower state, how strongly can this transition interact with light?
```

It is different from population.

```text
population: how many molecules are in the lower state
transition probability: how strongly one molecule in that state couples to the radiation field
```

Both are needed for an absorption line.

---

## Absorption notation

This note uses the spectroscopy absorption convention:

```text
upper <- lower
```

So:

```text
v3 = 2 <- v3 = 1
```

means absorption from lower state `v3 = 1` to upper state `v3 = 2`.

---

## Why population alone is not enough

Suppose many molecules occupy `v3 = 1`.

That tells us the `v3 = 2 <- v3 = 1` hot band has available absorbers.

But it does not yet tell us how strong the transition is.

Two transitions can have the same lower-state population but different strengths:

```text
transition A: strong quantum-mechanical coupling
transition B: weak quantum-mechanical coupling
```

Then transition A gives a larger spectral line than transition B.

So the line strength needs two kinds of information:

```text
how many molecules are available
how strongly the transition is allowed
```

The first comes from the population/distribution model.

The second comes from the line database.

---

## What "probability" means here

In this context, "transition probability" does not mean a simple percentage like:

```text
this molecule has a 20% chance to absorb
```

It means a quantum-mechanical rate or strength parameter that controls the transition.

The most common database quantity for this is the Einstein `A` coefficient:

```text
A_ul
```

where:

| Symbol | Meaning |
| --- | --- |
| `u` | upper state |
| `l` | lower state |
| `A_ul` | spontaneous emission probability per second from upper state `u` to lower state `l` |

Its unit is:

```text
s^-1
```

So `A_ul` says:

```text
if a molecule is in the upper state, how quickly can it spontaneously emit and fall to the lower state?
```

For absorption, we care about the opposite direction:

```text
upper <- lower
```

The same quantum-mechanical transition strength controls both directions. Einstein coefficient relations connect spontaneous emission, stimulated emission, and absorption.

So `A_ul` is often the database's compact way of storing the intrinsic transition strength.

---

## HITRAN vs ExoMol

HITRAN and ExoMol expose this information differently.

### HITRAN

HITRAN rows usually already look like spectral lines.

A HITRAN row gives quantities such as:

```text
line center
line intensity at reference temperature
lower-state energy
broadening parameters
quantum labels
```

The key line-intensity column is often called:

```text
sw
```

In this repo, `sw` is the line intensity at the reference temperature, usually `296 K`.

So for HITRAN:

```text
transition probability is already folded into the stored reference line intensity
```

HAPI can then rescale the intensity to another temperature using:

```text
lower-state energy
partition function ratio
stimulated-emission correction
```

Mental model:

```text
HITRAN gives a ready-made line strength at a reference temperature
```

### ExoMol

ExoMol is more state-based.

It usually gives:

```text
.states file: state energies, degeneracies, quantum labels
.trans file: upper state ID, lower state ID, Einstein A coefficient
.pf file: partition function
```

For ExoMol:

```text
transition probability is stored more directly as Einstein A
```

Then the repo reconstructs the line:

```text
line center = E_upper - E_lower
line strength = A_ul + degeneracies + populations + partition function + stimulated-emission factor
```

Mental model:

```text
ExoMol gives the ingredients, and the repo builds the line strength
```

---

## Where it fits in the full map

The larger map is:

```text
state distribution model + total density
    -> state population densities
    -> per-line effective absorber population
    -> per-line intensity / cross section
    -> broadened spectrum
```

The transition probability enters at this step:

```text
per-line effective absorber population
    + transition probability from HITRAN/ExoMol
    -> per-line intensity / cross section
```

Meaning:

```text
population says how many absorbers are available
transition probability says how strongly each absorber couples to light
```

Together they determine how strong the line is before broadening.

---

## Simple analogy

For one spectral line:

```text
line strength = number of available molecules * intrinsic transition strength
```

More explicitly:

```text
line strength
    depends on n_eff
    depends on transition probability
```

where:

```text
n_eff = net absorber population for this line
transition probability = database-provided quantum-mechanical strength
```

If `n_eff` is large but the transition probability is tiny, the line can still be weak.

If the transition probability is large but `n_eff` is tiny, the line can also be weak.

A strong observed line usually needs both:

```text
many molecules in the relevant lower state
strong allowed transition
```

---

## Relation to Treanor

Treanor does not tell us the transition probability.

Treanor tells us the state distribution:

```text
how many molecules are in v3 = 0, 1, 2, 3, ...
```

HITRAN/ExoMol tell us the transition strength:

```text
how strong is v3 = 2 <- v3 = 1 as a quantum transition?
```

So for the CH4 non-LTE workflow:

```text
Treanor supplies populations
HITRAN/ExoMol supplies transition strengths and line positions
Voigt broadening supplies line shapes
Beer-Lambert supplies propagation through the gas
```

---

## Important wording

It is safer to say:

```text
transition strength
```

or:

```text
Einstein A coefficient / line intensity
```

than to say only:

```text
transition probability
```

because HITRAN and ExoMol do not always store the same form of the information.

In short:

```text
HITRAN: often gives reference line intensity directly
ExoMol: often gives Einstein A, then line intensity is reconstructed
```

Both represent the intrinsic quantum-mechanical strength of the transition.
