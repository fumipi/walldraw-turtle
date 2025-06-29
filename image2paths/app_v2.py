import streamlit as st
import tempfile
import os
import io
import math
import numpy as np
import cv2
from skimage.morphology import skeletonize
import matplotlib.pyplot as plt
from svgpathtools import svg2paths2, Path, Line, CubicBezier, QuadraticBezier
import xml.etree.ElementTree as ET

# Constants
DEFAULT_SIZE = 100  # Default drawing area size in mm

# --- SVG to coordinate conversion (existing) ---
def process_svg(svg_file, paper_width_mm, paper_height_mm,
                curve_division_length_mm, line_division_length_mm,
                output_filename="output_points.csv"):
    with tempfile.NamedTemporaryFile(delete=False, suffix='.svg') as tmp_svg:
        tmp_svg.write(svg_file.read())
        tmp_svg_path = tmp_svg.name

    try:
        tree = ET.parse(tmp_svg_path)
        root = tree.getroot()
        viewbox = root.get('viewBox')
        if viewbox:
            vals = list(map(float, viewbox.strip().split()))
            min_x, min_y, svg_w, svg_h = vals
        else:
            min_x = min_y = 0.0
            svg_w = float(root.get('width', paper_width_mm))
            svg_h = float(root.get('height', paper_height_mm))

        paths, attributes, svg_attr = svg2paths2(tmp_svg_path)

        svg_ratio = svg_w / svg_h
        paper_ratio = paper_width_mm / paper_height_mm
        needs_rotation = (svg_ratio < 1 and paper_ratio > 1) or (svg_ratio > 1 and paper_ratio < 1)
        if needs_rotation:
            scale_x = paper_width_mm / svg_h
            scale_y = paper_height_mm / svg_w
        else:
            scale_x = paper_width_mm / svg_w
            scale_y = paper_height_mm / svg_h
        scale = min(scale_x, scale_y)
        offset_x = -min_x * scale - paper_width_mm / 2
        offset_y = -min_y * scale - paper_height_mm / 2

        all_subpaths = []
        for path in paths:
            for sub in path.continuous_subpaths():
                pts = []
                for seg in sub:
                    length = seg.length(error=1e-5)
                    if length == 0:
                        continue
                    div_len = line_division_length_mm if isinstance(seg, Line) else curve_division_length_mm
                    n = max(int(math.ceil((length * scale) / div_len)), 1)
                    for i in range(n+1):
                        t = i / n
                        p = seg.point(t)
                        if needs_rotation:
                            x = p.imag * scale + offset_x
                            y = p.real * scale + offset_y
                        else:
                            x = p.real * scale + offset_x
                            y = (svg_h - (p.imag - min_y)) * scale + offset_y
                        pts.append((round(x, 1), round(y, 1)))
                if pts:
                    all_subpaths.append(pts)

        return all_subpaths, output_filename, needs_rotation
    finally:
        os.remove(tmp_svg_path)

# --- Utility: sort coordinate subpaths for minimal travel ---
def sort_coordinates(subpaths):
    sorted_list = []
    cur = (0.0, 0.0)
    remaining = subpaths.copy()
    while remaining:
        dists = [math.hypot(sp[0][0] - cur[0], sp[0][1] - cur[1]) for sp in remaining]
        idx = dists.index(min(dists))
        chosen = remaining.pop(idx)
        sorted_list.append(chosen)
        cur = chosen[-1]
    return sorted_list

# --- Preview ---
def preview_paths(coordinates, paper_width_mm, paper_height_mm):
    fig, ax = plt.subplots(figsize=(5, 5))
    ax.set_xlim(-paper_width_mm / 2, paper_width_mm / 2)
    ax.set_ylim(-paper_height_mm / 2, paper_height_mm / 2)
    ax.set_aspect('equal')
    ax.grid(True, linestyle='--', alpha=0.5)
    for sp in coordinates:
        xs = [p[0] for p in sp]
        ys = [p[1] for p in sp]
        ax.plot(xs, ys, linewidth=0.1, color='black')
    return fig

# --- Streamlit App ---
st.set_page_config(page_title="Vectorize & Plot", layout="wide")
st.title("Pen Plotter Vectorizer & CSV Converter")

# Sidebar: method selection
method = st.sidebar.selectbox(
    "Select Input Method:", ["Upload SVG", "Edge Detection", "Centerline Extraction"],
)

# Common drawing area inputs
st.sidebar.markdown("### Drawing Area Settings (mm)")
paper_w = st.sidebar.number_input("Width", min_value=10.0, max_value=5000.0, value=100.0)
paper_h = st.sidebar.number_input("Height", min_value=10.0, max_value=5000.0, value=100.0)

if method == "Upload SVG":
    st.header("SVG to CSV Conversion")
    svg_file = st.file_uploader("Upload an SVG file", type=["svg"])
    curve_div = st.sidebar.number_input("Curve Division Length", min_value=0.1, max_value=1000.0, value=3.0)
    line_div = st.sidebar.number_input("Line Division Length", min_value=0.1, max_value=1000.0, value=100.0)
    if svg_file and st.button("Convert SVG to CSV"):
        coords, _, rot = process_svg(svg_file, paper_w, paper_h, curve_div, line_div)
        sorted_coords = sort_coordinates(coords)
        st.subheader("Preview of Sorted Paths")
        fig = preview_paths(sorted_coords, paper_w, paper_h)
        st.pyplot(fig, use_container_width=True)
        csv = "\n".join([
            ";".join(f"{x},{y}" for x, y in sp) for sp in sorted_coords
        ])
        st.download_button("Download CSV", data=csv, file_name="points.csv", mime="text/csv")

else:
    st.header(f"{method} Vectorization")
    img_file = st.file_uploader("Upload Image", type=["png", "jpg", "jpeg"])

    if img_file:
        # Read image
        file_bytes = np.frombuffer(img_file.read(), np.uint8)
        img = cv2.imdecode(file_bytes, cv2.IMREAD_GRAYSCALE)

        # Parameters
        if method == "Edge Detection":
            t1 = st.sidebar.slider("Canny Threshold1", 0, 255, 100)
            t2 = st.sidebar.slider("Canny Threshold2", 0, 255, 200)
                # <-- new blur step
            blur_ksize = st.sidebar.slider("Gaussian Blur Kernel (odd)", 1, 31, 3, step=2)
            blurred = cv2.GaussianBlur(img, (blur_ksize, blur_ksize), 0)
            processed = cv2.Canny(blurred, t1, t2)

        else:
            thr = st.sidebar.slider("Binarization Threshold", 0, 255, 225)
            _, bin_img = cv2.threshold(img, thr, 255, cv2.THRESH_BINARY_INV)
            skeleton = skeletonize(bin_img / 255)
            processed = (skeleton.astype(np.uint8) * 255)

        # Side-by-side original & mask previews
        col_orig, col_proc = st.columns(2)
        with col_orig:
            st.subheader("Original Image")
            st.image(img, width=300)
        with col_proc:
            st.subheader("Processed Mask")
            st.image(processed, width=300)

        if st.button("Generate Paths & CSV"):
            with st.spinner("Tracing contours and sorting..."):
                cnts, _ = cv2.findContours(processed, cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)
                h, w = processed.shape
                scale_x = paper_w / w
                scale_y = paper_h / h
                scale = min(scale_x, scale_y)
                all_paths = []
                for cnt in cnts:
                    pts = cnt.squeeze()
                    if pts.ndim != 2:
                        continue
                    path_mm = [
                        (
                            round(pt[0] * scale - paper_w / 2, 1),
                            round((h - pt[1]) * scale - paper_h / 2, 1),
                        )
                        for pt in pts
                    ]
                    all_paths.append(path_mm)
                sorted_paths = sort_coordinates(all_paths)

            # Display only CSV preview
            st.subheader("Preview of Sorted Paths")
            fig2 = preview_paths(sorted_paths, paper_w, paper_h)
            st.pyplot(fig2, use_container_width=True)

            # CSV download
            csv2 = "\n".join([
                ";".join(f"{x},{y}" for x, y in sp) for sp in sorted_paths
            ])
            st.download_button("Download CSV", data=csv2, file_name="points.csv", mime="text/csv")

# Footer
st.markdown("---")
st.markdown("*Developed with ❤️ by Team Ithaca*")