# app.py

import streamlit as st
from vectorizer.io      import load_image
from vectorizer.extract import preprocess, image_to_polyline
from vectorizer.smooth  import chaikin_curve, simplify_paths
from vectorizer.normalize import normalize_polylines
from vectorizer.svg     import create_svg
from vectorizer.export  import to_csv, to_gcode
import re

st.title("Vectorizer")

# --- File Uploader ---
img_file = st.file_uploader("Upload Image", type=['png','jpg','jpeg','webp'])
if not img_file:
    st.stop()

# --- Parameters UI ---
st.sidebar.header("Vectorizer Settings")
blur_ksize    = st.sidebar.slider("Gaussian kernel", 1, 9, 3, step=2)
canny_low     = st.sidebar.slider("Canny low", 0, 255, 50)
canny_high    = st.sidebar.slider("Canny high",0,255,150)
chaikin_iters = st.sidebar.slider("Chaikin iterations", 0, 5, 2)
rdp_eps       = st.sidebar.slider("RDP epsilon", 0.0, 10.0, 1.5)

# --- Export Options ---
st.sidebar.header("Export Options")
formats = st.sidebar.multiselect("Formats", ['SVG','CSV','G-code'], default=['SVG'], key='export_formats')
paper_w = st.sidebar.number_input("Paper width (mm)", 50.0, 1000.0, 200.0, key="pw")
paper_h = st.sidebar.number_input("Paper height(mm)", 50.0, 1000.0, 200.0, key="ph")
origin  = st.sidebar.selectbox("Origin", ['top_left','center','bottom_left'], key="origin")
# キャプションで補足説明
st.sidebar.caption(
    "Preview and SVG always use top-left origin.\n"
    "Selected origin applies only to CSV and G-code exports."
)

# --- 1) Vectorizer: preprocessing → raw polylines ---
img   = load_image(img_file)
img_h, img_w = img.shape[:2]
# compute automatic scale to fit paper size
scale_mm_per_px = min(paper_w / img_w, paper_h / img_h)
# preprocess image to raw polyline
proc  = preprocess(img, blur_ksize, canny_low, canny_high)
raw   = image_to_polyline(proc)           # (row, col) 系

# --- 2) Smooth: Chaikin + RDP ---
smoothed = [chaikin_curve(pts, chaikin_iters) for pts in raw]
simplified = [simplify_paths(pts, rdp_eps) for pts in smoothed]

st.write(f"Paths extracted: {len(simplified)}")

# --- 3) SVG Preview (always Chaikin‑included) ---
polys_px = normalize_polylines(
    simplified,
    img.shape,
    scale=1.0,
    origin='top_left'
)
svg_str = create_svg(
    polylines = polys_px,
    width=img.shape[1],
    height=img.shape[0],
    stroke = 'black',
    stroke_width = 1
)

# remove width/height attrs just for preview
svg_str_preview = re.sub(
    r'\s(width|height)="[^"]+"',
    "",
    svg_str
    )

# ─── SVG PREVIEW (responsive) ───
# 1) CSS for SVG preview
st.markdown(
    """
    <style>
      .svg_preview_container {
        max-width: 80vw;      /* ビューポート幅の 80% まで */
        max-height: 80vh;     /* ビューポート高さの 80% まで */
        overflow: auto;       /* はみ出したらスクロール */
        border: 1px solid #eee;
        padding: 4px;
      }
      .svg_preview_container svg {
        width: 100%;   /* force-full width */
        height: auto; /* preserve aspect */
        display: block;
      }
    </style>
    """,
    unsafe_allow_html=True
)

# embed the SVG inline
st.markdown(
    f'<div class="svg_preview_container">{svg_str_preview}</div>',
    unsafe_allow_html=True
)

# 座標変換 

#SVG用
polys_svg_mm = normalize_polylines(
    simplified,
    img.shape,
    scale=scale_mm_per_px,
    origin='top_left'
)

#CSV/GCode用
polys_dev = normalize_polylines(
    simplified,
    img.shape,
    scale=scale_mm_per_px,
    origin=origin
)

# 選んだフォーマットごとにボタンを出す
if len(formats)==0:
    st.info("Sidebar から出力フォーマットを選んでください")
else:
    for fmt in formats:
        if fmt == 'SVG':
            svg_mm = create_svg(
                polys_svg_mm,
                width=f"{paper_w}mm",
                height=f"{paper_h}mm")
            st.download_button(
                "Download SVG",
                svg_str,
                file_name="output.svg",
                mime="image/svg+xml",
                key="btn_svg"
            )
        elif fmt == 'CSV':
            csv_text = to_csv(polys_dev)
            st.download_button(
                "Download CSV",
                csv_text,
                file_name="output.csv",
                mime="text/csv",
                key="btn_csv"
            )
        elif fmt == 'G-code':
            gcode_text = to_gcode(polys_dev)
            st.download_button(
                "Download G-code",
                gcode_text,
                file_name="output.gcode",
                mime="text/plain",
                key="btn_gcode"
            )
