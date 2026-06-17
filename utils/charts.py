"""Reusable Plotly chart factories with MoJ palette + RTL Hebrew styling."""
from __future__ import annotations

from typing import Optional, Sequence

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


PALETTE = {
    "primary": "#19647E",   # dark teal — dominant brand
    "secondary": "#119DA4", # teal — secondary brand
    "accent": "#FFC857",    # gold — positive / highlight
    "warn": "#FFC857",      # gold — caution (shared with accent)
    "danger": "#4B3F72",    # deep purple — negative / severe
    "muted": "#69A257",     # green — neutral / disabled
}

# Mirror of PALETTE — kept so outline/error-bar uses still work after the revert.
_PALETTE_DARK = dict(PALETTE)

# Trial/no-trial canonical colors used everywhere
TRIAL_COLORS = {
    "ביקשו להישפט": PALETTE["secondary"],
    "שילמו קנס / אחר": PALETTE["accent"],
    "לא ביקשו להישפט": PALETTE["accent"],
}

LIKERT_3BAND_ORDER = ["במידה מועטה", "במידה בינונית", "במידה רבה"]
LIKERT_3BAND_COLORS = {
    "במידה מועטה": PALETTE["danger"],
    "במידה בינונית": PALETTE["warn"],
    "במידה רבה": PALETTE["secondary"],
}

YESNO_COLORS = {"כן": PALETTE["secondary"], "לא": PALETTE["danger"]}

# Sector — used on every page
SECTOR_COLORS = {
    "מגזר יהודי": PALETTE["secondary"],
    "מגזר ערבי": PALETTE["accent"],
    "לא ידוע": PALETTE["muted"],
}

GENDER_COLORS = {
    "גבר": PALETTE["primary"],
    "אישה": PALETTE["danger"],
}

# 3-level ordinal: "balance vs prosecution", and similar (כלל לא → באופן חלקי → באופן מלא)
BALANCE_COLORS = {
    "כלל לא": PALETTE["danger"],
    "באופן חלקי": PALETTE["warn"],
    "באופן מלא": PALETTE["secondary"],
}

# Awareness (3 ordered states from full awareness to none)
AWARENESS_COLORS = {
    "כן, ידעתי": PALETTE["secondary"],
    "ידעתי באופן חלקי": PALETTE["warn"],
    "לא ידעתי": PALETTE["danger"],
}

# Hearing status (6 distinct outcomes; uses full palette in fixed order)
HEARING_STATUS_COLORS = {
    "כן, בנוכחותי": PALETTE["primary"],
    "כן, אבל לא בנוכחותי (עו\"ד ייצג אותי)": PALETTE["secondary"],
    "כן, אבל לא התייצבתי (לא ידעתי על תאריך הדיון או בחרתי לא להתייצב)": PALETTE["accent"],
    "טרם נקבע דיון": "#6B5BA0",
    "לא נקבע דיון וההליך התבטל": PALETTE["danger"],
    "אין מענה": PALETTE["muted"],
}

# Sequence for any demographic / multi-category chart (districts, age bands, education, etc.)
DEMOGRAPHIC_SEQUENCE = [
    PALETTE["primary"], PALETTE["secondary"], PALETTE["accent"],
    PALETTE["danger"], PALETTE["muted"], "#6B5BA0",
]

NO_ANSWER_COLOR = PALETTE["muted"]


def _text_on(color: str) -> str:
    """Pick black or white text based on background luminance — keeps in-bar labels readable on dark fills."""
    if not color:
        return "black"
    c = color.strip()
    if c.startswith("rgb"):
        try:
            nums = c[c.find("(") + 1 : c.rfind(")")].split(",")
            r, g, b = [int(float(x)) for x in nums[:3]]
        except Exception:
            return "black"
    elif c.startswith("#"):
        h = c.lstrip("#")
        if len(h) == 3:
            h = "".join(ch * 2 for ch in h)
        if len(h) != 6:
            return "black"
        try:
            r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
        except ValueError:
            return "black"
    else:
        return "black"
    luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255
    return "white" if luminance < 0.55 else "black"


def _add_small_segment_warning(fig: go.Figure, group_counts: dict, threshold: int = 10) -> go.Figure:
    """Add annotation to chart if any segment has n < threshold.
    group_counts: dict mapping group labels to sample sizes.
    Returns the figure to allow chaining."""
    small_groups = {g: n for g, n in group_counts.items() if n < threshold}
    if small_groups:
        # Shorten warning text if too many groups
        group_text = ", ".join([f"{g} (n={n})" for g, n in list(small_groups.items())[:3]])
        if len(small_groups) > 3:
            group_text += f" + {len(small_groups) - 3} עוד"
        warning_text = f"⚠️ קבוצות קטנות (n<{threshold}): {group_text} — קשה להסיק מסקנות."
        
        fig.add_annotation(
            text=warning_text,
            xref="paper", yref="paper",
            x=0.5, y=0.94,
            showarrow=False,
            font=dict(size=12, color="#4B3F72"),
            bgcolor="rgba(255,255,255,0.95)",
            bordercolor="rgba(75,63,114,0.5)",
            borderwidth=1,
            borderpad=5,
            xanchor="center",
            yanchor="top",
        )
    return fig


def _base_layout(fig: go.Figure, height: int = 420) -> go.Figure:
    fig.update_layout(
        template="plotly_white",
        paper_bgcolor="white",
        plot_bgcolor="white",
        font=dict(family="Assistant, Arial, sans-serif", size=15, color="black"),
        title=dict(font=dict(color="black", size=18), y=0.97, yanchor="top"),
        margin=dict(l=135, r=40, t=90, b=80),
        height=height,
        autosize=False,  # Stop Streamlit from auto-compressing the chart and cutting RTL labels
        legend=dict(
            orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1,
            font=dict(color="black", size=14), bgcolor="rgba(0,0,0,0)",
        ),
        hoverlabel=dict(font_size=14, font_family="Assistant"),
        xaxis=dict(tickfont=dict(color="black", size=14), title=dict(font=dict(color="black", size=14)), automargin=True),
        yaxis=dict(tickfont=dict(color="black", size=14), title=dict(font=dict(color="black", size=14)), automargin=True),
    )
    # Force every bar trace to keep its text label INSIDE the plot area.
    fig.update_traces(
        selector=dict(type="bar"),
        constraintext="inside",
        cliponaxis=False,
    )
    return fig


def empty_state(message: str = "אין נתונים זמינים תחת הסינון הנוכחי") -> go.Figure:
    fig = go.Figure()
    fig.add_annotation(text=message, showarrow=False, font=dict(size=18, color="#888"))
    fig.update_layout(
        xaxis=dict(visible=False), yaxis=dict(visible=False),
        height=320, paper_bgcolor="#fafbfd", plot_bgcolor="#fafbfd",
        margin=dict(l=20, r=20, t=20, b=20),
    )
    return fig


def stacked_pct_bar(
    df: pd.DataFrame,
    group_col: str,
    value_col: str,
    title: Optional[str] = None,
    category_order: Optional[Sequence[str]] = None,
    color_map: Optional[dict] = None,
    show_mean: bool = False,
    mean_col: Optional[str] = None,
    height: int = 460,
) -> go.Figure:
    """Stacked-percent bar: rows = groups, segments = value_col categories.
    Annotates each bar with sample size; optionally shows numeric mean per group.
    """
    if df.empty or group_col not in df or value_col not in df:
        return empty_state()

    work = df[[group_col, value_col]].dropna()
    if work.empty:
        return empty_state()

    crosstab = (
        work.groupby([group_col, value_col]).size().unstack(fill_value=0)
    )
    n_per_group = crosstab.sum(axis=1)
    pct = crosstab.div(n_per_group, axis=0) * 100

    if category_order:
        pct = pct.reindex(columns=[c for c in category_order if c in pct.columns])

    fig = go.Figure()
    cmap = color_map or LIKERT_3BAND_COLORS
    for cat in pct.columns:
        fill = cmap.get(cat, PALETTE["muted"])
        fig.add_trace(go.Bar(
            x=pct.index.astype(str),
            y=pct[cat].values,
            name=str(cat),
            marker_color=fill,
            marker_line=dict(color=_PALETTE_DARK["primary"], width=1),
            hovertemplate=f"%{{x}}<br>{cat}: %{{y:.1f}}%<extra></extra>",
            text=[f"{v:.0f}%" if v >= 8 else "" for v in pct[cat].values],
            textposition="inside",
            insidetextanchor="middle",
            textfont=dict(color=_text_on(fill), size=14),
        ))

    fig.update_layout(barmode="stack", title=title)
    fig.update_xaxes(title="")
    fig.update_yaxes(title="", range=[0, 100], ticksuffix="%")

    annotations = []
    for i, grp in enumerate(pct.index):
        n = int(n_per_group.loc[grp])
        txt = f"n={n}"
        if show_mean and mean_col and mean_col in df.columns:
            series = df.loc[df[group_col] == grp, mean_col]
            mean_val = series.mean()
            std_val = series.std()
            if pd.notna(mean_val):
                if pd.notna(std_val):
                    txt = f"ממוצע {mean_val:.2f} ± {std_val:.2f} | n={n}"
                else:
                    txt = f"ממוצע {mean_val:.2f} | n={n}"
        annotations.append(dict(
            x=str(grp), y=97, xref="x", yref="y",
            text=txt, showarrow=False,
            font=dict(size=13, color="#1a1a2e"),
            bgcolor="rgba(255,255,255,0.85)",
            bordercolor="rgba(0,0,0,0.15)", borderwidth=1, borderpad=3,
        ))
    fig.update_layout(annotations=annotations)
    fig.update_traces(cliponaxis=False, constraintext="inside")
    
    # Add warning for small segments
    group_counts_dict = n_per_group.to_dict()
    fig = _add_small_segment_warning(fig, group_counts_dict, threshold=10)
    
    return _base_layout(fig, height=height)


def horizontal_pct_bar(
    df: pd.DataFrame,
    binary_cols: dict,
    group_col: Optional[str] = None,
    title: Optional[str] = None,
    height: int = 480,
    sort_desc: bool = True,
) -> go.Figure:
    """For multi-select binary columns (e.g. offense types).
    binary_cols: {df_col_name: 'hebrew label'}.
    If group_col is None: single % bar per category over the whole df.
    Else: clustered bars by group_col level.
    """
    if df.empty:
        return empty_state()
    cols = [c for c in binary_cols if c in df.columns]
    if not cols:
        return empty_state("עמודות העבירות לא נמצאו")

    fig = go.Figure()
    if group_col is None:
        rates = {binary_cols[c]: df[c].mean(skipna=True) * 100 for c in cols}
        counts = {binary_cols[c]: df[c].dropna().shape[0] for c in cols}
        s = pd.Series(rates).sort_values(ascending=sort_desc)
        fill = PALETTE["secondary"]
        fig.add_trace(go.Bar(
            x=s.values, y=s.index, orientation="h",
            marker_color=fill,
            marker_line=dict(color=_PALETTE_DARK["secondary"], width=1),
            text=[f"{v:.0f}%" if v >= 8 else "" for v in s.values],
            textposition="inside",
            insidetextanchor="middle",
            textfont=dict(color=_text_on(fill), size=13),
            customdata=[counts[label] for label in s.index],
            hovertemplate="%{y}: %{x:.1f}%<br>n=%{customdata}<extra></extra>",
        ))
    else:
        groups = [g for g in df[group_col].dropna().unique() if g != "nan"]
        long = []
        for g in groups:
            sub = df[df[group_col] == g]
            for c in cols:
                long.append({"group": g, "category": binary_cols[c], "pct": sub[c].mean(skipna=True) * 100, "n": len(sub)})
        long_df = pd.DataFrame(long)
        if long_df.empty:
            return empty_state()
        order = (
            long_df.groupby("category")["pct"].mean().sort_values(ascending=sort_desc).index.tolist()
        )
        palette_cycle = [PALETTE["primary"], PALETTE["secondary"], PALETTE["accent"], PALETTE["warn"], PALETTE["danger"]]
        dark_cycle = [_PALETTE_DARK["primary"], _PALETTE_DARK["secondary"], _PALETTE_DARK["accent"], _PALETTE_DARK["warn"], _PALETTE_DARK["danger"]]
        for i, g in enumerate(groups):
            sub = long_df[long_df["group"] == g].set_index("category").reindex(order).reset_index()
            fill = palette_cycle[i % len(palette_cycle)]
            line = dark_cycle[i % len(dark_cycle)]
            fig.add_trace(go.Bar(
                x=sub["pct"], y=sub["category"], orientation="h",
                name=str(g),
                marker_color=fill,
                marker_line=dict(color=line, width=1),
                text=[f"{v:.0f}%" if v >= 8 else "" for v in sub["pct"]],
                textposition="inside",
                insidetextanchor="middle",
                textfont=dict(color=_text_on(fill), size=13),
                customdata=sub["n"].tolist(),
                hovertemplate=f"{g}<br>%{{y}}: %{{x:.1f}}%<br>n=%{{customdata}}<extra></extra>",
            ))
        fig.update_layout(barmode="group")
    fig.update_layout(title=title)
    fig.update_xaxes(ticksuffix="%", title="אחוז מהמשיבים בקבוצה")
    fig.update_yaxes(title="", autorange="reversed")
    fig.update_traces(cliponaxis=False, constraintext="inside", insidetextanchor="middle")
    
    # Add warning for small segments
    if group_col is None:
        group_counts_dict = {str(idx): int(counts.get(idx, 0)) for idx in counts.keys()}
    else:
        group_counts_dict = {str(g): int(df[df[group_col] == g].shape[0]) for g in groups}
    fig = _add_small_segment_warning(fig, group_counts_dict, threshold=10)
    
    return _base_layout(fig, height=height)


def grouped_bar(
    df: pd.DataFrame,
    x_col: str,
    y_col: str,
    color_col: Optional[str] = None,
    title: Optional[str] = None,
    barmode: str = "group",
    height: int = 420,
    text: bool = True,
    color_map: Optional[dict] = None,
) -> go.Figure:
    if df.empty:
        return empty_state()
    fig = px.bar(
        df, x=x_col, y=y_col, color=color_col, barmode=barmode,
        color_discrete_map=color_map,
        text_auto=".0f" if text else False,
    )
    fig.update_layout(title=title)
    fig.update_traces(textposition="inside", textfont_size=14,
                      cliponaxis=False, constraintext="inside", insidetextanchor="middle")
    return _base_layout(fig, height=height)


def likert_summary_strip(df: pd.DataFrame, columns: list[tuple[str, str]], height: int = 300) -> go.Figure:
    """Horizontal bar showing mean ± SD of multiple likert columns side by side.
    columns: list of (numeric_col_name, hebrew_label).
    """
    if df.empty:
        return empty_state()
    rows = []
    for col, label in columns:
        if col in df.columns:
            series = df[col].dropna()
            if len(series) == 0:
                continue
            m = series.mean()
            sd = series.std() if len(series) > 1 else 0.0
            rows.append({"label": label, "mean": m, "sd": sd if pd.notna(sd) else 0.0, "n": len(series)})
    if not rows:
        return empty_state()
    s = pd.DataFrame(rows)
    _fill = PALETTE["primary"]
    fig = go.Figure(go.Bar(
        x=s["mean"], y=s["label"], orientation="h",
        marker_color=_fill,
        marker_line=dict(color=_PALETTE_DARK["primary"], width=1),
        error_x=dict(
            type="data", array=s["sd"], visible=True,
            color="#1a1a2e", thickness=1.6, width=8,
        ),
        text=[f"{m:.2f} ± {sd:.2f}" for m, sd in zip(s["mean"], s["sd"])],
        textposition="inside",
        insidetextanchor="middle",
        textfont=dict(color=_text_on(_fill), size=14),
        constraintext="inside",
        cliponaxis=False,
        customdata=np.stack([s["sd"].values, s["n"].values], axis=-1),
        hovertemplate="%{y}<br>ממוצע: %{x:.2f} / 5<br>סטיית תקן: %{customdata[0]:.2f}<br>n=%{customdata[1]}<extra></extra>",
    ))
    fig.update_xaxes(range=[0, 7.0], title="ציון ממוצע ± סטיית תקן (1-5)")
    fig.update_yaxes(autorange="reversed", title="")
    return _base_layout(fig, height=height)


def mean_sd_by_group(
    df: pd.DataFrame,
    group_col: str,
    value_col: str,
    title: Optional[str] = None,
    y_range: tuple[float, float] = (0, 7.0),
    y_axis_title: str = "ציון ממוצע ± סטיית תקן (1-5)",
    min_n: int = 5,
    color: Optional[str] = None,
    height: int = 420,
    sort_by_mean: bool = False,
) -> go.Figure:
    """Vertical bar: mean of `value_col` per `group_col`, with SD error bars and n labels."""
    if df.empty or group_col not in df or value_col not in df:
        return empty_state()
    work = df[[group_col, value_col]].dropna()
    if work.empty:
        return empty_state()
    agg = (
        work.groupby(group_col)[value_col]
        .agg(["mean", "std", "count"])
        .reset_index()
        .rename(columns={"count": "n"})
    )
    agg = agg[agg["n"] >= min_n]
    if agg.empty:
        return empty_state(f"אין קבוצה עם n≥{min_n}")
    agg["std"] = agg["std"].fillna(0.0)
    if sort_by_mean:
        agg = agg.sort_values("mean", ascending=False)
    _fill = color or PALETTE["primary"]
    fig = go.Figure(go.Bar(
        x=agg[group_col].astype(str), y=agg["mean"],
        marker_color=_fill,
        marker_line=dict(color=_PALETTE_DARK["primary"], width=1),
        error_y=dict(
            type="data", array=agg["std"], visible=True,
            color="#1a1a2e", thickness=1.6, width=10,
        ),
        text=[f"{m:.2f}±{sd:.2f}" for m, sd in zip(agg["mean"], agg["std"])],
        textposition="inside",
        insidetextanchor="middle",
        textfont=dict(color=_text_on(_fill), size=14),
        constraintext="inside",
        cliponaxis=False,
        hovertemplate="%{x}<br>ממוצע: %{y:.2f}<br>סטיית תקן: %{error_y.array:.2f}<extra></extra>",
    ))
    fig.update_layout(title=title)
    fig.update_yaxes(range=list(y_range), title=y_axis_title)
    fig.update_xaxes(title="")
    return _base_layout(fig, height=height)


def rate_by_group(
    df: pd.DataFrame,
    group_col: str,
    bool_series: pd.Series,
    title: Optional[str] = None,
    min_n: int = 5,
    color: Optional[str] = None,
    height: int = 420,
    suffix: str = "%",
    sort_by_value: bool = True,
) -> go.Figure:
    """Vertical bar: percentage of True in `bool_series` per `group_col`, with n labels."""
    if df.empty or group_col not in df:
        return empty_state()
    work = pd.DataFrame({"_g": df[group_col], "_v": bool_series.astype(float)}).dropna()
    if work.empty:
        return empty_state()
    agg = work.groupby("_g")["_v"].agg(["mean", "count"]).reset_index().rename(columns={"_g": group_col, "count": "n"})
    agg = agg[agg["n"] >= min_n]
    if agg.empty:
        return empty_state(f"אין קבוצה עם n≥{min_n}")
    agg["pct"] = agg["mean"] * 100
    if sort_by_value:
        agg = agg.sort_values("pct", ascending=False)
    _fill = color or PALETTE["secondary"]
    fig = go.Figure(go.Bar(
        x=agg[group_col].astype(str), y=agg["pct"],
        marker_color=_fill,
        marker_line=dict(color=_PALETTE_DARK["secondary"], width=1),
        text=[f"{p:.1f}{suffix}" for p in agg["pct"]],
        textposition="inside",
        insidetextanchor="middle",
        textfont=dict(color=_text_on(_fill), size=14),
        constraintext="inside",
        cliponaxis=False,
        hovertemplate="%{x}<br>%{y:.1f}" + suffix + "<extra></extra>",
    ))
    fig.update_layout(title=title)
    fig.update_yaxes(ticksuffix=suffix, title="", range=[0, max(agg["pct"].max() * 1.4, 10)])
    fig.update_xaxes(title="")
    return _base_layout(fig, height=height)


def donut(
    df: pd.DataFrame,
    column: str,
    title: Optional[str] = None,
    color_map: Optional[dict] = None,
    height: int = 360,
) -> go.Figure:
    if df.empty or column not in df:
        return empty_state()
    counts = df[column].dropna().value_counts()
    if counts.empty:
        return empty_state()
    colors = [(color_map or YESNO_COLORS).get(str(k), PALETTE["muted"]) for k in counts.index]
    fig = go.Figure(go.Pie(
        labels=counts.index.astype(str), values=counts.values, hole=0.55,
        marker=dict(colors=colors),
        textinfo="label+percent", textfont_size=16,
    ))
    fig.update_layout(title=title)
    return _base_layout(fig, height=height)


def trial_funnel(df: pd.DataFrame, height: int = 460) -> go.Figure:
    if df.empty:
        return empty_state()
    total = len(df)
    paid = int(df["paid_fine_track"].sum())
    trial = int(df["requested_trial"].sum())
    hearing = int((df["hearing_held_bin"] == "היה דיון בפועל").sum()) if "hearing_held_bin" in df else 0
    not_held = int((df["hearing_held_bin"] == "לא היה").sum()) if "hearing_held_bin" in df else 0
    fig = go.Figure(go.Funnel(
        y=["סך כל המשיבים", "שילמו קנס", "ביקשו להישפט", "התקיים דיון", "לא התקיים דיון"],
        x=[total, paid, trial, hearing, not_held],
        textinfo="value+percent initial",
        marker=dict(color=[PALETTE["primary"], PALETTE["accent"], PALETTE["secondary"], PALETTE["warn"], PALETTE["danger"]]),
        connector=dict(line=dict(color="#e0e6ed", width=1)),
    ))
    return _base_layout(fig, height=height)


def sunburst(df: pd.DataFrame, path: list[str], title: Optional[str] = None, height: int = 460) -> go.Figure:
    if df.empty:
        return empty_state()
    work = df[path].copy()
    for c in path:
        work[c] = work[c].astype(str).replace({"nan": "לא ידוע"})
    fig = px.sunburst(work, path=path, color=path[0],
                       color_discrete_sequence=[PALETTE["primary"], PALETTE["secondary"], PALETTE["accent"], PALETTE["warn"]])
    fig.update_layout(title=title)
    return _base_layout(fig, height=height)


def treemap(df: pd.DataFrame, binary_cols: dict, title: Optional[str] = None, height: int = 460) -> go.Figure:
    if df.empty:
        return empty_state()
    rows = []
    for c, lbl in binary_cols.items():
        if c in df.columns:
            rows.append({"category": lbl, "count": int(df[c].sum(skipna=True))})
    if not rows:
        return empty_state()
    s = pd.DataFrame(rows).sort_values("count", ascending=False)
    fig = px.treemap(s, path=["category"], values="count", color="count",
                      color_continuous_scale=["#E0EFF1", "#119DA4", "#19647E"])
    fig.update_layout(title=title)
    fig.update_traces(textinfo="label+value+percent root")
    return _base_layout(fig, height=height)


def heatmap_crosstab(df: pd.DataFrame, x: str, y: str, normalize: Optional[str] = "index", height: int = 480) -> go.Figure:
    if df.empty or x not in df or y not in df:
        return empty_state()
    work = df[[x, y]].dropna()
    if work.empty:
        return empty_state()
    if normalize:
        ct = pd.crosstab(work[y], work[x], normalize=normalize) * 100
        text = [[f"{v:.0f}%" for v in row] for row in ct.values]
        hover = "%{y} × %{x}: %{z:.1f}%<extra></extra>"
    else:
        ct = pd.crosstab(work[y], work[x])
        text = [[str(int(v)) for v in row] for row in ct.values]
        hover = "%{y} × %{x}: %{z}<extra></extra>"
    fig = go.Figure(go.Heatmap(
        z=ct.values, x=ct.columns.astype(str), y=ct.index.astype(str),
        text=text, texttemplate="%{text}",
        colorscale=[[0, "#EAF0F8"], [0.5, "#7AB4BC"], [1, "#19647E"]],
        hovertemplate=hover,
        colorbar=dict(title="%" if normalize else "n"),
    ))
    fig.update_layout(title=f"{y} × {x}")
    fig.update_yaxes(autorange="reversed")
    return _base_layout(fig, height=height)


def sankey_trial_flow(df: pd.DataFrame, height: int = 460) -> go.Figure:
    """Simple horizontal bar of the four final outcomes, color-coded by track.

    Uses two separate traces (one per track) so Plotly renders a normal
    legend with small color swatches.
    """
    if df.empty:
        return empty_state()
    total = len(df)
    paid = int(((~df["requested_trial"]) & (df["paid_fine_actual"] == "כן")).sum())
    not_paid = int(((~df["requested_trial"]) & (df["paid_fine_actual"] == "לא")).sum())
    held = int((df["requested_trial"] & (df["hearing_held_bin"] == "היה דיון בפועל")).sum())
    not_held = int((df["requested_trial"] & (df["hearing_held_bin"] == "לא היה")).sum())

    rows = [
        ("שילמו את הקנס", paid, "לא ביקשו להישפט", PALETTE["accent"]),
        ("לא שילמו את הקנס", not_paid, "לא ביקשו להישפט", PALETTE["accent"]),
        ("התקיים דיון", held, "ביקשו להישפט", PALETTE["secondary"]),
        ("לא התקיים דיון", not_held, "ביקשו להישפט", PALETTE["secondary"]),
    ]
    rows.sort(key=lambda r: r[1], reverse=True)
    all_labels = [r[0] for r in rows]
    max_val = max((r[1] for r in rows), default=1)

    fig = go.Figure()
    seen_tracks: set[str] = set()
    for track_name, color in [
        ("לא ביקשו להישפט", PALETTE["accent"]),
        ("ביקשו להישפט", PALETTE["secondary"]),
    ]:
        # Keep one bar per label so y-axis order stays consistent across traces;
        # zero out values for labels not in this track so they don't render.
        x_vals = []
        text_vals = []
        for lbl, val, trk, _c in rows:
            if trk == track_name:
                pct = (val / total * 100) if total else 0
                x_vals.append(val)
                text_vals.append(f"{val:,} ({pct:.1f}%)")
            else:
                x_vals.append(0)
                text_vals.append("")
        fig.add_trace(go.Bar(
            name=track_name,
            x=x_vals,
            y=all_labels,
            orientation="h",
            marker=dict(color=color, line=dict(color="white", width=1)),
            text=text_vals,
            textposition="inside",
            insidetextanchor="middle",
            textfont=dict(color="white", size=16),
            hovertemplate="%{y}<br>" + track_name + "<br>%{x:,} משיבים<extra></extra>",
            cliponaxis=False,
            constraintext="inside",
        ))

    fig.update_layout(
        barmode="overlay",
        title=f"תוצאות התהליך — סך הכל {total:,} משיבים",
        showlegend=True,
        legend=dict(
            title=dict(text="מסלול", font=dict(color="black")),
            orientation="v",
            yanchor="middle", y=0.5,
            xanchor="left", x=1.02,
            font=dict(color="black"),
            bgcolor="rgba(0,0,0,0)",
        ),
    )
    fig.update_xaxes(title="", showticklabels=False, range=[0, max_val * 1.05])
    fig.update_yaxes(title="", autorange="reversed")
    return _base_layout(fig, height=height)


def stacked_grouped_bar(
    df: pd.DataFrame,
    group_col: str,
    stack_col: str,
    facet_col: Optional[str] = None,
    title: Optional[str] = None,
    color_map: Optional[dict] = None,
    height: int = 460,
) -> go.Figure:
    """Group on x, stack a category, optionally facet by another col."""
    if df.empty:
        return empty_state()
    fig = px.histogram(
        df.dropna(subset=[group_col, stack_col]),
        x=group_col, color=stack_col, facet_col=facet_col,
        barnorm="percent", color_discrete_map=color_map,
        text_auto=".0f",
    )
    fig.update_layout(title=title, yaxis_title="אחוז", yaxis_ticksuffix="%")
    fig.update_traces(textposition="inside", textfont=dict(color="white", size=13))
    return _base_layout(fig, height=height)


def kpi_card_html(title: str, value: str, accent: str = "#0066cc", sub: str = "", std_dev: Optional[str] = None) -> str:
    """KPI card with optional standard deviation display."""
    sub_html = f"<div class='kpi-sub'>{sub}</div>" if sub else ""
    std_html = f"<div class='kpi-std'>סטיית תקן: {std_dev}</div>" if std_dev else ""
    return f"""
    <div class='kpi-card' style='border-right-color:{accent};'>
      <div class='kpi-title'>{title}</div>
      <div class='kpi-value'>{value}</div>
      {std_html}
      {sub_html}
    </div>
    """


def get_common_kpis(df: pd.DataFrame) -> dict:
    """Compute a small set of common KPIs used on pages.

    Returns dict with numeric values (not formatted):
      - total: number of rows in df
      - trial_pct: percent who requested trial (0-100)
      - trial_pct_std: std dev of requested_trial*100
      - paid_pct: percent who paid the fine among those who did not request trial
      - sat_avg: mean of `process_satisfaction_num` or None
      - sat_std: std dev of `process_satisfaction_num` or None
    """
    total = len(df) if df is not None else 0
    out = {
        "total": int(total),
        "trial_pct": 0.0,
        "trial_pct_std": 0.0,
        "paid_pct": 0.0,
        "sat_avg": None,
        "sat_std": None,
    }
    if total == 0:
        return out

    if "requested_trial" in df.columns:
        try:
            req = df["requested_trial"].astype(float)
            out["trial_pct"] = req.mean(skipna=True) * 100
            out["trial_pct_std"] = req.std(skipna=True) * 100 if req.notna().sum() > 1 else 0.0
        except Exception:
            out["trial_pct"] = 0.0
            out["trial_pct_std"] = 0.0

    if "paid_fine_actual" in df.columns and "requested_trial" in df.columns:
        try:
            no_trial = df[~df["requested_trial"].fillna(False)]
            if len(no_trial):
                out["paid_pct"] = no_trial["paid_fine_actual"].eq("כן").mean(skipna=True) * 100
        except Exception:
            out["paid_pct"] = 0.0

    if "process_satisfaction_num" in df.columns:
        series = df["process_satisfaction_num"].dropna()
        if len(series):
            out["sat_avg"] = float(series.mean())
            out["sat_std"] = float(series.std()) if series.count() > 1 else 0.0

    return out


def district_stats_bar(
    df: pd.DataFrame,
    numeric_col: str,
    district_col: str = "mahoz_short",
    title: Optional[str] = None,
    show_std: bool = True,
    min_n: int = 5,
    height: int = 500,
) -> go.Figure:
    """Bar chart showing mean ± SD by district (with n labels)."""
    if df.empty or numeric_col not in df:
        return empty_state()
    if district_col not in df.columns and "mahoz_short" in df.columns:
        district_col = "mahoz_short"
    if district_col not in df.columns:
        return empty_state("עמודת מחוז לא נמצאה")

    work = df[[district_col, numeric_col]].dropna()
    if work.empty:
        return empty_state()

    stats = work.groupby(district_col)[numeric_col].agg(["mean", "std", "count"]).reset_index()
    stats.columns = ["district", "mean", "std", "count"]
    stats = stats[stats["count"] >= min_n]
    if stats.empty:
        return empty_state(f"אין מחוז עם n≥{min_n}")
    stats["std"] = stats["std"].fillna(0.0)
    stats = stats.sort_values("mean", ascending=False)

    error_y = (
        dict(type="data", array=stats["std"], visible=True,
             color="#1a1a2e", thickness=1.6, width=10)
        if show_std else None
    )

    _fill = PALETTE["primary"]
    fig = go.Figure(go.Bar(
        x=stats["district"].astype(str),
        y=stats["mean"],
        error_y=error_y,
        marker_color=_fill,
        marker_line=dict(color=_PALETTE_DARK["primary"], width=1),
        text=[f"{m:.2f}±{s:.2f}" for m, s in zip(stats["mean"], stats["std"])],
        textposition="inside",
        insidetextanchor="middle",
        textfont=dict(color=_text_on(_fill), size=14),
        constraintext="inside",
        cliponaxis=False,
        customdata=np.stack([stats["std"].values, stats["count"].values], axis=-1),
        hovertemplate="<b>%{x}</b><br>ממוצע: %{y:.2f}<br>סטיית תקן: %{customdata[0]:.2f}<br>n=%{customdata[1]}<extra></extra>",
    ))

    fig.update_layout(title=title or "ממוצע ± סטיית תקן לפי מחוז")
    fig.update_xaxes(title="מחוז")
    fig.update_yaxes(title="ממוצע ± סטיית תקן", range=[0, 7.0])
    
    # Add warning for small segments
    district_counts = {str(d): int(c) for d, c in zip(stats["district"], stats["count"])}
    fig = _add_small_segment_warning(fig, district_counts, threshold=10)
    
    return _base_layout(fig, height=height)


def district_comparison_grouped(
    df: pd.DataFrame,
    numeric_cols: list[tuple[str, str]],
    districts: Optional[list[str]] = None,
    district_col: str = "mahoz_short",
    title: Optional[str] = None,
    min_n: int = 5,
    height: int = 500,
) -> go.Figure:
    """Grouped bar chart comparing multiple likert metrics (mean ± SD) across districts.
    numeric_cols: list of (column_name, hebrew_label) tuples."""
    if df.empty:
        return empty_state()
    if district_col not in df.columns and "mahoz_short" in df.columns:
        district_col = "mahoz_short"
    if district_col not in df.columns:
        return empty_state("עמודת מחוז לא נמצאה")

    if districts is None:
        counts = df[district_col].dropna().value_counts()
        districts = [d for d, n in counts.items() if n >= min_n]

    rows = []
    for col, label in numeric_cols:
        if col not in df.columns:
            continue
        for district in districts:
            sub = df[df[district_col] == district]
            series = sub[col].dropna()
            if len(series) < min_n:
                continue
            rows.append({
                "מחוז": str(district),
                "מדד": label,
                "ממוצע": series.mean(),
                "סטיית תקן": series.std() if len(series) > 1 else 0.0,
                "n": len(series),
            })

    if not rows:
        return empty_state(f"אין מחוז עם n≥{min_n}")

    result_df = pd.DataFrame(rows)
    result_df["סטיית תקן"] = result_df["סטיית תקן"].fillna(0.0)
    fig = px.bar(
        result_df,
        x="מחוז",
        y="ממוצע",
        color="מדד",
        barmode="group",
        error_y="סטיית תקן",
        color_discrete_sequence=[PALETTE["primary"], PALETTE["secondary"], PALETTE["accent"], PALETTE["warn"]],
        text=result_df["ממוצע"].round(2),
        hover_data={"n": True, "סטיית תקן": ":.2f"},
    )
    fig.update_traces(
        textposition="inside", insidetextanchor="middle",
        textfont=dict(size=13),
        constraintext="inside", cliponaxis=False,
    )
    for trace in fig.data:
        trace.textfont = dict(color=_text_on(getattr(trace.marker, "color", "")), size=13)
    fig.update_layout(title=title or "השוואת מדדים לפי מחוזות (ממוצע ± סטיית תקן)")
    fig.update_yaxes(title="ממוצע ± סטיית תקן", range=[0, 7.0])
    fig.update_xaxes(title="")
    
    # Add warning for small segments
    district_counts = {str(d): int(n) for d, n in zip(result_df["מחוז"], result_df["n"])}
    fig = _add_small_segment_warning(fig, district_counts, threshold=10)
    
    return _base_layout(fig, height=height)


def district_trial_flow(df: pd.DataFrame, district_col: str = "mahoz_short", height: int = 480) -> go.Figure:
    """Stacked bar — trial vs no-trial counts per district, sorted by total."""
    if df.empty:
        return empty_state()
    if district_col not in df.columns and "mahoz_short" in df.columns:
        district_col = "mahoz_short"
    if district_col not in df.columns:
        return empty_state("עמודת מחוז לא נמצאה")

    districts = [d for d in df[district_col].dropna().unique() if pd.notna(d)]
    data = []
    for district in districts:
        sub = df[df[district_col] == district]
        total = len(sub)
        if total == 0:
            continue
        trial = int(sub["requested_trial"].sum())
        no_trial = total - trial
        data.append({
            "מחוז": str(district),
            "ביקשו להישפט": trial,
            "לא ביקשו להישפט": no_trial,
            "trial_pct": (trial / total * 100) if total else 0,
            "total": total,
        })

    if not data:
        return empty_state()

    result_df = pd.DataFrame(data).sort_values("total", ascending=False)

    fig = go.Figure()
    _accent = PALETTE["accent"]
    _secondary = PALETTE["secondary"]
    fig.add_trace(go.Bar(
        x=result_df["מחוז"], y=result_df["לא ביקשו להישפט"],
        name="לא ביקשו להישפט", marker_color=_accent,
        marker_line=dict(color=_PALETTE_DARK["accent"], width=1),
        text=result_df["לא ביקשו להישפט"], textposition="inside",
        insidetextanchor="middle",
        textfont=dict(color=_text_on(_accent), size=13),
    ))
    fig.add_trace(go.Bar(
        x=result_df["מחוז"], y=result_df["ביקשו להישפט"],
        name="ביקשו להישפט", marker_color=_secondary,
        marker_line=dict(color=_PALETTE_DARK["secondary"], width=1),
        text=result_df["ביקשו להישפט"], textposition="inside",
        insidetextanchor="middle",
        textfont=dict(color=_text_on(_secondary), size=13),
    ))

    annotations = [
        dict(x=row["מחוז"], y=row["total"] * 0.97, xref="x", yref="y",
             text=f"{row['trial_pct']:.0f}% הישפטות | n={row['total']}",
             showarrow=False, yanchor="top",
             font=dict(size=13, color="#1a1a2e"),
             bgcolor="rgba(255,255,255,0.85)",
             bordercolor="rgba(0,0,0,0.15)", borderwidth=1, borderpad=3)
        for _, row in result_df.iterrows()
    ]

    fig.update_layout(
        title="התפלגות מסלול לפי מחוז",
        barmode="stack",
        annotations=annotations,
    )
    fig.update_traces(cliponaxis=False, constraintext="inside")
    fig.update_yaxes(title="מספר משיבים")
    fig.update_xaxes(title="מחוז")
    
    # Add warning for small segments
    district_counts = {str(d): int(t) for d, t in zip(result_df["מחוז"], result_df["total"])}
    fig = _add_small_segment_warning(fig, district_counts, threshold=10)

    return _base_layout(fig, height=height)


def sector_outcomes_stack(df: pd.DataFrame, height: int = 340) -> go.Figure:
    """100%-stacked horizontal rows comparing sector composition of key outcomes.

    One row per outcome (requested trial / paid fine / satisfied). Each row is
    split into Jewish vs Arab segments by share of that outcome's population.
    """
    if df is None or df.empty:
        return empty_state()

    outcomes: list[tuple[str, pd.DataFrame]] = []
    if "requested_trial" in df.columns:
        outcomes.append(("ביקשו להישפט", df[df["requested_trial"]]))
    if {"requested_trial", "paid_fine_actual"}.issubset(df.columns):
        outcomes.append((
            " שילמו את הקנס<br> (מבין מי שלא ביקשו להישפט)",
            df[(~df["requested_trial"]) & (df["paid_fine_actual"] == "כן")],
        ))
    if "process_satisfaction_num" in df.columns:
        outcomes.append((
            "מרוצים מהתהליך (4-5)",
            df[df["process_satisfaction_num"] >= 4],
        ))

    rows = []
    for label, g in outcomes:
        n_total = len(g)
        if n_total == 0:
            continue
        for sector in ["מגזר יהודי", "מגזר ערבי"]:
            n_sec = int((g["migzar"] == sector).sum())
            rows.append({
                "outcome": label, "sector": sector,
                "count": n_sec, "pct": (n_sec / n_total) * 100,
                "total": n_total,
            })
    if not rows:
        return empty_state()
    long = pd.DataFrame(rows)

    sector_colors = {"מגזר יהודי": PALETTE["secondary"], "מגזר ערבי": PALETTE["accent"]}
    sector_outlines = {"מגזר יהודי": _PALETTE_DARK["secondary"], "מגזר ערבי": _PALETTE_DARK["accent"]}

    fig = go.Figure()
    for sector in ["מגזר יהודי", "מגזר ערבי"]:
        sub = long[long["sector"] == sector]
        if sub.empty:
            continue
        fill = sector_colors[sector]
        fig.add_trace(go.Bar(
            y=sub["outcome"], x=sub["pct"], orientation="h",
            name=sector,
            marker_color=fill,
            marker_line=dict(color=sector_outlines[sector], width=1),
            text=[f"{p:.0f}%  n={c}" if p >= 8 else "" for p, c in zip(sub["pct"], sub["count"])],
            textposition="inside", insidetextanchor="middle",
            textfont=dict(color=_text_on(fill), size=13),
            constraintext="inside", cliponaxis=False,
            customdata=np.stack([sub["count"].values, sub["total"].values], axis=-1),
            hovertemplate=(
                f"{sector}<br>%{{y}}<br>%{{x:.1f}}%  "
                "(n=%{customdata[0]} מתוך %{customdata[1]})<extra></extra>"
            ),
        ))

    fig.update_layout(
        barmode="stack",
        title="פילוח לפי מגזר — תוצאות מרכזיות (אחוז מתוך כל קבוצה)",
    )
    fig.update_xaxes(range=[0, 100], ticksuffix="%", title="")
    fig.update_yaxes(title="", autorange="reversed")
    return _base_layout(fig, height=height)


def gender_outcomes_stack(df: pd.DataFrame, height: int = 340) -> go.Figure:
    """100%-stacked horizontal rows comparing gender composition of key outcomes.

    Same shape as sector_outcomes_stack but splits each outcome by gender
    (גבר / אישה) instead of by sector.
    """
    if df is None or df.empty:
        return empty_state()

    outcomes: list[tuple[str, pd.DataFrame]] = []
    if "requested_trial" in df.columns:
        outcomes.append(("ביקשו להישפט", df[df["requested_trial"]]))
    if {"requested_trial", "paid_fine_actual"}.issubset(df.columns):
        outcomes.append((
            "שילמו את הקנס <br>(מבין מי שלא ביקשו להישפט)",
            df[(~df["requested_trial"]) & (df["paid_fine_actual"] == "כן")],
        ))
    if "process_satisfaction_num" in df.columns:
        outcomes.append((
            "מרוצים מהתהליך (4-5)",
            df[df["process_satisfaction_num"] >= 4],
        ))

    rows = []
    for label, g in outcomes:
        n_total = len(g)
        if n_total == 0:
            continue
        for gender in ["גבר", "אישה"]:
            n_g = int((g["gender"] == gender).sum())
            rows.append({
                "outcome": label, "gender": gender,
                "count": n_g, "pct": (n_g / n_total) * 100,
                "total": n_total,
            })
    if not rows:
        return empty_state()
    long = pd.DataFrame(rows)

    gender_colors = {"גבר": PALETTE["primary"], "אישה": PALETTE["danger"]}
    gender_outlines = {"גבר": _PALETTE_DARK["primary"], "אישה": _PALETTE_DARK["danger"]}

    fig = go.Figure()
    for gender in ["גבר", "אישה"]:
        sub = long[long["gender"] == gender]
        if sub.empty:
            continue
        fill = gender_colors[gender]
        fig.add_trace(go.Bar(
            y=sub["outcome"], x=sub["pct"], orientation="h",
            name=gender,
            marker_color=fill,
            marker_line=dict(color=gender_outlines[gender], width=1),
            text=[f"{p:.0f}%  n={c}" if p >= 8 else "" for p, c in zip(sub["pct"], sub["count"])],
            textposition="inside", insidetextanchor="middle",
            textfont=dict(color=_text_on(fill), size=13),
            constraintext="inside", cliponaxis=False,
            customdata=np.stack([sub["count"].values, sub["total"].values], axis=-1),
            hovertemplate=(
                f"{gender}<br>%{{y}}<br>%{{x:.1f}}%  "
                "(n=%{customdata[0]} מתוך %{customdata[1]})<extra></extra>"
            ),
        ))

    fig.update_layout(
        barmode="stack",
        title="פילוח לפי מגדר — תוצאות מרכזיות (אחוז מתוך כל קבוצה)",
    )
    fig.update_xaxes(range=[0, 100], ticksuffix="%", title="")
    fig.update_yaxes(title="", autorange="reversed")

    fig = _base_layout(fig, height=height)

    fig.update_layout(
        margin=dict(l=135, r=20, t=50, b=20), 
        autosize=False # Stopped Streamlit from auto compressing it Zzz..
    )
    
    return fig

    #return _base_layout(fig, height=height)
