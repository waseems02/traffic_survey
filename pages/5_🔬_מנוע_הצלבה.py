"""Page 5 — מנוע הצלבה: dynamic crosstab builder (X × Y)."""
from __future__ import annotations

import os

import pandas as pd
import plotly.express as px
import streamlit as st

from utils.charts import PALETTE, _text_on, empty_state, heatmap_crosstab
from utils.charts import kpi_card_html, get_common_kpis
from utils.filters import init_global_filters, require_data


st.set_page_config(layout="wide", page_title="מנוע הצלבה")


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
      <h1>🔬 מנוע הצלבה דינמי</h1>
      <p>בנה הצלבה (Crosstab) של כל שני משתנים בנתונים — כדי לחקור דפוסים מעבר למה שהוצג במצגת</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# KPI row
kpis = get_common_kpis(df)
if {"requested_trial", "hearing_held_bin"}.issubset(df.columns):
    trial_hearing = df.loc[df['requested_trial'].fillna(False), 'hearing_held_bin'].dropna()
    hearing_pct = trial_hearing.eq("היה דיון בפועל").mean() * 100 if len(trial_hearing) else 0.0
    hearing_sub = f"מבין מבקשי ההישפט (n={len(trial_hearing)})" if len(trial_hearing) else "אין מספיק נתונים"
    hearing_value = f"{hearing_pct:.1f}%" if len(trial_hearing) else "-"
else:
    hearing_sub = "אין מספיק נתונים"
    hearing_value = "-"

k1, k2, k3, k4, k5 = st.columns(5)
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
    st.markdown(
        kpi_card_html("דיון בפועל בקרב מבקשי הישפטות", hearing_value, PALETTE["warn"],
                      sub=hearing_sub),
        unsafe_allow_html=True,
    )
with k5:
    sat_str = f"{kpis['sat_avg']:.2f} / 5" if kpis['sat_avg'] is not None else "-"
    sat_std_str = f"{kpis['sat_std']:.2f}" if kpis['sat_std'] is not None else "-"
    st.markdown(
        kpi_card_html("שביעות רצון מהתהליך", sat_str, PALETTE["danger"],
                      sub="ציון ממוצע", std_dev=sat_std_str),
        unsafe_allow_html=True,
    )


# Curated lists of canonical Hebrew-labeled columns to expose
DEMO_VARS = {
    "מגזר": "migzar",
    "מגדר": "gender",
    "קבוצת גיל": "age_band",
    "מחוז": "mahoz",
    "השכלה": "education",
    "מצב משפחתי": "family_status",
    "הכנסה משפחתית": "income",
    "דתיות": "religiosity",
    "שנת דוח": "report_year_bin",
    "כמות דוחות": "report_count_bin",
    "אופן קבלת הדוח": "report_channel_bin",
    "מקור הדוח": "report_source",
}

TARGET_VARS = {
    "מסלול (ביקשו להישפט)": "trial_label",
    "שילמו את הקנס בפועל": "paid_fine_actual",
    "מודעות להמרת דוח באזהרה": "aware_convert_warning",
    "ביקשו המרה לאזהרה": "asked_convert_warning",
    "התייעצות עם עו\"ד": "lawyer_consult_bin",
    "האם התקיים דיון בפועל": "hearing_held_bin",
    "מעקב סטטוס הבקשה": "tracked_status",
    "ייצוג ע\"י עו\"ד בדיון": "lawyer_repped",
    "המלצה לחבר": "friend_recommendation",
    "ביקש ראיות נוספות": "evidence_requested",
}


c1, c2, c3 = st.columns(3)
with c1:
    x_label = st.selectbox("ציר X — משתנה דמוגרפי/הקשרי", list(DEMO_VARS.keys()), index=0)
with c2:
    y_label = st.selectbox("ציר Y — משתנה התנהגותי/תוצאתי", list(TARGET_VARS.keys()), index=0)
with c3:
    normalize_choice = st.selectbox(
        "נירמול",
        ["שורה (לפי X) — אחוזים", "עמודה (לפי Y) — אחוזים", "סך הכל — אחוזים", "ספירות מוחלטות"],
        index=0,
    )

x_col = DEMO_VARS[x_label]
y_col = TARGET_VARS[y_label]

norm_map = {
    "שורה (לפי X) — אחוזים": "columns",
    "עמודה (לפי Y) — אחוזים": "index",
    "סך הכל — אחוזים": "all",
    "ספירות מוחלטות": None,
}
normalize = norm_map[normalize_choice]


st.markdown("<div class='section-header'>מטריצת ההצלבה</div>", unsafe_allow_html=True)

work = df[[x_col, y_col]].dropna()
if work.empty:
    st.plotly_chart(empty_state("אין שורות עם ערך בשני המשתנים תחת הסינון הנוכחי."), use_container_width=True)
    st.stop()


# Avoid extremely long Hebrew district names breaking the layout
if x_col == "mahoz":
    work[x_col] = work[x_col].astype(str).str[:30] + "..."


st.plotly_chart(
    heatmap_crosstab(work, x=x_col, y=y_col, normalize=normalize, height=520),
    use_container_width=True,
)


# =========================================================
# Stacked-bar view alongside the heatmap
# =========================================================
st.markdown("<div class='section-header'>תצוגה גרפית — % בתוך כל קבוצה</div>", unsafe_allow_html=True)

ct_pct = pd.crosstab(work[x_col], work[y_col], normalize="index") * 100
ct_long = ct_pct.reset_index().melt(id_vars=x_col, var_name=y_label, value_name="אחוז")

fig = px.bar(
    ct_long, x=x_col, y="אחוז", color=y_label, barmode="stack",
    color_discrete_sequence=px.colors.qualitative.Set2,
    text=ct_long["אחוז"].round(1),
)
fig.update_traces(texttemplate="%{text}%", textposition="inside",
                    insidetextanchor="middle",
                    constraintext="inside", cliponaxis=False,
                    textfont=dict(color="black", size=11))
fig.update_layout(template="plotly_white", height=480,
                    paper_bgcolor="white", plot_bgcolor="white",
                    font=dict(color="black"),
                    margin=dict(l=135, r=40, t=90, b=80),
                    autosize=False,
                    title=dict(text=f"{y_label} בתוך כל {x_label}",
                               font=dict(color="black")),
                    legend=dict(font=dict(color="black")),legend_title=dict(text=y_label, font=dict(color="black")))
fig.update_yaxes(ticksuffix="%", range=[0, 100], title="", automargin=True,
                    tickfont=dict(color="black"), title_font=dict(color="black"))
fig.update_xaxes(title=x_label, automargin=True,
                    tickfont=dict(color="black"), title_font=dict(color="black"))
st.plotly_chart(fig, use_container_width=True)


# =========================================================
# Raw crosstab table
# =========================================================
st.markdown("<div class='section-header'>טבלת הצלבה גולמית</div>", unsafe_allow_html=True)

ct = pd.crosstab(work[x_col], work[y_col], margins=True, margins_name="סה\"כ")
st.dataframe(
    ct.style.background_gradient(cmap="Blues", axis=None),
    use_container_width=True,
)


# Simple chi-square indication
try:
    from scipy.stats import chi2_contingency
    chi2, p, dof, _ = chi2_contingency(pd.crosstab(work[x_col], work[y_col]))
    significance = "✅ מובהק סטטיסטית (p < 0.05)" if p < 0.05 else "⚪ לא נמצא קשר מובהק (p ≥ 0.05)"
    st.markdown(
        f"""
        <div class='insight-box'>
          <h4>🧮 מבחן Chi-square לעצמאות</h4>
          <p>χ² = {chi2:.2f} | dof = {dof} | p-value = {p:.4f}</p>
          <p><b>{significance}</b></p>
        </div>
        """,
        unsafe_allow_html=True,
    )
except ImportError:
    st.caption("💡 התקן את scipy לקבלת מבחני סטטיסטיקה (pip install scipy)")
except Exception as exc:
    st.caption(f"לא ניתן לחשב מבחן Chi-square: {exc}")


st.markdown(
    """
    <div class='muted-note'>
      💡 טיפ: הסינון הגלובלי בצד עדיין פעיל — הצלבה תתבצע רק על המשיבים המסוננים. שנה פילטרים כדי לבחון דפוסים בתת-מדגמים שונים.
    </div>
    """,
    unsafe_allow_html=True,
)
