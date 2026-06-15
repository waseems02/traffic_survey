"""Page 3 — ההליך המשפטי (PPT slides 25-31) — only trial-seekers subset."""
from __future__ import annotations

import os

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from utils.charts import (
    PALETTE,
    _text_on,
    LIKERT_3BAND_COLORS,
    LIKERT_3BAND_ORDER,
    BALANCE_COLORS,
    HEARING_STATUS_COLORS,
    donut,
    empty_state,
    kpi_card_html,
    likert_summary_strip,
    stacked_pct_bar,
)
from utils.data_loader import likert_to_3band
from utils.filters import init_global_filters, require_data
from utils.insights import render_insight


st.set_page_config(layout="wide", page_title="ההליך המשפטי")


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
      <h1>⚖️ ההליך המשפטי</h1>
      <p>נתוני מבקשי ההישפטות — בהירות התהליך, סטטוס הדיון, ראיות ופסק דין.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

req = df[df["requested_trial"].fillna(False)].copy()

# KPI row
trial_count = len(req)
if trial_count:
    hearing_pct = req["hearing_held_bin"].eq("היה דיון בפועל").mean() * 100 if "hearing_held_bin" in req.columns else 0.0
    evidence_pct = req["evidence_requested"].eq("כן").mean() * 100 if "evidence_requested" in req.columns else 0.0
    sat_series = req["process_satisfaction_num"].dropna() if "process_satisfaction_num" in req.columns else []
    sat_avg = float(sat_series.mean()) if len(sat_series) else None
    sat_std = float(sat_series.std()) if len(sat_series) > 1 else 0.0
else:
    hearing_pct = 0.0
    evidence_pct = 0.0
    sat_avg = None
    sat_std = 0.0

k1, k2, k3, k4 = st.columns(4)
with k1:
    st.markdown(
        kpi_card_html("סך המבקשים להישפט", f"{trial_count:,}", PALETTE["primary"],
                      sub="מתוך המסוננים"),
        unsafe_allow_html=True,
    )
with k2:
    st.markdown(
        kpi_card_html("דיון בפועל בקרב מבקשי הישפטות", f"{hearing_pct:.1f}%", PALETTE["secondary"],
                      sub="מבין מבקשי ההישפטות"),
        unsafe_allow_html=True,
    )
with k3:
    st.markdown(
        kpi_card_html("ביקשו ראיות נוספות", f"{evidence_pct:.1f}%", PALETTE["accent"],
                      sub="מבין מבקשי ההישפטות"),
        unsafe_allow_html=True,
    )
with k4:
    sat_str = f"{sat_avg:.2f} / 5" if sat_avg is not None else "-"
    sat_std_str = f"{sat_std:.2f}" if sat_avg is not None else ""
    st.markdown(
        kpi_card_html("שביעות רצון מהתהליך", sat_str, PALETTE["warn"],
                      sub="ציון ממוצע בקרב מבקשי ההישפטות בלבד", std_dev=sat_std_str),
        unsafe_allow_html=True,
    )


st.markdown(
    """
    <div class='insight-box'>
      <h4>📖 על מה העמוד הזה</h4>
      <p>החלק הזה בדוח עוסק רק במבקשי ההישפטות — הקבוצה הקטנה יחסית שבחרה להתעמת עם המערכת במקום לשלם. כאן מתבררות שאלות הליבה של הרפורמה: עד כמה תהליך הגשת הבקשה ברור, האם הנגישות לראיות מאפשרת ניהול עניין הוגן, האם הדיון אכן מתקיים בכלל, מה תחושת הנשפט מול השופט והתביעה, והאם פסק הדין מובן והוגן בעיניו. הפערים בין מגזרים — כולל בייצוג ע"י עו"ד ובשיעור הדיונים שאכן התקיימו — בולטים במיוחד בחלק זה.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# =========================================================
# 1. בהירות התהליך + מעקב סטטוס
# =========================================================
st.markdown("<div class='section-header'>1. בהירות התהליך ומעקב סטטוס</div>", unsafe_allow_html=True)

c1, c2 = st.columns([1, 1])
with c1:
    work = req.copy()
    work["likert_band"] = likert_to_3band(work["trial_clarity"])
    work["group"] = work["migzar"].fillna("לא ידוע")
    fig = stacked_pct_bar(
        work.dropna(subset=["likert_band", "group"]),
        group_col="group", value_col="likert_band",
        category_order=LIKERT_3BAND_ORDER, color_map=LIKERT_3BAND_COLORS,
        show_mean=True, mean_col="trial_clarity_num",
        title="בהירות תהליך הגשת הבקשה — לפי מגזר",
    )
    fig.update_layout(height=520, margin=dict(l=10, r=10, t=60, b=80))
    st.plotly_chart(fig, use_container_width=True)

with c2:
        fig_donut = donut(
            req,
            "tracked_status",
            title="האם ידעו לעקוב אחר הסטטוס?",
            color_map={
                "כן, בצורה ברורה": PALETTE["accent"],
                "כן, אבל באופן חלקי בלבד/ לא מאוד ברור כיצד לעקוב": PALETTE["warn"],
                "לא ידעתי איך לעקוב": PALETTE["danger"],
            },
        )
        # Give the circle as much room as possible: tight margins, no legend
        # (labels already appear on each slice via textinfo="label+percent").
        fig_donut.update_traces(domain=dict(x=[0, 1], y=[0, 1]))
        fig_donut.update_layout(
            margin=dict(l=10, r=10, t=40, b=10),
            showlegend=False,
            height=500,
        )
        st.plotly_chart(fig_donut, use_container_width=True)
    

render_insight("trial_clarity", df)


# =========================================================
# 2. בקשת וקבלת ראיות
# =========================================================
st.markdown("<div class='section-header'>2. בקשת וקבלת ראיות</div>", unsafe_allow_html=True)

c1, c2, c3 = st.columns(3)
with c1:
    # 1. Capture the donut chart
    fig1 = donut(req, "evidence_requested", title="האם ביקשו ראיות נוספות?")
    
    # 2. Maximize size and push legend down
    fig1.update_layout(
        height=480,
        margin=dict(l=10, r=10, t=60, b=80),
        legend=dict(
            orientation="h",
            yanchor="top",
            y=-0.15,
            xanchor="center",
            x=0.5
        )
    )
    st.plotly_chart(fig1, use_container_width=True)

with c2:
    asked = req[req["evidence_requested"] == "כן"]
    
    # 1. Capture the conditional donut chart
    fig2 = donut(
        asked,
        "evidence_received",
        title="האם קיבלו את הראיות? (מתוך מי שביקשו)",
        color_map={
            "כן, באופן מלא": PALETTE["accent"],
            "כן, באופן חלקי": PALETTE["warn"],
            "לא קיבלתי כלל": PALETTE["danger"],
        },
    )
    
    # 2. Maximize size and push legend down to match c1
    fig2.update_layout(
        height=480,
        margin=dict(l=10, r=10, t=60, b=80),
        legend=dict(
            orientation="h",
            yanchor="top",
            y=-0.15,
            xanchor="center",
            x=0.5
        )
    )
    st.plotly_chart(fig2, use_container_width=True)

with c3:
    if "evidence_difficulty" in req.columns:
        work = req.copy()
        work["likert_band"] = likert_to_3band(work["evidence_difficulty"])
        counts = work["likert_band"].dropna().value_counts()
        if len(counts):
            counts = counts.reindex([c for c in LIKERT_3BAND_ORDER if c in counts.index])
            fill_per_bar = [LIKERT_3BAND_COLORS[c] for c in counts.index]
            fig = go.Figure(go.Bar(
                x=counts.index, y=counts.values,
                marker_color=fill_per_bar,
                text=counts.values, textposition="inside",
                constraintext="inside", cliponaxis=False,
                insidetextanchor="middle",
                textfont=dict(color=[_text_on(c) for c in fill_per_bar]),
            ))
            
            # Optimized the bar chart layout to visually match columns 1 and 2
            fig.update_layout(
                template="plotly_white",
                paper_bgcolor="white", plot_bgcolor="white",
                font=dict(color="black"),
                margin=dict(l=30, r=30, t=60, b=80), # Tightened left margin from 135 to 30
                autosize=False,
                title="קושי בקבלת הראיות",title_font=dict(color="black"),
                height=480,                          # Matched height perfectly to the donuts
            )
            fig.update_yaxes(title="כמות משיבים", automargin=True,tickfont=dict(color='black'),title_font=dict(color='black')) # Added y-axis title and optimized margins
            fig.update_xaxes(automargin=True, tickangle=0,tickfont=dict(color='black')) # Forced flat horizontal labels
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.plotly_chart(empty_state(), use_container_width=True)
    else:
        st.plotly_chart(empty_state(), use_container_width=True)

render_insight("evidence", df)


st.markdown("<div class='section-header'>3. האם התקיים דיון בפועל</div>", unsafe_allow_html=True)

_hearing = df.dropna(subset=["migzar"]).copy()
_hearing["hearing_held"] = _hearing["hearing_held"].fillna("אין מענה")

st.plotly_chart(
    stacked_pct_bar(
        _hearing,
        group_col="migzar",
        value_col="hearing_held",
        category_order=[
            "כן, בנוכחותי",
            "כן, אבל לא בנוכחותי (עו\"ד ייצג אותי)",
            "כן, אבל לא התייצבתי (לא ידעתי על תאריך הדיון או בחרתי לא להתייצב)",
            "טרם נקבע דיון",
            "לא נקבע דיון וההליך התבטל",
            "אין מענה",
        ],
        color_map=HEARING_STATUS_COLORS,
        title="האם התקיים דיון בפועל לפי מגזר",
    ),
    use_container_width=True,
)

# =========================================================
# 4. ייצוג ע"י עורך דין בדיון (only those who attended a hearing)
# =========================================================
st.markdown("<div class='section-header'>4. ייצוג ע\"י עורך דין בדיון</div>", unsafe_allow_html=True)

attended = req[req["hearing_held"].isin([
    "כן, בנוכחותי",
    "כן, אבל לא בנוכחותי (עו\"ד ייצג אותי)",
])]
if len(attended):
    work = attended.copy()
    work["repped"] = work["lawyer_repped"].apply(
        lambda x: "כן — עו\"ד ייצג" if isinstance(x, str) and x.startswith("כן")
        else ("לא — ייצגתי את עצמי" if isinstance(x, str) and x.startswith("לא") else None)
    )
    work = work.dropna(subset=["repped"])
    if len(work):
        st.plotly_chart(
            stacked_pct_bar(
                work, group_col="migzar", value_col="repped",
                color_map={
                    "כן — עו\"ד ייצג": PALETTE["secondary"],
                    "לא — ייצגתי את עצמי": PALETTE["muted"],
                },
                title="ייצוג ע\"י עו\"ד — לפי מגזר",
            ),
            use_container_width=True,
        )
    else:
        st.info("אין נתוני ייצוג עורך דין בסינון הנוכחי.")
else:
    st.info("אין נתוני דיון בפועל בסינון הנוכחי.")

render_insight("lawyer_repped", df)


st.markdown("<div class='section-header'>5. יחס השופט ואיזון</div>", unsafe_allow_html=True)

_strip_fig = likert_summary_strip(
    df,
    columns=[
        ("judge_fair_num", "יחס השופט (הוגן ומכבד)"),
        ("judge_voice_num", "הזדמנות להשמיע גרסה"),
    ],
    height=300,
)
_strip_fig.update_layout(
    title=dict(
        text="יחס השופט והזדמנות להשמיע גרסה — ציון ממוצע (1-5)",
        font=dict(color="black", size=18),
        x=0.5,
        xanchor="right",
        y=0.95,
        yanchor="top",
    ),
    margin=dict(l=135, r=40, t=80, b=40),
)
st.plotly_chart(_strip_fig, use_container_width=True)

c1, c2 = st.columns(2)
with c1:
    work = df.copy()
    work["likert_band"] = likert_to_3band(work["judge_fair"])
    st.plotly_chart(
        stacked_pct_bar(
            work.dropna(subset=["likert_band", "migzar"]),
            group_col="migzar",
            value_col="likert_band",
            category_order=LIKERT_3BAND_ORDER,
            color_map=LIKERT_3BAND_COLORS,
            #show_mean=True,
            mean_col="judge_fair_num",
            title="יחס השופט — לפי מגזר",
        ),
        use_container_width=True,
    )

with c2:
    balance_order = ["כלל לא", "באופן חלקי", "באופן מלא"]
    st.plotly_chart(
        stacked_pct_bar(
            df.dropna(subset=["balance_perception", "migzar"]),
            group_col="migzar",
            value_col="balance_perception",
            category_order=balance_order,
            color_map=BALANCE_COLORS,
            title="איזון מול התביעה/המשטרה — לפי מגזר",
        ),
        use_container_width=True,
    )


st.markdown("<div class='section-header'>6. הבנה והוגנות פסק הדין</div>", unsafe_allow_html=True)

c1, c2 = st.columns(2)
for col, label, container in [
    ("verdict_understood", "מובנות פסק הדין", c1),
    ("verdict_fair", "הוגנות פסק הדין", c2),
]:
    with container:
        work = df.copy()
        work["likert_band"] = likert_to_3band(work[col])
        st.plotly_chart(
            stacked_pct_bar(
                work.dropna(subset=["likert_band", "migzar"]),
                group_col="migzar",
                value_col="likert_band",
                category_order=LIKERT_3BAND_ORDER,
                color_map=LIKERT_3BAND_COLORS,
                show_mean=True,
                mean_col=f"{col}_num",
                title=label,
            ),
            use_container_width=True,
        )

render_insight("judge_perception", df)


st.markdown("<div class='section-header'>7. מה היו משנים בתהליך</div>", unsafe_allow_html=True)

change_col = None
for c in df.columns:
    if "הליך המשפטי" in str(c) and "לשנות" in str(c):
        change_col = c
        break

if change_col:
    free = df[change_col].dropna().astype(str)
    free = free[free.str.len() > 1]
    no_answer_count = int(len(df) - len(free))
    if len(free):
        st.markdown(f"**{len(free)} תגובות חופשיות נאספו.** ענן המילים והנושאים המרכזיים מבוססים על תשובות חופשיות של המשיבים.")
        themes_keywords = {
            "הוגנות / יחס": ["הוגנ", "יחס", "מכבד", "כבוד"],
            "מהירות / זמני המתנה": ["זמן", "מהיר", "המתנ", "תור", "ארוך"],
            "ראיות / מידע": ["ראי", "מידע", "הסבר"],
            "ייצוג / עו\"ד": ["עו\"ד", "עורך דין", "ייצוג"],
            "בירוקרטיה / פישוט": ["מסובך", "בירוקר", "תהליך", "פישוט"],
            "השופט": ["שופט"],
            "המשטרה / השוטר": ["שוטר", "משטר", "תביעה"],
            "ערעור": ["ערעור"],
            "אחר": [],
        }
        theme_counts = {t: 0 for t in themes_keywords}
        for resp in free:
            matched = False
            for theme, keys in themes_keywords.items():
                if theme == "אחר":
                    continue
                if any(k in resp for k in keys):
                    theme_counts[theme] += 1
                    matched = True
            if not matched:
                theme_counts["אחר"] += 1
        s = pd.Series(theme_counts).sort_values(ascending=True)
        fig = go.Figure(go.Bar(
            x=s.values, y=s.index, orientation="h",
            marker_color=PALETTE["secondary"],
            text=s.values, textposition="inside",
            constraintext="inside", cliponaxis=False,
            insidetextanchor="middle", textfont=dict(color=[_text_on(PALETTE["secondary"])] * len(s)),
        ))
        fig.update_layout(
            template="plotly_white",
            paper_bgcolor="white", plot_bgcolor="white",
            font=dict(color="black"),
            margin=dict(l=135, r=40, t=90, b=80),
            autosize=False,
            title=dict(
                text=f"נושאים מרכזיים בהמלצות לשינוי (n={len(free)})",
                font=dict(color="black")
            ),
            height=420,
            xaxis=dict(
                tickfont=dict(color="black"),
                title_font=dict(color="black"),
                automargin=True,
        ),
            yaxis=dict(
                tickfont=dict(color="black"),
                title_font=dict(color="black"),
                automargin=True,
        ),
            legend=dict(
                font=dict(color="black")
        ),
            )
        st.plotly_chart(fig, use_container_width=True)
        st.markdown(
            f"<p style='color:black;'>📝 <b>{no_answer_count} אנשים לא ענו</b> — לכן הסטטיסטיקה אינה מבוססת על 100% מהמשיבים.</p>",
            unsafe_allow_html=True)

render_insight("what_to_change", df)


st.markdown(
    """
    <div class='insight-box'>
      <h4>🧭 סיכום העמוד</h4>
      <p>ההליך המשפטי הוא הצוואר הצר של החוויה. בהירות התהליך חלקית בלבד, מעקב הסטטוס לא תמיד נגיש, הראיות מתקבלות בקושי, ורק כמחצית מהמבקשים אכן מגיעים לדיון בפועל. תחושת האיזון מול התביעה חלשה — רק 20% מהמשיבים חשו שהיה איזון אמיתי בינם לבין התביעה/משטרה, במיוחד במגזר היהודי. ההמלצה הברורה: הרפורמה הדיגיטלית צריכה להבטיח דף סטטוס בזמן-אמת, נגישות מלאה לראיות, וחיזוק תחושת ההוגנות והאיזון — לא רק בהירות תהליכית. בנוסף, שיעור גבוה של נשפטים בלי ייצוג משפטי מחייב שעיצוב המערכת הדיגיטלית יניח מראש שהאזרח מייצג את עצמו.</p>
    </div>
    """,
    unsafe_allow_html=True,
)
