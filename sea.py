import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import os
import json
import base64
import glob
import re

# ==========================================
# CONFIG
# ==========================================
USE_NOTEBOOK      = True
MARKER_KEYWORDS   = ("cost of india", "marine food estimate", "cost")
NOTEBOOK          = "Seadb.ipynb"
BG_IMAGE          = "sea bg.jpg"

# ==========================================
# 1. PAGE SETUP
# ==========================================
st.set_page_config(
    page_title="Marine Quest: Catch & Climate 2007-2012",
    layout="wide",
    page_icon="🐟",
)
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .block-container {padding: 0rem;}
    iframe {border: none; width: 100%; height: 100vh;}
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. BACKGROUND
# ==========================================
bg_base64 = ""
if os.path.exists(BG_IMAGE):
    with open(BG_IMAGE, "rb") as f:
        bg_base64 = base64.b64encode(f.read()).decode()

# ==========================================
# 3. REPLAY NOTEBOOK IN ORDER
# ==========================================
def build_ordered_page(nb_path, bg_b64):
    if not os.path.exists(nb_path):
        return "<h2 style='color:#f59e0b; text-align:center; margin-top:50px;'>⚠️ Seadb.ipynb not found. Please make sure it is in the same folder.</h2>"

    with open(nb_path, "r", encoding="utf-8") as f:
        nb = json.load(f)

    ordered_html = ""
    codex_injected = False

    for cell in nb.get("cells", []):
        # Get cell source text
        src = cell.get("source", "")
        if isinstance(src, list):
            src = "".join(src)
        src_lower = src.lower()

        # Check if this is the cell we want to replace with the Codex
        is_marker_cell = (
            cell.get("cell_type") == "code"
            and any(kw in src_lower for kw in MARKER_KEYWORDS)
            and ("html" in src_lower or "display" in src_lower)
        )

        if is_marker_cell:
            codex_injected = True
            # The notebook cell already contains our HTML output,
            # so we just process its outputs normally below.
            pass

        # Loop through the HTML outputs of this cell
        for output in cell.get("outputs", []):
            if "data" in output and "text/html" in output["data"]:
                raw = output["data"]["text/html"]
                if isinstance(raw, list):
                    raw = "".join(raw)
                
                # Inject the background image if Jupyter stripped it
                if bg_b64:
                    raw = raw.replace("data:image/jpeg;base64,", f"data:image/jpeg;base64,{bg_b64}")
                
                ordered_html += raw

    return ordered_html

# ==========================================
# 4. ASSEMBLE FULL HTML PAGE
# ==========================================
body_html = build_ordered_page(NOTEBOOK, bg_base64)

# Wrap everything in a clean HTML shell with Plotly loaded
full_html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <!-- Load Plotly to render the interactive year-wise graphs! -->
    <script src="https://cdn.plot.ly/plotly-2.27.0.min.js"></script>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Press+Start+2P&display=swap');
        body {{
            margin: 0; padding: 0;
            background-image: url('data:image/jpeg;base64,{bg_base64}');
            background-size: cover; background-attachment: fixed;
            font-family: 'Press Start 2P', cursive;
        }}
        #wrapper {{ padding: 20px; }}
    </style>
</head>
<body>
    <div id="wrapper">
        {body_html}
    </div>
</body>
</html>
"""

# ==========================================
# 5. RENDER
# ==========================================
try:
    # Streamlit >= 1.37 (newer versions dropped the 'scrolling' arg)
    st.iframe(full_html, height=5000)
except AttributeError:
    # Streamlit < 1.37
    components.html(full_html, height=5000, scrolling=True)