"""Page 2 — הבנה, חלופות והתמודדות בפועל (PPT slides 17-23)."""
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
    YESNO_COLORS,
    donut,
    empty_state,
    horizontal_pct_bar,
    likert_summary_strip,
    stacked_pct_bar,
)
from utils.charts import kpi_card_html, get_common_kpis
from utils.data_loader import NO_TRIAL_REASONS, likert_to_3band
from utils.filters import init_global_filters, require_data
from utils.insights import render_insight


st.set_page_config(layout="wide", page_title="הבנה וחלופות")


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
      <h1>🧠 הבנה, חלופות והתמודדות בפועל</h1>
      <p>מה הבינו, מה ידעו, את מי התייעצו, ואיך הגיבו בפועל</p>
    </div>
    """,
    unsafe_allow_html=True,
)


# KPIs
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
# 1. תפיסות הליבה (PPT 17)
# =========================================================
st.markdown("<div class='section-header'>1. תפיסות כלפי קבלת הדוח</div>", unsafe_allow_html=True)

st.plotly_chart(
    likert_summary_strip(
        df,
        columns=[
            ("understand_offense_num", "הבנת העבירה והעונש"),
            ("understand_options_num", "הבנת אפשרויות הפעולה"),
            ("report_justified_num", "מוצדקות הדוח"),
            ("voice_heard_num", "האפשרות להשמיע קול"),
        ],
        height=330,
    ),
    use_container_width=True,
)

c1, c2 = st.columns(2)
for col, label, container in [
    ("understand_offense", "הבנת העבירה והעונש — לפי מסלול × מגזר", c1),
    ("report_justified", "מוצדקות הדוח — לפי מסלול × מגזר", c2),
]:
    with container:
        work = df.copy()
        work["likert_band"] = likert_to_3band(work[col])
        work["group"] = work["trial_label"] + " — " + work["migzar"].fillna("לא ידוע")
        fig = stacked_pct_bar(
            work.dropna(subset=["likert_band", "group"]),
            group_col="group",
            value_col="likert_band",
            category_order=LIKERT_3BAND_ORDER,
            color_map=LIKERT_3BAND_COLORS,
            show_mean=True,
            mean_col=f"{col}_num",
            title=label,
        )
        st.plotly_chart(fig, use_container_width=True)

render_insight("understanding", df)


# =========================================================
# 2. מודעות לחלופות (PPT 18-19)
# =========================================================
st.markdown("<div class='section-header'>2. מודעות לחלופות הקיימות</div>", unsafe_allow_html=True)

c1, c2 = st.columns([1, 1.3])
with c1:
    no_trial = df[~df["requested_trial"]]
    awareness = pd.DataFrame({
        "category": ["ידעו על המרה לאזהרה", "ידעו על בקשה להישפט", "לא ידעו כלל"],
        "pct": [
            no_trial["aware_convert"].mean(skipna=True) * 100,
            no_trial["aware_trial"].mean(skipna=True) * 100,
            no_trial["aware_none"].mean(skipna=True) * 100,
        ],
    })
    fig = px.bar(awareness, x="category", y="pct",
                  color="category",
                  color_discrete_sequence=[PALETTE["accent"], PALETTE["secondary"], PALETTE["danger"]],
                  text=[f"{v:.1f}%" for v in awareness["pct"]])
    fig.update_layout(showlegend=False, height=380, template="plotly_white",
                      paper_bgcolor="white", plot_bgcolor="white",
                      font=dict(color="black"),
                      title="מודעות בקרב מי שלא ביקשו להישפט")
    fig.update_traces(textposition="inside", insidetextanchor="middle",
                      constraintext="inside", cliponaxis=False)
    for tr in fig.data:
        tr.textfont = dict(color=_text_on(tr.marker.color))
    fig.update_yaxes(ticksuffix="%", title="", automargin=True)
    fig.update_xaxes(title="")
    st.plotly_chart(fig, use_container_width=True)

with c2:
    rows = []
    for m in df["migzar"].dropna().unique():
        sub = no_trial[no_trial["migzar"] == m]
        if len(sub) == 0:
            continue
        rows.append({"מגזר": m, "סוג": "ידעו על המרה לאזהרה", "pct": sub["aware_convert"].mean(skipna=True) * 100})
        rows.append({"מגזר": m, "סוג": "ידעו על בקשה להישפט", "pct": sub["aware_trial"].mean(skipna=True) * 100})
        rows.append({"מגזר": m, "סוג": "לא ידעו כלל", "pct": sub["aware_none"].mean(skipna=True) * 100})
    if rows:
        seg_df = pd.DataFrame(rows)
        fig = px.bar(seg_df, x="מגזר", y="pct", color="סוג", barmode="group",
                      color_discrete_sequence=[PALETTE["accent"], PALETTE["secondary"], PALETTE["danger"]],
                      text=seg_df["pct"].round(1))
        fig.update_traces(texttemplate="%{text}%", textposition="inside", insidetextanchor="middle",
                          constraintext="inside", cliponaxis=False)
        for tr in fig.data:
            tr.textfont = dict(color=_text_on(tr.marker.color))
        fig.update_layout(height=380, template="plotly_white",
                          paper_bgcolor="white", plot_bgcolor="white",
                          font=dict(color="black"),
                          title="מודעות לחלופות לפי מגזר")
        fig.update_yaxes(ticksuffix="%", title="", automargin=True)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.plotly_chart(empty_state(), use_container_width=True)

render_insight("awareness", df)


# =========================================================
# 3. התייעצות עם עורך דין (PPT 20-21)
# =========================================================
st.markdown("<div class='section-header'>3. צורך בליווי משפטי</div>", unsafe_allow_html=True)

st.plotly_chart(
    stacked_pct_bar(
        df.dropna(subset=["lawyer_consult_bin"]),
        group_col="trial_label",
        value_col="lawyer_consult_bin",
        category_order=["לא חשתי צורך להתייעץ או להיעזר בעורך דין", "חשבתי להתייעץ עם עורך דין", "כן, התייעצתי/נעזרתי בעורך דין"],
        color_map={
            "לא חשתי צורך להתייעץ או להיעזר בעורך דין": PALETTE["muted"],
            "חשבתי להתייעץ עם עורך דין": PALETTE["warn"],
            "כן, התייעצתי/נעזרתי בעורך דין": PALETTE["secondary"],
        },
        title="צורך בליווי עו\"ד לפי מסלול",
    ),
    use_container_width=True,
)


work = df.copy()
work["group"] = work["trial_label"] + " — " + work["migzar"].fillna("לא ידוע")
st.plotly_chart(
    stacked_pct_bar(
        work.dropna(subset=["lawyer_consult_bin", "group"]),
        group_col="group",
        value_col="lawyer_consult_bin",
        category_order=["לא חשתי צורך להתייעץ או להיעזר בעורך דין", "חשבתי להתייעץ עם עורך דין", "כן, התייעצתי/נעזרתי בעורך דין"],
        color_map={
            "לא חשתי צורך להתייעץ או להיעזר בעורך דין": PALETTE["muted"],
            "חשבתי להתייעץ עם עורך דין": PALETTE["warn"],
            "כן, התייעצתי/נעזרתי בעורך דין": PALETTE["secondary"],
        },
        title="צורך בליווי עו\"ד — מסלול × מגזר",
    ),
    use_container_width=True,
)

render_insight("lawyer", df)


# =========================================================
# 4. המרת הדוח לאזהרה + חסמי הישפטות (PPT 22)
# =========================================================
st.markdown("<div class='section-header'>4. המרת הדוח לאזהרה וחסמי הישפטות</div>", unsafe_allow_html=True)

c1, c2 = st.columns([1, 1.2])
with c1:
    base = df[(~df["requested_trial"]) & (df["aware_convert"] == 1)]
    rows = []
    for m in ["מגזר יהודי", "מגזר ערבי"]:
        sub = base[base["migzar"] == m]
        if len(sub):
            rate = sub["asked_convert_warning"].eq("כן").mean() * 100
            rows.append({"מגזר": m, "שיעור שביקשו המרה (%)": rate, "n": len(sub)})
    if rows:
        conv_df = pd.DataFrame(rows)
        fig = px.bar(conv_df, x="מגזר", y="שיעור שביקשו המרה (%)",
                      color="מגזר",
                      color_discrete_sequence=[PALETTE["primary"], PALETTE["accent"]],
                      text=[f"{v:.1f}%" for v in conv_df['שיעור שביקשו המרה (%)']])
        fig.update_traces(textposition="inside", insidetextanchor="middle",
                          constraintext="inside", cliponaxis=False)
        for tr in fig.data:
            tr.textfont = dict(color=_text_on(tr.marker.color))
        fig.update_layout(showlegend=False, height=400, template="plotly_white",
                          paper_bgcolor="white", plot_bgcolor="white",
                          font=dict(color="black"),
                          title="שיעור בקשת המרה לאזהרה (מודעים בלבד)")
        fig.update_yaxes(ticksuffix="%", range=[0, 80], automargin=True)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.plotly_chart(empty_state(), use_container_width=True)

with c2:
    reasons_pct = {}
    no_trial_aware = df[(~df["requested_trial"])]
    for col, label in NO_TRIAL_REASONS.items():
        if col in no_trial_aware.columns:
            val = no_trial_aware[col].mean(skipna=True)
            if pd.notna(val):
                reasons_pct[label] = val * 100
    if reasons_pct:
        s = pd.Series(reasons_pct).sort_values(ascending=True)
        fig = go.Figure(go.Bar(
            x=s.values, y=s.index, orientation="h",
            marker_color=PALETTE["danger"],
            text=[f"{v:.1f}%" for v in s.values],
            textposition="inside",
            constraintext="inside", cliponaxis=False,
            insidetextanchor="middle", textfont=dict(color="white"),
        ))
        fig.update_layout(title="חסמים לבקשת הישפטות / סיבות אי-המרה",
                          height=400, template="plotly_white")
        fig.update_xaxes(ticksuffix="%", title="")
        fig.update_yaxes(title="", automargin=True)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.plotly_chart(empty_state(), use_container_width=True)

render_insight("conversion", df)


# =========================================================
# 5. תשלום קנס בפועל (PPT 23)
# =========================================================
st.markdown("<div class='section-header'>5. תשלום הקנס בפועל</div>", unsafe_allow_html=True)

paid_base = df[~df["requested_trial"]]
rows = []
for m in ["מגזר יהודי", "מגזר ערבי"]:
    sub = paid_base[paid_base["migzar"] == m]
    if len(sub):
        rate = sub["paid_fine_actual"].eq("כן").mean() * 100
        rows.append({"מגזר": m, "% שילמו": rate, "% לא שילמו": 100 - rate, "n": len(sub)})
if rows:
    pay_df = pd.DataFrame(rows)
    fig = go.Figure()
    fig.add_trace(go.Bar(name="כן — שילמו", x=pay_df["מגזר"], y=pay_df["% שילמו"],
                          marker_color=PALETTE["accent"],
                          text=[f"{v:.1f}%" for v in pay_df["% שילמו"]],
                          textposition="inside", insidetextanchor="middle",
                          constraintext="inside", cliponaxis=False,
                          textfont=dict(color="white", size=14)))
    fig.add_trace(go.Bar(name="לא — לא שילמו", x=pay_df["מגזר"], y=pay_df["% לא שילמו"],
                          marker_color=PALETTE["danger"],
                          text=[f"{v:.1f}%" for v in pay_df["% לא שילמו"]],
                          textposition="inside", insidetextanchor="middle",
                          constraintext="inside", cliponaxis=False,
                          textfont=dict(color="white", size=14)))
    fig.update_layout(barmode="stack", template="plotly_white", height=420,
                      title="שיעור תשלום הקנס בקרב מי שלא ביקשו להישפט")
    fig.update_yaxes(ticksuffix="%", range=[0, 100], automargin=True)
    st.plotly_chart(fig, use_container_width=True)
else:
    st.plotly_chart(empty_state(), use_container_width=True)

render_insight("fine_payment", df)
