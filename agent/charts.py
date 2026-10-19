"""Turns a chart spec + a result DataFrame into a Plotly figure, using one fixed, validated palette.

Palette: the dataviz reference palette (validated with validate_palette.js: all checks pass in light
mode; three light slots sit below 3:1 contrast, so every chart also ships a table view).
Rules followed: color follows the entity (never its rank), at most 8 series, one y-axis,
2px lines, thin bars, hairline grid, a legend only when there are 2+ series.
"""
import pandas as pd
import plotly.graph_objects as go

SERIES = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300", "#6250d6", "#e34948"]
INK, INK_2, MUTED = "#0b0b0b", "#52514e", "#898781"
GRID, AXIS, SURFACE = "#e1e0d9", "#c3c2b7", "#fcfcfb"
FONT = 'system-ui, -apple-system, "Segoe UI", sans-serif'
MAX_SERIES = 8


def apply_filter(df: pd.DataFrame, filt: dict) -> pd.DataFrame:
    for col, val in (filt or {}).items():
        if col in df.columns:
            vals = val if isinstance(val, list) else [val]
            if pd.api.types.is_datetime64_any_dtype(df[col]):  # dates in a spec arrive as 'YYYY-MM-DD' text
                vals = pd.to_datetime(vals).tz_localize(None) if df[col].dt.tz is None else pd.to_datetime(vals, utc=True)
            df = df[df[col].isin(vals)]
    return df


def prepare(df: pd.DataFrame, spec: dict) -> pd.DataFrame:
    """Filter, sort and limit the rows a chart will show."""
    d = apply_filter(df.copy(), spec.get("filter"))
    y = spec["y"]
    if spec["type"] == "bar":
        d = d.sort_values(y, ascending=False)
        if spec.get("top_n"):
            d = d.head(int(spec["top_n"]))
    elif spec["type"] == "line":
        d = d.sort_values(spec["x"])
    return d


def _fmt(kind, values=None):
    """(hover format, tick format). Percent ticks get a decimal when the values are small."""
    small = values is not None and len(values) and float(abs(values).max()) < 0.1
    return {"percent": (".1%", ".1%" if small else ".0%"),
            "points": (".1%", ".1%" if small else ".0%"),  # a gap in percentage points, stored as a fraction
            "currency": ("$,.0f", "$,.0f"), "number": (",.0f", ",.0f"),
            "decimal": (",.2f", ",.2f")}.get(kind, (",.2f", ",.2f"))


def _color_map(values):
    """Stable entity -> color: sorted names, so a filter never repaints the survivors."""
    return {v: SERIES[i % len(SERIES)] for i, v in enumerate(sorted(map(str, values)))}


UNITS = {"percent": " (%)", "points": " (pts)", "currency": " ($)"}


def humanize(col: str) -> str:
    return col.replace("_", " ").strip().capitalize()


def axis_titles(spec: dict) -> tuple:
    """(category/time axis title, value axis title): from the spec, or derived from the column names."""
    x_title = spec.get("x_title") or humanize(spec["x"])
    y_title = spec.get("y_title") or humanize(spec["y"]) + UNITS.get(spec.get("y_format"), "")
    return x_title, y_title


def figure(df: pd.DataFrame, spec: dict, color_domain=None) -> go.Figure:
    """color_domain: every value the color column can take (from the unfiltered data), so a filter never
    changes which color an entity gets."""
    d = prepare(df, spec)
    x, y, color = spec["x"], spec["y"], spec.get("color") or None
    hover_fmt, tick_fmt = _fmt(spec.get("y_format"), d[y].dropna() if y in d else None)
    suffix = ""
    if spec.get("y_format") == "points":  # show a gap between rates as "+3.1 pts", not "3.1%"
        d[y] = d[y] * 100
        hover_fmt, tick_fmt, suffix = "+.1f", ".1f", " pts"
        if spec.get("reference_value") is not None:
            spec = {**spec, "reference_value": spec["reference_value"] * 100}
    fig = go.Figure()

    if spec["type"] == "line":
        groups = [(None, d)] if not color else list(d.groupby(color, sort=False))
        if color and len(groups) > MAX_SERIES:  # keep the largest series; never generate a 9th hue
            keep = d.groupby(color)[y].sum().nlargest(MAX_SERIES).index
            groups = [(k, g) for k, g in groups if k in keep]
        cmap = _color_map(color_domain if color_domain is not None else [k for k, _ in groups if k is not None])
        for name, g in groups:
            c = cmap.get(str(name), SERIES[0])
            fig.add_trace(go.Scatter(
                x=g[x], y=g[y], mode="lines+markers", name=str(name) if name is not None else y,
                line=dict(width=2, color=c, shape="linear"), marker=dict(size=6, color=c, line=dict(width=2, color=SURFACE)),
                hovertemplate=f"<b>%{{y:{hover_fmt}}}</b>  {name if name is not None else ''}<extra></extra>"))
        fig.update_layout(hovermode="x unified")
    else:  # bar: horizontal, so long category names stay readable
        d = d.iloc[::-1]  # largest at the top
        if color:
            cmap = _color_map(color_domain if color_domain is not None else d[color].unique())
            for name, g in d.groupby(color, sort=False):
                fig.add_trace(go.Bar(y=g[x].astype(str), x=g[y], orientation="h", name=str(name),
                                     marker=dict(color=cmap[str(name)], cornerradius=4),
                                     hovertemplate=f"%{{y}}: <b>%{{x:{hover_fmt}}}</b><extra>{name}</extra>"))
            fig.update_layout(barmode="group")
        else:
            fig.add_trace(go.Bar(y=d[x].astype(str), x=d[y], orientation="h", marker=dict(color=SERIES[0], cornerradius=4),
                                 text=d[y], texttemplate=f"%{{text:{hover_fmt}}}{suffix}", textposition="outside",
                                 textfont=dict(color=INK_2, size=11), cliponaxis=False,
                                 hovertemplate=f"%{{y}}: <b>%{{x:{hover_fmt}}}{suffix}</b><extra></extra>"))
        vals = list(d[y].dropna()) + ([spec["reference_value"]] if spec.get("reference_value") is not None else [])
        if vals:  # pad the value axis so labels outside the bar ends never hit the category names
            lo, hi = min(0, min(vals)), max(0, max(vals))
            pad = (hi - lo) * 0.14 or 1
            fig.update_xaxes(range=[lo - (pad if lo < 0 else 0), hi + pad])
        if spec.get("reference_value") is not None and spec.get("reference_label"):  # benchmark line, labelled in the subtitle
            fig.add_vline(x=spec["reference_value"], line=dict(color=INK_2, width=1, dash="dot"))

    n_series = len(fig.data)
    subtitle = spec.get("subtitle", "")
    if spec["type"] == "bar" and spec.get("reference_value") is not None and spec.get("reference_label"):
        subtitle += f" Dotted line: {spec['reference_label']}."
    x_title, y_title = axis_titles(spec)
    title_font = dict(color=INK_2, size=12)
    value_axis = dict(tickformat=tick_fmt, gridcolor=GRID, gridwidth=1, zeroline=True, zerolinecolor=AXIS,
                      tickfont=dict(color=MUTED, size=11), title=dict(text=y_title, font=title_font, standoff=8))
    value_axis["automargin"] = True
    value_axis["ticksuffix"] = suffix
    cat_axis = dict(showgrid=False, linecolor=AXIS, tickfont=dict(color=INK_2, size=11), automargin=True,
                    title=dict(text=x_title, font=title_font, standoff=8))
    fig.update_layout(
        template="none", paper_bgcolor=SURFACE, plot_bgcolor=SURFACE, font=dict(family=FONT, color=INK, size=12),
        title=dict(text=f"<b>{spec['title']}</b>" + (f"<br><span style='font-size:12px;color:{INK_2}'>{subtitle}</span>"
                                                       if subtitle else ""), x=0, xanchor="left", font=dict(size=15)),
        showlegend=n_series > 1, legend=dict(orientation="h", y=-0.22, x=0, font=dict(color=INK_2, size=11)),
        margin=dict(l=10, r=40, t=70, b=50), bargap=0.35, bargroupgap=0.08,
        height=max(240, 34 * len(d) + 170) if spec["type"] == "bar" and not color else 430,  # keeps bars thin
        hoverlabel=dict(bgcolor="white", bordercolor=GRID, font=dict(color=INK, family=FONT)),
        xaxis=value_axis if spec["type"] == "bar" else cat_axis,
        yaxis=cat_axis if spec["type"] == "bar" else value_axis,
    )
    return fig


def table(df: pd.DataFrame, spec: dict) -> pd.DataFrame:
    """The table view behind a chart: the same rows, readable formats."""
    d = prepare(df, spec)
    cols = [c for c in dict.fromkeys([spec["x"], spec.get("color"), spec["y"], *spec.get("extra_columns", [])]) if c and c in d]
    out = d[cols].copy()
    fmt = spec.get("y_format")
    for c in out.columns:
        if pd.api.types.is_datetime64_any_dtype(out[c]):
            out[c] = out[c].dt.strftime("%Y-%m-%d")
        if pd.api.types.is_float_dtype(out[c]):
            if fmt in ("percent", "points") and out[c].abs().max() <= 1.5:
                out[c] = out[c].map(lambda v: f"{v:.1%}" if pd.notna(v) else "")
            else:
                out[c] = out[c].map(lambda v: f"{v:,.2f}" if pd.notna(v) else "")
    x_title, y_title = axis_titles(spec)
    return out.rename(columns={spec["x"]: x_title, spec["y"]: y_title,
                               **({spec["color"]: humanize(spec["color"])} if spec.get("color") else {})})
