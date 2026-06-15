"""Narrative insight boxes for each chart family, derived from the PPT.

Use `render_insight(key, df)` to render a styled blue box. When `df` is
supplied, dynamic computations appended in italics show the live numbers
from the current filtered sample.
"""
from __future__ import annotations

from typing import Callable, Optional

import pandas as pd
import streamlit as st


def _box(title: str, body: str, live: Optional[str] = None) -> None:
    live_html = f"<p class='live-stat'>📊 מהמדגם המסונן הנוכחי: {live}</p>" if live else ""
    st.markdown(
        f"""
        <div class='insight-box'>
          <h4>💡 {title}</h4>
          <p>{body}</p>
          {live_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


# Each key maps to (title, body, optional dynamic-stat callable)
INSIGHTS: dict[str, tuple[str, str, Optional[Callable[[pd.DataFrame], str]]]] = {
    "report_count": (
        "כמות הדוחות שקיבלו",
        "מרבית המשיבים קיבלו דו”ח יחיד בלבד. אצל אלו שביקשו להישפט מספר הדוחות הממוצע מעט גבוה יותר, ובשני הקהלים המגזר הערבי מציג ממוצע מעט גבוה יותר מהיהודי .",
        lambda df: f"{(df['report_count_bin']=='קיבלתי דו\"ח  אחד').mean()*100:.1f}% קיבלו דוח אחד בלבד",
    ),
    "report_year": (
        "מועד קבלת הדוח האחרון",
        "עיקר הדוחות האחרונים התקבלו בשנתיים האחרונות — הבסיס המחקרי נשען ברובו על חוויה יחסית טרייה.  ",
        lambda df: f"{(df['report_year_bin']=='דוח בשנים 24-25').mean()*100:.1f}% קיבלו דוח ב-2024-2025",
    ),
    "offense_type": (
        "סוגי העבירות הנפוצים",
        "סוגי הדוחות הנפוצים ביותר הם בגין מהירות ושימוש בטלפון, ואחריהם נסיעה בנתיב תחבורה ציבורית.",
        lambda df: f"מהירות: {df['offense_speeding'].mean()*100:.1f}% | טלפון: {df['offense_phone'].mean()*100:.1f}%",
    ),
    "report_source": (
        "ממי ואיך התקבל הדוח",
        "מרבית הדוחות התקבלו ממשטרת ישראל, במיוחד במגזר הערבי ובקרב מי שלא ביקשו להישפט. ניכרים גם הבדלים בערוצי המסירה בין המגזרים: יותר מסירה ישירה על־ידי שוטר במגזר הערבי ויותר מסירה בדואר במגזר היהודי. הממצאים מצביעים על הצורך באחידות במסרים ובחוויית השירות בין הגורמים האוכפים וערוצי המסירה.",
        lambda df: f"{(df['report_source']=='משטרת ישראל').mean()*100:.1f}% מהדוחות ממשטרת ישראל",
    ),
    "report_channel": (
        "אופן קבלת הדוח לפי תוצאה",
        "למרות בולטות הדוחות הפיזיים משוטר בשטח, ניכר מעבר לחלופות אחרות ובייחוד לדואר בדוחות מהשנתיים האחרונות. אופן הקבלה קשור גם לתוצאות בפועל — דוח משוטר בשטח מעורר יותר אנטגוניזם ופחות משלמים בפועל את הקנס.",
        None,
    ),
    "understanding": (
        "הבנת הדוח ותחושת הוגנות",
        "הבנה טובה של העבירה והעונש + הבנה סבירה של אפשרויות הפעולה. אבל — תחושת המוצדקות של הדוח ותחושת היכולת להשמיע קול חלשות בהרבה, יותר בקרב המבקשים להישפט ובמגזר היהודי. ",
        lambda df: (
            f"הבנת העבירה: {df['understand_offense_num'].mean():.2f}/5 | "
            f"הבנת אפשרויות: {df['understand_options_num'].mean():.2f}/5 | "
            f"מוצדקות: {df['report_justified_num'].mean():.2f}/5"
        ),
    ),
    "awareness": (
        "מודעות לחלופות",
        "חוסר ידע בולט לגבי החלופות הקיימות להתמודדות עם הדוחות — הרבה החלטות מתקבלות בלי מודעות מלאה. כשליש ממי שלא ביקש להישפט לא ידעו כלל על האפשרות להמרה/בקשה להישפט, ומעל למחצית ממי שביקשו להישפט לא ידעו שאפשר לבקש המרה לאזהרה. חשוב להבליט, לפשט ולהסביר באמצעות \"מסך חובה\" בתהליך הדיגיטלי.",
        lambda df: (
            f"לא ידעו כלל: {(df['aware_none']==1).mean()*100:.1f}% מהמשיבים"
        ),
    ),
    "lawyer": (
        "התייעצות עם עורך דין",
        "מרבית האנשים שלא ביקשו להישפט לא חשו צורך בעורך דין. בקרב המבקשים להישפט הצורך הנתפס גבוה בהרבה — במיוחד במגזר הערבי. המשיבים אשר חשבו להתייעץ עם עו\"ד פירטו כי המחיר וחוסר הידיעה כיצד להתייעץ היו חסמים מרכזיים.",
        None,
    ),
    "conversion": (
        "פער המגזרים בבקשת המרה",
        "פער מגזרי קיצוני בשיעור מבקשי המרת הדוח לאזהרה: 30% בלבד מהערבים מול שיעור יותר מכפול של 64% מהיהודים. החסמים: חוסר אמון בתועלת + חשש להחמרה + מורכבות תהליך.",
        lambda df: _conversion_stats(df),
    ),
    "fine_payment": (
        "תשלום הקנס בפועל",
        "מרבית אלו שלא ביקשו להישפט שילמו בפועל את הקנס — במיוחד במגזר הערבי (ציות גבוה). 18% מהיהודים לא שילמו — שיעור לא מבוטל.",
        lambda df: _payment_stats(df),
    ),
    "trial_clarity": (
        "בהירות הליך הבקשה להישפט",
        "תהליך הגשת הבקשה להישפט נתפס ברור רק ברמה חלקית — חסם קריטי. כמחצית תופסים את בהירות התהליך במידה מועטה/בינונית בלבד (יותר במגזר הערבי). כרבע עד שליש לא ידעו איך לעקוב אחר הסטטוס. בית הדין הדיגיטלי חייב לכלול \"דף סטטוס\" בזמן-אמת.",
        lambda df: f"בהירות ממוצעת: {df['trial_clarity_num'].mean():.2f}/5",
    ),
    "evidence": (
        "ראיות בתיק",
        "מרבית המבקשים להישפט לא ביקשו כלל לקבל ראיות. בפועל כשליש בלבד ביקשו, ורוב הקיבלו את הראיות (יותר במגזר הערבי). 3 מכל 4 ציינו שנתקלו בקשיים בקבלת הראיות.",
        lambda df: _evidence_stats(df),
    ),
    "hearing": (
        "דיון בפועל",
        "רק מעט יותר ממחצית מבקשי הישפטות הגיעו למצב של דיון בפועל. במגזר היהודי שיעור גבוה משמעותית נכחו בעצמם בדיון בניגוד למגזר הערבי שמסתמך יותר על ייצוג עו\"ד. בתיקי 2025 שיעור הדיון בפועל נמוך עם הרבה תיקים שעדיין ממתינים. ממדדי ההצלחה המרכזיים של הרפורמה צריך להיות קיצור זמן עד דיון/סגירה.",
        lambda df: _hearing_stats(df),
    ),
    "lawyer_repped": (
        "בית הדין כ\"בית דין ללא ייצוג\"",
        "מרבית הנוכחים בדיון לא יוצגו ע\"י עו\"ד — במיוחד במגזר היהודי. שיעור המיוצגים גבוה משמעותית במגזר הערבי. תכנון חוויית המשתמש לאחר הרפורמה צריכה להניח שהאזרח מייצג את עצמו ללא תיווך משפטי.",
        None,
    ),
    "judge_perception": (
        "תפיסות יחס השופט והאיזון",
        "יחס השופט נתפס חיובי יחסית, האפשרות להשמיע גרסה בינונית-חיובית. אבל תחושת האיזון מול התביעה/המשטרה חלשה — מרבית הנוכחים הרגישו שהאיזון היה חלקי או לא קיים, בייחוד במגזר היהודי. ברפורמה הדיגיטלית צריך לחזק באופן גלוי את תחושת האיזון וההוגנות.",
        lambda df: (
            f"יחס השופט: {df['judge_fair_num'].mean():.2f}/5 | "
            f"הזדמנות להשמיע: {df['judge_voice_num'].mean():.2f}/5"
        ),
    ),
    "verdict": (
        "הבנה והוגנות פסק הדין",
        "פסק הדין נתפס מובן יותר משהוא נתפס כהוגן. ההבדל בולט במיוחד אצל מי שלא נכחו בעצמם בדיון או לא היו מיוצגים היטב.",
        lambda df: (
            f"מובנות: {df['verdict_understood_num'].mean():.2f}/5 | "
            f"הוגנות: {df['verdict_fair_num'].mean():.2f}/5"
        ),
    ),
    "what_to_change": (
        "מה היו משנים בתהליך",
        "מרבית המבקשים להישפט היו משנים משהו: יותר הוגנות ויחס (במגזר היהודי), רמת הסבר ומידע, פישוט הבירוקרטיה וזירוז זמני המתנה (יותר במגזר הערבי). ציר ההבטחה של הרפורמה: הוגן יותר, ברור יותר, ומהיר יותר.",
        None,
    ),
    "satisfaction": (
        "שביעות רצון והרתעה",
        "ההמלצה 'לשלם ולשכוח' מגיעה לרוב מאלו שויתרו מראש על זכותם להישפט – זוהי הרמת ידיים ולא החלטה מושכלת. מנגד, מי שהתמודדו מול המערכת ובחרו להישפט, ממליצים חד-משמעית לפנות לייעוץ ולדרוש את יומכם בבית המשפט – עצה שנשענת על ניסיון מוכח בשטח.",
        lambda df: (
            f"שביעות רצון: {df['process_satisfaction_num'].mean():.2f}/5 | "
            f"זהירות עתידית: {df['future_caution_num'].mean():.2f}/5"
        ),
    ),
    "friend_recommendation": (
        "המלצה לחבר שקיבל דוח",
        "מי שלא ביקשו להישפט ממליצים בעיקר \"לשלם מיד\" — המלצה של כניעה ולא בחירה מודעת. לעומתם, מי שביקשו להישפט ממליצים לבקש להישפט ולפנות לייעוץ — המלצה מבוססת ניסיון. ",
        None,
    ),
}


def _conversion_stats(df: pd.DataFrame) -> str:
    base = df[(~df["requested_trial"]) & (df["aware_convert"] == 1)]
    if base.empty:
        return "אין מספיק נתונים"
    parts = []
    for m in ["מגזר יהודי", "מגזר ערבי"]:
        sub = base[base["migzar"] == m]
        if len(sub):
            rate = sub["asked_convert_warning"].eq("כן").mean() * 100
            parts.append(f"{m}: {rate:.1f}% (n={len(sub)})")
    return " | ".join(parts) if parts else "אין מספיק נתונים"


def _payment_stats(df: pd.DataFrame) -> str:
    base = df[~df["requested_trial"]]
    if base.empty:
        return "אין מספיק נתונים"
    parts = []
    for m in ["מגזר יהודי", "מגזר ערבי"]:
        sub = base[base["migzar"] == m]
        if len(sub):
            rate = sub["paid_fine_actual"].eq("כן").mean() * 100
            parts.append(f"{m}: {rate:.1f}% שילמו")
    return " | ".join(parts) if parts else "אין מספיק נתונים"


def _evidence_stats(df: pd.DataFrame) -> str:
    if "lawyer_repped" not in df.columns or "evidence_requested" not in df.columns:
        return "אין מספיק נתונים"
    work = df.dropna(subset=["lawyer_repped", "evidence_requested"])
    if work.empty:
        return "אין מספיק נתונים"
    rep = work[work["lawyer_repped"].eq("כן")]
    nonrep = work[work["lawyer_repped"].eq("לא")]
    if rep.empty or nonrep.empty:
        return "אין מספיק נתונים להשוואה בין מי שיוצג למי שלא"
    rep_rate = rep["evidence_requested"].eq("כן").mean() * 100
    nonrep_rate = nonrep["evidence_requested"].eq("כן").mean() * 100
    if abs(rep_rate - nonrep_rate) < 2:
        return f"שיעור מבקשי הראיות היה כמעט זהה בין מי שיוצג ע\"י עו\"ד ({rep_rate:.1f}%) ומי שלא ({nonrep_rate:.1f}%)."
    direction = "יותר" if rep_rate > nonrep_rate else "פחות"
    return f"מי שיוצג ע\"י עו\"ד ביקש ראיות {direction} ({rep_rate:.1f}% לעומת {nonrep_rate:.1f}%)."


def _hearing_stats(df: pd.DataFrame) -> str:
    base = df[df["requested_trial"]]
    if base.empty:
        return "אין מספיק נתונים"
    rate = base["hearing_held_bin"].eq("היה דיון בפועל").mean() * 100
    return f"דיון התקיים בפועל אצל {rate:.1f}% ממבקשי הישפטות (n={len(base)})"


def render_insight(key: str, df: Optional[pd.DataFrame] = None) -> None:
    if key not in INSIGHTS:
        return
    title, body, dyn = INSIGHTS[key]
    live = None
    if dyn is not None and df is not None and len(df) > 0:
        try:
            live = dyn(df)
        except Exception:
            live = None
    _box(title, body, live)
