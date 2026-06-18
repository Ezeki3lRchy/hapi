"""Generate the standard ExoMol absorbance-spectrum workflow diagram.

Run:
    ~/hapi-venv/bin/python docs/figures/exomol_standard_workflow.py

Output:
    docs/exomol_standard_workflow.svg

Academic/publication style. Eight-step linear pipeline. The two physics steps
that make ExoMol different from HITRAN (compute Q(T) and build S(T) from the
Einstein A coefficient) carry the 'emphasis' fill. HITRAN pre-tabulates these
quantities; ExoMol makes you compute them.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt

from _style import Box, draw_arrow, draw_box, draw_title, setup_figure


def build_figure():
    W, H = 1100, 1170
    fig, ax = setup_figure(W, H)

    draw_title(
        ax, W / 2, H - 32,
        r"Standard ExoMol workflow:  states + transitions  $\to$  absorbance spectrum",
        r"Line intensities are built from Einstein $A$ coefficients and a partition function $Q(T)$ — not rescaled from a reference-temperature table.",
    )

    col_w = 840
    col_x = (W - col_w) / 2
    box_h = 78
    tall_h = 92
    title_only_h = 46
    row_gap = 20

    y_cursor = H - 90

    def next_y(h=box_h):
        nonlocal y_cursor
        top_y = y_cursor
        y_cursor = y_cursor - h - row_gap
        return top_y - h

    boxes = [
        Box(
            x=col_x, y=next_y(h=tall_h), w=col_w, h=tall_h, style="input", tag="1.",
            title="Download ExoMol dataset files",
            math=r".def (metadata) | .states ($E_i, g_i$, quantum numbers) | .trans ($A_{ul}$, upper/lower IDs) | optional .pf, .broad",
        ),
        Box(
            x=col_x, y=next_y(), w=col_w, h=box_h, style="input", tag="2.",
            title="Set gas case and spectral grid",
            math=r"$T,\ P,\ x,\ L,\quad [\tilde{\nu}_{\min},\ \tilde{\nu}_{\max}],\ \Delta\tilde{\nu}$",
        ),
        Box(
            x=col_x, y=next_y(), w=col_w, h=box_h, style="emphasis", tag="3.",
            title=r"Compute (or load) the partition function at $T$",
            math=r"$Q(T) = \sum_i g_i\, e^{-c_2 E_i / T}$   (or read from the .pf file)",
        ),
        Box(
            x=col_x, y=next_y(h=tall_h), w=col_w, h=tall_h, style="emphasis", tag="4.",
            title="Build line position and intensity from first principles",
            math=r"$\tilde{\nu}_i = E_u - E_l, \quad S_i(T) = \dfrac{g_u\, A_{ul}}{8\pi c\, \tilde{\nu}_i^{\,2}}\, \dfrac{e^{-c_2 E_l/T}\,[\,1 - e^{-c_2 \tilde{\nu}_i/T}\,]}{Q(T)}$",
        ),
        Box(
            x=col_x, y=next_y(h=tall_h), w=col_w, h=tall_h, style="process", tag="5.",
            title="Assign broadening (from .broad, from HITRAN proxy, or a default)",
            math=r"$\alpha_D \propto \tilde{\nu}_i\sqrt{T/M}, \quad \gamma_L = \gamma_\mathrm{ref}(P/P_\mathrm{ref})(T_\mathrm{ref}/T)^{n}$   per line / per $J$",
        ),
        Box(
            x=col_x, y=next_y(), w=col_w, h=box_h, style="process", tag="6.",
            title=r"Voigt profile + sum $\to$ absorption coefficient",
            math=r"$\alpha(\tilde{\nu}) = n_\mathrm{total}\, \sum_i S_i(T)\, \phi_{\mathrm{V},i}(\tilde{\nu}; T, P),\quad n_\mathrm{total} = Px/(k_B T)$",
        ),
        Box(
            x=col_x, y=next_y(), w=col_w, h=box_h, style="process", tag="7.",
            title="Beer-Lambert propagation",
            math=r"$\tau(\tilde{\nu}) = e^{-\alpha(\tilde{\nu}) L}, \qquad A(\tilde{\nu}) = -\ln \tau(\tilde{\nu})$",
        ),
        Box(
            x=col_x, y=next_y(h=title_only_h), w=col_w, h=title_only_h, style="output", tag="8.",
            title=r"Absorbance spectrum   $A(\tilde{\nu})$   (LTE at a single temperature $T$)",
        ),
    ]
    for b in boxes:
        draw_box(ax, b)
    for upper, lower in zip(boxes[:-1], boxes[1:]):
        draw_arrow(ax, upper.cx, upper.bottom, lower.cx, lower.top)

    return fig


def main() -> None:
    out_path = Path(__file__).resolve().parents[1] / "exomol_standard_workflow.svg"
    fig = build_figure()
    fig.savefig(out_path, format="svg", bbox_inches=None, pad_inches=0)
    plt.close(fig)
    print(f"wrote {out_path}  ({out_path.stat().st_size/1024:.1f} KB)")


if __name__ == "__main__":
    main()
