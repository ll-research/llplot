"""One plotting style for every project: SciencePlots (science + no-latex) plus the llplot palette layer.

    import llplot
    llplot.setup()
    fig, ax = llplot.figure("single")
    llplot.lines(ax, x, {"Monte Carlo": y1, "Sobol QMC": y2})
    llplot.savefig(fig, "fig/convergence.png")
"""
from pathlib import Path

import matplotlib
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap

__version__ = "0.1.0"
__all__ = ["setup", "figure", "lines", "image", "savefig",
           "CATEGORICAL", "SEQUENTIAL", "DIVERGING", "INK", "INK2", "MUTED", "WIDTHS"]

STYLES_DIR = Path(__file__).parent / "styles"
CATEGORICAL = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300", "#6250d6", "#e34948"]
INK, INK2, MUTED = "#0b0b0b", "#52514e", "#898781"
SEQUENTIAL = ["#cde2fb", "#9ec5f4", "#6da7ec", "#3987e5", "#256abf", "#184f95", "#0d366b"]  # one hue, light -> dark
DIVERGING = ["#184f95", "#3987e5", "#9ec5f4", "#f0efec", "#f3b0ae", "#e34948", "#a32a29"]   # blue <- gray -> red
WIDTHS = {"single": 3.5, "double": 7.2}  # inches: one / two journal columns
COLORMAPS = {"llplot_seq": SEQUENTIAL, "llplot_div": DIVERGING, "am_seq": SEQUENTIAL, "am_div": DIVERGING}  # am_*: amkit names


def setup(grid=False, latex=False):
    """Apply the house style and register the colormaps llplot_seq / llplot_div.

    grid: add a light grid. latex: render text with LaTeX (needs a LaTeX install).
    """
    for name, colors in COLORMAPS.items():
        if name not in matplotlib.colormaps:
            matplotlib.colormaps.register(LinearSegmentedColormap.from_list(name, colors))
    names = ["science"] + ([] if latex else ["no-latex"]) + (["grid"] if grid else []) + ["llplot"]
    plt.style.use([STYLES_DIR / f"{n}.mplstyle" for n in names])
    plt.rcParams["image.cmap"] = "llplot_seq"


def figure(width="single", ratio=0.7, nrows=1, ncols=1, **kw):
    """plt.subplots at journal width ("single" 3.5 in, "double" 7.2 in, or inches); each panel keeps `ratio`."""
    w = WIDTHS.get(width, width)
    return plt.subplots(nrows, ncols, figsize=(w, w / ncols * ratio * nrows), **kw)


def lines(ax, x, series, err=None, label_ends=True, markers_max=12):
    """Plot named series in fixed palette order. err: optional {name: yerr}. Direct-labels <= 4 series."""
    ends = []
    for name, y in series.items():
        every = max(1, len(y) // markers_max)
        (ln,) = ax.plot(x, y, label=name, markevery=every)
        if err and name in err:
            ax.fill_between(x, [a - b for a, b in zip(y, err[name])], [a + b for a, b in zip(y, err[name])],
                            color=ln.get_color(), alpha=0.15, linewidth=0)
        ends.append((y[-1], name))
    if label_ends and len(series) <= 4:
        _label_ends(ax, x[-1], ends)
    if len(series) >= 2:
        ax.legend()
    return ax


def _label_ends(ax, x_end, ends, min_gap_pt=9):
    """Direct labels at line ends, nudged apart vertically so they never overlap."""
    fig = ax.figure
    fig.canvas.draw()
    to_pt = 72 / fig.dpi
    placed = sorted((ax.transData.transform((x_end, y))[1] * to_pt, y, name) for y, name in ends)
    for i in range(1, len(placed)):
        if placed[i][0] - placed[i - 1][0] < min_gap_pt:
            placed[i] = (placed[i - 1][0] + min_gap_pt, placed[i][1], placed[i][2])
    for pos, y, name in placed:
        dy = pos - ax.transData.transform((x_end, y))[1] * to_pt
        ax.annotate(name, (x_end, y), xytext=(4, dy), textcoords="offset points", va="center", fontsize="small", color=INK2)


def image(ax, data, label=None, diverging=False, **kw):
    """2-D field with the house colormap (llplot_seq, or llplot_div centred on 0) and a colorbar; no grid over data."""
    if diverging:
        vmax = float(abs(data).max())
        kw = {"cmap": "llplot_div", "vmin": -vmax, "vmax": vmax, **kw}
    im = ax.imshow(data, **kw)
    ax.grid(False)
    cb = ax.figure.colorbar(im, ax=ax)
    if label:
        cb.set_label(label)
    return im


def savefig(fig, path, max_kb=300):
    """Save within a size budget (keeps git history small) and close the figure. PNG dpi is lowered until it fits."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.suffix == ".png":
        for dpi in (200, 150, 110, 80):
            fig.savefig(path, dpi=dpi)
            if path.stat().st_size <= max_kb * 1024:
                break
    else:
        fig.savefig(path)
    size_kb = path.stat().st_size / 1024
    if size_kb > max_kb * (1 if path.suffix == ".png" else 3):
        print(f"[llplot] warning: {path} is {size_kb:.0f} kB; rasterize dense layers (rasterized=True) or use PNG")
    plt.close(fig)
    return path
