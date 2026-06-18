"""Electronic-band emission synthesis for diatomic molecules (OH A²Σ⁺–X²Π).

This is the *emission* counterpart to ``research/absorbance.py``. Where the
absorption path populates the lower state and computes a cross-section, here we
populate the **upper** electronic state and compute spontaneous-emission
intensity from the same ExoMol ``.states``/``.trans`` line list:

    I_line ∝ N(upper) · A_Einstein · (h c ν)          [energy / spectral radiance]

with the upper-state population governed by one or two temperatures:

    single-T :  N(u) ∝ g_u · exp(-c₂ · E_u / T)
    two-T    :  N(u) ∝ g_u · exp(-c₂ · G_vib(v') / T_vib) · exp(-c₂ · E_rot / T_rot)

where ``E_rot = E_u - G_vib(v')`` and ``G_vib(v')`` is the band origin (the
lowest-energy level of the upper electronic state with vibrational quantum
number ``v'``). The two-temperature form is the standard optical-emission
plasma-thermometry model: ``T_rot`` sets the rotational envelope, ``T_vib`` the
relative vibrational-band intensities.

Grid construction and the Voigt profile are reused from ``research.spectra``.
The ExoMol OH ``.states`` file has 8 whitespace columns
(``id E g J e/f v F1/F2 elec``), so it needs a dedicated parser distinct from
the CH₄ loader in ``research.exomol``.

References:
    Yousefi & Bernath (2018), JQSRT — OH A²Σ⁺–X²Π line list (MoLLIST).
    Emission intensity: Herzberg, *Spectra of Diatomic Molecules*, §I-V.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import numpy as np

from .io import iter_bz2_text_lines
from .models import SpectralWindow
from .spectra import build_grid, doppler_hwhm_cm, voigt_profile_cm

# Second radiation constant c₂ = hc/k_B in cm·K (matches research.treanor.HC_OVER_KB
# and hapi's SECOND_RADIATION_CONSTANT, CODATA 2018).
SECOND_RADIATION_CONSTANT_CM_K = 1.438776877

# OH (16O-1H) isotopologue mass from the MoLLIST .def file (Da).
OH_MASS_DA = 17.002740


@dataclass(frozen=True)
class DiatomLevels:
    """Upper/lower energy levels parsed from an ExoMol diatomic ``.states`` file.

    Arrays are indexed directly by ExoMol state id (index 0 is unused padding),
    so a transition's ``upper_id``/``lower_id`` look up energy/degeneracy in O(1).
    """

    energy_cm: np.ndarray          # term value above the X(v=0,J_min) ground, cm⁻¹
    g_total: np.ndarray            # total statistical weight
    j_value: np.ndarray            # rotational quantum number J (float; OH is half-integer)
    v_number: np.ndarray           # vibrational quantum number v
    is_upper: np.ndarray           # bool: electronic state == upper_label (e.g. 'A')
    upper_label: str
    lower_label: str
    band_origin_cm: dict[int, float]  # v' -> lowest term value of the upper electronic state

    @property
    def n_states(self) -> int:
        return int(self.energy_cm.shape[0] - 1)


@dataclass(frozen=True)
class EmissionConditions:
    """Plasma / gas conditions for an emission synthesis.

    ``t_vib_k`` defaults to ``t_rot_k`` (thermal / single-temperature limit).
    Broadening: a Gaussian apparatus function (``instrument_fwhm_cm``) is added
    in quadrature to thermal Doppler width; ``lorentz_hwhm_cm`` covers pressure
    and natural broadening (small in low-pressure plasmas).
    """

    t_rot_k: float
    t_vib_k: float | None = None
    instrument_fwhm_cm: float = 2.0
    lorentz_hwhm_cm: float = 0.0
    mass_da: float = OH_MASS_DA

    @property
    def t_vib(self) -> float:
        return self.t_rot_k if self.t_vib_k is None else self.t_vib_k

    @property
    def is_two_temperature(self) -> bool:
        return self.t_vib_k is not None and not np.isclose(self.t_vib_k, self.t_rot_k)


@dataclass
class EmissionSpectrum:
    """Result of an emission synthesis on a wavenumber grid."""

    wavenumber_cm: np.ndarray
    wavelength_nm: np.ndarray
    intensity: np.ndarray
    conditions: EmissionConditions
    metadata: dict[str, Any] = field(default_factory=dict)


# Gaussian FWHM -> HWHM helper (FWHM = 2 * HWHM for a Gaussian).
def _instrument_hwhm_cm(instrument_fwhm_cm: float) -> float:
    return 0.5 * instrument_fwhm_cm


@dataclass(frozen=True)
class StatesColumns:
    """Column indices (0-based) of the fields we need in an ExoMol ``.states`` file.

    ExoMol layouts vary by dataset: OH MoLLIST is 8 columns with the electronic
    label at index 7 and ``v`` at 5; N₂ WCCRMT carries an uncertainty column and
    7 quanta, putting ``ElecState`` at 8 and ``v`` at 9. Energy/g/J are always the
    first fields after the id.
    """

    energy: int = 1
    g_total: int = 2
    j: int = 3
    v: int = 5
    elec: int = 7
    min_fields: int = 8


# Pre-built column maps for the datasets used in this workspace.
OH_MOLLIST_COLUMNS = StatesColumns(v=5, elec=7, min_fields=8)
N2_WCCRMT_COLUMNS = StatesColumns(v=9, elec=8, min_fields=12)


def load_diatom_levels(
    states_path: Path,
    *,
    upper_label: str = "A",
    lower_label: str = "X",
    columns: StatesColumns = OH_MOLLIST_COLUMNS,
) -> DiatomLevels:
    """Parse an ExoMol diatomic ``.states`` file using a configurable column map.

    Defaults match OH MoLLIST (``id E g J e/f v F1/F2 elec``); pass
    ``columns=N2_WCCRMT_COLUMNS`` for the N₂ second-positive layout
    (``id E g J unc +/- e/f g/u ElecState v Fi N``). ``upper_label`` is matched by
    exact string equality against the electronic-state field (``"A"``, ``"C3Piu"``).
    """
    ids: list[int] = []
    energies: list[float] = []
    g_tot: list[float] = []
    j_vals: list[float] = []
    v_nums: list[int] = []
    elec: list[str] = []

    for raw_line in iter_bz2_text_lines(states_path):
        parts = raw_line.split()
        if len(parts) < columns.min_fields:
            continue
        ids.append(int(parts[0]))
        energies.append(float(parts[columns.energy]))
        g_tot.append(float(parts[columns.g_total]))
        j_vals.append(float(parts[columns.j]))
        v_nums.append(int(parts[columns.v]))
        elec.append(parts[columns.elec])

    if not ids:
        raise RuntimeError(f"No states parsed from {states_path}")

    max_id = max(ids)
    energy_cm = np.full(max_id + 1, np.nan, dtype=np.float64)
    g_total = np.zeros(max_id + 1, dtype=np.float64)
    j_value = np.full(max_id + 1, -1.0, dtype=np.float64)
    v_number = np.full(max_id + 1, -1, dtype=np.int32)
    is_upper = np.zeros(max_id + 1, dtype=bool)

    for sid, e, g, j, v, es in zip(ids, energies, g_tot, j_vals, v_nums, elec):
        energy_cm[sid] = e
        g_total[sid] = g
        j_value[sid] = j
        v_number[sid] = v
        is_upper[sid] = es == upper_label

    # Band origins: lowest term value among upper-state levels for each v'.
    band_origin: dict[int, float] = {}
    for sid in ids:
        if not is_upper[sid]:
            continue
        v = int(v_number[sid])
        e = float(energy_cm[sid])
        if v not in band_origin or e < band_origin[v]:
            band_origin[v] = e

    return DiatomLevels(
        energy_cm=energy_cm,
        g_total=g_total,
        j_value=j_value,
        v_number=v_number,
        is_upper=is_upper,
        upper_label=upper_label,
        lower_label=lower_label,
        band_origin_cm=band_origin,
    )


def collect_emission_lines(
    trans_path: Path,
    levels: DiatomLevels,
    conditions: EmissionConditions,
    window: SpectralWindow,
    *,
    wing_cm: float = 5.0,
    relative_intensity_floor: float = 1.0e-6,
) -> tuple[np.ndarray, np.ndarray, dict[str, int]]:
    """Read ``.trans`` and return (line_wavenumber, line_emission_intensity, stats).

    Only transitions whose upper level is in the upper electronic state and whose
    wavenumber falls inside ``[wn_min - wing, wn_max + wing]`` are kept. Lines
    weaker than ``relative_intensity_floor`` times the strongest are dropped.
    """
    c2 = SECOND_RADIATION_CONSTANT_CM_K
    t_rot = conditions.t_rot_k
    t_vib = conditions.t_vib
    origins = levels.band_origin_cm

    search_min = window.wn_min - wing_cm
    search_max = window.wn_max + wing_cm

    line_wn: list[float] = []
    line_int: list[float] = []
    stats = {"parsed": 0, "in_window": 0, "kept": 0}

    for raw_line in iter_bz2_text_lines(trans_path):
        parts = raw_line.split()
        if len(parts) < 3:
            continue
        upper_id = int(parts[0])
        lower_id = int(parts[1])
        a_value = float(parts[2])
        stats["parsed"] += 1

        if upper_id >= levels.energy_cm.shape[0] or lower_id >= levels.energy_cm.shape[0]:
            continue
        if not levels.is_upper[upper_id]:
            continue  # emission populates the upper electronic state only

        e_up = levels.energy_cm[upper_id]
        e_low = levels.energy_cm[lower_id]
        nu = e_up - e_low
        if nu < search_min or nu > search_max:
            continue
        stats["in_window"] += 1

        g_up = levels.g_total[upper_id]
        v_up = int(levels.v_number[upper_id])
        g_vib = origins.get(v_up, e_up)
        e_rot = e_up - g_vib

        # Two-temperature upper-state population (single-T when t_vib == t_rot).
        population = g_up * np.exp(-c2 * g_vib / t_vib) * np.exp(-c2 * e_rot / t_rot)
        # Spontaneous emission energy intensity: N_upper * A * (h c ν) ∝ pop * A * ν.
        intensity = population * a_value * nu

        line_wn.append(nu)
        line_int.append(intensity)
        stats["kept"] += 1

    wn = np.asarray(line_wn, dtype=np.float64)
    inten = np.asarray(line_int, dtype=np.float64)
    if inten.size:
        peak = inten.max()
        if peak > 0:
            mask = inten >= relative_intensity_floor * peak
            wn, inten = wn[mask], inten[mask]
    return wn, inten, stats


@dataclass
class PrecomputedLines:
    """In-window upper-state transitions with temperature-independent factors fixed.

    Extracted in a single streaming pass over a (possibly huge) ``.trans`` file so
    that a temperature scan can recompute intensities in memory without re-reading
    the file. ``band_origin`` is the upper electronic-vibrational band origin for
    each line, so ``e_rot = e_upper - band_origin`` and the two-temperature
    population is ``g_upper · exp(-c₂·band_origin/T_vib) · exp(-c₂·e_rot/T_rot)``.
    """

    wavenumber: np.ndarray
    a_value: np.ndarray
    g_upper: np.ndarray
    e_upper: np.ndarray
    band_origin: np.ndarray
    n_scanned: int

    @property
    def e_rot(self) -> np.ndarray:
        return self.e_upper - self.band_origin


def precompute_emission_lines(
    trans_path: Path,
    levels: DiatomLevels,
    window: SpectralWindow,
    *,
    wing_cm: float = 5.0,
) -> PrecomputedLines:
    """One streaming pass over ``.trans``; keep in-window lines whose upper level is
    in the upper electronic state. The transition wavenumber (4th column, when
    present) is used for the window test to avoid an energy lookup per line."""
    search_min = window.wn_min - wing_cm
    search_max = window.wn_max + wing_cm
    energy = levels.energy_cm
    g_total = levels.g_total
    v_number = levels.v_number
    is_upper = levels.is_upper
    origins = levels.band_origin_cm
    n_states = energy.shape[0]

    wn: list[float] = []
    av: list[float] = []
    gu: list[float] = []
    eu: list[float] = []
    bo: list[float] = []
    scanned = 0

    for raw_line in iter_bz2_text_lines(trans_path):
        parts = raw_line.split()
        if len(parts) < 3:
            continue
        scanned += 1
        upper_id = int(parts[0])
        if upper_id >= n_states or not is_upper[upper_id]:
            continue
        if len(parts) >= 4:
            nu = float(parts[3])
        else:
            lower_id = int(parts[1])
            if lower_id >= n_states:
                continue
            nu = float(energy[upper_id] - energy[lower_id])
        if nu < search_min or nu > search_max:
            continue
        wn.append(nu)
        av.append(float(parts[2]))
        gu.append(float(g_total[upper_id]))
        eu.append(float(energy[upper_id]))
        bo.append(float(origins.get(int(v_number[upper_id]), energy[upper_id])))

    return PrecomputedLines(
        wavenumber=np.asarray(wn, dtype=np.float64),
        a_value=np.asarray(av, dtype=np.float64),
        g_upper=np.asarray(gu, dtype=np.float64),
        e_upper=np.asarray(eu, dtype=np.float64),
        band_origin=np.asarray(bo, dtype=np.float64),
        n_scanned=scanned,
    )


def _gaussian_hwhm_for(window: SpectralWindow, conditions: EmissionConditions) -> float:
    window_center = 0.5 * (window.wn_min + window.wn_max)
    gauss_doppler = float(doppler_hwhm_cm(np.asarray([window_center]), conditions.t_rot_k, conditions.mass_da)[0])
    return float(np.hypot(gauss_doppler, _instrument_hwhm_cm(conditions.instrument_fwhm_cm)))


def synthesize_from_lines(
    lines: PrecomputedLines,
    conditions: EmissionConditions,
    window: SpectralWindow,
    *,
    relative_intensity_floor: float = 1.0e-6,
) -> EmissionSpectrum:
    """Fast synthesis from precomputed lines for a given (T_rot, T_vib). No file I/O."""
    c2 = SECOND_RADIATION_CONSTANT_CM_K
    t_rot = conditions.t_rot_k
    t_vib = conditions.t_vib

    population = lines.g_upper * np.exp(-c2 * lines.band_origin / t_vib) * np.exp(-c2 * lines.e_rot / t_rot)
    intensity = population * lines.a_value * lines.wavenumber

    grid = build_grid(window)
    spectrum = np.zeros_like(grid)
    gaussian_hwhm = _gaussian_hwhm_for(window, conditions)
    half_width = max(5.0, 10.0 * (gaussian_hwhm + conditions.lorentz_hwhm_cm))

    if intensity.size:
        peak = float(intensity.max())
        keep = intensity >= relative_intensity_floor * peak if peak > 0 else np.ones_like(intensity, dtype=bool)
        centers = lines.wavenumber[keep]
        weights = intensity[keep]
        for center, weight in zip(centers, weights):
            lo = np.searchsorted(grid, center - half_width, side="left")
            hi = np.searchsorted(grid, center + half_width, side="right")
            if hi <= lo:
                continue
            local = grid[lo:hi]
            spectrum[lo:hi] += weight * voigt_profile_cm(local, float(center), gaussian_hwhm, conditions.lorentz_hwhm_cm)
        n_lines = int(weights.size)
    else:
        n_lines = 0

    metadata: dict[str, Any] = {
        "n_lines": n_lines,
        "n_scanned": lines.n_scanned,
        "t_rot_k": t_rot,
        "t_vib_k": t_vib,
        "two_temperature": conditions.is_two_temperature,
        "instrument_fwhm_cm": conditions.instrument_fwhm_cm,
        "gaussian_hwhm_cm": gaussian_hwhm,
        "lorentz_hwhm_cm": conditions.lorentz_hwhm_cm,
    }
    return EmissionSpectrum(
        wavenumber_cm=grid,
        wavelength_nm=1.0e7 / grid,
        intensity=spectrum,
        conditions=conditions,
        metadata=metadata,
    )


def synthesize_emission(
    states_path: Path,
    trans_path: Path,
    conditions: EmissionConditions,
    window: SpectralWindow,
    *,
    upper_label: str = "A",
    lower_label: str = "X",
    levels: DiatomLevels | None = None,
    wing_cm: float = 5.0,
) -> EmissionSpectrum:
    """Synthesize an electronic-band emission spectrum on the window grid.

    Pass a pre-loaded ``levels`` to avoid re-parsing ``.states`` across a scan.
    """
    if levels is None:
        levels = load_diatom_levels(states_path, upper_label=upper_label, lower_label=lower_label)

    line_wn, line_int, stats = collect_emission_lines(
        trans_path, levels, conditions, window, wing_cm=wing_cm
    )

    grid = build_grid(window)
    spectrum = np.zeros_like(grid)

    # Doppler width is evaluated at the window center (negligible variation across
    # the narrow A-X window) and combined in quadrature with the instrument Gaussian.
    window_center = 0.5 * (window.wn_min + window.wn_max)
    gauss_doppler = float(doppler_hwhm_cm(np.asarray([window_center]), conditions.t_rot_k, conditions.mass_da)[0])
    instr_hwhm = _instrument_hwhm_cm(conditions.instrument_fwhm_cm)
    gaussian_hwhm = float(np.hypot(gauss_doppler, instr_hwhm))

    # Add each line as a Voigt profile over a local slice for efficiency.
    half_width = max(wing_cm, 10.0 * (gaussian_hwhm + conditions.lorentz_hwhm_cm))
    for center, weight in zip(line_wn, line_int):
        lo = np.searchsorted(grid, center - half_width, side="left")
        hi = np.searchsorted(grid, center + half_width, side="right")
        if hi <= lo:
            continue
        local = grid[lo:hi]
        profile = voigt_profile_cm(local, float(center), gaussian_hwhm, conditions.lorentz_hwhm_cm)
        spectrum[lo:hi] += weight * profile

    wavelength_nm = 1.0e7 / grid

    metadata: dict[str, Any] = {
        "n_lines": int(line_wn.size),
        "t_rot_k": conditions.t_rot_k,
        "t_vib_k": conditions.t_vib,
        "two_temperature": conditions.is_two_temperature,
        "instrument_fwhm_cm": conditions.instrument_fwhm_cm,
        "gaussian_hwhm_cm": gaussian_hwhm,
        "lorentz_hwhm_cm": conditions.lorentz_hwhm_cm,
        "upper_label": upper_label,
        "lower_label": lower_label,
        **stats,
    }
    return EmissionSpectrum(
        wavenumber_cm=grid,
        wavelength_nm=wavelength_nm,
        intensity=spectrum,
        conditions=conditions,
        metadata=metadata,
    )


# --------------------------------------------------------------------------- #
# Comparison helpers against measured spectra (wavelength, intensity CSVs).
# --------------------------------------------------------------------------- #
def area_normalize(x: np.ndarray, y: np.ndarray) -> np.ndarray:
    """Normalize ``y`` to unit integral over ``x`` (trapezoid). Matches the way
    USLTPSS-style fit overlays are area-normalized to the measurement."""
    area = float(np.trapz(y, x)) if hasattr(np, "trapz") else float(np.trapezoid(y, x))
    if area <= 0.0:
        return y
    return y / area


def load_measured_csv(path: Path) -> tuple[np.ndarray, np.ndarray]:
    """Load a two-(or more-)column wavelength[nm], intensity CSV. Extra trailing
    empty columns (as in Example_2) are ignored; only the first two are read."""
    wl: list[float] = []
    inten: list[float] = []
    with path.open("r", encoding="utf-8") as handle:
        for raw in handle:
            row = raw.strip()
            if not row:
                continue
            cells = row.split(",")
            try:
                x = float(cells[0])
                y = float(cells[1])
            except (ValueError, IndexError):
                continue
            wl.append(x)
            inten.append(y)
    return np.asarray(wl, dtype=np.float64), np.asarray(inten, dtype=np.float64)


def resample_to(model_nm: np.ndarray, model_y: np.ndarray, target_nm: np.ndarray) -> np.ndarray:
    """Interpolate a model spectrum onto a target wavelength grid.

    ``model_nm`` is descending when derived from an ascending wavenumber grid, so
    it is sorted ascending before interpolation.
    """
    order = np.argsort(model_nm)
    return np.interp(target_nm, model_nm[order], model_y[order], left=0.0, right=0.0)


def rms_residual(measured_y: np.ndarray, model_y: np.ndarray) -> float:
    """Root-mean-square residual between two equal-length, comparably-scaled series."""
    diff = measured_y - model_y
    return float(np.sqrt(np.mean(diff * diff)))
