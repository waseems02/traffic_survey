"""Global sidebar filters used by every page."""
from __future__ import annotations

import pandas as pd
import streamlit as st


def _multiselect_all(label: str, options: list, key: str) -> list:
    options = [o for o in options if pd.notna(o) and str(o).lower() != "nan"]
    return st.sidebar.multiselect(label, options=options, default=options, key=key)


def render_sidebar_filters(df: pd.DataFrame) -> pd.DataFrame:
    """Render filter widgets in the sidebar; return filtered DataFrame."""
    st.sidebar.markdown("<h2 style='text-align:right;margin-top:0;'>מסננים גלובליים</h2>", unsafe_allow_html=True)
    st.sidebar.caption("הסינון משפיע על כל הדפים והגרפים")

    migzar = _multiselect_all("מגזר", sorted(df["migzar"].dropna().unique()), "f_migzar")
    gender = _multiselect_all("מגדר", sorted(df["gender"].dropna().unique()), "f_gender")
    age_band = _multiselect_all("קבוצת גיל", sorted(df["age_band"].dropna().unique()), "f_age")

    trial_choice = st.sidebar.radio(
        "מסלול",
        options=["הכל", "ביקשו להישפט", "שילמו קנס / אחר"],
        index=0, horizontal=False, key="f_trial",
    )

    year_options = sorted([y for y in df["report_year_bin"].dropna().unique() if y not in ("nan",)])
    year = _multiselect_all("שנת דוח", year_options, "f_year")

    mahoz_col = "mahoz_short" if "mahoz_short" in df.columns else "mahoz"
    mahoz_options = sorted(df[mahoz_col].dropna().unique())
    mahoz = st.sidebar.multiselect("מחוז (אופציונלי)", options=mahoz_options, default=[], key="f_mahoz")

    filtered = df.copy()
    if migzar:
        filtered = filtered[filtered["migzar"].isin(migzar)]
    if gender:
        filtered = filtered[filtered["gender"].isin(gender)]
    if age_band:
        filtered = filtered[filtered["age_band"].isin(age_band)]
    if year:
        filtered = filtered[filtered["report_year_bin"].isin(year)]
    if mahoz:
        filtered = filtered[filtered[mahoz_col].isin(mahoz)]
    if trial_choice == "ביקשו להישפט":
        filtered = filtered[filtered["requested_trial"]]
    elif trial_choice == "שילמו קנס / אחר":
        filtered = filtered[~filtered["requested_trial"]]

    st.sidebar.markdown("---")
    st.sidebar.metric("משיבים תחת הסינון", f"{len(filtered):,} / {len(df):,}")

    return filtered

def _load_raw_data(default_path: str = "data.xlsx") -> pd.DataFrame | None:
    df = st.session_state.get("raw_data")
    if df is None:
        from utils.data_loader import load_default_or_upload

        df = load_default_or_upload(default_path)
        if df is not None:
            st.session_state["raw_data"] = df
    return df


def init_global_filters(default_path: str = "data.xlsx") -> pd.DataFrame | None:
    """Load raw data if needed, render the shared sidebar filters, and update session state."""
    df = _load_raw_data(default_path)
    if df is None:
        return None
    filtered = render_sidebar_filters(df)
    st.session_state["filtered_data"] = filtered
    return filtered


def require_data(default_path: str = "data.xlsx") -> pd.DataFrame:
    """Pages call this to fetch the active filtered dataset, or stop the page."""
    if st.session_state.get("filtered_data") is None:
        if init_global_filters(default_path) is None:
            st.warning(
                "⚠️ לא נטענו נתונים. פתח את דף הבית או העלה קובץ כדי להתחיל."
            )
            st.stop()

    df = st.session_state.get("filtered_data")
    if df is None or len(df) == 0:
        st.warning("⚠️ לא נמצאו נתונים. ודא שטענת את הקובץ בדף הבית, ושלא סיננת יותר מדי.")
        st.stop()
    return df
