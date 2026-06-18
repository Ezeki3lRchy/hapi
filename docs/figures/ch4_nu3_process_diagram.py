"""Generate the CH4 nu3 Boltzmann-vs-Treanor process diagram.

Run:
    ~/hapi-venv/bin/python docs/figures/ch4_nu3_process_diagram.py

Output:
    docs/ch4_nu3_process_diagram.svg

Academic/publication style. Shared inputs at top, two parallel columns in
the middle (path (a) LTE/Boltzmann vs path (b) non-LTE/Treanor), shared
line-shape and Beer-Lambert machinery at the bottom. The 'emphasis' fill
marks the steps that distinguish the two paths; everything else is white.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt

from _style import Box, draw_arrow, draw_box, draw_title, setup_figure


def build_figure():
    W, H = 1100, 944
    fig, ax = setup_figure(W, H)

    draw_title(
        ax, W / 2, H - 32,
        r"CH$_4$ $\nu_3$ absorption:  Boltzmann / HITRAN (a)  vs  Treanor non-LTE (b)",
        "Shared trunk at top; per-line ratio bridges the population-model substitution to spectrum effects.",
    )

    # Layout
    trunk_w = 820
    trunk_x = (W - trunk_w) / 2
    col_w = 520
    left_col_x = 30
    right_col_x = W - col_w - 30

    box_h = 62
    box_h_ratio = 88  # box 6 carries title + subtitle + tall fraction
    row_gap = 22
    title_only_h = 42

    y_input      = H - 100
    y_branch_hdr = y_input - box_h - row_gap
    y_col_row1   = y_branch_hdr - box_h - row_gap
    y_col_row2   = y_col_row1 - box_h - row_gap
    y_col_row3   = y_col_row2 - box_h - row_gap
    y_ratio      = y_col_row3 - box_h - row_gap
    y_voigt      = y_ratio - box_h_ratio - row_gap
    y_beer       = y_voigt - box_h - row_gap
    y_output     = y_beer - title_only_h - row_gap

    # Shared input
    inputs = Box(
        x=trunk_x, y=y_input - box_h, w=trunk_w, h=box_h,
        style="input", tag="1.",
        title="Inputs: gas case + line list + spectral grid",
        math=r"$P,\ x,\ L,\quad S_i,\ \tilde{\nu}_i,\ E_l,\ g_l,\ g_u,\quad \tilde{\nu}_{\min},\ \tilde{\nu}_{\max},\ \Delta\tilde{\nu}$",
    )
    draw_box(ax, inputs)

    # Branch headers
    boltz_header = Box(
        x=left_col_x, y=y_branch_hdr - box_h, w=col_w, h=box_h,
        style="emphasis", tag="(a) 2.",
        title="LTE assumption: one temperature",
        math=r"$T$  (single temperature)",
    )
    treanor_header = Box(
        x=right_col_x, y=y_branch_hdr - box_h, w=col_w, h=box_h,
        style="emphasis", tag="(b) 2.",
        title="non-LTE assumption: two temperatures",
        math=r"$T_0$ (translational),  $T_v$ (vibrational)",
    )
    draw_box(ax, boltz_header)
    draw_box(ax, treanor_header)

    # Left column (Boltzmann)
    boltz_scaling = Box(
        x=left_col_x, y=y_col_row1 - box_h, w=col_w, h=box_h,
        style="emphasis", tag="(a) 3.",
        title="Boltzmann population law  (folded into HITRAN $S(T)$)",
        math=r"$S(T) = S(T_\mathrm{ref})\, \frac{Q(T_\mathrm{ref})}{Q(T)}\, e^{-c_2 E_l (1/T - 1/T_\mathrm{ref})}$",
    )
    boltz_stim = Box(
        x=left_col_x, y=y_col_row2 - box_h, w=col_w, h=box_h,
        style="emphasis", tag="(a) 4.",
        title="Stimulated-emission correction  (folded into $S(T)$)",
        math=r"$\times\ \frac{1 - e^{-c_2 \tilde{\nu}/T}}{1 - e^{-c_2 \tilde{\nu}/T_\mathrm{ref}}}$",
    )
    boltz_note = Box(
        x=left_col_x, y=y_col_row3 - box_h, w=col_w, h=box_h,
        style="process", tag="(a) 5.",
        title=r"Populations folded into $S(T)$ (recoverable as $n_l^{\mathrm{B}}$)",
        math=r"$n_l^{\mathrm{B}}(v_{3,l};\, T_0)$  recovers from $T_0$ and $E_l$;  not a named step",
    )
    draw_box(ax, boltz_scaling)
    draw_box(ax, boltz_stim)
    draw_box(ax, boltz_note)

    # Right column (Treanor)
    tr_dist = Box(
        x=right_col_x, y=y_col_row1 - box_h, w=col_w, h=box_h,
        style="emphasis", tag="(b) 3.",
        title="Treanor population law  (explicit relative distribution)",
        math=r"$f_\mathrm{Tr}(v_3;\, T_0, T_v) = N_{v_3} / N_0$",
    )
    tr_nv3 = Box(
        x=right_col_x, y=y_col_row2 - box_h, w=col_w, h=box_h,
        style="process", tag="(b) 4.",
        title="State populations (absolute)",
        math=r"$n(v_3) = n_\mathrm{total}\, f_\mathrm{Tr}(v_3)$",
    )
    tr_neff = Box(
        x=right_col_x, y=y_col_row3 - box_h, w=col_w, h=box_h,
        style="process", tag="(b) 5.",
        title="Per-line effective absorber (explicit)",
        math=r"$n_\mathrm{eff} = n_l - (g_l / g_u)\, n_u$",
    )
    draw_box(ax, tr_dist)
    draw_box(ax, tr_nv3)
    draw_box(ax, tr_neff)

    # Shared tail
    ratio = Box(
        x=trunk_x, y=y_ratio - box_h_ratio, w=trunk_w, h=box_h_ratio,
        style="emphasis", tag="6.",
        title="Per-line non-LTE / LTE absorbance ratio  (whole-process effect)",
        subtitle=r"From (a):  $T_0$ $\rightarrow$ re-evaluate $n_l^{\mathrm{B}}$ per line.   From (b):  $n_l^{\mathrm{Tr}}$ per line.",
        math=r"$\alpha_i^{\mathrm{Tr}}(\tilde{\nu}) = \frac{n_l^{\mathrm{Tr}}(v_{3,l};\, T_0, T_v)}{n_l^{\mathrm{B}}(v_{3,l};\, T_0)}\; \alpha_i^{\mathrm{LTE}}(\tilde{\nu};\, T_0)$",
    )
    voigt = Box(
        x=trunk_x, y=y_voigt - box_h, w=trunk_w, h=box_h,
        style="process", tag="7.",
        title="Voigt broadening (Doppler + Lorentz)",
        math=r"$\alpha(\tilde{\nu}) = \sum_i n_{\mathrm{eff},i}\, S_i\, \phi_i(\tilde{\nu};\, T, P)$",
    )
    beer = Box(
        x=trunk_x, y=y_beer - box_h, w=trunk_w, h=box_h,
        style="process", tag="8.",
        title="Beer-Lambert propagation",
        math=r"$\tau(\tilde{\nu}) = e^{-\alpha(\tilde{\nu}) L}, \qquad A(\tilde{\nu}) = -\ln \tau(\tilde{\nu})$",
    )
    out = Box(
        x=trunk_x, y=y_output - title_only_h, w=trunk_w, h=title_only_h,
        style="output", tag="9.",
        title="Absorbance spectrum   (LTE or non-LTE, depending on the branch)",
    )
    draw_box(ax, ratio)
    draw_box(ax, voigt)
    draw_box(ax, beer)
    draw_box(ax, out)

    # Arrows
    draw_arrow(ax, inputs.cx, inputs.bottom, boltz_header.cx, boltz_header.top)
    draw_arrow(ax, inputs.cx, inputs.bottom, treanor_header.cx, treanor_header.top)

    draw_arrow(ax, boltz_header.cx, boltz_header.bottom, boltz_scaling.cx, boltz_scaling.top)
    draw_arrow(ax, boltz_scaling.cx, boltz_scaling.bottom, boltz_stim.cx, boltz_stim.top)
    draw_arrow(ax, boltz_stim.cx, boltz_stim.bottom, boltz_note.cx, boltz_note.top)

    draw_arrow(ax, treanor_header.cx, treanor_header.bottom, tr_dist.cx, tr_dist.top)
    draw_arrow(ax, tr_dist.cx, tr_dist.bottom, tr_nv3.cx, tr_nv3.top)
    draw_arrow(ax, tr_nv3.cx, tr_nv3.bottom, tr_neff.cx, tr_neff.top)

    draw_arrow(ax, boltz_note.cx, boltz_note.bottom, ratio.cx, ratio.top)
    draw_arrow(ax, tr_neff.cx, tr_neff.bottom, ratio.cx, ratio.top)

    draw_arrow(ax, ratio.cx, ratio.bottom, voigt.cx, voigt.top)
    draw_arrow(ax, voigt.cx, voigt.bottom, beer.cx, beer.top)
    draw_arrow(ax, beer.cx, beer.bottom, out.cx, out.top)

    return fig


def main() -> None:
    out_path = Path(__file__).resolve().parents[1] / "ch4_nu3_process_diagram.svg"
    fig = build_figure()
    fig.savefig(out_path, format="svg", bbox_inches=None, pad_inches=0)
    plt.close(fig)
    print(f"wrote {out_path}  ({out_path.stat().st_size/1024:.1f} KB)")


if __name__ == "__main__":
    main()
