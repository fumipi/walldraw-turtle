import streamlit as st
import tempfile
import os
import math
import numpy as np
import cv2
from skimage.morphology import skeletonize
import matplotlib.pyplot as plt
from svgpathtools import svg2paths2, Line
import xml.etree.ElementTree as ET

# --- Utility functions ---

def rdp(points, epsilon):
    """Ramer-Douglas-Peucker path simplification."""
    if len(points) < 3:
        return points
    # find farthest point
    first, last = points[0], points[-1]
    def perp_dist(pt, a, b):
        # distance from pt to line a-b
        num = abs((b[1] - a[1]) * pt[0] - (b[0] - a[0]) * pt[1] + b[0]*a[1] - b[1]*a[0])
        den = math.hypot(b[1] - a[1], b[0] - a[0])
        return num / den if den != 0 else 0
    max_dist, idx = 0.0, 0
    for i in range(1, len(points)-1):
        d = perp_dist(points[i], first, last)
        if d > max_dist:
            max_dist, idx = d, i
    if max_dist > epsilon:
        left = rdp(points[:idx+1], epsilon)
        right = rdp(points[idx:], epsilon)
        return left[:-1] + right
    else:
        return [first, last]


def sort_coordinates(subpaths):
    sorted_list = []
    cur = (0.0, 0.0)
    remaining = subpaths.copy()
    while remaining:
        dists = [math.hypot(sp[0][0]-cur[0], sp[0][1]-cur[1]) for sp in remaining]
        idx = dists.index(min(dists))
        chosen = remaining.pop(idx)
        sorted_list.append(chosen)
        cur = chosen[-1]
    return sorted_list


def preview_paths(coordinates, paper_w, paper_h):
    fig, ax = plt.subplots(figsize=(4,4))
    ax.set_xlim(-paper_w/2, paper_w/2)
    ax.set_ylim(-paper_h/2, paper_h/2)
    ax.set_aspect('equal')
    ax.grid(True, linestyle='--', alpha=0.5)
    for sp in coordinates:
        xs, ys = zip(*sp)
        ax.plot(xs, ys, linewidth=0.7, color='black')
    return fig


# --- SVG processing ---
def process_svg(svg_file, paper_w, paper_h, curve_div, line_div):
    # save to temp
    with tempfile.NamedTemporaryFile(delete=False, suffix='.svg') as tmp:
        tmp.write(svg_file.read())
        tmp_path = tmp.name
    try:
        tree = ET.parse(tmp_path)
        root = tree.getroot()
        vb = root.get('viewBox')
        if vb:
            min_x, min_y, svg_w, svg_h = map(float, vb.split())
        else:
            min_x = min_y = 0.0
            svg_w = float(root.get('width', paper_w))
            svg_h = float(root.get('height', paper_h))
        paths, _, _ = svg2paths2(tmp_path)
        ratio_svg = svg_w/svg_h
        ratio_p = paper_w/paper_h
        needs_rot = (ratio_svg<1 and ratio_p>1) or (ratio_svg>1 and ratio_p<1)
        scale = min(paper_w/(svg_h if needs_rot else svg_w), paper_h/(svg_w if needs_rot else svg_h))
        off_x = -min_x*scale - paper_w/2
        off_y = -min_y*scale - paper_h/2
        subpaths = []
        for path in paths:
            for sub in path.continuous_subpaths():
                pts = []
                for seg in sub:
                    length = seg.length(error=1e-5)
                    if length<=0: continue
                    div = line_div if isinstance(seg, Line) else curve_div
                    n = max(int(math.ceil((length*scale)/div)),1)
                    for i in range(n+1):
                        p = seg.point(i/n)
                        if needs_rot:
                            x = p.imag*scale + off_x
                            y = p.real*scale + off_y
                        else:
                            x = p.real*scale + off_x
                            y = (svg_h - p.imag)*scale + off_y
                        pts.append((round(x,1),round(y,1)))
                if pts: subpaths.append(pts)
        return subpaths
    finally:
        os.remove(tmp_path)

# --- Streamlit UI ---
st.set_page_config(page_title="Vectorizer", layout="wide")
st.title("Pen Plotter Vectorizer & CSV Converter")
method = st.sidebar.selectbox("Input Method:", ["Upload SVG","Edge Detection","Centerline Extraction"])
st.sidebar.markdown("### Paper size (mm)")
paper_w = st.sidebar.number_input("Width",10.0,5000.0,100.0)
paper_h = st.sidebar.number_input("Height",10.0,5000.0,100.0)

# common simplification control
epsilon = st.sidebar.slider("Simplify tolerance (mm)",0.0,10.0,1.0,0.1)

if method=="Upload SVG":
    st.header("SVG to CSV")
    svg_file = st.file_uploader("Upload SVG",type=["svg"])
    curve_div = st.sidebar.number_input("Curve div (mm)",0.1,1000.0,3.0)
    line_div = st.sidebar.number_input("Line div (mm)",0.1,1000.0,100.0)
    if svg_file and st.button("Run"):
        raw = process_svg(svg_file,paper_w,paper_h,curve_div,line_div)
        simp = [rdp(sp,epsilon) for sp in raw]
        ordered = sort_coordinates(simp)
        st.subheader("Preview of Simplified & Sorted Paths")
        fig = preview_paths(ordered,paper_w,paper_h)
        st.pyplot(fig,use_container_width=True)
        csv = "\n".join([";".join(f"{x},{y}" for x,y in sp) for sp in ordered])
        st.download_button("Download CSV",data=csv,file_name="points.csv",mime="text/csv")

else:
    st.header(f"{method}")
    img_file = st.file_uploader("Upload Image",type=["png","jpg","jpeg"])
    if img_file:
        arr = np.frombuffer(img_file.read(),np.uint8)
        gray = cv2.imdecode(arr,cv2.IMREAD_GRAYSCALE)
        if method=="Edge Detection":
            k = st.sidebar.slider("Blur ksize (odd)",1,31,3,2)
            t1 = st.sidebar.slider("Canny Th1",0,255,100)
            t2 = st.sidebar.slider("Canny Th2",0,255,200)
            proc = cv2.Canny(cv2.GaussianBlur(gray,(k,k),0),t1,t2)
        else:
            thr = st.sidebar.slider("Binarize Th",0,255,128)
            _,b = cv2.threshold(gray,thr,255,cv2.THRESH_BINARY_INV)
            proc = (skeletonize(b/255).astype(np.uint8)*255)
        col1,col2 = st.columns(2)
        with col1:
            st.subheader("Original")
            st.image(gray,width=300)
        with col2:
            st.subheader("Mask")
            st.image(proc,width=300)
        if st.button("Generate CSV"):
            cnts,_ = cv2.findContours(proc,cv2.RETR_LIST,cv2.CHAIN_APPROX_NONE)
            h,w=proc.shape;scale=min(paper_w/w,paper_h/h)
            paths=[]
            for c in cnts:
                pts=c.squeeze()
                if pts.ndim!=2: continue
                paths.append([(round(p[0]*scale-paper_w/2,1),round((h-p[1])*scale-paper_h/2,1)) for p in pts])
            simp=[rdp(sp,epsilon) for sp in paths]
            ordered=sort_coordinates(simp)
            st.subheader("Preview of Simplified & Sorted Paths")
            fig2=preview_paths(ordered,paper_w,paper_h)
            st.pyplot(fig2,use_container_width=True)
            csv2="\n".join([";".join(f"{x},{y}" for x,y in sp) for sp in ordered])
            st.download_button("Download CSV",data=csv2,file_name="points.csv",mime="text/csv")

st.markdown("---")
st.markdown("*Made with ❤️ by Team Ithaca*")