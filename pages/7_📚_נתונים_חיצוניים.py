"""Page 7 — נתונים חיצוניים.

External datasets that complement the survey: MoJ case-outcome data (File 1),
police reports filed to courts (File 2), and 6 years of trial-request records
(Files 3 + 4). Each section is title → description → chart.

To add another dataset: write a loader in utils/external_loaders.py that
returns a clean long-form DataFrame, then append a dict to SECTIONS below.
"""
from __future__ import annotations

import os

import plotly.express as px
import streamlit as st

from utils.charts import PALETTE, _base_layout, empty_state
from utils.external_loaders import (
    load_closure_reasons,
    load_conviction_acquittal_rates,
    load_process_outcomes,
    load_reports_by_fine,
    load_reports_by_year,
    load_reports_entered_by_year,
    load_top_courts,
    load_top_offenses,
    load_trial_request_rate_by_fine,
    load_trial_requests_by_religion_gender,
    load_trial_requests_by_year,
)


# =============================================================================
#  Section definitions
# =============================================================================
PALETTE_SEQ = [
    PALETTE["primary"], PALETTE["secondary"], PALETTE["accent"],
    PALETTE["danger"], PALETTE["muted"], PALETTE["warn"],
]

SECTIONS: list[dict] = [
    # ---- משרד המשפטים ----
    {
        "category": "משרד המשפטים",
        "title": "סיבות סגירת תיקי תעבורה (תת\"ע) לפי שנה",
        "description": (
            "התפלגות סיבות סגירת תיקי תעבורה בבתי המשפט על פי נתוני מה\"ב. "
            "רוב התיקים נסגרים בפסק דין או בהסדר טיעון. "
            "נתוני 2025 חלקיים ולכן נמוכים מהותית משנים קודמות."
        ),
        "loader": load_closure_reasons,
        "chart": {
            "type": "bar", "x": "reason", "y": "count", "color": "year",
            "barmode": "group", "sort_y_desc": True,
            "wrap_x_labels": True, "wrap_len": 14,
            "log_y": True, "height": 720,
        },
    },
    {
        "category": "משרד המשפטים",
        "title": "תוצאות הליך תיקי תעבורה לפי שנה",
        "description": (
            "פילוח תוצאות ההליך המשפטי בתיקי תעבורה — הרשעה/אשמה ללא הרשעה, זיכוי/מחיקה, "
            "צירוף תיקים והפסקת הליכים. הרשעה היא התוצאה השכיחה בהרבה."
        ),
        "loader": load_process_outcomes,
        "chart": {"type": "bar", "x": "year", "y": "count", "color": "category", "barmode": "stack"},
    },
    {
        "category": "משרד המשפטים",
        "title": "אחוז הרשעות וזיכויים לפי שנה",
        "description": (
            "שיעורי הרשעה וזיכוי בתיקי תעבורה שהסתיימו בפסק דין. "
            "שיעור ההרשעות יציב סביב 93-95% בשנים 2022-2024."
        ),
        "loader": load_conviction_acquittal_rates,
        "chart": {"type": "line", "x": "year", "y": "pct", "color": "metric", "y_suffix": "%"},
    },
    # ---- משטרה ----
    {
        "category": "משטרה",
        "title": "סך דוחות משטרה שהוגשו לבתי משפט לפי שנה",
        "description": (
            "מספר ברירות המשפט שהוגשו לבתי המשפט על ידי משטרת ישראל. "
            "ניתן לראות ירידה משמעותית מ-845 אלף ב-2022 ל-683 אלף ב-2023, "
            "עם עלייה חלקית ב-2024."
        ),
        "loader": load_reports_by_year,
        "chart": {"type": "bar", "x": "year", "y": "total"},
    },
    {
        "category": "משטרה",
        "title": "15 סוגי העבירות הנפוצות ביותר בדוחות המשטרה",
        "description": (
            "העבירות שנתנו עליהן הכי הרבה דוחות בשנים 2022-2024. "
            "שימוש בטלפון נייד ללא דיבורית מוביל בפער גדול, "
            "ואחריו עבירות מהירות בדרכים לא עירוניות."
        ),
        "loader": load_top_offenses,
        "chart": {
            "type": "horizontal_bar", "x": "סמל עבירה", "y": "total",
            "wrap_y_labels": True, "wrap_len": 22, "height": 820,
            "tick_font_size": 11, "left_margin": 260,
        },
    },
    {
        "category": "משטרה",
        "title": "התפלגות דוחות המשטרה לפי גובה הקנס",
        "description": (
            "כמה דוחות ניתנו לפי כל תעריף קנס (2022-2024). "
            "רוב הדוחות הם על 250 ₪, ואחריהם 500, 1000, ו-750 ₪. "
            "קנסות של 1,500 ₪ ניתנים על עבירות חמורות יותר ולכן פחות שכיחים."
        ),
        "loader": load_reports_by_fine,
        "chart": {"type": "bar", "x": "קנס", "y": "total", "text_inside": True},
    },
    {
        "category": "משטרה",
        "title": "דוחות שנכנסו לבית משפט לעומת דוחות שלא נכנסו לפי שנה",
        "description": (
            "מבין הדוחות שהמשטרה נתנה — כמה מהם בפועל הגיעו לבית המשפט "
            "(בעקבות בקשת הישפטות או אי-תשלום) לעומת אלה שנסגרו בתשלום ולא נכנסו. "
            "בכל השנים כ-60% מהדוחות נכנסו לבית משפט."
        ),
        "loader": load_reports_entered_by_year,
        "chart": {"type": "bar", "x": "year", "y": "total", "color": "נכנס", "barmode": "group"},
    },
    # ---- בתי משפט ----
    {
        "category": "בתי משפט",
        "title": "15 בתי המשפט המובילים לפי נפח דוחות תעבורה",
        "description": (
            "בתי המשפט שאליהם הוגשו מרבית ברירות המשפט בשנים 2022-2024. "
            "בית משפט לתעבורה מרכז-פ\"ת מוביל בהפרש ניכר עם למעלה מ-450 אלף דוחות."
        ),
        "loader": load_top_courts,
        "chart": {"type": "horizontal_bar", "x": "בית משפט", "y": "total"},
    },
    {
        "category": "בתי משפט",
        "title": "בקשות להישפט לפי שנה — מגמה 2019-2024",
        "description": (
            "סך בקשות להישפט שהוגשו על ברירות משפט בשש השנים האחרונות "
            "(שילוב של שני מקורות נתונים: 2019-2021 ו-2022-2024). "
            "בולטת קפיצה חדה בשנים 2021 ו-2024 עם למעלה מ-100,000 בקשות בכל אחת מהן."
        ),
        "loader": load_trial_requests_by_year,
        "chart": {"type": "line", "x": "year", "y": "total"},
    },
    {
        "category": "בתי משפט",
        "title": "בקשות להישפט לפי דת ומגדר",
        "description": (
            "פילוח סך הבקשות להישפט (2019-2024) לפי דת המבקש ומגדרו. "
            "ניתן לראות פערים משמעותיים בין גברים לנשים בכל קבוצות הדת."
        ),
        "loader": load_trial_requests_by_religion_gender,
        "chart": {"type": "bar", "x": "דת אזרח", "y": "total", "color": "מין אזרח", "barmode": "group"},
    },
    {
        "category": "בתי משפט",
        "title": "שיעור בקשות להישפט לפי גובה הקנס",
        "description": (
            "אחוז מברירות המשפט שהפכו לבקשות להישפט, מפולח לפי גובה הקנס (2022-2024). "
            "ברור שככל שהקנס גבוה יותר — כך שיעור מבקשי ההישפטות גבוה יותר, "
            "מ-0.7% על קנסות של 100 ₪ ועד 16.7% על קנסות של 1,500 ₪."
        ),
        "loader": load_trial_request_rate_by_fine,
        "chart": {"type": "bar", "x": "קנס", "y": "אחוז בקשות להישפט", "y_suffix": "%"},
    },
]

CATEGORY_ORDER = ["משרד המשפטים", "משטרה", "בתי משפט"]

# Categories that get a visible section header on the page. The first category
# (משרד המשפטים) is skipped so it flows directly under the page hero.
CATEGORY_HEADERS = {"משטרה", "בתי משפט"}

# Display text for each category header.
CATEGORY_LABELS = {
    "משטרה":    "לפי נתוני המשטרה",
    "בתי משפט": "לפי נתוני בתי המשפט",
}


# =============================================================================
#  Page setup
# =============================================================================
st.set_page_config(layout="wide", page_title="נתונים חיצוניים", page_icon="📚")


def _inject_css() -> None:
    path = os.path.join(os.path.dirname(__file__), "..", "assets", "styles.css")
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


_inject_css()


# =============================================================================
#  Chart builder
# =============================================================================
def _wrap_label(label: str, max_len: int = 12) -> str:
    """Break a long Hebrew label into multiple lines using <br>, splitting on spaces."""
    words = str(label).split()
    if not words:
        return str(label)
    lines, current = [], ""
    for word in words:
        candidate = f"{current} {word}".strip()
        if len(candidate) > max_len and current:
            lines.append(current)
            current = word
        else:
            current = candidate
    if current:
        lines.append(current)
    return "<br>".join(lines)


def _build_chart(df, spec: dict, title: str):
    if df is None or df.empty:
        return empty_state("אין נתונים זמינים")

    chart_type = spec.get("type", "bar")
    x = spec.get("x")
    y = spec.get("y")
    color = spec.get("color")
    barmode = spec.get("barmode", "group")
    y_suffix = spec.get("y_suffix", "")

    if chart_type == "bar":
        work = df.sort_values(y, ascending=False) if spec.get("sort_y_desc") else df
        if spec.get("wrap_x_labels"):
            work = work.copy()
            work[x] = work[x].map(lambda v: _wrap_label(v, spec.get("wrap_len", 12)))
        fig = px.bar(
            work, x=x, y=y, color=color, barmode=barmode,
            color_discrete_sequence=PALETTE_SEQ,
            text_auto=".2s" if work[y].max() >= 1000 else True,
        )
        # On log scale small bars can't fit their label inside — force outside.
        text_pos = "outside" if spec.get("log_y") else ("inside" if spec.get("text_inside") else "outside")
        fig.update_traces(
            textposition=text_pos,
            insidetextanchor="middle",
            cliponaxis=False,
            constraintext="inside",
        )
        if spec.get("log_y"):
            fig.update_yaxes(type="log")
        if y_suffix:
            fig.update_yaxes(ticksuffix=y_suffix)

    elif chart_type == "horizontal_bar":
        # x = category col, y = value col — orient horizontally
        work = df.sort_values(y, ascending=True)
        if spec.get("wrap_y_labels"):
            work = work.copy()
            work[x] = work[x].map(lambda v: _wrap_label(v, spec.get("wrap_len", 20)))
        fig = px.bar(
            work, x=y, y=x, orientation="h",
            color_discrete_sequence=[PALETTE["primary"]],
            text_auto=".2s" if work[y].max() >= 1000 else True,
        )
        fig.update_traces(textposition="outside", cliponaxis=False)
        fig.update_yaxes(title="", tickfont=dict(size=spec.get("tick_font_size", 14), color="black"))
        if spec.get("left_margin"):
            fig.update_layout(margin=dict(l=spec["left_margin"], r=40, t=90, b=80))
        if y_suffix:
            fig.update_xaxes(ticksuffix=y_suffix)

    elif chart_type == "line":
        fig = px.line(
            df, x=x, y=y, color=color, markers=True,
            color_discrete_sequence=PALETTE_SEQ,
        )
        fig.update_traces(line=dict(width=3), marker=dict(size=10))
        if y_suffix:
            fig.update_yaxes(ticksuffix=y_suffix)

    elif chart_type == "pie":
        fig = px.pie(
            df, names=x, values=y, hole=0.4,
            color_discrete_sequence=PALETTE_SEQ,
        )
        fig.update_traces(textinfo="label+percent", textfont_size=14)

    else:
        return empty_state(f"סוג גרף לא נתמך: {chart_type}")

    fig.update_layout(title=title)
    return _base_layout(fig, height=spec.get("height", 460))


# =============================================================================
#  Render
# =============================================================================
st.markdown(
    """
    <div class='page-header'>
      <h1>📚 נתונים חיצוניים</h1>
      <p>נתונים ממקורות חיצוניים (משרד המשפטים, משטרה, בתי משפט) המשלימים את ממצאי הסקר</p>
    </div>
    """,
    unsafe_allow_html=True,
)


def _sorted_categories(sections: list[dict]) -> list[str]:
    present = {s["category"] for s in sections}
    ordered = [c for c in CATEGORY_ORDER if c in present]
    extras = sorted(present - set(CATEGORY_ORDER))
    return ordered + extras


for category in _sorted_categories(SECTIONS):
    items = [s for s in SECTIONS if s["category"] == category]

    if category in CATEGORY_HEADERS:
        label = CATEGORY_LABELS.get(category, category)
        st.markdown(
            f"""
            <div class='cmp-hero' style='margin-top: 2rem;'>
              <div class='cmp-hero__title'>{label}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    for section in items:
        st.markdown(
            f"<div class='section-header'>{section['title']}</div>",
            unsafe_allow_html=True,
        )
        st.markdown(
            f"<div class='insight-box'><p>{section['description']}</p></div>",
            unsafe_allow_html=True,
        )
        try:
            df = section["loader"]()
        except Exception as exc:
            st.error(f"שגיאה בטעינת הנתונים: {exc}")
            continue
        fig = _build_chart(df, section["chart"], section["title"])
        st.plotly_chart(fig, use_container_width=True)
        st.markdown("<br>", unsafe_allow_html=True)
