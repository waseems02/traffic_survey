"""Page 0 — סקירה כללית (overview KPIs and headline charts)."""
from __future__ import annotations

import os

import streamlit as st

from utils.charts import (
    PALETTE,
    kpi_card_html,
    sankey_trial_flow,
    sunburst,
    horizontal_pct_bar,
    district_stats_bar,
    district_comparison_grouped,
    district_trial_flow,
    sector_outcomes_stack,
    gender_outcomes_stack,
)
from utils.data_loader import OFFENSE_COLS
from utils.filters import init_global_filters, require_data


st.set_page_config(layout="wide", page_title="סקירה כללית", page_icon="📊")


def _inject_css():
    path = os.path.join(os.path.dirname(__file__), "..", "assets", "styles.css")
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


_inject_css()


with st.sidebar:
    st.markdown("<div class='sb-section'>פעולות</div>", unsafe_allow_html=True)
    if st.button("🔄 החלף קובץ נתונים", use_container_width=True):
        st.session_state["replace_data_mode"] = True
        st.session_state.pop("uploaded_bytes", None)
        st.cache_data.clear()
        st.rerun()


init_global_filters()
filtered = require_data()
df = st.session_state.get("raw_data", filtered)


st.markdown(
    """
    <div class='page-header'>
      <h1>📊 סקירה כללית</h1>
      <p>תמונת-על של ממצאי הסקר — מדדי מפתח, פילוחים, וזרימת מסע מקבל הדוח</p>
    </div>
    """,
    unsafe_allow_html=True,
)


st.markdown("<div class='section-header'>מדדי מפתח</div>", unsafe_allow_html=True)

total = len(filtered)
trial_pct = filtered["requested_trial"].mean() * 100 if total else 0
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


st.markdown("<div class='section-header'>על הסקר</div>", unsafe_allow_html=True)
st.markdown(
    """
    <div class='insight-box'>
      <h4>🎯 מטרות</h4>
      <p>הסקר נועד למפות את חוויית האזרח המקבל דו"ח תעבורה, משלב קבלת הדו"ח וההיכרות עם חלופות התגובה, דרך ההתנהלות עם ההליך המשפטי, ועד להערכת שביעות הרצון והצעות לשיפור. ממצאי הסקר ישמשו בסיס להשוואה (As-Is) לקראת יישום רפורמת חוק "הפרות תעבורה מנהליות" והקמת בית דין מקוון לתעבורה על ידי משרד המשפטים.</p>
      <h4>🔬 מתודולוגיה</h4>
      <p><b>שיטה:</b> מילוי עצמי באינטרנט (Panel View), דגימה הסתברותית אקראית, עבודת שדה 11/2025 – 1/2026.</p>
      <p><b>מדגם:</b> 505 משיבים — 263 שבחרו לא להישפט (177 יהודים, 86 ערבים) | 242 שבחרו להישפט (161 יהודים, 81 ערבים).</p>
      <p>הסקר נעשה באמצעות פאנל אינטרנטי (מילוי עצמי באינטרנט) על ידי חברת CI מידע שיווקי, בין התאריכים 11/2025-1/2026, מתוך כלל הנהגים בישראל. בעקבות רצון לחקור הן את הנהגים המבקשים לשלם מיד (המהווים יותר מ-80% מהנהגים) והן את המבקשים להישפט, הדגימה נעשתה מכל קבוצה בנפרד. לפיכך כלל הניתוחים מוצגים בנפרד.</p>
      <p>יש לשים לב כי ההתפלגות הכללית של הסקר נותנת ייצוג עודף של המבקשים להישפט.</p>
      <p>מתוך נתוני המשטרה המשקפים את כלל אוכלוסיית הנהגים: כ-50% מכלל הדוחות ניתנים למגזר הערבי, וכ-50% מהמבקשים להישפט הינם מהמגזר הערבי. מעל 80% מהנשפטים הם גברים (בשני המגזרים).</p>
      <h4>💡 התמצאות בדו"ח</h4>
      <p>ניתן לעבור בין חלקי הדוח באמצעות לחיצה על האייקונים מצד ימין.</p>
      <p>ניתן לעשות שימוש במסננים של המשתנים הדמוגרפיים על מנת לראות פילוחים נוספים של הנתונים.</p>
      <p>ניתן לראות את גודל המדגם המתעדכן עבור כל גרף בראש העמוד, או מצד ימין מתחת למסננים.</p>
    </div>
    """,
    unsafe_allow_html=True,
)


st.markdown("<div class='section-header'>תוצאות מרכזיות של הסקר</div>", unsafe_allow_html=True)
st.markdown(
    """
    <div class='insight-box'>
      <p>בעמוד זה מוצגת תמונת-על של ממצאי הסקר. ראשית, פילוח שלוש התוצאות המרכזיות — בקשת הישפטות, תשלום הקנס בפועל, ושביעות רצון מהתהליך — לפי מגזר ולפי מגדר, המצביע על פערים בולטים בין הקבוצות השונות באופן ההתמודדות עם הדוח. בהמשך מוצג גרף זרימה (Sankey) המתאר את מסע מקבל הדוח, מנקודת קבלת הדוח ועד התוצאה בפועל (תשלום הקנס או קיום דיון).</p>
      <p>לאחר מכן מוצג הרכב המדגם — שילוב של מגזר, מגדר וגיל — לצד התפלגות סוגי העבירות הנפוצות במדגם. הניתוח הגיאוגרפי משווה בין מחוזות המשטרה השונים בארבעה ממדים: שביעות רצון מהתהליך, הבנת העבירה, התפלגות מסלול ההישפטות, ומדדי תפיסה משווים.</p>
      <p><b>שימו לב:</b> ההתפלגות בכל גרף תלויה במסננים שנבחרו בראש העמוד. כל תובנה כאן צריכה להיקרא יחד עם ההערה במתודולוגיה — המדגם פוצל מראש בין מבקשי הישפטות ללא־מבקשים, ולכן השוואות בין הקבוצות אינן משקפות שכיחות אמיתית באוכלוסייה.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    "<div class='section-header'>תוצאות מרכזיות לפי מגזר</div>",
    unsafe_allow_html=True,
)
st.plotly_chart(sector_outcomes_stack(filtered), use_container_width=True)

st.markdown(
    "<div class='section-header'>תוצאות מרכזיות לפי מגדר</div>",
    unsafe_allow_html=True,
)
st.plotly_chart(gender_outcomes_stack(filtered), use_container_width=True)


st.markdown("<div class='section-header'>זרימת המסע — מקבלת הדוח לתוצאה</div>", unsafe_allow_html=True)

chart_col, insight_col = st.columns([2, 1.2])
with chart_col:
    st.plotly_chart(sankey_trial_flow(filtered), use_container_width=True)

with insight_col:
    st.markdown(
        """
        <div class='insight-box'>
          <p>הגרף הבא מציג את ארבע התוצאות הסופיות של מסע מקבל הדוח, ממוינות מהשכיחה ביותר לפחות שכיחה. אורך כל עמודה ואחוז המוצג בתוכה מתייחסים לכלל המשיבים בסינון הנוכחי.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


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


st.info("💡 השתמש בתפריט הצדדי כדי לנווט בין דפי הניתוח. הסינון משפיע על כל הדפים והגרפים אוטומטית.")
