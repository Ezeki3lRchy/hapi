"""Generate the standard HITRAN absorbance-spectrum workflow diagram.

Run:
    ~/hapi-venv/bin/python docs/figures/hitran_standard_workflow.py

Output:
    docs/hitran_standard_workflow.svg

Academic/publication style. Seven-step linear pipeline. The key physics step
(intensity rescaling) carries the 'emphasis' fill; everything else is white.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt

from _style import Box, draw_arrow, draw_box, draw_title, setup_figure


def build_figure():
    W, H = 1100, 1040
    fig, ax = setup_figure(W, H)

    draw_title(
        ax, W / 2, H - 32,
        r"Standard HITRAN workflow:  line list  $\to$  absorbance spectrum",
        r"LTE single-temperature $T$.  HITRAN provides pre-tabulated line intensities at $T_\mathrm{ref} = 296\,\mathrm{K}$.",
    )

    col_w = 840
    col_x = (W - col_w) / 2
    box_h = 78
    tall_h = 92
    title_only_h = 46
    row_gap = 22

    y_cursor = H - 90

    def next_y(h=box_h):
        nonlocal y_cursor
        top_y = y_cursor
        y_cursor = y_cursor - h - row_gap
        return top_y - h

    boxes = [
        Box(
            x=col_x, y=next_y(), w=col_w, h=box_h, style="input", tag="1.",
            title="Load HITRAN line list",
            math=r"per line: $\tilde{\nu}_i,\ S_i(T_\mathrm{ref}),\ E''_i,\ \gamma_\mathrm{air},\ \gamma_\mathrm{self},\ n_\mathrm{air},\ \delta_\mathrm{air}$",
        ),
        Box(
            x=col_x, y=next_y(), w=col_w, h=box_h, style="input", tag="2.",
            title="Set gas case and spectral grid",
            math=r"$T,\ P,\ x,\ L,\quad [\tilde{\nu}_{\min},\ \tilde{\nu}_{\max}],\ \Delta\tilde{\nu}$",
        ),
        Box(
            x=col_x, y=next_y(h=tall_h), w=col_w, h=tall_h, style="emphasis", tag="3.",
            title=r"Rescale line intensities from $T_\mathrm{ref}$ to target $T$  (Boltzmann + stim. emission)",
            math=r"$S_i(T) = S_i(T_\mathrm{ref})\, \dfrac{Q(T_\mathrm{ref})}{Q(T)}\, e^{-c_2 E''_i (1/T - 1/T_\mathrm{ref})}\, \dfrac{1 - e^{-c_2 \tilde{\nu}_i/T}}{1 - e^{-c_2 \tilde{\nu}_i/T_\mathrm{ref}}}$",
        ),
        Box(
            x=col_x, y=next_y(h=tall_h), w=col_w, h=tall_h, style="process", tag="4.",
            title=r"Build Voigt profile for each line  (Doppler $\oplus$ Lorentz)",
            math=r"$\alpha_D \propto \tilde{\nu}_i\sqrt{T/M}, \quad \gamma_L = \gamma_\mathrm{air}(P_\mathrm{air}/P_\mathrm{ref})(T_\mathrm{ref}/T)^{n_\mathrm{air}} + \gamma_\mathrm{self}\, x$",
        ),
        Box(
            x=col_x, y=next_y(), w=col_w, h=box_h, style="process", tag="5.",
            title=r"Sum lines $\to$ absorption coefficient",
            math=r"$\alpha(\tilde{\nu}) = n_\mathrm{total}\, \sum_i S_i(T)\, \phi_{\mathrm{V},i}(\tilde{\nu}; T, P),\quad n_\mathrm{total} = Px/(k_B T)$",
        ),
        Box(
            x=col_x, y=next_y(), w=col_w, h=box_h, style="process", tag="6.",
            title="Beer-Lambert propagation",
            math=r"$\tau(\tilde{\nu}) = e^{-\alpha(\tilde{\nu}) L}, \qquad A(\tilde{\nu}) = -\ln \tau(\tilde{\nu})$",
        ),
        Box(
            x=col_x, y=next_y(h=title_only_h), w=col_w, h=title_only_h, style="output", tag="7.",
            title=r"Absorbance spectrum   $A(\tilde{\nu})$   (LTE at a single temperature $T$)",
        ),
    ]
    for b in boxes:
        draw_box(ax, b)
    for upper, lower in zip(boxes[:-1], boxes[1:]):
        draw_arrow(ax, upper.cx, upper.bottom, lower.cx, lower.top)

    return fig


def main() -> None:
    out_path = Path(__file__).resolve().parents[1] / "hitran_standard_workflow.svg"
    fig = build_figure()
    fig.savefig(out_path, format="svg", bbox_inches=None, pad_inches=0)
    plt.close(fig)
    print(f"wrote {out_path}  ({out_path.stat().st_size/1024:.1f} KB)")


if __name__ == "__main__":
    main()
