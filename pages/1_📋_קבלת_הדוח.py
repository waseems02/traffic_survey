"""Page 1 — קבלת הדוח (PPT slides 4-15)."""
from __future__ import annotations

import os

import pandas as pd
import plotly.express as px
import streamlit as st

from utils.charts import (
    PALETTE,
    _text_on,
    empty_state,
    grouped_bar,
    horizontal_pct_bar,
    stacked_pct_bar,
)
from utils.charts import kpi_card_html, get_common_kpis
from utils.data_loader import OFFENSE_COLS
from utils.filters import init_global_filters, require_data
from utils.insights import render_insight


st.set_page_config(layout="wide", page_title="קבלת הדוח")


def _inject_css():
    path = os.path.join(os.path.dirname(__file__), "..", "assets", "styles.css")
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


_inject_css()

init_global_filters()

df = require_data()


st.markdown(
    """
    <div class='page-header'>
      <h1>📋 קבלת הדוח — תחילת התהליך</h1>
      <p>פרופיל הדוחות שהתקבלו: כמות, מועד, סוג העבירה, מקור הדוח ואופן הקבלה</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# KPI row (same style as Home)
kpis = get_common_kpis(df)
k1, k2, k3, k4 = st.columns(4)
with k1:
    st.markdown(
        kpi_card_html("סך כל המשיבים בסינון", f"{kpis['total']:,}", PALETTE["primary"],
                      sub=f"מתוך {len(df):,} במדגם המלא"),
        unsafe_allow_html=True,
    )
with k2:
    st.markdown(
        kpi_card_html("שיעור בקשות הישפטות", f"{kpis['trial_pct']:.1f}%", PALETTE["secondary"],
                      sub="מתוך המסוננים"),
        unsafe_allow_html=True,
    )
with k3:
    st.markdown(
        kpi_card_html("שילמו את הקנס בפועל", f"{kpis['paid_pct']:.1f}%", PALETTE["accent"],
                      sub="בקרב מי שלא ביקשו להישפט"),
        unsafe_allow_html=True,
    )
with k4:
    sat_str = f"{kpis['sat_avg']:.2f} / 5" if kpis['sat_avg'] is not None else "-"
    sat_std_str = f"{kpis['sat_std']:.2f}" if kpis['sat_std'] is not None else "-"
    st.markdown(
        kpi_card_html("שביעות רצון מהתהליך", sat_str, PALETTE["warn"],
                      sub="ציון ממוצע", std_dev=sat_std_str),
        unsafe_allow_html=True,
    )


# =========================================================
# 1. כמות הדוחות שקיבלו (PPT 4-5)
# =========================================================
st.markdown("<div class='section-header'>1. כמות הדוחות שקיבלו</div>", unsafe_allow_html=True)

c1, c2 = st.columns([1, 1.4])

with c1:
    counts = df["report_count_bin"].dropna().value_counts(normalize=True) * 100
    counts = counts.reset_index()
    counts.columns = ["category", "pct"]
    fig = px.bar(
        counts, x="category", y="pct",
        color="category",
        color_discrete_sequence=[PALETTE["primary"], PALETTE["secondary"]],
        text=[f"{v:.1f}%" for v in counts["pct"]],
    )
    fig.update_layout(showlegend=False, height=380, template="plotly_white",
                      paper_bgcolor="white", plot_bgcolor="white",
                      font=dict(color="black"),
                      margin=dict(l=135, r=40, t=90, b=80),
                      autosize=False,
                      title="התפלגות כמות דוחות שהתקבלה",title_font_color="black")
    fig.update_traces(textposition="inside", insidetextanchor="middle",
                      constraintext="inside", cliponaxis=False)
    # px.bar maps category→color; pick contrast color per trace from its marker.
    for tr in fig.data:
        tr.textfont = dict(color=_text_on(tr.marker.color))
    fig.update_yaxes(title="pct", ticksuffix="%", automargin=True,tickfont=dict(color="black"))
    fig.update_xaxes(title="", automargin=True,tickfont=dict(color="black"))
    st.plotly_chart(fig, use_container_width=True)

with c2:
    avg_rows = []
    for label, sub in [("ביקשו להישפט", df[df["requested_trial"]]),
                       ("שילמו קנס / אחר", df[~df["requested_trial"]])]:
        for m in ["מגזר יהודי", "מגזר ערבי"]:
            sub_m = sub[sub["migzar"] == m]
            n = (sub_m["report_count_bin"] == "קיבלתי יותר מדו\"ח אחד").sum()
            tot = len(sub_m)
            avg_rows.append({"מסלול": label, "מגזר": m,
                             "% בעלי 2+ דוחות": (n / tot * 100) if tot else 0,
                             "n": tot})
    avg_df = pd.DataFrame(avg_rows)
    fig2 = px.bar(
        avg_df, x="מגזר", y="% בעלי 2+ דוחות", color="מסלול", barmode="group",
        color_discrete_map={"ביקשו להישפט": PALETTE["secondary"], "שילמו קנס / אחר": PALETTE["accent"]},
        text="% בעלי 2+ דוחות",
    )
    fig2.update_traces(texttemplate="%{text:.1f}%", textposition="inside",
                       insidetextanchor="middle",
                       constraintext="inside", cliponaxis=False)
    for tr in fig2.data:
        tr.textfont = dict(color=_text_on(tr.marker.color))
    fig2.update_layout(height=380, template="plotly_white",
                       paper_bgcolor="white", plot_bgcolor="white",
                       font=dict(color="black"),
                       margin=dict(l=135, r=40, t=90, b=80),
                       autosize=False,
                       title="שיעור בעלי 2+ דוחות — מסלול × מגזר",title_font_color="black", legend_title="מסלול", legend=dict(font=dict(color="black")))
    fig2.update_yaxes(ticksuffix="%", title="", automargin=True,tickfont=dict(color="black"))
    fig2.update_xaxes(automargin=True,title="", tickfont=dict(color="black"))
    st.plotly_chart(fig2, use_container_width=True)

render_insight("report_count", df)


# =========================================================
# 2. מועד קבלת הדוח (PPT 6-7)
# =========================================================
st.markdown("<div class='section-header'>2. מועד קבלת הדוח האחרון</div>", unsafe_allow_html=True)

st.plotly_chart(
    stacked_pct_bar(
        df.dropna(subset=["report_year_bin"]),
        group_col="migzar",
        value_col="report_year_bin",
        category_order=["דוח בשנים 24-25", "דוחות ישנים יותר"],
        color_map={"דוח בשנים 24-25": PALETTE["secondary"], "דוחות ישנים יותר": PALETTE["muted"]},
        title="התפלגות שנת הדוח לפי מגזר",
    ),
    use_container_width=True,
)

render_insight("report_year", df)


# =========================================================
# 3. סוגי עבירות (PPT 8-13) — tabs per segmentation
# =========================================================
st.markdown("<div class='section-header'>3. סוגי העבירות שהתקבלו</div>", unsafe_allow_html=True)

tab_labels = ["כללי", "מגדר", "גיל", "מסלול", "כמות דוחות", "שנת דוח", "אופן קבלה", "מחוז"]
tabs = st.tabs(tab_labels)

with tabs[0]:
    st.plotly_chart(horizontal_pct_bar(df, OFFENSE_COLS, title="סוגי העבירות בכללי"), use_container_width=True)

with tabs[1]:
    st.plotly_chart(horizontal_pct_bar(df, OFFENSE_COLS, title="סוגי העבירות לפי מגדר", group_col="gender"), use_container_width=True)

with tabs[2]:
    st.plotly_chart(horizontal_pct_bar(df, OFFENSE_COLS, title="סוגי העבירות לפי גיל", group_col="age_band"), use_container_width=True)

with tabs[3]:
    st.plotly_chart(horizontal_pct_bar(df, OFFENSE_COLS, title="סוגי העבירות לפי מסלול", group_col="trial_label"), use_container_width=True)

with tabs[4]:
    st.plotly_chart(horizontal_pct_bar(df, OFFENSE_COLS, title="סוגי העבירות לפי כמות דוחות", group_col="report_count_bin"), use_container_width=True)

with tabs[5]:
    st.plotly_chart(horizontal_pct_bar(df, OFFENSE_COLS, title="סוגי העבירות לפי שנת דוח", group_col="report_year_bin"), use_container_width=True)

with tabs[6]:
    st.plotly_chart(horizontal_pct_bar(df, OFFENSE_COLS, title="סוגי העבירות לפי אופן קבלה", group_col="report_channel_bin"), use_container_width=True)

with tabs[7]:
    if "mahoz_short" in df.columns:
        st.plotly_chart(horizontal_pct_bar(df, OFFENSE_COLS, title="סוגי העבירות לפי מחוז", group_col="mahoz_short", height=560), use_container_width=True)
    else:
        st.info("נתוני המחוזות לא זמינים")

render_insight("offense_type", df)


# =========================================================
# 4. ממי ואיך התקבל הדוח (PPT 14-15)
# =========================================================
st.markdown("<div class='section-header'>4. ממי ואיך התקבל הדוח</div>", unsafe_allow_html=True)

c1, c2 = st.columns(2)
with c1:
    src = df["report_source"].dropna()
    s = src.value_counts(normalize=True).reset_index() * 1
    s.columns = ["category", "pct"]
    s["pct"] = s["pct"] * 100
    fig = px.bar(s, x="category", y="pct",
                  color="category",
                  color_discrete_sequence=[PALETTE["primary"], PALETTE["secondary"], PALETTE["muted"]],
                  text=[f"{v:.1f}%" for v in s["pct"]])
    fig.update_layout(showlegend=False, height=380, template="plotly_white",
                      paper_bgcolor="white", plot_bgcolor="white",
                      font=dict(color="black"),
                      margin=dict(l=135, r=40, t=90, b=80),
                      autosize=False,
                      title="מקור הדוח",title_font_color="black", coloraxis_showscale=False)
    fig.update_traces(textposition="inside", insidetextanchor="middle",
                      constraintext="inside", cliponaxis=False)
    for tr in fig.data:
        tr.textfont = dict(color=_text_on(tr.marker.color))
    fig.update_yaxes(dict(tickfont=dict(color="black"), range=[0, max(s["pct"].max() * 1.15, 10)], automargin=True))
    fig.update_xaxes(dict(tickfont=dict(color="black"), title="", automargin=True))
    st.plotly_chart(fig, use_container_width=True)

with c2:
    ch = df["report_channel"].dropna()
    s = ch.value_counts(normalize=True).reset_index()
    s.columns = ["category", "pct"]
    s["pct"] = s["pct"] * 100
    fig = px.bar(s, x="pct", y="category", orientation="h",
                  color="pct", color_continuous_scale=["#cfe0f5", "#003366"],
                  text=[f"{v:.1f}%" for v in s["pct"]])
    fig.update_layout(showlegend=False, height=380, template="plotly_white",
                      paper_bgcolor="white", plot_bgcolor="white",
                      font=dict(color="black"),
                      margin=dict(l=135, r=40, t=90, b=80),
                      autosize=False,
                      title="אופן קבלת הדוח",title_font_color="black", coloraxis_showscale=False)
    # Colorscale produces a per-bar fill; pick text color per-bar from the pct.
    pct_max, pct_min = float(s["pct"].max()), float(s["pct"].min())
    span = max(pct_max - pct_min, 1e-9)
    per_text = ["white" if (p - pct_min) / span > 0.5 else "black" for p in s["pct"]]
    fig.update_traces(textposition="inside", insidetextanchor="middle",
                      constraintext="inside", cliponaxis=False,
                      textfont=dict(color=per_text))
    fig.update_xaxes(dict(tickfont=dict(color="black"), ticksuffix="%", title="", range=[0, max(s["pct"].max() * 1.2, 10)], automargin=True))
    fig.update_yaxes(dict(tickfont=dict(color="black"), title="", autorange="reversed", automargin=True,showgrid=True, gridcolor="black",gridwidth=1.2))
    st.plotly_chart(fig, use_container_width=True)


st.plotly_chart(
    stacked_pct_bar(
        df.dropna(subset=["report_channel_bin"]),
        group_col="trial_label",
        value_col="report_channel_bin",
        color_map={"פיזית משוטר בשטח": PALETTE["primary"], "כל השאר": PALETTE["accent"]},
        title="אופן הקבלה לפי מסלול",
    ),
    use_container_width=True,
)

render_insight("report_source", df)
render_insight("report_channel", df)
