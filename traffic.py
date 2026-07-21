"""Home page — full-screen landing splash for the Traffic-Reports dashboard."""
from __future__ import annotations

import os

import streamlit as st

import base64
from utils.data_loader import (
    append_excel_bytes,
    clear_comparison,
    comparison_label,
    load_comparison_or_none,
    load_default_or_upload,
    main_label,
    set_comparison_bytes,
    set_main_label,
)

@st.cache_data
def get_img_as_base64(file_path: str) -> str:
    """Load an image file and return its base64-encoded string."""
    with open(file_path, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()

img = get_img_as_base64("static/SurveyIc.png")
israel_img = get_img_as_base64("assets/Israel_image.jpg")

def _inject_shared_css() -> None:
    """Load the shared assets/styles.css so the sidebar theme applies on the home page too."""
    path = os.path.join(os.path.dirname(__file__), "assets", "styles.css")
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


st.set_page_config(
    page_title="סקר מקבלי דוחות תעבורה",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded",
)

_inject_shared_css()

st.markdown(
    f"""
    <style>

      /* Apply the magicpattern SVG as the home-page background.
         Uses .stApp (with !important) so it wins over styles.css which
         also targets .stApp with !important. The sidebar keeps its own
         dark theme because [data-testid="stSidebar"] is a child of .stApp
         and sets its own background with !important. */
      .stApp,
      [data-testid="stAppViewContainer"],
      [data-testid="stMain"],
      section.main {{
        min-height: 100vh;
        background-size: cover !important;
        background-position: center center !important;
        background-repeat: repeat !important;
        background-image: url("data:image/svg+xml;utf8,%3Csvg viewBox=%220 0 2000 1400%22 xmlns=%22http:%2F%2Fwww.w3.org%2F2000%2Fsvg%22%3E%3Cmask id=%22b%22 x=%220%22 y=%220%22 width=%222000%22 height=%221400%22%3E%3Cpath fill=%22url(%23a)%22 d=%22M0 0h2000v1400H0z%22%2F%3E%3C%2Fmask%3E%3Cpath fill=%22%23000336%22 d=%22M0 0h2000v1400H0z%22%2F%3E%3Cg style=%22transform-origin:center center%22 stroke=%22%234c4e72%22 stroke-width=%222.6%22 mask=%22url(%23b)%22%3E%3Cpath fill=%22none%22 d=%22M0 0h80v80H0zM80 0h80v80H80zM160 0h80v80h-80zM240 0h80v80h-80zM320 0h80v80h-80z%22%2F%3E%3Cpath fill=%22%234c4e721a%22 d=%22M400 0h80v80h-80z%22%2F%3E%3Cpath fill=%22%234c4e720e%22 d=%22M480 0h80v80h-80z%22%2F%3E%3Cpath fill=%22%234c4e7276%22 d=%22M560 0h80v80h-80z%22%2F%3E%3Cpath fill=%22none%22 d=%22M640 0h80v80h-80zM720 0h80v80h-80zM800 0h80v80h-80zM880 0h80v80h-80zM960 0h80v80h-80zM1040 0h80v80h-80z%22%2F%3E%3Cpath fill=%22%234c4e722d%22 d=%22M1120 0h80v80h-80z%22%2F%3E%3Cpath fill=%22%234c4e72d5%22 d=%22M1200 0h80v80h-80z%22%2F%3E%3Cpath fill=%22none%22 d=%22M1280 0h80v80h-80z%22%2F%3E%3Cpath fill=%22%234c4e7240%22 d=%22M1360 0h80v80h-80z%22%2F%3E%3Cpath fill=%22%234c4e7266%22 d=%22M1440 0h80v80h-80z%22%2F%3E%3Cpath fill=%22none%22 d=%22M1520 0h80v80h-80z%22%2F%3E%3Cpath fill=%22%234c4e72e6%22 d=%22M1600 0h80v80h-80z%22%2F%3E%3Cpath fill=%22none%22 d=%22M1680 0h80v80h-80zM1760 0h80v80h-80zM1840 0h80v80h-80zM1920 0h80v80h-80zM0 80h80v80H0z%22%2F%3E%3Cpath fill=%22%234c4e7246%22 d=%22M80 80h80v80H80z%22%2F%3E%3Cpath fill=%22none%22 d=%22M160 80h80v80h-80z%22%2F%3E%3Cpath fill=%22%234c4e7233%22 d=%22M240 80h80v80h-80z%22%2F%3E%3Cpath fill=%22none%22 d=%22M320 80h80v80h-80zM400 80h80v80h-80zM480 80h80v80h-80zM560 80h80v80h-80zM640 80h80v80h-80z%22%2F%3E%3Cpath fill=%22%234c4e7255%22 d=%22M720 80h80v80h-80z%22%2F%3E%3Cpath fill=%22none%22 d=%22M800 80h80v80h-80zM880 80h80v80h-80zM960 80h80v80h-80zM1040 80h80v80h-80z%22%2F%3E%3Cpath fill=%22%234c4e72a2%22 d=%22M1120 80h80v80h-80z%22%2F%3E%3Cpath fill=%22%234c4e725e%22 d=%22M1200 80h80v80h-80z%22%2F%3E%3Cpath fill=%22%234c4e7204%22 d=%22M1280 80h80v80h-80z%22%2F%3E%3Cpath fill=%22%234c4e7224%22 d=%22M1360 80h80v80h-80z%22%2F%3E%3Cpath fill=%22none%22 d=%22M1440 80h80v80h-80zM1520 80h80v80h-80z%22%2F%3E%3Cpath fill=%22%234c4e7268%22 d=%22M1600 80h80v80h-80z%22%2F%3E%3Cpath fill=%22none%22 d=%22M1680 80h80v80h-80zM1760 80h80v80h-80zM1840 80h80v80h-80zM1920 80h80v80h-80zM0 160h80v80H0zM80 160h80v80H80zM160 160h80v80h-80z%22%2F%3E%3Cpath fill=%22%234c4e72f8%22 d=%22M240 160h80v80h-80z%22%2F%3E%3Cpath fill=%22none%22 d=%22M320 160h80v80h-80zM400 160h80v80h-80zM480 160h80v80h-80z%22%2F%3E%3Cpath fill=%22%234c4e7276%22 d=%22M560 160h80v80h-80z%22%2F%3E%3Cpath fill=%22none%22 d=%22M640 160h80v80h-80zM720 160h80v80h-80zM800 160h80v80h-80zM880 160h80v80h-80zM960 160h80v80h-80z%22%2F%3E%3Cpath fill=%22%234c4e72e2%22 d=%22M1040 160h80v80h-80z%22%2F%3E%3Cpath fill=%22none%22 d=%22M1120 160h80v80h-80zM1200 160h80v80h-80z%22%2F%3E%3Cpath fill=%22%234c4e721b%22 d=%22M1280 160h80v80h-80z%22%2F%3E%3Cpath fill=%22none%22 d=%22M1360 160h80v80h-80zM1440 160h80v80h-80zM1520 160h80v80h-80z%22%2F%3E%3Cpath fill=%22%234c4e72f9%22 d=%22M1600 160h80v80h-80z%22%2F%3E%3Cpath fill=%22none%22 d=%22M1680 160h80v80h-80zM1760 160h80v80h-80z%22%2F%3E%3Cpath fill=%22%234c4e7293%22 d=%22M1840 160h80v80h-80z%22%2F%3E%3Cpath fill=%22%234c4e725a%22 d=%22M1920 160h80v80h-80z%22%2F%3E%3Cpath fill=%22none%22 d=%22M0 240h80v80H0zM80 240h80v80H80zM160 240h80v80h-80z%22%2F%3E%3Cpath fill=%22%234c4e7252%22 d=%22M240 240h80v80h-80z%22%2F%3E%3Cpath fill=%22%234c4e725d%22 d=%22M320 240h80v80h-80z%22%2F%3E%3Cpath fill=%22%234c4e7245%22 d=%22M400 240h80v80h-80z%22%2F%3E%3Cpath fill=%22none%22 d=%22M480 240h80v80h-80zM560 240h80v80h-80zM640 240h80v80h-80zM720 240h80v80h-80z%22%2F%3E%3Cpath fill=%22%234c4e728b%22 d=%22M800 240h80v80h-80z%22%2F%3E%3Cpath fill=%22%234c4e72e3%22 d=%22M880 240h80v80h-80z%22%2F%3E%3Cpath fill=%22%234c4e72e4%22 d=%22M960 240h80v80h-80z%22%2F%3E%3Cpath fill=%22none%22 d=%22M1040 240h80v80h-80zM1120 240h80v80h-80zM1200 240h80v80h-80zM1280 240h80v80h-80zM1360 240h80v80h-80z%22%2F%3E%3Cpath fill=%22%234c4e72f9%22 d=%22M1440 240h80v80h-80z%22%2F%3E%3Cpath fill=%22%234c4e7207%22 d=%22M1520 240h80v80h-80z%22%2F%3E%3Cpath fill=%22%234c4e729c%22 d=%22M1600 240h80v80h-80z%22%2F%3E%3Cpath fill=%22none%22 d=%22M1680 240h80v80h-80z%22%2F%3E%3Cpath fill=%22%234c4e72bf%22 d=%22M1760 240h80v80h-80z%22%2F%3E%3Cpath fill=%22none%22 d=%22M1840 240h80v80h-80z%22%2F%3E%3Cpath fill=%22%234c4e72e5%22 d=%22M1920 240h80v80h-80z%22%2F%3E%3Cpath fill=%22none%22 d=%22M0 320h80v80H0zM80 320h80v80H80zM160 320h80v80h-80z%22%2F%3E%3Cpath fill=%22%234c4e721c%22 d=%22M240 320h80v80h-80z%22%2F%3E%3Cpath fill=%22none%22 d=%22M320 320h80v80h-80z%22%2F%3E%3Cpath fill=%22%234c4e72fd%22 d=%22M400 320h80v80h-80z%22%2F%3E%3Cpath fill=%22none%22 d=%22M480 320h80v80h-80zM560 320h80v80h-80z%22%2F%3E%3Cpath fill=%22%234c4e7266%22 d=%22M640 320h80v80h-80z%22%2F%3E%3Cpath fill=%22none%22 d=%22M720 320h80v80h-80z%22%2F%3E%3Cpath fill=%22%234c4e7267%22 d=%22M800 320h80v80h-80z%22%2F%3E%3Cpath fill=%22none%22 d=%22M880 320h80v80h-80zM960 320h80v80h-80z%22%2F%3E%3Cpath fill=%22%234c4e726a%22 d=%22M1040 320h80v80h-80z%22%2F%3E%3Cpath fill=%22none%22 d=%22M1120 320h80v80h-80z%22%2F%3E%3Cpath fill=%22%234c4e72a6%22 d=%22M1200 320h80v80h-80z%22%2F%3E%3Cpath fill=%22none%22 d=%22M1280 320h80v80h-80z%22%2F%3E%3Cpath fill=%22%234c4e7278%22 d=%22M1360 320h80v80h-80z%22%2F%3E%3Cpath fill=%22%234c4e72a6%22 d=%22M1440 320h80v80h-80z%22%2F%3E%3Cpath fill=%22%234c4e720e%22 d=%22M1520 320h80v80h-80z%22%2F%3E%3Cpath fill=%22%234c4e72be%22 d=%22M1600 320h80v80h-80z%22%2F%3E%3Cpath fill=%22none%22 d=%22M1680 320h80v80h-80z%22%2F%3E%3Cpath fill=%22%234c4e72be%22 d=%22M1760 320h80v80h-80z%22%2F%3E%3Cpath fill=%22none%22 d=%22M1840 320h80v80h-80zM1920 320h80v80h-80zM0 400h80v80H0z%22%2F%3E%3Cpath fill=%22%234c4e725c%22 d=%22M80 400h80v80H80z%22%2F%3E%3Cpath fill=%22%234c4e7221%22 d=%22M160 400h80v80h-80z%22%2F%3E%3Cpath fill=%22none%22 d=%22M240 400h80v80h-80z%22%2F%3E%3Cpath fill=%22%234c4e7258%22 d=%22M320 400h80v80h-80z%22%2F%3E%3Cpath fill=%22none%22 d=%22M400 400h80v80h-80zM480 400h80v80h-80zM560 400h80v80h-80zM640 400h80v80h-80zM720 400h80v80h-80zM800 400h80v80h-80zM880 400h80v80h-80z%22%2F%3E%3Cpath fill=%22%234c4e7234%22 d=%22M960 400h80v80h-80z%22%2F%3E%3Cpath fill=%22none%22 d=%22M1040 400h80v80h-80zM1120 400h80v80h-80zM1200 400h80v80h-80z%22%2F%3E%3Cpath fill=%22%234c4e72ce%22 d=%22M1280 400h80v80h-80z%22%2F%3E%3Cpath fill=%22none%22 d=%22M1360 400h80v80h-80zM1440 400h80v80h-80zM1520 400h80v80h-80zM1600 400h80v80h-80zM1680 400h80v80h-80zM1760 400h80v80h-80zM1840 400h80v80h-80zM1920 400h80v80h-80zM0 480h80v80H0zM80 480h80v80H80zM160 480h80v80h-80zM240 480h80v80h-80zM320 480h80v80h-80z%22%2F%3E%3Cpath fill=%22%234c4e7266%22 d=%22M400 480h80v80h-80z%22%2F%3E%3Cpath fill=%22%234c4e7276%22 d=%22M480 480h80v80h-80z%22%2F%3E%3Cpath fill=%22none%22 d=%22M560 480h80v80h-80z%22%2F%3E%3Cpath fill=%22%234c4e729b%22 d=%22M640 480h80v80h-80z%22%2F%3E%3Cpath fill=%22none%22 d=%22M720 480h80v80h-80z%22%2F%3E%3Cpath fill=%22%234c4e7206%22 d=%22M800 480h80v80h-80z%22%2F%3E%3Cpath fill=%22none%22 d=%22M880 480h80v80h-80zM960 480h80v80h-80zM1040 480h80v80h-80zM1120 480h80v80h-80z%22%2F%3E%3Cpath fill=%22%234c4e7232%22 d=%22M1200 480h80v80h-80z%22%2F%3E%3Cpath fill=%22none%22 d=%22M1280 480h80v80h-80zM1360 480h80v80h-80zM1440 480h80v80h-80zM1520 480h80v80h-80zM1600 480h80v80h-80z%22%2F%3E%3Cpath fill=%22%234c4e7295%22 d=%22M1680 480h80v80h-80z%22%2F%3E%3Cpath fill=%22none%22 d=%22M1760 480h80v80h-80zM1840 480h80v80h-80z%22%2F%3E%3Cpath fill=%22%234c4e728f%22 d=%22M1920 480h80v80h-80z%22%2F%3E%3Cpath fill=%22%234c4e72e0%22 d=%22M0 560h80v80H0z%22%2F%3E%3Cpath fill=%22%234c4e72a8%22 d=%22M80 560h80v80H80z%22%2F%3E%3Cpath fill=%22%234c4e726b%22 d=%22M160 560h80v80h-80z%22%2F%3E%3Cpath fill=%22none%22 d=%22M240 560h80v80h-80zM320 560h80v80h-80zM400 560h80v80h-80z%22%2F%3E%3Cpath fill=%22%234c4e7253%22 d=%22M480 560h80v80h-80z%22%2F%3E%3Cpath fill=%22none%22 d=%22M560 560h80v80h-80zM640 560h80v80h-80zM720 560h80v80h-80zM800 560h80v80h-80z%22%2F%3E%3Cpath fill=%22%234c4e72fe%22 d=%22M880 560h80v80h-80z%22%2F%3E%3Cpath fill=%22none%22 d=%22M960 560h80v80h-80z%22%2F%3E%3Cpath fill=%22%234c4e72f8%22 d=%22M1040 560h80v80h-80z%22%2F%3E%3Cpath fill=%22none%22 d=%22M1120 560h80v80h-80z%22%2F%3E%3Cpath fill=%22%234c4e72d1%22 d=%22M1200 560h80v80h-80z%22%2F%3E%3Cpath fill=%22none%22 d=%22M1280 560h80v80h-80zM1360 560h80v80h-80zM1440 560h80v80h-80z%22%2F%3E%3Cpath fill=%22%234c4e72cb%22 d=%22M1520 560h80v80h-80z%22%2F%3E%3Cpath fill=%22none%22 d=%22M1600 560h80v80h-80zM1680 560h80v80h-80zM1760 560h80v80h-80zM1840 560h80v80h-80zM1920 560h80v80h-80zM0 640h80v80H0zM80 640h80v80H80zM160 640h80v80h-80zM240 640h80v80h-80z%22%2F%3E%3Cpath fill=%22%234c4e728b%22 d=%22M320 640h80v80h-80z%22%2F%3E%3Cpath fill=%22%234c4e72b6%22 d=%22M400 640h80v80h-80z%22%2F%3E%3Cpath fill=%22none%22 d=%22M480 640h80v80h-80zM560 640h80v80h-80zM640 640h80v80h-80zM720 640h80v80h-80zM800 640h80v80h-80zM880 640h80v80h-80zM960 640h80v80h-80zM1040 640h80v80h-80z%22%2F%3E%3Cpath fill=%22%234c4e7296%22 d=%22M1120 640h80v80h-80z%22%2F%3E%3Cpath fill=%22%234c4e72ee%22 d=%22M1200 640h80v80h-80z%22%2F%3E%3Cpath fill=%22%234c4e72b3%22 d=%22M1280 640h80v80h-80z%22%2F%3E%3Cpath fill=%22%234c4e7215%22 d=%22M1360 640h80v80h-80z%22%2F%3E%3Cpath fill=%22none%22 d=%22M1440 640h80v80h-80zM1520 640h80v80h-80z%22%2F%3E%3Cpath fill=%22%234c4e7206%22 d=%22M1600 640h80v80h-80z%22%2F%3E%3Cpath fill=%22none%22 d=%22M1680 640h80v80h-80z%22%2F%3E%3Cpath fill=%22%234c4e72ce%22 d=%22M1760 640h80v80h-80z%22%2F%3E%3Cpath fill=%22%234c4e7205%22 d=%22M1840 640h80v80h-80z%22%2F%3E%3Cpath fill=%22none%22 d=%22M1920 640h80v80h-80z%22%2F%3E%3Cpath fill=%22%234c4e726a%22 d=%22M0 720h80v80H0z%22%2F%3E%3Cpath fill=%22%234c4e729d%22 d=%22M80 720h80v80H80z%22%2F%3E%3Cpath fill=%22%234c4e726f%22 d=%22M160 720h80v80h-80z%22%2F%3E%3Cpath fill=%22%234c4e72bd%22 d=%22M240 720h80v80h-80z%22%2F%3E%3Cpath fill=%22none%22 d=%22M320 720h80v80h-80z%22%2F%3E%3Cpath fill=%22%234c4e7217%22 d=%22M400 720h80v80h-80z%22%2F%3E%3Cpath fill=%22%234c4e7248%22 d=%22M480 720h80v80h-80z%22%2F%3E%3Cpath fill=%22%234c4e7291%22 d=%22M560 720h80v80h-80z%22%2F%3E%3Cpath fill=%22none%22 d=%22M640 720h80v80h-80z%22%2F%3E%3Cpath fill=%22%234c4e720c%22 d=%22M720 720h80v80h-80z%22%2F%3E%3Cpath fill=%22none%22 d=%22M800 720h80v80h-80zM880 720h80v80h-80zM960 720h80v80h-80z%22%2F%3E%3Cpath fill=%22%234c4e7293%22 d=%22M1040 720h80v80h-80z%22%2F%3E%3Cpath fill=%22none%22 d=%22M1120 720h80v80h-80zM1200 720h80v80h-80zM1280 720h80v80h-80zM1360 720h80v80h-80zM1440 720h80v80h-80zM1520 720h80v80h-80zM1600 720h80v80h-80zM1680 720h80v80h-80zM1760 720h80v80h-80z%22%2F%3E%3Cpath fill=%22%234c4e728e%22 d=%22M1840 720h80v80h-80z%22%2F%3E%3Cpath fill=%22none%22 d=%22M1920 720h80v80h-80z%22%2F%3E%3Cpath fill=%22%234c4e72ca%22 d=%22M0 800h80v80H0z%22%2F%3E%3Cpath fill=%22none%22 d=%22M80 800h80v80H80zM160 800h80v80h-80z%22%2F%3E%3Cpath fill=%22%234c4e7255%22 d=%22M240 800h80v80h-80z%22%2F%3E%3Cpath fill=%22none%22 d=%22M320 800h80v80h-80z%22%2F%3E%3Cpath fill=%22%234c4e7262%22 d=%22M400 800h80v80h-80z%22%2F%3E%3Cpath fill=%22none%22 d=%22M480 800h80v80h-80zM560 800h80v80h-80zM640 800h80v80h-80zM720 800h80v80h-80z%22%2F%3E%3Cpath fill=%22%234c4e7235%22 d=%22M800 800h80v80h-80z%22%2F%3E%3Cpath fill=%22none%22 d=%22M880 800h80v80h-80z%22%2F%3E%3Cpath fill=%22%234c4e72d7%22 d=%22M960 800h80v80h-80z%22%2F%3E%3Cpath fill=%22none%22 d=%22M1040 800h80v80h-80z%22%2F%3E%3Cpath fill=%22%234c4e72e6%22 d=%22M1120 800h80v80h-80z%22%2F%3E%3Cpath fill=%22%234c4e72a5%22 d=%22M1200 800h80v80h-80z%22%2F%3E%3Cpath fill=%22none%22 d=%22M1280 800h80v80h-80zM1360 800h80v80h-80zM1440 800h80v80h-80zM1520 800h80v80h-80zM1600 800h80v80h-80zM1680 800h80v80h-80zM1760 800h80v80h-80zM1840 800h80v80h-80zM1920 800h80v80h-80z%22%2F%3E%3Cpath fill=%22%234c4e727e%22 d=%22M0 880h80v80H0z%22%2F%3E%3Cpath fill=%22%234c4e7238%22 d=%22M80 880h80v80H80z%22%2F%3E%3Cpath fill=%22%234c4e72e9%22 d=%22M160 880h80v80h-80z%22%2F%3E%3Cpath fill=%22%234c4e729c%22 d=%22M240 880h80v80h-80z%22%2F%3E%3Cpath fill=%22none%22 d=%22M320 880h80v80h-80z%22%2F%3E%3Cpath fill=%22%234c4e72ee%22 d=%22M400 880h80v80h-80z%22%2F%3E%3Cpath fill=%22%234c4e720a%22 d=%22M480 880h80v80h-80z%22%2F%3E%3Cpath fill=%22%234c4e7244%22 d=%22M560 880h80v80h-80z%22%2F%3E%3Cpath fill=%22none%22 d=%22M640 880h80v80h-80z%22%2F%3E%3Cpath fill=%22%234c4e7251%22 d=%22M720 880h80v80h-80z%22%2F%3E%3Cpath fill=%22none%22 d=%22M800 880h80v80h-80zM880 880h80v80h-80zM960 880h80v80h-80z%22%2F%3E%3Cpath fill=%22%234c4e7217%22 d=%22M1040 880h80v80h-80z%22%2F%3E%3Cpath fill=%22none%22 d=%22M1120 880h80v80h-80z%22%2F%3E%3Cpath fill=%22%234c4e7263%22 d=%22M1200 880h80v80h-80z%22%2F%3E%3Cpath fill=%22%234c4e72b3%22 d=%22M1280 880h80v80h-80z%22%2F%3E%3Cpath fill=%22none%22 d=%22M1360 880h80v80h-80zM1440 880h80v80h-80zM1520 880h80v80h-80zM1600 880h80v80h-80zM1680 880h80v80h-80zM1760 880h80v80h-80z%22%2F%3E%3Cpath fill=%22%234c4e720f%22 d=%22M1840 880h80v80h-80z%22%2F%3E%3Cpath fill=%22none%22 d=%22M1920 880h80v80h-80zM0 960h80v80H0z%22%2F%3E%3Cpath fill=%22%234c4e72d5%22 d=%22M80 960h80v80H80z%22%2F%3E%3Cpath fill=%22none%22 d=%22M160 960h80v80h-80zM240 960h80v80h-80zM320 960h80v80h-80zM400 960h80v80h-80zM480 960h80v80h-80zM560 960h80v80h-80zM640 960h80v80h-80zM720 960h80v80h-80zM800 960h80v80h-80zM880 960h80v80h-80z%22%2F%3E%3Cpath fill=%22%234c4e72a8%22 d=%22M960 960h80v80h-80z%22%2F%3E%3Cpath fill=%22%234c4e7253%22 d=%22M1040 960h80v80h-80z%22%2F%3E%3Cpath fill=%22%234c4e728b%22 d=%22M1120 960h80v80h-80z%22%2F%3E%3Cpath fill=%22%234c4e729e%22 d=%22M1200 960h80v80h-80z%22%2F%3E%3Cpath fill=%22%234c4e7247%22 d=%22M1280 960h80v80h-80z%22%2F%3E%3Cpath fill=%22none%22 d=%22M1360 960h80v80h-80z%22%2F%3E%3Cpath fill=%22%234c4e7220%22 d=%22M1440 960h80v80h-80z%22%2F%3E%3Cpath fill=%22none%22 d=%22M1520 960h80v80h-80zM1600 960h80v80h-80zM1680 960h80v80h-80zM1760 960h80v80h-80z%22%2F%3E%3Cpath fill=%22%234c4e723b%22 d=%22M1840 960h80v80h-80z%22%2F%3E%3Cpath fill=%22none%22 d=%22M1920 960h80v80h-80zM0 1040h80v80H0z%22%2F%3E%3Cpath fill=%22%234c4e72fb%22 d=%22M80 1040h80v80H80z%22%2F%3E%3Cpath fill=%22%234c4e72a2%22 d=%22M160 1040h80v80h-80z%22%2F%3E%3Cpath fill=%22none%22 d=%22M240 1040h80v80h-80zM320 1040h80v80h-80zM400 1040h80v80h-80zM480 1040h80v80h-80zM560 1040h80v80h-80zM640 1040h80v80h-80zM720 1040h80v80h-80z%22%2F%3E%3Cpath fill=%22%234c4e72fb%22 d=%22M800 1040h80v80h-80z%22%2F%3E%3Cpath fill=%22none%22 d=%22M880 1040h80v80h-80zM960 1040h80v80h-80z%22%2F%3E%3Cpath fill=%22%234c4e72b1%22 d=%22M1040 1040h80v80h-80z%22%2F%3E%3Cpath fill=%22none%22 d=%22M1120 1040h80v80h-80zM1200 1040h80v80h-80zM1280 1040h80v80h-80zM1360 1040h80v80h-80zM1440 1040h80v80h-80zM1520 1040h80v80h-80zM1600 1040h80v80h-80zM1680 1040h80v80h-80z%22%2F%3E%3Cpath fill=%22%234c4e724e%22 d=%22M1760 1040h80v80h-80z%22%2F%3E%3Cpath fill=%22none%22 d=%22M1840 1040h80v80h-80z%22%2F%3E%3Cpath fill=%22%234c4e72d6%22 d=%22M1920 1040h80v80h-80z%22%2F%3E%3Cpath fill=%22none%22 d=%22M0 1120h80v80H0z%22%2F%3E%3Cpath fill=%22%234c4e7212%22 d=%22M80 1120h80v80H80z%22%2F%3E%3Cpath fill=%22%234c4e72a0%22 d=%22M160 1120h80v80h-80z%22%2F%3E%3Cpath fill=%22%234c4e726d%22 d=%22M240 1120h80v80h-80z%22%2F%3E%3Cpath fill=%22none%22 d=%22M320 1120h80v80h-80zM400 1120h80v80h-80zM480 1120h80v80h-80zM560 1120h80v80h-80zM640 1120h80v80h-80zM720 1120h80v80h-80zM800 1120h80v80h-80zM880 1120h80v80h-80z%22%2F%3E%3Cpath fill=%22%234c4e7252%22 d=%22M960 1120h80v80h-80z%22%2F%3E%3Cpath fill=%22none%22 d=%22M1040 1120h80v80h-80zM1120 1120h80v80h-80zM1200 1120h80v80h-80zM1280 1120h80v80h-80z%22%2F%3E%3Cpath fill=%22%234c4e721c%22 d=%22M1360 1120h80v80h-80z%22%2F%3E%3Cpath fill=%22none%22 d=%22M1440 1120h80v80h-80zM1520 1120h80v80h-80zM1600 1120h80v80h-80zM1680 1120h80v80h-80zM1760 1120h80v80h-80zM1840 1120h80v80h-80z%22%2F%3E%3Cpath fill=%22%234c4e72ee%22 d=%22M1920 1120h80v80h-80z%22%2F%3E%3Cpath fill=%22none%22 d=%22M0 1200h80v80H0z%22%2F%3E%3Cpath fill=%22%234c4e72d2%22 d=%22M80 1200h80v80H80z%22%2F%3E%3Cpath fill=%22none%22 d=%22M160 1200h80v80h-80z%22%2F%3E%3Cpath fill=%22%234c4e72cd%22 d=%22M240 1200h80v80h-80z%22%2F%3E%3Cpath fill=%22none%22 d=%22M320 1200h80v80h-80zM400 1200h80v80h-80zM480 1200h80v80h-80zM560 1200h80v80h-80zM640 1200h80v80h-80zM720 1200h80v80h-80z%22%2F%3E%3Cpath fill=%22%234c4e721d%22 d=%22M800 1200h80v80h-80z%22%2F%3E%3Cpath fill=%22%234c4e72ae%22 d=%22M880 1200h80v80h-80z%22%2F%3E%3Cpath fill=%22none%22 d=%22M960 1200h80v80h-80zM1040 1200h80v80h-80zM1120 1200h80v80h-80zM1200 1200h80v80h-80zM1280 1200h80v80h-80zM1360 1200h80v80h-80zM1440 1200h80v80h-80zM1520 1200h80v80h-80zM1600 1200h80v80h-80zM1680 1200h80v80h-80zM1760 1200h80v80h-80zM1840 1200h80v80h-80zM1920 1200h80v80h-80zM0 1280h80v80H0zM80 1280h80v80H80z%22%2F%3E%3Cpath fill=%22%234c4e722f%22 d=%22M160 1280h80v80h-80z%22%2F%3E%3Cpath fill=%22none%22 d=%22M240 1280h80v80h-80zM320 1280h80v80h-80z%22%2F%3E%3Cpath fill=%22%234c4e7201%22 d=%22M400 1280h80v80h-80z%22%2F%3E%3Cpath fill=%22none%22 d=%22M480 1280h80v80h-80zM560 1280h80v80h-80zM640 1280h80v80h-80zM720 1280h80v80h-80zM800 1280h80v80h-80z%22%2F%3E%3Cpath fill=%22%234c4e7250%22 d=%22M880 1280h80v80h-80z%22%2F%3E%3Cpath fill=%22none%22 d=%22M960 1280h80v80h-80zM1040 1280h80v80h-80zM1120 1280h80v80h-80zM1200 1280h80v80h-80z%22%2F%3E%3Cpath fill=%22%234c4e72f2%22 d=%22M1280 1280h80v80h-80z%22%2F%3E%3Cpath fill=%22none%22 d=%22M1360 1280h80v80h-80z%22%2F%3E%3Cpath fill=%22%234c4e7233%22 d=%22M1440 1280h80v80h-80z%22%2F%3E%3Cpath fill=%22none%22 d=%22M1520 1280h80v80h-80z%22%2F%3E%3Cpath fill=%22%234c4e7273%22 d=%22M1600 1280h80v80h-80z%22%2F%3E%3Cpath fill=%22none%22 d=%22M1680 1280h80v80h-80zM1760 1280h80v80h-80z%22%2F%3E%3Cpath fill=%22%234c4e728c%22 d=%22M1840 1280h80v80h-80z%22%2F%3E%3Cpath fill=%22%234c4e72ca%22 d=%22M1920 1280h80v80h-80z%22%2F%3E%3Cpath fill=%22none%22 d=%22M0 1360h80v80H0zM80 1360h80v80H80zM160 1360h80v80h-80z%22%2F%3E%3Cpath fill=%22%234c4e720a%22 d=%22M240 1360h80v80h-80z%22%2F%3E%3Cpath fill=%22none%22 d=%22M320 1360h80v80h-80zM400 1360h80v80h-80zM480 1360h80v80h-80z%22%2F%3E%3Cpath fill=%22%234c4e72be%22 d=%22M560 1360h80v80h-80z%22%2F%3E%3Cpath fill=%22none%22 d=%22M640 1360h80v80h-80zM720 1360h80v80h-80zM800 1360h80v80h-80zM880 1360h80v80h-80z%22%2F%3E%3Cpath fill=%22%234c4e720a%22 d=%22M960 1360h80v80h-80z%22%2F%3E%3Cpath fill=%22%234c4e72e2%22 d=%22M1040 1360h80v80h-80z%22%2F%3E%3Cpath fill=%22none%22 d=%22M1120 1360h80v80h-80z%22%2F%3E%3Cpath fill=%22%234c4e7259%22 d=%22M1200 1360h80v80h-80z%22%2F%3E%3Cpath fill=%22none%22 d=%22M1280 1360h80v80h-80zM1360 1360h80v80h-80zM1440 1360h80v80h-80zM1520 1360h80v80h-80z%22%2F%3E%3Cpath fill=%22%234c4e7204%22 d=%22M1600 1360h80v80h-80z%22%2F%3E%3Cpath fill=%22none%22 d=%22M1680 1360h80v80h-80zM1760 1360h80v80h-80z%22%2F%3E%3Cpath fill=%22%234c4e7258%22 d=%22M1840 1360h80v80h-80z%22%2F%3E%3Cpath fill=%22none%22 d=%22M1920 1360h80v80h-80z%22%2F%3E%3C%2Fg%3E%3Cdefs%3E%3CradialGradient id=%22a%22%3E%3Cstop offset=%2246.4%25%22 stop-color=%22%23fff%22 stop-opacity=%220%22%2F%3E%3Cstop offset=%22100%25%22 stop-color=%22%23fff%22 stop-opacity=%22.536%22%2F%3E%3C%2FradialGradient%3E%3C%2Fdefs%3E%3C%2Fsvg%3E");
      }}
      [data-testid="stSidebar"] {{
        background-image: url("data:image/png;base64,{img}") !important;
        background-size: contain !important;
        background-position: center bottom !important;
        background-repeat: no-repeat !important;
      }}
      [data-testid="stHeader"] {{ background: transparent; }}

    .block-container {{
        min-height: calc(100vh - 4rem);
        display: flex;
        align-items: center;
        justify-content: center;
        padding-top: 2rem !important;
        padding-bottom: 2rem !important;
      }}

      /* Hero card — nudged toward the left of the viewport. */
      .home-hero {{
        text-align: center;
        color: #ffffff;
        max-width: 880px;
        padding: 36px 28px;
        transform: translateX(-8rem);
      }}
      @media (max-width: 900px) {{
        .home-hero {{ transform: none; }}
      }}
      .home-hero h1 {{
        font-size: clamp(2.4rem, 5vw, 4.4rem);
        line-height: 1.1;
        margin: 0 0 18px 0;
        color: #ffffff;
        text-shadow: 0 6px 24px rgba(0,0,0,.55);
        letter-spacing: 0.5px;
      }}
      .home-hero .home-subtitle {{
        font-size: clamp(1.05rem, 1.6vw, 1.5rem);
        color: #e9eef7;
        margin: 0 0 26px 0;
        text-shadow: 0 2px 12px rgba(0,0,0,.45);
      }}
      .home-hero .home-meta {{
        color: #c8cfdb;
        font-size: 1rem;
        margin: 4px 0;
        text-shadow: 0 2px 8px rgba(0,0,0,.4);
      }}
      .home-hero .home-divider {{
        width: 90px;
        height: 3px;
        background: linear-gradient(90deg, #ffd479, transparent);
        margin: 22px auto 24px auto;
        border-radius: 2px;
        transform: scaleX(0);
        transform-origin: center;
        animation: divider-grow 0.9s ease-out 0.6s forwards;
      }}
      .home-hero .home-hint {{
        margin-top: 28px;
        font-size: 0.95rem;
        color: #b8c0d0;
        opacity: 0.9;
      }}

      /* Staggered fade + slide-up animation. */
      .home-hero .anim {{
        opacity: 0;
        transform: translateY(24px);
        animation: hero-rise 0.9s cubic-bezier(.22,.61,.36,1) forwards;
      }}
      .home-hero .anim.d1 {{ animation-delay: 0.15s; }}
      .home-hero .anim.d2 {{ animation-delay: 0.45s; }}
      .home-hero .anim.d3 {{ animation-delay: 0.95s; }}
      .home-hero .anim.d4 {{ animation-delay: 1.20s; }}
      .home-hero .anim.d5 {{ animation-delay: 1.45s; }}
      .home-hero .anim.d6 {{ animation-delay: 1.85s; }}

      @keyframes hero-rise {{
        to {{ opacity: 1; transform: translateY(0); }}
      }}
      @keyframes divider-grow {{
        to {{ transform: scaleX(1); }}
      }}

      @media (prefers-reduced-motion: reduce) {{
        .home-hero .anim,
        .home-hero .home-divider {{
          animation: none;
          opacity: 1;
          transform: none;
        }}
      }}

      /* State-of-Israel emblem — fixed to the top-left, framed with a soft
         gold ring that echoes the .home-divider gradient. */
      .home-emblem {{
        position: fixed;
        top: 1.75rem;
        left: 1.75rem;
        z-index: 100;
        width: 96px;
        height: 96px;
        border-radius: 14px;
        overflow: hidden;
        background: #000336;
        box-shadow:
          0 10px 28px rgba(0, 0, 0, 0.45),
          0 0 0 2px rgba(255, 212, 121, 0.55),
          0 0 24px rgba(255, 212, 121, 0.20);
        animation: emblem-enter 1.1s cubic-bezier(.22,.61,.36,1) 0.25s both;
        transition: transform 0.25s ease, box-shadow 0.25s ease;
      }}
      .home-emblem:hover {{
        transform: translateY(-2px) scale(1.03);
        box-shadow:
          0 14px 34px rgba(0, 0, 0, 0.55),
          0 0 0 2px rgba(255, 212, 121, 0.85),
          0 0 32px rgba(255, 212, 121, 0.35);
      }}
      .home-emblem img {{
        width: 100%;
        height: 100%;
        object-fit: cover;
        display: block;
      }}
      @keyframes emblem-enter {{
        from {{ opacity: 0; transform: translateY(-18px) scale(0.82); }}
        to   {{ opacity: 1; transform: translateY(0) scale(1); }}
      }}
      @media (max-width: 700px) {{
        .home-emblem {{ width: 72px; height: 72px; top: 1rem; left: 1rem; }}
      }}
      @media (prefers-reduced-motion: reduce) {{
        .home-emblem {{ animation: none; }}
      }}
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    f"""
    <div class='home-emblem' title='מדינת ישראל'>
      <img src='data:image/jpeg;base64,{israel_img}' alt='סמל מדינת ישראל'/>
    </div>
    """,
    unsafe_allow_html=True,
)

replace_data_mode = st.session_state.get("replace_data_mode", False)
append_data_mode = st.session_state.get("append_data_mode", False)
compare_data_mode = st.session_state.get("compare_data_mode", False)

with st.sidebar:
    st.markdown(
        "<div class='sb-section'>פעולות על נתונים</div>",
        unsafe_allow_html=True,
    )

    if st.button("🔄 החלף קובץ נתונים", use_container_width=True):
        st.session_state["replace_data_mode"] = True
        st.session_state["append_data_mode"] = False
        st.session_state["compare_data_mode"] = False
        st.session_state.pop("uploaded_bytes", None)
        st.cache_data.clear()
        st.rerun()

    if st.button("➕ הוסף נתונים לקובץ הקיים", use_container_width=True):
        st.session_state["append_data_mode"] = True
        st.session_state["replace_data_mode"] = False
        st.session_state["compare_data_mode"] = False
        st.rerun()

    if st.button("📊 העלה קובץ להשוואה", use_container_width=True):
        st.session_state["compare_data_mode"] = True
        st.session_state["replace_data_mode"] = False
        st.session_state["append_data_mode"] = False
        st.rerun()

    if st.session_state.get("uploaded_bytes"):
        if st.button("↩️ חזרה לקובץ הנתונים המקורי", use_container_width=True):
            st.session_state.pop("uploaded_bytes", None)
            st.session_state["replace_data_mode"] = False
            st.session_state["append_data_mode"] = False
            st.session_state["compare_data_mode"] = False
            st.cache_data.clear()
            st.rerun()

    if st.session_state.get("comparison_bytes"):
        st.markdown(
            f"""
            <div class='sb-badge'>
              <span class='sb-badge__dot'></span>
              <span>השוואה פעילה: <b>{comparison_label()}</b></span>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("🗑️ הסר קובץ ההשוואה", use_container_width=True):
            clear_comparison()
            st.rerun()

if append_data_mode:
    st.info("➕ הוספת נתונים: הקובץ שתעלה יצורף לנתונים הקיימים ללא שינוי בקובץ המקורי.")
    appended = st.file_uploader(
        "העלאת קובץ אקסל חדש לצירוף (.xlsx)",
        type=["xlsx", "xls"],
        key="append_uploader",
    )
    if appended is not None:
        try:
            combined_bytes, new_rows, total_rows = append_excel_bytes(
                appended.getvalue(), default_path="data.xlsx"
            )
        except Exception as exc:
            st.error(f"שגיאה בצירוף הקובץ: {exc}")
            st.stop()
        st.session_state["uploaded_bytes"] = combined_bytes
        st.session_state["append_data_mode"] = False
        st.cache_data.clear()
        st.success(
            f"נוספו {new_rows} שורות חדשות. סה\"כ {total_rows} שורות בנתונים המאוחדים."
        )
        st.rerun()
    st.stop()

if compare_data_mode:
    st.info(
        "📊 קובץ להשוואה: הקובץ שתעלה יישמר בנפרד מהקובץ הראשי. "
        "עבור לעמוד '📈 השוואה בין שנים' כדי להשוות בין שני הקבצים."
    )
    c1, c2 = st.columns(2)
    with c1:
        main_lbl = st.text_input(
            "תווית הקובץ הראשי (למשל: 2025)",
            value=st.session_state.get("main_label", "2025"),
            key="main_label_input",
        )
    with c2:
        comp_lbl = st.text_input(
            "תווית הקובץ להשוואה (למשל: 2026)",
            value=st.session_state.get("comparison_label", "2026"),
            key="comp_label_input",
        )
    comparison_upload = st.file_uploader(
        "העלאת קובץ אקסל להשוואה (.xlsx)",
        type=["xlsx", "xls"],
        key="compare_uploader",
    )
    if comparison_upload is not None:
        try:
            n_rows = set_comparison_bytes(comparison_upload.getvalue(), label=comp_lbl)
            set_main_label(main_lbl)
        except Exception as exc:
            st.error(f"שגיאה בטעינת הקובץ להשוואה: {exc}")
            st.stop()
        st.session_state["compare_data_mode"] = False
        st.success(
            f"נטענו {n_rows} שורות לקובץ ההשוואה '{comp_lbl}'. "
            f"עבור לעמוד 📈 השוואה בין שנים לצפייה."
        )
        st.rerun()
    st.stop()

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

st.session_state["raw_data"] = df

st.markdown(
    """
    <div class='home-hero'>
      <h1 class='anim d1'>סקר מקבלי דוחות תעבורה</h1>
      <p class='home-subtitle anim d2'>סקר טרום-רפורמה של משרד המשפטים</p>
      <div class='home-divider'></div>
      <p class='home-meta anim d3'>אפריל 2026</p>
      <p class='home-meta anim d4'>שלומית כהן · וסים סעדי</p>
      <p class='home-meta anim d5'>תכנון מדיניות ואסטרטגיה, משרד המשפטים</p>
      <p class='home-hint anim d6'>👈 בחר עמוד מהתפריט הצדדי כדי להתחיל</p>
    </div>
    """,
    unsafe_allow_html=True,
)
