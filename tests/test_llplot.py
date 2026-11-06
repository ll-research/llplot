import matplotlib

matplotlib.use("Agg")
import numpy as np  # noqa: E402
import pytest  # noqa: E402

import llplot  # noqa: E402


@pytest.fixture(autouse=True)
def style():
    llplot.setup()
    llplot.setup()  # twice is fine


def test_figure_widths():
    for name, inches in llplot.WIDTHS.items():
        fig, _ = llplot.figure(name)
        assert fig.get_size_inches()[0] == pytest.approx(inches)
        matplotlib.pyplot.close(fig)


def test_colormaps_and_palette():
    assert matplotlib.rcParams["image.cmap"] == "llplot_seq"
    assert "am_seq" in matplotlib.colormaps and "am_div" in matplotlib.colormaps
    first = matplotlib.rcParams["axes.prop_cycle"].by_key()["color"][0]
    assert matplotlib.colors.to_hex(first) == llplot.CATEGORICAL[0]


def test_lines_direct_labels():
    fig, ax = llplot.figure()
    x = np.linspace(0, 1, 30)
    llplot.lines(ax, x, {"a": x, "b": x + 0.001})
    labels = [t.get_text() for t in ax.texts]
    assert labels == ["a", "b"]
    to_pt = 72 / fig.dpi
    final = [ax.transData.transform(t.xy)[1] * to_pt + t.xyann[1] for t in ax.texts]
    assert final[1] - final[0] == pytest.approx(9)  # nudged apart by min_gap_pt
    matplotlib.pyplot.close(fig)


def test_image_diverging_is_symmetric():
    fig, ax = llplot.figure()
    im = llplot.image(ax, np.array([[-1.0, 3.0]]), diverging=True)
    assert im.get_clim() == (-3.0, 3.0)
    matplotlib.pyplot.close(fig)


def test_savefig_size_budget(tmp_path):
    fig, ax = llplot.figure("double")
    ax.imshow(np.random.default_rng(0).random((80, 80)))  # ~61 kB at 200 dpi, ~43 kB at 110
    path = llplot.savefig(fig, tmp_path / "sub" / "noise.png", max_kb=50)
    assert path.exists() and path.stat().st_size <= 50 * 1024
    assert not matplotlib.pyplot.get_fignums()
