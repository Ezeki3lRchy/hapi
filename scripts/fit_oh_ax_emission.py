"""Fit OH A²Σ⁺–X²Π emission spectra against measured USLTPSS CSV files.

Forward model: research.emission (ExoMol OH MoLLIST line list).
- Single-temperature scan  -> rotational temperature (thermal case).
- Two-temperature scan      -> T_rot, T_vib (non-equilibrium case).

Both measured and model spectra are area-normalized before comparison, matching
the way the reference fit overlays are normalized. Outputs an overlay HTML and a
CSV of (wavelength_nm, measured, best_model) into artifacts/.

Run from the repo root:
    ~/hapi-venv/bin/python3 scripts/fit_oh_ax_emission.py
"""

from __future__ import annotations

import itertools
from pathlib import Path

import numpy as np
import plotly.graph_objects as go

from research.emission import (
    EmissionConditions,
    area_normalize,
    load_diatom_levels,
    load_measured_csv,
    resample_to,
    rms_residual,
    synthesize_emission,
)
from research.io import ensure_directory
from research.models import SpectralWindow

ROOT = Path(__file__).resolve().parents[1]
OH_DIR = ROOT / "exomol_db" / "OH_MoLLIST"
STATES = OH_DIR / "16O-1H__MoLLIST.states.bz2"
TRANS = OH_DIR / "16O-1H__MoLLIST.trans.bz2"
USLTPSS = ROOT / "USLTPSS"
ARTIFACTS = ROOT / "artifacts" / "oh_ax_emission_fits"


def window_from_measured(wl_nm: np.ndarray, *, pad_nm: float = 0.5, step_cm: float = 0.5) -> SpectralWindow:
    lo_nm = float(wl_nm.min()) - pad_nm
    hi_nm = float(wl_nm.max()) + pad_nm
    return SpectralWindow(wn_min=1.0e7 / hi_nm, wn_max=1.0e7 / lo_nm, wn_step=step_cm)


def evaluate(levels, window, measured_nm, measured_norm, *, t_rot, t_vib, instr_fwhm_cm):
    """Synthesize one (t_rot, t_vib, instrument) point and return (rms, model_on_measured_grid)."""
    cond = EmissionConditions(t_rot_k=t_rot, t_vib_k=t_vib, instrument_fwhm_cm=instr_fwhm_cm)
    spec = synthesize_emission(STATES, TRANS, cond, window, levels=levels)
    model_on_grid = resample_to(spec.wavelength_nm, spec.intensity, measured_nm)
    model_norm = area_normalize(measured_nm, model_on_grid)
    return rms_residual(measured_norm, model_norm), model_norm


def fit_case(
    name: str,
    csv_path: Path,
    levels,
    *,
    t_rot_grid,
    t_vib_grid,
    instr_grid,
):
    print(f"\n=== {name} ===")
    measured_nm, measured_raw = load_measured_csv(csv_path)
    window = window_from_measured(measured_nm)
    measured_norm = area_normalize(measured_nm, measured_raw)
    print(f"  points={measured_nm.size}  range={measured_nm.min():.2f}-{measured_nm.max():.2f} nm")

    best = None  # (rms, t_rot, t_vib, instr, model_norm)
    for t_rot, instr in itertools.product(t_rot_grid, instr_grid):
        for t_vib in t_vib_grid:
            # t_vib None means lock to t_rot (single temperature).
            tv = t_rot if t_vib is None else t_vib
            rms, model_norm = evaluate(
                levels, window, measured_nm, measured_norm,
                t_rot=t_rot, t_vib=tv, instr_fwhm_cm=instr,
            )
            if best is None or rms < best[0]:
                best = (rms, t_rot, tv, instr, model_norm)

    rms, t_rot, t_vib, instr, model_norm = best
    tag = "single-T" if np.isclose(t_rot, t_vib) else "two-T"
    print(f"  BEST [{tag}]  T_rot={t_rot:.0f} K  T_vib={t_vib:.0f} K  instr_FWHM={instr:.1f} cm⁻¹  RMS={rms:.3e}")

    ensure_directory(ARTIFACTS)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=measured_nm, y=measured_norm, mode="lines", name="measured", line=dict(color="black", width=1)))
    fig.add_trace(go.Scatter(x=measured_nm, y=model_norm, mode="lines", name=f"model T_rot={t_rot:.0f}K T_vib={t_vib:.0f}K", line=dict(color="crimson", width=2)))
    fig.update_layout(
        title=f"OH A-X emission fit — {name} (RMS={rms:.2e})",
        xaxis_title="Wavelength (nm)", yaxis_title="Area-normalized intensity",
        template="plotly_white",
    )
    html_path = ARTIFACTS / f"{name}_fit.html"
    fig.write_html(html_path, include_plotlyjs="cdn")

    csv_out = ARTIFACTS / f"{name}_fit.csv"
    with csv_out.open("w", encoding="utf-8") as fh:
        fh.write("wavelength_nm,measured_norm,model_norm\n")
        for x, m, md in zip(measured_nm, measured_norm, model_norm):
            fh.write(f"{x:.5f},{m:.8e},{md:.8e}\n")
    print(f"  wrote {html_path.name}, {csv_out.name}")
    return best


def main() -> None:
    levels = load_diatom_levels(STATES)

    # Thermal case: single temperature (t_vib locked to t_rot via None).
    fit_case(
        "Example_2_thermal_OH",
        USLTPSS / "Example_2_thermal_OH_surfatron.csv",
        levels,
        t_rot_grid=range(800, 4001, 200),
        t_vib_grid=[None],
        instr_grid=[2.0, 4.0, 6.0, 8.0],
    )

    # Non-equilibrium case: independent T_rot and T_vib (two-temperature).
    fit_case(
        "Example_3_nonequilibrium_OH",
        USLTPSS / "Example_3_non-equilibrium_OH.csv",
        levels,
        t_rot_grid=range(600, 3001, 300),
        t_vib_grid=[1000, 2000, 3000, 4000, 6000, 8000],
        instr_grid=[3.0, 6.0, 9.0],
    )


if __name__ == "__main__":
    main()
