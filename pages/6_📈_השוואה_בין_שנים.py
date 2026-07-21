"""Page 6 — year-over-year comparison view.

Shows the main dataset (e.g. 2025 wave) side-by-side with an optional
second dataset (e.g. 2026 wave) uploaded via the home page. Inspired by
the Muni100 Power-BI layout: text panel on the left, Israel map in the
middle, comparison bar chart on the right.
"""
from __future__ import annotations

import os

import numpy as np
import pandas as pd
import streamlit as st

from utils.charts import (
    COMPARISON_COLORS,
    PALETTE,
    comparison_kpi_card,
    empty_state,
    israel_district_map,
    year_comparison_bar,
    _mean_by_group,
    _percent_by_group,
    _rate_by_group,
)
from utils.data_loader import (
    comparison_label,
    load_comparison_or_none,
    load_default_or_upload,
    main_label,
)


st.set_page_config(layout="wide", page_title="השוואה בין שנים", page_icon="📈")


def _inject_css():
    path = os.path.join(os.path.dirname(__file__), "..", "assets", "styles.css")
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


_inject_css()


# -----------------------------------------------------------------------------
#  Data loading
# -----------------------------------------------------------------------------
main_df = st.session_state.get("raw_data")
if main_df is None:
    main_df = load_default_or_upload("data.xlsx")
    if main_df is not None:
        st.session_state["raw_data"] = main_df

comp_df = load_comparison_or_none()
lbl_main = main_label()
lbl_comp = comparison_label()

if main_df is None:
    st.warning("⚠️ לא נטענו נתונים. חזור לדף הבית וטען את קובץ הנתונים הראשי.")
    st.stop()


# -----------------------------------------------------------------------------
#  Hero
# -----------------------------------------------------------------------------
st.markdown(
    f"""
    <div class='cmp-hero'>
      <div class='cmp-hero__title'>📈 השוואה בין שנים</div>
      <div class='cmp-hero__sub'>
        השווה בין גל הסקר הנוכחי לבין גל סקר קודם — פילוח לפי מחוז, מגזר, מגדר, גיל ועוד.
      </div>
      <div class='cmp-hero__tags'>
        <span class='cmp-tag cmp-tag--main'>● {lbl_main} · {len(main_df):,} משיבים</span>
        <span class='cmp-tag cmp-tag--comp'>● {lbl_comp} · {(len(comp_df) if comp_df is not None else 0):,} משיבים</span>
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)


# -----------------------------------------------------------------------------
#  Empty state: no comparison dataset uploaded
# -----------------------------------------------------------------------------
if comp_df is None:
    st.markdown(
        f"""
        <div class='cmp-empty'>
          <h3>אין עדיין קובץ להשוואה 📊</h3>
          <p>כדי להשוות בין <b>{lbl_main}</b> לבין גל סקר נוסף, חזור לדף הבית ולחץ על
             <code>📊 העלה קובץ להשוואה</code> בסרגל הצדדי, ולאחר מכן העלה את הקובץ.</p>
          <p>ניתן גם לתת שם מותאם אישית לכל גל (למשל: <b>2025</b> ו-<b>2026</b>) כדי שהתוויות
             בגרפים יהיו ברורות.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    # Still show the main dataset alone so the layout is not empty
    st.markdown("<div class='section-header'>תצוגה מוקדמת של הקובץ הראשי</div>", unsafe_allow_html=True)
    st.dataframe(main_df.head(25), use_container_width=True)
    st.stop()


# -----------------------------------------------------------------------------
#  Toolbar — filters + metric picker
# -----------------------------------------------------------------------------
def _shared_options(col: str) -> list:
    values: set = set()
    for d in [main_df, comp_df]:
        if d is not None and col in d.columns:
            values.update(v for v in d[col].dropna().unique().tolist() if str(v).lower() != "nan")
    return sorted(values, key=lambda x: str(x))


st.markdown("<div class='cmp-toolbar'>", unsafe_allow_html=True)
tc1, tc2, tc3, tc4, tc5 = st.columns([1.6, 1.1, 1.1, 1.1, 1.1])

METRICS = {
    "שיעור בקשות הישפטות":  ("rate", "requested_trial", "%"),
    "שילמו את הקנס (מי שלא ביקש להישפט)": ("paid", None, "%"),
    "שביעות רצון מהתהליך (ממוצע 1-5)": ("mean", "process_satisfaction_num", ""),
    "הבנת העבירה (ממוצע 1-5)": ("mean", "understand_offense_num", ""),
    "עידוד לזהירות בעתיד (ממוצע 1-5)": ("mean", "future_caution_num", ""),
    "הדוח היה מוצדק (ממוצע 1-5)": ("mean", "report_justified_num", ""),
}

with tc1:
    metric_label = st.selectbox("📐 מדד להשוואה", options=list(METRICS.keys()), index=0)
metric_kind, metric_col, x_suffix = METRICS[metric_label]

with tc2:
    year_opts = _shared_options("report_year_bin")
    sel_years = st.multiselect("שנת דוח", options=year_opts, default=year_opts, key="cmp_year")
with tc3:
    gender_opts = _shared_options("gender")
    sel_gender = st.multiselect("מגדר", options=gender_opts, default=gender_opts, key="cmp_gender")
with tc4:
    migzar_opts = _shared_options("migzar")
    sel_migzar = st.multiselect("מגזר", options=migzar_opts, default=migzar_opts, key="cmp_migzar")
with tc5:
    age_opts = _shared_options("age_band")
    sel_age = st.multiselect("גיל", options=age_opts, default=age_opts, key="cmp_age")

st.markdown("</div>", unsafe_allow_html=True)


def _apply_filters(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    if sel_years and "report_year_bin" in out.columns:
        out = out[out["report_year_bin"].isin(sel_years)]
    if sel_gender and "gender" in out.columns:
        out = out[out["gender"].isin(sel_gender)]
    if sel_migzar and "migzar" in out.columns:
        out = out[out["migzar"].isin(sel_migzar)]
    if sel_age and "age_band" in out.columns:
        out = out[out["age_band"].isin(sel_age)]
    return out


f_main = _apply_filters(main_df)
f_comp = _apply_filters(comp_df)


# -----------------------------------------------------------------------------
#  Metric helpers
# -----------------------------------------------------------------------------
def _metric_by_group(df: pd.DataFrame, group_col: str) -> pd.Series:
    if df is None or df.empty or group_col not in df.columns:
        return pd.Series(dtype=float)
    if metric_kind == "rate":
        return _rate_by_group(df, group_col, df[metric_col].astype(float))
    if metric_kind == "paid":
        no_trial = df[~df["requested_trial"].fillna(False)]
        return _percent_by_group(no_trial, group_col, "paid_fine_actual", "כן")
    if metric_kind == "mean":
        return _mean_by_group(df, group_col, metric_col)
    return pd.Series(dtype=float)


def _metric_total(df: pd.DataFrame) -> float:
    if df is None or df.empty:
        return float("nan")
    if metric_kind == "rate":
        return float(df[metric_col].astype(float).mean() * 100) if metric_col in df.columns else float("nan")
    if metric_kind == "paid":
        no_trial = df[~df["requested_trial"].fillna(False)]
        if not len(no_trial):
            return float("nan")
        return float(no_trial["paid_fine_actual"].eq("כן").mean() * 100)
    if metric_kind == "mean":
        if metric_col not in df.columns:
            return float("nan")
        s = df[metric_col].dropna()
        return float(s.mean()) if len(s) else float("nan")
    return float("nan")


# -----------------------------------------------------------------------------
#  KPI row
# -----------------------------------------------------------------------------
k1, k2, k3 = st.columns(3)
kpi_suffix = x_suffix or "/5"

with k1:
    st.markdown(
        comparison_kpi_card(
            "כלל המדגם (לאחר סינון)",
            float(len(f_main)),
            float(len(f_comp)),
            main_label=lbl_main, comp_label=lbl_comp,
            suffix="",
            accent=PALETTE["primary"],
        ).replace(".0", ""),
        unsafe_allow_html=True,
    )
with k2:
    st.markdown(
        comparison_kpi_card(
            metric_label,
            _metric_total(f_main),
            _metric_total(f_comp),
            main_label=lbl_main, comp_label=lbl_comp,
            suffix=kpi_suffix,
            accent=PALETTE["secondary"],
        ),
        unsafe_allow_html=True,
    )
with k3:
    # secondary KPI: satisfaction if the selected metric isn't already satisfaction
    if metric_col == "process_satisfaction_num":
        sec_col = "future_caution_num"
        sec_label = "עידוד לזהירות (ממוצע)"
    else:
        sec_col = "process_satisfaction_num"
        sec_label = "שביעות רצון מהתהליך (ממוצע)"
    m_val = float(f_main[sec_col].dropna().mean()) if sec_col in f_main.columns and f_main[sec_col].notna().any() else float("nan")
    c_val = float(f_comp[sec_col].dropna().mean()) if sec_col in f_comp.columns and f_comp[sec_col].notna().any() else float("nan")
    st.markdown(
        comparison_kpi_card(
            sec_label, m_val, c_val,
            main_label=lbl_main, comp_label=lbl_comp,
            suffix="/5",
            accent=PALETTE["accent"],
        ),
        unsafe_allow_html=True,
    )


# -----------------------------------------------------------------------------
#  Main grid — text panel | map | comparison bar chart
# -----------------------------------------------------------------------------
st.markdown(
    "<div class='section-header'>השוואה גיאוגרפית — לפי מחוז</div>",
    unsafe_allow_html=True,
)

g1, g2, g3 = st.columns([1, 1.4, 1.6])

with g1:
    st.markdown(
        f"""
        <div class='cmp-panel'>
          <h4>אודות ההשוואה</h4>
          <p>הגרף שמימין משווה את המדד <b>{metric_label}</b> בין
             <span style='color:{COMPARISON_COLORS["main"]};font-weight:800'>{lbl_main}</span>
             ל-<span style='color:#8a5a00;font-weight:800'>{lbl_comp}</span> — עבור כל מחוז בנפרד.
          </p>
          <p>המפה מציגה את אותם ערכים בפריסה גיאוגרפית: גודל הבועה = ערך ב-{lbl_main},
             וצבע הבועה מבטא את הכיוון של השינוי (ירוק = עלייה, אדום = ירידה).</p>
          <p><b>שים לב:</b> ההשוואה מכבדת את המסננים בראש העמוד — שנת דוח, מגדר, מגזר וגיל.</p>
          <ul class='cmp-panel__list'>
            <li>▲ ירוק = המדד עלה בין השנים</li>
            <li>▼ אדום = המדד ירד בין השנים</li>
            <li>▬ אפור = כמעט אין הבדל</li>
          </ul>
        </div>
        """,
        unsafe_allow_html=True,
    )

with g2:
    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
    st.plotly_chart(
        israel_district_map(
            f_main, f_comp,
            metric_fn=lambda d: _metric_by_group(d, "mahoz_short"),
            main_label=lbl_main, comp_label=lbl_comp,
            x_suffix=x_suffix or "",
            height=500,
        ),
        use_container_width=True,
    )

with g3:
    st.plotly_chart(
        year_comparison_bar(
            f_main, f_comp,
            group_col="mahoz_short",
            metric_fn=lambda d: _metric_by_group(d, "mahoz_short"),
            main_label=lbl_main, comp_label=lbl_comp,
            title=f"{metric_label} — לפי מחוז",
            x_suffix=x_suffix or "",
            height=500,
        ),
        use_container_width=True,
    )


# -----------------------------------------------------------------------------
#  Secondary comparisons — sector, gender, age
# -----------------------------------------------------------------------------
st.markdown(
    "<div class='section-header'>השוואה לפי פילוחים דמוגרפיים</div>",
    unsafe_allow_html=True,
)

d1, d2 = st.columns(2)
with d1:
    st.plotly_chart(
        year_comparison_bar(
            f_main, f_comp,
            group_col="migzar",
            metric_fn=lambda d: _metric_by_group(d, "migzar"),
            main_label=lbl_main, comp_label=lbl_comp,
            title=f"{metric_label} — לפי מגזר",
            x_suffix=x_suffix or "",
            height=380,
        ),
        use_container_width=True,
    )
with d2:
    st.plotly_chart(
        year_comparison_bar(
            f_main, f_comp,
            group_col="gender",
            metric_fn=lambda d: _metric_by_group(d, "gender"),
            main_label=lbl_main, comp_label=lbl_comp,
            title=f"{metric_label} — לפי מגדר",
            x_suffix=x_suffix or "",
            height=380,
        ),
        use_container_width=True,
    )

st.plotly_chart(
    year_comparison_bar(
        f_main, f_comp,
        group_col="age_band",
        metric_fn=lambda d: _metric_by_group(d, "age_band"),
        main_label=lbl_main, comp_label=lbl_comp,
        title=f"{metric_label} — לפי קבוצת גיל",
        x_suffix=x_suffix or "",
        height=460,
    ),
    use_container_width=True,
)

st.info(
    "💡 טיפ: החלף את המדד בראש העמוד כדי לראות את אותה השוואה עבור מדד אחר. "
    "ניתן להסיר את קובץ ההשוואה בסרגל הצדדי של דף הבית."
)
