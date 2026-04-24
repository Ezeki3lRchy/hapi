# Generalized absorption law for non-Boltzmann level populations

## 1. Scope

This note summarizes the absorption law for a two-level transition when the level populations are **not** assumed to follow a Boltzmann distribution. It is a clean way to see how stimulated emission modifies the usual Beer-Lambert law.

We consider a transition between

- lower level $1$
- upper level $2$

with

- energies $E_1$ and $E_2$
- degeneracies $g_1$ and $g_2$
- transition frequency $\nu_0 = (E_2-E_1)/h$

---

## 2. Definitions

Let

- $n_1$: population density of level $1$
- $n_2$: population density of level $2$
- $B_{12}$: Einstein coefficient for absorption
- $B_{21}$: Einstein coefficient for stimulated emission
- $A_{21}$: Einstein coefficient for spontaneous emission
- $\rho(\nu)$: spectral radiation energy density
- $\phi(\nu)$: normalized line-shape function

with

$$
\int \phi(\nu)\, d\nu = 1
$$

### SI units used in this note

- $E_1$, $E_2$: joule ($\mathrm{J}$)
- $h$: joule-second ($\mathrm{J\,s}$)
- $\nu$, $\nu_0$: hertz ($\mathrm{Hz}$)
- $g_1$, $g_2$: dimensionless
- $n_1$, $n_2$: number density, $\mathrm{m^{-3}}$
- $A_{21}$: spontaneous-emission rate coefficient, $\mathrm{s^{-1}}$
- $\rho(\nu)$: spectral radiation energy density, $\mathrm{J\,m^{-3}\,Hz^{-1}}$
- $\phi(\nu)$: line-shape function, $\mathrm{Hz^{-1}}$
- $R_{\mathrm{abs}}(\nu)$, $R_{\mathrm{stim}}(\nu)$, $R_{\mathrm{net}}(\nu)$: frequency-resolved rate densities, $\mathrm{m^{-3}\,s^{-1}\,Hz^{-1}}$
- $R_{\mathrm{abs}}$: total rate density integrated over frequency, $\mathrm{m^{-3}\,s^{-1}}$
- $I_\nu$: specific intensity, $\mathrm{W\,m^{-2}\,sr^{-1}\,Hz^{-1}}$
- $\kappa_\nu$: absorption coefficient, $\mathrm{m^{-1}}$
- $j_\nu$: emission coefficient, $\mathrm{W\,m^{-3}\,sr^{-1}\,Hz^{-1}}$
- $B_{12}$, $B_{21}$: Einstein $B$ coefficients; with $\rho(\nu)$ treated as spectral energy density per unit frequency, a common SI unit is $\mathrm{m^3\,J^{-1}\,s^{-2}}$

Here, $\mathrm{sr^{-1}}$ means "per steradian." A steradian ($\mathrm{sr}$) is the SI unit of solid angle, so it indicates that $I_\nu$ and $j_\nu$ are resolved not only by frequency but also by propagation direction.

For the Einstein $B$ coefficients, note that units can look different across books because authors do not always group the frequency dependence and line-shape factor in the same way. The physical meaning is the same: they measure how strongly the radiation field drives absorption or stimulated emission.

---

## 3. Net radiative transition rate

For radiation near frequency $\nu$, the upward absorption rate per unit volume is

$$
R_{\mathrm{abs}}(\nu) = n_1 B_{12}\rho(\nu)\phi(\nu)
$$

Here, "per unit volume" means **per cubic meter** of the medium. Because the expression is resolved at a particular frequency $\nu$, it is best read as a **frequency-resolved rate density**, that is, a rate per cubic meter per hertz around $\nu$. To get the total absorption rate in a finite volume $V$ over a small frequency interval $d\nu$, use

$$
d\dot{N}_{\mathrm{abs}} = R_{\mathrm{abs}}(\nu)\,V\,d\nu
$$

and to get the total line-integrated rate, integrate over frequency.

This expression says that the absorption rate at frequency $\nu$ is set by four factors:

- $n_1$: how many particles are available in the lower state to absorb
- $B_{12}$: the Einstein absorption coefficient, which tells how easily radiation drives absorption from level $1$ to level $2$
- $\rho(\nu)$: the spectral radiation energy density, meaning how much radiation energy is present at frequency $\nu$
- $\phi(\nu)$: the line-shape function, meaning how strongly the transition responds at that frequency relative to line center

In simple terms, $B_{12}$ tells how easy it is for light to make a particle jump from level $1$ to level $2$. A larger $B_{12}$ means that, for the same lower-state population, radiation density, and line shape, the medium absorbs more strongly because the transition is easier for the radiation field to drive.

Physically, absorption is largest when many particles occupy level $1$, the radiation field is strong near the transition, and $\nu$ lies where the line shape is large. Because $\phi(\nu)$ is normalized, it does not create extra total absorption by itself; it distributes the absorption strength over frequency according to Doppler, pressure, or other broadening mechanisms.

Depending on convention, $R_{\mathrm{abs}}(\nu)$ is often interpreted as a frequency-resolved rate density rather than a frequency-integrated total rate. In that case, integrating over frequency gives the total upward absorption rate:

$$
R_{\mathrm{abs}}
=
n_1 B_{12}\int \rho(\nu)\phi(\nu)\,d\nu
$$

If $\rho(\nu)$ varies slowly across the line, this is approximately

$$
R_{\mathrm{abs}} \approx n_1 B_{12}\rho(\nu_0)
$$

where $\nu_0$ is the line-center frequency.

The downward stimulated emission rate per unit volume is

$$
R_{\mathrm{stim}}(\nu) = n_2 B_{21}\rho(\nu)\phi(\nu)
$$

Therefore, the **net removal of photons from the beam** is

$$
R_{\mathrm{net}}(\nu)
=
\left(n_1 B_{12} - n_2 B_{21}\right)\rho(\nu)\phi(\nu)
$$

This is the main place where non-equilibrium enters: $n_1$ and $n_2$ are left completely general.

---

## 4. Convert rate into attenuation of intensity

For a beam with specific intensity $I_\nu$ propagating along $z$, the radiative transfer equation is

$$
\frac{dI_\nu}{dz} = -\kappa_\nu I_\nu + j_\nu
$$

where

- $I_\nu$: specific intensity at frequency $\nu$, meaning the radiative intensity resolved by frequency and propagation direction
- $\kappa_\nu$ is the absorption coefficient
- $j_\nu$ is the emission coefficient

This equation states that the change of spectral intensity along the path is the balance between a loss term and a source term:

- $-\kappa_\nu I_\nu$: attenuation of the beam by the medium
- $+j_\nu$: radiation added into the beam by the medium

So if absorption dominates, $I_\nu$ decreases with distance, while if emission dominates, $I_\nu$ increases. The coefficient $\kappa_\nu$ has units of inverse length and measures how strongly the medium removes radiation at frequency $\nu$. The coefficient $j_\nu$ measures how strongly the medium emits radiation into that same frequency and propagation direction.

> For the operational definition of $\kappa_\nu$ (differential and energy-balance forms), its units, physical interpretations (mean free path, optical depth, cross-section factorization $\kappa_\nu = n\sigma$), sign convention, and link to the radiative transfer equation, see [[Absorption Coefficient]].

### Extinction vs. net absorption in this note

In the present discussion, the key point is that $\kappa_\nu$ is not just ordinary absorption. It represents the **net extinction** produced by true absorption from level $1$ minus the return of photons through stimulated emission from level $2$. If spontaneous emission and other emissive processes are **neglected** in the propagation direction of interest, then $j_\nu \approx 0$ and the transfer equation reduces to

$$
\frac{dI_\nu}{dz} = -\kappa_\nu I_\nu
$$

which is the differential Beer-Lambert form.

### Deriving $\kappa_\nu$ from the Einstein $B$ coefficients

The claim below is that

$$
\kappa_\nu
=
\frac{h\nu}{4\pi}
\left(n_1 B_{12} - n_2 B_{21}\right)\phi(\nu)
$$

Rather than post it by assertion, it is worth seeing **each factor earn its place**. The derivation has four steps: (i) convert the directional beam into an isotropic-equivalent field the atom can respond to, (ii) write the per-atom induced-transition rate, (iii) multiply by $h\nu$ and the lower-state density to get energy absorbed per unit volume, (iv) match to the definition of $\kappa_\nu$. The same bookkeeping, repeated for $n_2 B_{21}$, gives the stimulated-emission term.

A convention choice is implicit in this formula: the Einstein $B$'s here are those defined against the **mean intensity** $J_\nu$, so that the per-atom stimulated absorption rate is $R_{12}=B_{12}\,\bar J$ with $\bar J = \int \phi(\nu)\,J_\nu\,d\nu$. The earlier use of $\rho(\nu)$ in Section 3 is a pedagogical shorthand — for a consistent dimensional treatment at the $\kappa_\nu$ step, the beam is expressed through its contribution to $J_\nu$ rather than to $\rho(\nu)$. The equivalent form in the energy-density ($u$) convention is $\kappa_\nu = (h\nu/c)(n_1 B_{12}^{(u)}-n_2 B_{21}^{(u)})\phi(\nu)$, with $B^{(u)} = (4\pi/c)\,B^{(J)}$. Both are the same physics; only the label on $B$ changes.

**Step 1 — From a directional beam to $J_\nu$.**  A beam of specific intensity $I_\nu$ coming from solid angle $d\Omega$ around direction $\hat n$ contributes

$$
dJ_\nu = I_\nu\,\frac{d\Omega}{4\pi}
$$

to the mean intensity, because $J_\nu \equiv \tfrac{1}{4\pi}\oint I_\nu\,d\Omega$. This is **where the $1/(4\pi)$ enters** — not from the geometry of the atom, but from the definition of $J_\nu$ as an angular *average* over $4\pi$ sr. An atom couples to the field in all directions, so a beam that occupies only $d\Omega$ of the sphere drives it as though its mean intensity were diluted by $d\Omega/(4\pi)$.

**Step 2 — Per-atom induced transition rate.**  Within frequency interval $d\nu$, the rate of stimulated absorption per atom from this beam slice is

$$
dR_{12} = B_{12}\,\phi(\nu)\,dJ_\nu\,d\nu = B_{12}\,\phi(\nu)\,I_\nu\,\frac{d\Omega}{4\pi}\,d\nu
$$

The profile $\phi(\nu)$ spreads the frequency-integrated $B_{12}$ over the actual line shape.

**Step 3 — Energy absorbed per unit volume per unit time.**  Each transition removes one photon of energy $h\nu$ from the beam. With $n_1$ atoms in the lower state per unit volume, the energy removed from this slice per unit time per unit volume is

$$
dE_\mathrm{abs} = h\nu\,n_1\,dR_{12} = h\nu\,n_1 B_{12}\,\phi(\nu)\,I_\nu\,\frac{d\Omega}{4\pi}\,d\nu
$$

**Step 4 — Match to the definition of $\kappa_\nu$.**  By definition of the absorption coefficient, the energy extracted per unit volume per unit time from a beam of specific intensity $I_\nu$ in $d\Omega\,d\nu$ is

$$
dE_\mathrm{abs} = \kappa_\nu\,I_\nu\,d\Omega\,d\nu
$$

Setting the two expressions for $dE_\mathrm{abs}$ equal and cancelling the common factor $I_\nu\,d\Omega\,d\nu$:

$$
\kappa_\nu^{(\mathrm{pure\,abs})} = \frac{h\nu}{4\pi}\,n_1 B_{12}\,\phi(\nu)
$$

**Step 5 — Subtract stimulated emission.**  A photon in the beam can also *stimulate* an atom in the upper state to emit a photon **into the same beam mode** (same direction, same frequency, same phase), partly refilling what absorption removed. The very same chain of reasoning, with $n_1 B_{12} \to n_2 B_{21}$, gives

$$
\kappa_\nu^{(\mathrm{stim})} = \frac{h\nu}{4\pi}\,n_2 B_{21}\,\phi(\nu)
$$

The **net** absorption coefficient is the difference:

$$
\kappa_\nu
=
\frac{h\nu}{4\pi}
\left(n_1 B_{12} - n_2 B_{21}\right)\phi(\nu)
$$

### Reading off the factors

Every factor in the final expression traces back to one concrete step above:

- $h\nu$ — converts a photon-counting rate ($\mathrm{s^{-1}}$) into an energy rate ($\mathrm{W}$). $\kappa_\nu$ measures energy attenuation, not photon counts, so the photon energy has to appear.
- $\phi(\nu)$ — distributes the frequency-integrated coupling $B_{12}$ across the actual line shape (Doppler, Lorentz, Voigt). Without $\phi$, the formula would give a delta-function-like absorption at a single frequency.
- $n_1 B_{12} - n_2 B_{21}$ — the **net upward rate coefficient**. Absorption from the lower state minus stimulated emission from the upper state. When $n_2/g_2 > n_1/g_1$ this quantity is negative: the medium amplifies the beam (see Section 8 on population inversion).
- $1/(4\pi)$ — the "mean-intensity" conversion factor. Einstein's $B$'s couple to $J_\nu$ (the angular average of $I_\nu$), but absorption is observed on a beam of specific intensity $I_\nu$. The $4\pi\,\mathrm{sr}$ of the unit sphere mediates the two.

### Why the $1/(4\pi)$ does not mean "atoms only see a fraction of the beam"

A common misreading is that the $1/(4\pi)$ encodes some geometric cross section — as if the atom intercepts only $d\Omega/(4\pi)$ of the beam. That is not the physics. An atom has no preferred orientation in the absence of external fields, and electric-dipole interactions respond to the field in all directions. The $1/(4\pi)$ is purely a **bookkeeping factor** that follows from the convention of defining $B_{12}$ against $J_\nu$, not against $I_\nu$. Using the energy-density convention for $B$, the same formula reads $(h\nu/c)(\ldots)\phi(\nu)$ with no $4\pi$ visible; the physics is identical.

Using the Einstein relation

$$
g_1 B_{12} = g_2 B_{21}
$$

we obtain

$$
\kappa_\nu
=
\frac{h\nu}{4\pi} B_{12}\phi(\nu)
\left[
n_1 - \left(\frac{g_1}{g_2}\right)n_2
\right]
$$

This is the **general absorption coefficient** for an arbitrary non-Boltzmann population distribution.

## Important point

The relation

$$
g_1 B_{12} = g_2 B_{21}
$$

does **not** mean Boltzmann equilibrium is being assumed for the level populations.

It is an Einstein-coefficient relation between transition probabilities. The **Boltzmann assumption enters later**, only if we replace the population ratio by

$$
\frac{n_2}{n_1}
=
\frac{g_2}{g_1}\exp\left(-\frac{h\nu}{kT}\right)
$$

So these are two different ideas:

- $g_1 B_{12} = g_2 B_{21}$: relation between microscopic radiative coefficients
- $n_2/n_1 = (g_2/g_1)e^{-h\nu/kT}$: thermal-equilibrium population distribution

---

## 5. Generalized Beer-Lambert law - Absorption Law

If emission can be neglected over the path segment, then

$$
\frac{dI_\nu}{dz} = -\kappa_\nu I_\nu
$$

Integrating from $0$ to $z$ gives

$$
I_\nu(z)
=
I_\nu(0)
\exp\left[
-\int_0^z \kappa_\nu(z')\,dz'
\right]
$$

For a uniform medium of length $L$,

$$
I_\nu(L) = I_\nu(0)e^{-\kappa_\nu L}
$$

with

$$
\kappa_\nu
=
\frac{h\nu}{4\pi} B_{12}\phi(\nu)
\left[
n_1 - \left(\frac{g_1}{g_2}\right)n_2
\right]
$$

Hence

$$
I_\nu(L)
=
I_\nu(0)
\exp\left\{
-\frac{h\nu}{4\pi} B_{12}\phi(\nu)
\left[
n_1 - \left(\frac{g_1}{g_2}\right)n_2
\right]L
\right\}
$$

This is the Beer-Lambert law generalized to non-equilibrium populations.

---

## 6. Cross section form

Define the absorption cross section for level $1$ as

$$
\sigma_{12}(\nu) = \frac{h\nu}{4\pi} B_{12}\phi(\nu)
$$

Then the absorption coefficient becomes

$$
\kappa_\nu
=
\sigma_{12}(\nu)
\left[
n_1 - \left(\frac{g_1}{g_2}\right)n_2
\right]
$$

and

$$
I_\nu(L)
=
I_\nu(0)
\exp\left\{
-\sigma_{12}(\nu)
\left[
n_1 - \left(\frac{g_1}{g_2}\right)n_2
\right]L
\right\}
$$

This suggests defining an **effective absorber density**

$$
n_{\mathrm{eff}}
=
n_1 - \left(\frac{g_1}{g_2}\right)n_2
$$

So the attenuation can be written as

$$
I_\nu(L) = I_\nu(0)\exp\left[-\sigma_{12}(\nu)n_{\mathrm{eff}}L\right]
$$

### Physical meaning

The absorber density is **not just** the lower-state density $n_1$.

The upper-state population $n_2$ reduces net absorption because stimulated emission returns photons to the beam. That is why the correction term appears with a minus sign.

---

## 7. Recovery of the usual Boltzmann result

If the populations are in thermal equilibrium, then

$$
\frac{n_2}{n_1}
=
\frac{g_2}{g_1}\exp\left(-\frac{h\nu}{kT}\right)
$$

Therefore,

$$
\left(\frac{g_1}{g_2}\right)n_2
=
n_1\exp\left(-\frac{h\nu}{kT}\right)
$$

and thus

$$
n_1 - \left(\frac{g_1}{g_2}\right)n_2
=
n_1\left[1-\exp\left(-\frac{h\nu}{kT}\right)\right]
$$

Substituting into the general expression gives

$$
\kappa_\nu
=
\frac{h\nu}{4\pi} B_{12}\phi(\nu)\,
n_1\left[1-\exp\left(-\frac{h\nu}{kT}\right)\right]
$$

This is the standard equilibrium result.

So the familiar correction factor

$$
1-\exp\left(-\frac{h\nu}{kT}\right)
$$

is not fundamental by itself. It is only the special thermal-equilibrium form of the more general factor

$$
n_1 - \left(\frac{g_1}{g_2}\right)n_2
$$

> For a student-oriented walk-through of this reduction — the physical meaning of $1 - e^{-h\nu/kT}$ as "stimulated emission in disguise," limiting cases ($h\nu \gg kT$ vs. $h\nu \ll kT$), a numerical table across visible / IR / microwave transitions, and the connection to HITRAN line strengths $S_{ij}(T)$ — see [[Stimulated Emission Correction]].

---

## 8. Population inversion

If

$$
n_2 > \left(\frac{g_2}{g_1}\right)n_1
$$

then

$$
n_1 - \left(\frac{g_1}{g_2}\right)n_2 < 0
$$

and therefore

$$
\kappa_\nu < 0
$$

In that case the medium does not attenuate the beam. It amplifies it.

This is the condition for **gain** or **population inversion**.

---

## 9. What is neglected when writing pure absorption

The simplified law

$$
\frac{dI_\nu}{dz} = -\kappa_\nu I_\nu
$$

assumes that the emission term $j_\nu$ can be neglected over the path of interest.

That can be reasonable when

- the external beam is strong compared with local spontaneous emission into the observed direction
- the path is short
- one only wants the net extinction of a probe beam

If spontaneous emission along the line of sight is important, one should keep the full transfer equation

$$
\frac{dI_\nu}{dz} = -\kappa_\nu I_\nu + j_\nu
$$

---

## 10. Compact summary

For a two-level system with arbitrary level populations, the net absorption coefficient is

$$
\kappa_\nu
=
\frac{h\nu}{4\pi} B_{12}\phi(\nu)
\left[
n_1 - \left(\frac{g_1}{g_2}\right)n_2
\right]
$$

or, in cross-section form,

$$
\kappa_\nu = \sigma_{12}(\nu)n_{\mathrm{eff}}
$$

with

$$
\sigma_{12}(\nu) = \frac{h\nu}{4\pi}B_{12}\phi(\nu),
\qquad
n_{\mathrm{eff}} = n_1 - \left(\frac{g_1}{g_2}\right)n_2
$$

Then the generalized Beer-Lambert law for a uniform medium is

$$
I_\nu(L) = I_\nu(0)e^{-\kappa_\nu L}
$$

The usual thermal factor $1-e^{-h\nu/kT}$ appears only after imposing the Boltzmann relation on $n_2/n_1$.

---

## 11. One-line intuition

**Net absorption = true absorption from the lower level - stimulated emission from the upper level.**

That is why the lower-state population alone is not enough when the populations are not in thermal equilibrium.
