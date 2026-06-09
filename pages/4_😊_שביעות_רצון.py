"""Page 4 — שביעות רצון והמלצות (PPT slides 33-34)."""
from __future__ import annotations

import os

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from utils.charts import (
    PALETTE,
    _text_on,
    LIKERT_3BAND_COLORS,
    LIKERT_3BAND_ORDER,
    empty_state,
    likert_summary_strip,
    stacked_pct_bar,
    district_stats_bar,
    district_comparison_grouped,
    district_trial_flow,
)
from utils.charts import kpi_card_html, get_common_kpis
from utils.data_loader import likert_to_3band
from utils.filters import init_global_filters, require_data
from utils.insights import render_insight


st.set_page_config(layout="wide", page_title="שביעות רצון והמלצות")


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
      <h1>😊 שביעות רצון והמלצות</h1>
      <p>איך תופסים את התהליך בסוף הדרך, ומה ממליצים לעשות לחבר שקיבל דוח</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# KPI row
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
# 1. שביעות רצון + הרתעה (PPT 33)
# =========================================================
st.markdown("<div class='section-header'>1. שביעות רצון מהתהליך והשפעה על נהיגה עתידית</div>", unsafe_allow_html=True)

fig = likert_summary_strip(
    df,
    columns=[
        ("process_satisfaction_num", "שביעות רצון מהתהליך"),
        ("future_caution_num", "עידוד לנהיגה זהירה בעתיד"),
    ],
    height=280,
    )
fig.update_traces(textfont_color='white')
fig.update_layout(title=dict(text=""))
st.plotly_chart(fig,use_container_width=True)

c1, c2 = st.columns(2)
with c1:
    work = df.copy()
    work["likert_band"] = likert_to_3band(work["process_satisfaction"])
    work["group"] = work["trial_label"] + " <br> " + work["migzar"].fillna("לא ידוע")
    st.plotly_chart(
        stacked_pct_bar(
            work.dropna(subset=["likert_band", "group"]),
            group_col="group", value_col="likert_band",
            category_order=LIKERT_3BAND_ORDER, color_map=LIKERT_3BAND_COLORS,
            title="שביעות רצון — מסלול × מגזר",
        ),
        use_container_width=True,
    )
with c2:
    work = df.copy()
    work["likert_band"] = likert_to_3band(work["future_caution"])
    work["group"] = work["trial_label"] + " <br> " + work["migzar"].fillna("לא ידוע")
    st.plotly_chart(
        stacked_pct_bar(
            work.dropna(subset=["likert_band", "group"]),
            group_col="group", value_col="likert_band",
            category_order=LIKERT_3BAND_ORDER, color_map=LIKERT_3BAND_COLORS,
            show_mean=True,
            title="עידוד לנהיגה זהירה — מסלול × מגזר",
        ),
        use_container_width=True,
    )

render_insight("satisfaction", df)


# =========================================================
# 2. המלצה לחבר (PPT 34)
# =========================================================
st.markdown("<div class='section-header'>2. המלצה לחבר שקיבל דוח</div>", unsafe_allow_html=True)

rec = df["friend_recommendation"].dropna()
rec = rec[~rec.isin(["אחר, פרט:", "לא יודע"])]

if len(rec):
    rows = []
    for trial_label in ["ביקשו להישפט", "שילמו קנס / אחר"]:
        sub = df[df["trial_label"] == trial_label]
        if len(sub):
            counts = sub["friend_recommendation"].value_counts  (normalize=True) * 100
            for cat, pct in counts.items():
                if cat in ["אחר, פרט:", "לא יודע"]:
                    continue
                rows.append({"מסלול": trial_label, "": cat, "אחוז": pct})

    rec_df = pd.DataFrame(rows)
    if len(rec_df):
        order = (
            rec_df.groupby("")["אחוז"].mean().sort_values(ascending=True).index.tolist()
        )
        fig = px.bar(
            rec_df, y="", x="אחוז", color="מסלול", barmode="group",
            orientation="h",
            color_discrete_map={"ביקשו להישפט": PALETTE["secondary"], "שילמו קנס / אחר": PALETTE["accent"]},
            category_orders={"": order},
            text=rec_df["אחוז"].round(1),
        )
        fig.update_traces(texttemplate="%{text}%", textposition="inside",
                          insidetextanchor="middle",
                          constraintext="inside", cliponaxis=False)
        for tr in fig.data:
            tr.textfont = dict(color=_text_on(tr.marker.color))
        fig.update_layout(
            template="plotly_white", height=460,
            paper_bgcolor="white", plot_bgcolor="white",
            font=dict(color="black"),
            margin=dict(l=135, r=40, t=90, b=80),
            autosize=False,
            title=dict(
                text="מה היו ממליצים לחבר — לפי מסלול",
                font=dict(color="black"),
            ),
            xaxis=dict(
                tickfont=dict(color="black"),
                title_font=dict(color="black"),
                automargin=True,
                ticksuffix="%",
            ),
            yaxis=dict(
                tickfont=dict(color="black"),
                title_font=dict(color="black"),
                automargin=True,
                showgrid=True,
                gridcolor="black",
                gridwidth=1
            ),
            legend=dict(
                font=dict(color="black"),
                title=dict(font=dict(color="black")),
            ),
        )
        st.plotly_chart(fig, use_container_width=True)
    # By sector
    rows2 = []
    for trial_label in ["ביקשו להישפט", "שילמו קנס / אחר"]:
        for m in ["מגזר יהודי", "מגזר ערבי"]:
            sub = df[(df["trial_label"] == trial_label) & (df["migzar"] == m)]
            if len(sub) >= 5:
                counts = sub["friend_recommendation"].value_counts(normalize=True) * 100
                for cat, pct in counts.items():
                    if cat in ["אחר, פרט:", "לא יודע"]:
                        continue
                    rows2.append({"קבוצה": f"{trial_label} — {m}", "המלצה": cat, "אחוז": pct})

    if rows2:
        rec_df2 = pd.DataFrame(rows2)
        fig2 = px.bar(
            rec_df2, x="קבוצה", y="אחוז", color="המלצה", barmode="stack",
            color_discrete_sequence=px.colors.qualitative.Set2,
            text=rec_df2["אחוז"].round(1),
        )
        fig2.update_traces(texttemplate="%{text}%", textposition="inside",
                            insidetextanchor="middle",
                            constraintext="inside", cliponaxis=False,
                            textfont=dict(color="white", size=11))
        fig2.update_layout(template="plotly_white", height=480,
                            paper_bgcolor="white", plot_bgcolor="white",
                            font=dict(color="black"),
                            margin=dict(l=135, r=40, t=90, b=80),
                            autosize=False,
                            title=dict(text="המלצות לחבר — לפי מסלול × מגזר",
                                       font=dict(color="black")),
                            legend=dict(font=dict(color="black")),legend_title_font_color="black",
                            xaxis=dict(tickfont=dict(color="black"), title_font=dict(color="black"), automargin=True),
                            yaxis=dict(tickfont=dict(color="black"), title_font=dict(color="black"), automargin=True))
        fig2.update_yaxes(ticksuffix="%", title="", automargin=True)
        fig2.update_xaxes(automargin=True)
        st.plotly_chart(fig2, use_container_width=True)
else:
    st.plotly_chart(empty_state(), use_container_width=True)

render_insight("friend_recommendation", df)


# =========================================================
# 3. ניתוח לפי מחוזות
# =========================================================
st.markdown("<div class='section-header'>3. שביעות רצון לפי מחוזות</div>", unsafe_allow_html=True)

if "mahoz_short" in df.columns and df["mahoz_short"].notna().any():
    c1, c2 = st.columns(2)
    with c1:
            district_stats_bar(df, "process_satisfaction_num", title="שביעות רצון מהתהליך — לפי מחוז"),
            use_container_width=True,
    
    with c2:
        st.plotly_chart(
            district_stats_bar(df, "future_caution_num", title="עידוד לנהיגה זהירה — לפי מחוז"),
            use_container_width=True,
        )

    st.plotly_chart(    
        district_comparison_grouped(
            df,
            numeric_cols=[
                ("process_satisfaction_num", "שביעות רצון"),
                ("future_caution_num", "עידוד לזהירות"),
            ],
            title="השוואת שביעות רצון ועידוד לזהירות לפי מחוזות (ממוצע ± סטיית תקן)"
            
        ),
        use_container_width=True,
    )

    st.plotly_chart(
        district_trial_flow(df),
        use_container_width=True,
    )
else:
    st.info("נתוני המחוזות לא זמינים בסינון הנוכחי")
