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
    DEMOGRAPHIC_SEQUENCE,
    empty_state,
    likert_summary_strip,
    stacked_pct_bar,
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


st.markdown(
    """
    <div class='insight-box'>
      <p>שביעות הרצון מהתהליך נמוכה במיוחד בקרב המבקשים להישפט בשני המגזרים — סימן ברור לכך שההליך המשפטי, ולא רק עצם הקנס, הוא מקור הכאב. עם זאת, נראה כי הדוחות מעודדים באופן בינוני נהיגה זהירה, עידוד לנהיגה זהירה נשמר יחסית יציב בכל הקבוצות, בקרב המשיבים שלא היו מרוצים מהתהליך. ההמלצות לחבר משקפות שני קולות נפרדים — מי שוויתרו על ההליך ממליצים "לשלם ולשכוח", ואילו מי שעברו את ההליך ממליצים לפנות לייעוץ ולדרוש את יומם בבית המשפט. ההבדל הזה הוא לב הרפורמה: להפוך את המסלול המשפטי לאפשרות אמיתית — ברורה, נגישה, ובעלת ערך — ולא לתהליך שמרתיע מראש.</p>
    </div>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# 1. שביעות רצון + הרתעה (PPT 33)
# =========================================================
st.markdown("<div class='section-header'>1. שביעות רצון מהתהליך והשפעה על נהיגה עתידית</div>", unsafe_allow_html=True)

chart_col, insight_col = st.columns([2, 1.2])
with chart_col:
    fig = likert_summary_strip(
        df,
        columns=[
            ("process_satisfaction_num", "שביעות רצון מהתהליך"),
            ("future_caution_num", "עידוד לנהיגה זהירה בעתיד"),
        ],
        height=280,
        )
    fig.update_traces(textfont_color='white')
    fig.update_layout(title=dict(text="שביעות רצון מהתהליך ועידוד לנהיגה זהירה — ציון ממוצע ± סטיית תקן (1-5)"))
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

with insight_col:
    _sat_mean = df["process_satisfaction_num"].mean()
    _caution_mean = df["future_caution_num"].mean()
    _sat_str = f"{_sat_mean:.2f}/5" if pd.notna(_sat_mean) else "-"
    _caution_str = f"{_caution_mean:.2f}/5" if pd.notna(_caution_mean) else "-"
    st.markdown(
        f"""
        <div class='insight-box'>
          <h4>💡 שביעות רצון מהתהליך והשפעה על נהיגה עתידית</h4>
          <p>שני המדדים הללו תופסים שתי זוויות שונות של אותו תהליך: עד כמה החוויה הייתה נוחה ועד כמה היא הותירה השפעה התנהגותית. בולט הפער בין השניים — שביעות הרצון מהתהליך נמוכה יותר מהציון על עידוד לנהיגה זהירה, מה שמרמז שגם תהליך הנחווה כלא־ידידותי עדיין מצליח לשרת את המטרה ההרתעתית של מערכת האכיפה.</p>
          <p>בחיתוך לפי מסלול × מגזר ניכר כי שביעות הרצון נמוכה במיוחד בקרב המבקשים להישפט בשני המגזרים — סימן לכך שהמפגש עם ההליך המשפטי עצמו, ולא רק עם הקנס, הוא נקודת הכאב המרכזית. עידוד לנהיגה זהירה, לעומת זאת, נשאר יציב יחסית בין הקבוצות, כלומר המסר ההרתעתי מועבר באופן רוחבי גם כאשר התהליך עצמו אינו מספק.</p>
          <p class='live-stat'>📊 מהמדגם המסונן הנוכחי: שביעות רצון ממוצעת: {_sat_str} | עידוד לנהיגה זהירה: {_caution_str}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


# =========================================================
# 2. המלצה לחבר (PPT 34)
# =========================================================
st.markdown("<div class='section-header'>2. המלצה לחבר שקיבל דוח</div>", unsafe_allow_html=True)

chart_col, insight_col = st.columns([2, 1.2])
with chart_col:
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
            fig = px.bar(
                rec_df, x="מסלול", y="אחוז", color="", barmode="stack",
                color_discrete_sequence=DEMOGRAPHIC_SEQUENCE,
                text=rec_df["אחוז"].round(1),
            )
            fig.update_traces(texttemplate="%{text}%", textposition="inside",
                              insidetextanchor="middle",
                              constraintext="inside", cliponaxis=False,
                              textfont=dict(color="white", size=13))
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
                    title="",
                ),
                yaxis=dict(
                    tickfont=dict(color="black"),
                    title_font=dict(color="black"),
                    automargin=True,
                    ticksuffix="%",
                    title="",
                ),
                legend=dict(
                    font=dict(color="black"),
                    title=dict(text="המלצה", font=dict(color="black")),
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
                color_discrete_sequence=DEMOGRAPHIC_SEQUENCE,
                text=rec_df2["אחוז"].round(1),
            )
            fig2.update_traces(texttemplate="%{text}%", textposition="inside",
                                insidetextanchor="middle",
                                constraintext="inside", cliponaxis=False,
                                textfont=dict(color="white", size=13))
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

with insight_col:
    render_insight("friend_recommendation", df)
    render_insight("satisfaction", df)


