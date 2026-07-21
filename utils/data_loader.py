"""Data loader for the Ministry of Justice traffic-reports dataset.

Single source of truth: maps the long Hebrew questionnaire headers to short
canonical column names used everywhere in the dashboard. Handles cleaning,
likert parsing, and removal of header-meta artefact rows that were pasted
into the source spreadsheet.
"""
from __future__ import annotations

import hashlib
import os
from io import BytesIO
from typing import Optional, Union

import numpy as np
import pandas as pd
import streamlit as st


COLUMN_MAP: dict[str, str] = {
    "Record ID": "record_id",
    "סמן/י את מינך:": "gender",
    "מהו גילך?": "age_raw",
    "לאיזה מגזר הינך משתייך?": "migzar",
    "באיזה מחוז אתה גר?": "mahoz",
    "דתיות": "religiosity",
    "גיל.1": "age_band",
    "דוח אחד לעומת 2 ומעלה": "report_count_bin",
    "שנת דוח": "report_year_bin",
    "שנת דוח.1": "report_year_bin_alt",
    "קיבלו דוח ושילמו קנס": "_paid_fine_flag",
    "קיבלו דוח וביקשו להישפט": "_requested_trial_flag",
    "ממי קיבלת את הדו\"ח? ": "report_source",
    "איך קיבלת את הדו\"ח? ": "report_channel",
    "אופן קבלת הדוח": "report_channel_bin",
    "מהירות": "offense_speeding",
    "שימוש בטלפון": "offense_phone",
    "אור אדום": "offense_red_light",
    "חגורת בטיחות": "offense_seatbelt",
    "נסיעה בשוליים": "offense_shoulder",
    "נסיעה בנתיב תחבורה ציבורית": "offense_bus_lane",
    "שינויים ברכב בניגוד לחוק (כמו חלונות כהים)": "offense_illegal_upgrades",
    "אי ציות לתמרור": "offense_sign",
    "חניה": "offense_parking",
    "סוג דוח אחר – אנא פרט": "offense_other",
    "ולגבי תחושותיך לגבי הדו\"ח שקיבלת...האם לדעתך הדו\"ח היה מוצדק?": "report_justified",
    "האם הרגשת שיש לך אפשרות להשמיע את קולך או את גרסתך ביחס לדו\"ח?": "voice_heard",
    "ובאופן ספציפי, האם ידעת שהיה באפשרותך לבקש להמיר את הדו\"ח באזהרה ולא להישפט?": "aware_convert_warning",
    "כן, ידעתי שיכולתי להמיר את הדו\"ח באזהרה": "aware_convert",
    "כן, ידעתי שיכולתי לבקש להישפט": "aware_trial",
    "לא ידעתי כלל שהייתי יכול להמיר את הדו\"ח באזהרה או לבקש להישפט": "aware_none",
    "ואיך התמודדת ופעלת לגבי דו\"ח התעבורה שקיבלת...האם לאחר שקיבלת את הדו\"ח חשת צורך בליווי או התייעצות של עורך דין?": "lawyer_consult",
    "ואיך התמודדת ופעלת לגבי דו\"ח התעבורה שקיבלת...האם לאחר שקיבלת את הדו\"ח חשת צורך בליווי או התייעצות של עורך דין?.1": "lawyer_consult_bin",
    "האם ביקשת להמיר את הדו\"ח לאזהרה?": "asked_convert_warning",
    "ביקשתי להמיר לאזהרה": "no_trial_reason_converted",
    "לא היה בזה צורך מבחינתי": "no_trial_reason_unneeded",
    "התהליך נראה לי מסובך": "no_trial_reason_complex",
    "לא האמנתי שיש טעם": "no_trial_reason_pointless",
    "חששתי שהבקשה להישפט תוביל להחמרה": "no_trial_reason_worsening",
    "בשל שיקול כלכלי": "no_trial_reason_cost",
    "אחר, פרט": "no_trial_reason_other",
    "והאם בפועל שילמת את הקנס שבדו\"ח? ": "paid_fine_actual",
    " כעת תישאל לגבי ההליך המשפטי שעברת...באיזו מידה תהליך הגשת הבקשה להישפט היה ברור לך?  ": "trial_clarity",
    "האם ידעת כיצד לעקוב אחרי סטטוס הבקשה שהגשת להישפט?": "tracked_status",
    "האם ביקשת לקבל ראיות (מעבר לראיות שקיבלת עם הדו\"ח) בנוגע לתיק?": "evidence_requested",
    "האם קיבלת את הראיות בתיק?": "evidence_received",
    " האם נתקלת בקשיים בקבלת הראיות? ": "evidence_difficulty",
    "האם התקיים דיון בפועל?": "hearing_held",
    "האם התקיים דיון בפועל?.1": "hearing_held_bin",
    "האם עורך דין ייצג אותך בדיון בביהמ\"ש?": "lawyer_repped",
    "באיזו מידה לדעתך השופט/ת התייחס/ה אליך באופן הוגן ומכבד?  ": "judge_fair",
    "ועד כמה הרגשת שניתנה לך הזדמנות אמיתית להשמיע את גרסתך?  ": "judge_voice",
    "האם לדעתך היה איזון בין העמדה שלך לבין זו של התביעה/המשטרה?": "balance_perception",
    " עד כמה ההחלטה/פסק הדין שניתן בתיק היה מובן לך?  ": "verdict_understood",
    " ועד כמה ההחלטה/פסק הדין שניתן בתיק היה הוגן בעיניך?  ": "verdict_fair",
    "עד כמה היית מרוצה מהתהליך": "process_satisfaction",
    "באיזו מידה הדו\"ח שקיבלת עודד אותך לנהוג בזהירות רבה יותר בעתיד": "future_caution",
    "ובהסתכלות לאחור מה היית ממליץ לחבר שקיבל דו\"ח תעבורה לעשות? ": "friend_recommendation",
    "באיזו שנה קיבלת רישיון נהיגה?": "license_year",
    "השכלה": "education",
    "מצב משפחתי": "family_status",
    "הכנסה": "income",
    "[Topic:   Question: עד כמה הבנת או לא הבנת מה העבירה שבגינה קיבלת את הדוח ומה העונש?דרג בין 1 ל-5, כש-5 פירושו במידה רבה מאוד ו- 1 כלל לא]": "understand_offense",
    "[Topic:   Question: לאזרח שמקבל דו\"ח תעבורה כמה אפשרויות פעולה: לשלם על הדו\"ח, לבקש להישפט או להמיר את הדו\"ח לאזהרה.עד כמה הבנת או לא הבנת את אפשרויות ה": "understand_options",
}


OFFENSE_COLS: dict[str, str] = {
    "offense_speeding": "מהירות מופרזת",
    "offense_phone": "שימוש בטלפון",
    "offense_red_light": "אי ציות לרמזור אדום",
    "offense_seatbelt": "אי חגירת חגורה",
    "offense_bus_lane": "נסיעה בנת\"צ",
    "offense_sign": "אי ציות לתמרור",
    "offense_shoulder": "נסיעה בשוליים",
    "offense_illegal_upgrades": "שינויים לא חוקיים ברכב",
    "offense_parking": "חניה",
}


NO_TRIAL_REASONS: dict[str, str] = {
    "no_trial_reason_converted": "ביקשתי להמיר לאזהרה",
    "no_trial_reason_unneeded": "לא היה בזה צורך",
    "no_trial_reason_complex": "התהליך נראה מסובך",
    "no_trial_reason_pointless": "לא האמנתי שיש טעם",
    "no_trial_reason_worsening": "חששתי להחמרה",
    "no_trial_reason_cost": "שיקול כלכלי",
    "no_trial_reason_other": "אחר",
}


LIKERT_LABELS = {
    "5- במידה רבה מאוד": 5,
    "4": 4,
    "3": 3,
    "2": 2,
    "1- כלל לא": 1,
}


MAHOZ_SHORT: dict[str, str] = {
    "מחוז הצפון": "צפון",
    "מחוז המרכז": "מרכז",
    "מחוז חיפה": "חיפה",
    "מחוז תל אביב": "תל אביב",
    "מחוז ירושלים": "ירושלים",
    "מחוז הדרום": "דרום",
    "יהודה ושומרון": "יו\"ש",
}


def _short_mahoz(s: pd.Series) -> pd.Series:
    """Truncate the verbose mahoz label to a clean short district name."""
    def _map(val):
        if pd.isna(val):
            return np.nan
        text = str(val).strip()
        for prefix, short in MAHOZ_SHORT.items():
            if text.startswith(prefix):
                return short
        return text[:25]
    return s.map(_map)


def to_likert_numeric(s: pd.Series) -> pd.Series:
    """Convert PPT-style Hebrew likert labels to numeric 1-5 (NaN for 'לא יודע')."""
    return s.map(LIKERT_LABELS).astype("float")


def likert_to_3band(s: pd.Series) -> pd.Series:
    """Collapse 1-5 to {מועטה(1-2), בינונית(3), רבה(4-5)} for stacked bars."""
    num = to_likert_numeric(s)
    out = pd.Series(index=s.index, dtype="object")
    out[num <= 2] = "במידה מועטה"
    out[num == 3] = "במידה בינונית"
    out[num >= 4] = "במידה רבה"
    return out


def _binary_selected(s: pd.Series) -> pd.Series:
    """Map Selected/Not Selected (and 1/0) to 1/0 ints, NaN preserved."""
    if pd.api.types.is_numeric_dtype(s):
        return pd.to_numeric(s, errors="coerce")
    mapping = {"Selected": 1, "Not Selected": 0, "1": 1, "0": 0, 1: 1, 0: 0}
    return s.map(mapping).astype("float")


def _strip_artifact_rows(df: pd.DataFrame) -> pd.DataFrame:
    """Drop the PPT-summary rows accidentally placed in the data range.
    Strategy: keep rows where Record ID is a long numeric (>10 digits).
    """
    rid = df["Record ID"].astype(str)
    mask = rid.str.fullmatch(r"\d{10,}")
    return df.loc[mask].copy()


@st.cache_data(show_spinner=False)
def load_clean(source: Union[str, bytes, BytesIO], cache_key: Optional[str] = None) -> pd.DataFrame:
    """Read the survey workbook and return a cleaned canonical DataFrame.

    `source` may be a path or a BytesIO/bytes payload from `st.file_uploader`.
    `cache_key` is incorporated into the cache so changed file bytes invalidate.
    """
    _ = cache_key  # only used to key the cache
    if isinstance(source, (bytes, bytearray)):
        df_raw = pd.read_excel(BytesIO(source))
    elif isinstance(source, BytesIO):
        source.seek(0)
        df_raw = pd.read_excel(source)
    else:
        df_raw = pd.read_excel(source)

    df_raw = _strip_artifact_rows(df_raw)
    df_raw.columns = [str(c).replace("\xa0", " ") for c in df_raw.columns]

    df = df_raw.rename(columns=COLUMN_MAP).copy()

    for col in ["gender", "migzar", "mahoz", "religiosity", "age_band",
                "report_count_bin", "report_year_bin", "report_year_bin_alt",
                "education", "family_status", "income",
                "report_source", "report_channel", "report_channel_bin",
                "lawyer_consult_bin", "hearing_held_bin"]:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip().replace({"nan": np.nan, "None": np.nan})

    df["age_raw"] = pd.to_numeric(df["age_raw"], errors="coerce")
    df["license_year"] = pd.to_numeric(df.get("license_year"), errors="coerce")

    df["requested_trial"] = _binary_selected(df.get("_requested_trial_flag", pd.Series(dtype="float"))).fillna(0).astype(int).eq(1)
    df["paid_fine_track"] = _binary_selected(df.get("_paid_fine_flag", pd.Series(dtype="float"))).fillna(0).astype(int).eq(1)
    df["trial_label"] = np.where(df["requested_trial"], "ביקשו להישפט", "שילמו קנס / אחר")

    for col in list(OFFENSE_COLS) + list(NO_TRIAL_REASONS) + ["aware_convert", "aware_trial", "aware_none"]:
        if col in df.columns:
            df[col] = _binary_selected(df[col])

    for col in ["understand_offense", "understand_options", "report_justified",
                "voice_heard", "trial_clarity", "evidence_difficulty",
                "judge_fair", "judge_voice", "verdict_understood",
                "verdict_fair", "process_satisfaction", "future_caution"]:
        if col in df.columns:
            df[f"{col}_num"] = to_likert_numeric(df[col])

    df["report_received_year"] = _unify_report_year(df)

    if "mahoz" in df.columns:
        df["mahoz_short"] = _short_mahoz(df["mahoz"])

    return df.reset_index(drop=True)


def _unify_report_year(df: pd.DataFrame) -> pd.Series:
    """Combine the 3 conditional 'when did you receive your report' columns into one."""
    candidates = [
        "ככל שזכור לך, מתי קיבלת את דו\"ח התעבורה שלך? קיבלו דוח אחד ",
        "ככל שזכור לך, מתי קיבלת את דו\"ח התעבורה האחרון שלך?  קיבלו יותר מדוח ולא ביקשו להשפט",
        "ככל שזכור לך, מתי קיבלת את דו\"ח התעבורה האחרון שלך?קיבלו יותר מדוח וביקשו להשפט",
    ]
    out = pd.Series(np.nan, index=df.index, dtype="object")
    for c in candidates:
        if c in df.columns:
            mask = out.isna() & df[c].notna() & df[c].astype(str).str.strip().ne("")
            out[mask] = df.loc[mask, c]
    out = out.astype(str).str.extract(r"(20\d{2})", expand=False)
    return out


def load_default_or_upload(default_path: str = "data.xlsx") -> Optional[pd.DataFrame]:
    """Return a cleaned DataFrame. Auto-load default if present; allow override via uploader."""
    df = None
    cache_key = None

    if "uploaded_bytes" in st.session_state and st.session_state["uploaded_bytes"]:
        payload = st.session_state["uploaded_bytes"]
        cache_key = hashlib.sha1(payload).hexdigest()
        df = load_clean(payload, cache_key=cache_key)
    elif os.path.exists(default_path):
        cache_key = f"{default_path}:{os.path.getmtime(default_path)}"
        df = load_clean(default_path, cache_key=cache_key)

    return df


def _read_raw_excel(source: Union[str, bytes, BytesIO]) -> pd.DataFrame:
    """Read an Excel source into a raw DataFrame without any cleaning."""
    if isinstance(source, (bytes, bytearray)):
        return pd.read_excel(BytesIO(source))
    if isinstance(source, BytesIO):
        source.seek(0)
        return pd.read_excel(source)
    return pd.read_excel(source)


def set_comparison_bytes(new_bytes: bytes, label: Optional[str] = None) -> int:
    """Store a *second* dataset in session state without touching the main data.

    Used by the year-over-year comparison view: the main dataset stays as the
    baseline (e.g. 2025 wave), while this holds the second wave (e.g. 2026).
    Returns the number of raw rows in the uploaded workbook.
    """
    raw = _read_raw_excel(new_bytes)
    st.session_state["comparison_bytes"] = bytes(new_bytes)
    st.session_state["comparison_label"] = (label or "").strip() or "קובץ להשוואה"
    st.cache_data.clear()
    return len(raw)


def clear_comparison() -> None:
    """Drop the second dataset from session state."""
    st.session_state.pop("comparison_bytes", None)
    st.session_state.pop("comparison_label", None)
    st.cache_data.clear()


def load_comparison_or_none() -> Optional[pd.DataFrame]:
    """Return the cleaned comparison DataFrame, or None if none uploaded."""
    payload = st.session_state.get("comparison_bytes")
    if not payload:
        return None
    cache_key = hashlib.sha1(payload).hexdigest()
    return load_clean(payload, cache_key=cache_key)


def comparison_label() -> str:
    """Human label for the comparison dataset (falls back to a default)."""
    return st.session_state.get("comparison_label") or "קובץ להשוואה"


def main_label() -> str:
    """Human label for the primary dataset."""
    return st.session_state.get("main_label") or "קובץ ראשי"


def set_main_label(label: str) -> None:
    st.session_state["main_label"] = (label or "").strip() or "קובץ ראשי"


def append_excel_bytes(
    new_bytes: bytes,
    default_path: str = "data.xlsx",
) -> tuple[bytes, int, int]:
    """Append rows from `new_bytes` to the currently-active dataset.

    The currently-active source is the previously uploaded bytes (if any),
    otherwise the on-disk default file. Returns (combined_xlsx_bytes, new_rows,
    total_rows). Existing data is never modified — only the in-memory/session
    payload is updated by the caller.
    """
    if "uploaded_bytes" in st.session_state and st.session_state["uploaded_bytes"]:
        existing_df = _read_raw_excel(st.session_state["uploaded_bytes"])
    elif os.path.exists(default_path):
        existing_df = _read_raw_excel(default_path)
    else:
        existing_df = pd.DataFrame()

    new_df = _read_raw_excel(new_bytes)

    combined = pd.concat([existing_df, new_df], ignore_index=True, sort=False)

    buf = BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as writer:
        combined.to_excel(writer, index=False)
    return buf.getvalue(), len(new_df), len(combined)
