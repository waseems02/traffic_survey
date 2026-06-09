"""Home page — Ministry of Justice Traffic-Reports dashboard."""
from __future__ import annotations

import os

import pandas as pd
import streamlit as st

from utils.charts import (
    PALETTE,
    _text_on,
    kpi_card_html,
    sankey_trial_flow,
    sunburst,
    grouped_bar,
    horizontal_pct_bar,
    district_stats_bar,
    district_comparison_grouped,
    district_trial_flow,
    sector_outcomes_stack,
    gender_outcomes_stack,
)
from utils.data_loader import OFFENSE_COLS, load_clean, load_default_or_upload
from utils.filters import render_sidebar_filters
from utils.insights import render_insight


st.set_page_config(
    page_title="מערכת אנליטיקה - מקבלי דוחות תעבורה",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded",
)


def inject_css():
    path = os.path.join(os.path.dirname(__file__), "assets", "styles.css")
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


inject_css()


st.markdown(
    """
    <div class='dashboard-hero'>
      <h1>⚖️ מערכת אנליטיקה — מקבלי דוחות תעבורה</h1>
      <p>מחקר טרום-רפורמה של משרד המשפטים | 505 משיבים | אפריל 2026</p>
    </div>
    """,
    unsafe_allow_html=True,
)


replace_data_mode = st.session_state.get("replace_data_mode", False)

with st.sidebar:
    if st.button("🔄 החלף קובץ נתונים"):
        st.session_state["replace_data_mode"] = True
        st.session_state.pop("uploaded_bytes", None)
        st.cache_data.clear()
        st.rerun()

if replace_data_mode:
    df = None
else:
    df = load_default_or_upload("data.xlsx")

if df is None:
    message = "⚠️ העלה קובץ אקסל חדש כדי להחליף את קובץ הנתונים הנוכחי:" if replace_data_mode else "⚠️ קובץ הנתונים `data.xlsx` לא נמצא. ניתן להעלות קובץ ידנית:"
    st.warning(message)
    uploaded = st.file_uploader(
        "העלאת קובץ אקסל (.xlsx)",
        type=["xlsx", "xls"],
        key="home_uploader",
    )
    if uploaded is not None:
        st.session_state["uploaded_bytes"] = uploaded.getvalue()
        st.session_state["replace_data_mode"] = False
        st.rerun()
    st.stop()

filtered = render_sidebar_filters(df)
st.session_state["raw_data"] = df
st.session_state["filtered_data"] = filtered

st.markdown("<div class='section-header'>מדדי מפתח</div>", unsafe_allow_html=True)

total = len(filtered)
trial_pct = filtered["requested_trial"].mean() * 100 if total else 0
trial_pct_std = (filtered["requested_trial"].std() * 100) if total else 0
paid_pct = filtered.loc[~filtered["requested_trial"], "paid_fine_actual"].eq("כן").mean() * 100 if total else 0
sat_avg = filtered["process_satisfaction_num"].mean() if total else 0
sat_std = filtered["process_satisfaction_num"].std() if total else 0


k1, k2, k3, k4 = st.columns(4)
with k1:
    st.markdown(
        kpi_card_html("סך כל המשיבים בסינון", f"{total:,}", PALETTE["primary"],
                      sub=f"מתוך {len(df):,} במדגם המלא"),
        unsafe_allow_html=True,
    )
with k2:
    st.markdown(
        kpi_card_html("שיעור בקשות הישפטות", f"{trial_pct:.1f}%", PALETTE["secondary"],
                      sub="מתוך המסוננים"),
        unsafe_allow_html=True,
    )
with k3:
    st.markdown(
        kpi_card_html("שילמו את הקנס בפועל", f"{paid_pct:.1f}%", PALETTE["accent"],
                      sub="בקרב מי שלא ביקשו להישפט"),
        unsafe_allow_html=True,
    )
with k4:
    sat_str = f"{sat_avg:.2f} / 5" if sat_avg else "-"
    sat_std_str = f"{sat_std:.2f}" if sat_std else "-"
    st.markdown(
        kpi_card_html("שביעות רצון מהתהליך", sat_str, PALETTE["warn"],
                      sub="ציון ממוצע",
                      std_dev=sat_std_str),
        unsafe_allow_html=True,
    )


st.markdown(
    "<div class='section-header'>בכלליות — תוצאות מרכזיות לפי מגזר</div>",
    unsafe_allow_html=True,
)
st.plotly_chart(sector_outcomes_stack(filtered), use_container_width=True)

st.markdown(
    "<div class='section-header'>בכלליות — תוצאות מרכזיות לפי מגדר</div>",
    unsafe_allow_html=True,
)
st.plotly_chart(gender_outcomes_stack(filtered), use_container_width=True)


st.markdown("<div class='section-header'>זרימת המסע — מקבלת הדוח לתוצאה</div>", unsafe_allow_html=True)
st.plotly_chart(sankey_trial_flow(filtered), use_container_width=True)


st.markdown("<div class='section-header'>הרכב המדגם</div>", unsafe_allow_html=True)
c1, c2 = st.columns([1.2, 1])
with c1:
    st.markdown("**מגזר × מגדר × גיל**")
    st.plotly_chart(
        sunburst(filtered, path=["migzar", "gender", "age_band"], title="הרכב המדגם לפי מגזר, מגדר וקבוצת גיל"),
        use_container_width=True,
    )
with c2:
    st.markdown("**סוגי העבירות הנפוצים במדגם**")
    st.plotly_chart(
        horizontal_pct_bar(filtered, OFFENSE_COLS, sort_desc=True, title="ההתפלגות של סוגי העבירות במדגם"),
        use_container_width=True,
    )

st.markdown("<div class='section-header'>ניתוח לפי מחוזות</div>", unsafe_allow_html=True)
districts = sorted([d for d in filtered["mahoz_short"].dropna().unique() if str(d).lower() != "nan"]) if "mahoz_short" in filtered.columns else []
if districts and len(filtered) > 0:
    c1, c2 = st.columns(2)
    with c1:
        st.plotly_chart(
            district_stats_bar(filtered, "process_satisfaction_num", title="שביעות רצון מהתהליך לפי מחוז"),
            use_container_width=True,
        )
    with c2:
        st.plotly_chart(
            district_stats_bar(filtered, "understand_offense_num", title="הבנת העבירה לפי מחוז"),
            use_container_width=True,
        )

    st.plotly_chart(
        district_trial_flow(filtered),
        use_container_width=True,
    )

    st.plotly_chart(
        district_comparison_grouped(
            filtered,
            numeric_cols=[
                ("process_satisfaction_num", "שביעות רצון"),
                ("future_caution_num", "עידוד לזהירות"),
                ("report_justified_num", "מוצדקות הדוח"),
            ],
        ),
        use_container_width=True,
    )
else:
    st.info("אין נתונים זמינים לניתוח לפי מחוז")

st.markdown("<div class='section-header'>על המחקר</div>", unsafe_allow_html=True)
st.markdown(
    """
    <div class='insight-box'>
      <h4>🎯 מטרת המחקר</h4>
      <p>הבנת חוויית האזרח המקבל דו"ח תעבורה — מקבלת הדו"ח, דרך מודעות לחלופות התגובה והתמודדות בפועל, ההליך המשפטי, ועד שביעות רצון והמלצות. המחקר משמש כ-As-Is טרום ביצוע רפורמת חוק "הפרות תעבורה מנהליות" של משרד המשפטים.</p>
      <p><b>מתודולוגיה:</b> מילוי עצמי באינטרנט (Panel View), דגימה הסתברותית אקראית, עבודת שדה 11/2025 – 1/2026.</p>
      <p><b>מדגם:</b> 505 מרואיינים — 263 שבחרו לא להישפט (177 יהודים, 86 ערבים) | 242 שבחרו להישפט (161 יהודים, 81 ערבים).</p>
    </div>
    """,
    unsafe_allow_html=True,
)


st.info("💡 השתמש בתפריט הצדדי כדי לנווט בין דפי הניתוח. הסינון משפיע על כל הדפים והגרפים אוטומטית.")
