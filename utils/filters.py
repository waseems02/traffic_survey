"""Global sidebar filters used by every page."""
from __future__ import annotations

import pandas as pd
import streamlit as st


def _clean_options(options: list) -> list:
    return [o for o in options if pd.notna(o) and str(o).lower() != "nan"]


_SIDEBAR_CSS = """
<style>
/* Sidebar filter panel — blends into the dark navy sidebar (no white card). */
[data-testid="stSidebar"] .st-key-sidefilters {
  background: rgba(255,255,255,0.04) !important;
  padding: 14px 14px 12px 14px !important;
  margin: 6px 0 12px 0 !important;
  border-radius: 10px !important;
  border: 1px solid rgba(255,255,255,0.08) !important;
  box-shadow: none !important;
}
[data-testid="stSidebar"] .st-key-sidefilters label,
[data-testid="stSidebar"] .st-key-sidefilters .stMarkdown,
[data-testid="stSidebar"] .st-key-sidefilters .stMarkdown p {
  color: #eaf1f9 !important;
  font-weight: 600 !important;
}
[data-testid="stSidebar"] .st-key-sidefilters [data-baseweb="select"] > div {
  background: rgba(255,255,255,0.06) !important;
  border-radius: 8px !important;
  border: 1px solid rgba(255,255,255,0.14) !important;
  color: #eaf1f9 !important;
}
[data-testid="stSidebar"] .st-key-sidefilters [data-baseweb="tag"] {
  background: #3a8bd8 !important;
  color: #ffffff !important;
}
[data-testid="stSidebar"] .st-key-sidefilters div[role="radiogroup"] {
  background: transparent !important;
  border: none !important;
  gap: 4px !important;
}
[data-testid="stSidebar"] .st-key-sidefilters div[role="radiogroup"] label {
  background: rgba(255,255,255,0.05) !important;
  border: 1px solid rgba(255,255,255,0.10) !important;
  border-radius: 8px !important;
  padding: 6px 10px !important;
  color: #eaf1f9 !important;
}
[data-testid="stSidebar"] .st-key-sidefilters div[role="radiogroup"] label p {
  color: #eaf1f9 !important;
}
[data-testid="stSidebar"] .st-key-sidefilters div[role="radiogroup"] label:has(input:checked) {
  background: #3a8bd8 !important;
  border-color: #66aaf0 !important;
  color: #ffffff !important;
}
[data-testid="stSidebar"] .st-key-sidefilters div[role="radiogroup"] label:has(input:checked) p {
  color: #ffffff !important;
}

.side-filter-title {
  color: #ffffff;
  font-weight: 800;
  font-size: 1rem;
  letter-spacing: 0.2px;
  margin: 0 0 10px 0;
  display: flex; align-items: center; gap: 8px;
}
.side-filter-count {
  display: block;
  color: #8fbbf0 !important;
  font-weight: 700;
  font-size: 0.85rem;
  margin-top: 12px;
  padding-top: 10px;
  border-top: 1px solid rgba(255,255,255,0.10);
}
</style>
"""


def render_sidebar_filters(df: pd.DataFrame) -> pd.DataFrame:
    """Render filter widgets inside the left sidebar; return filtered DataFrame."""
    mahoz_col = "mahoz_short" if "mahoz_short" in df.columns else "mahoz"

    st.markdown(_SIDEBAR_CSS, unsafe_allow_html=True)

    try:
        panel = st.sidebar.container(key="sidefilters")
    except TypeError:
        panel = st.sidebar.container()

    with panel:
        st.markdown(
            "<div class='side-filter-title'><span>🔎 מסננים גלובליים</span></div>",
            unsafe_allow_html=True,
        )

        migzar_opts = _clean_options(sorted(df["migzar"].dropna().unique()))
        migzar = st.multiselect("מגזר", options=migzar_opts, default=migzar_opts, key="f_migzar")

        gender_opts = _clean_options(sorted(df["gender"].dropna().unique()))
        gender = st.multiselect("מגדר", options=gender_opts, default=gender_opts, key="f_gender")

        age_opts = _clean_options(sorted(df["age_band"].dropna().unique()))
        age_band = st.multiselect("גיל", options=age_opts, default=age_opts, key="f_age")

        year_opts = _clean_options(sorted(df["report_year_bin"].dropna().unique()))
        year = st.multiselect("שנת דוח", options=year_opts, default=year_opts, key="f_year")

        mahoz_options = _clean_options(sorted(df[mahoz_col].dropna().unique()))
        mahoz = st.multiselect("מחוז", options=mahoz_options, default=[], key="f_mahoz")

        trial_choice = st.radio(
            "מסלול",
            options=["הכל", "ביקשו להישפט", "שילמו קנס / אחר"],
            index=0, key="f_trial",
        )

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

        st.markdown(
            f"<span class='side-filter-count'>משיבים תחת הסינון: <b>{len(filtered):,}</b> / {len(df):,}</span>",
            unsafe_allow_html=True,
        )

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
