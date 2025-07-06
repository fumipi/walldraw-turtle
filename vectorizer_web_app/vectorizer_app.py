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


def remove_duplicate_paths(paths, endpoint_tolerance=3.0, shape_similarity_threshold=0.8):
    """
    Remove duplicate or very similar paths based on endpoint distance and shape similarity.
    
    Args:
        paths: List of path coordinates
        endpoint_tolerance: Maximum distance between endpoints to consider paths similar (mm)
        shape_similarity_threshold: Threshold for shape similarity (0-1, higher = more similar)
    
    Returns:
        List of unique paths
    """
    if len(paths) <= 1:
        return paths
    
    def path_length(path):
        """Calculate total length of a path."""
        if len(path) < 2:
            return 0
        total = 0
        for i in range(len(path) - 1):
            total += math.hypot(path[i+1][0] - path[i][0], path[i+1][1] - path[i][1])
        return total
    
    def endpoint_distance(path1, path2):
        """Calculate minimum distance between endpoints of two paths."""
        if len(path1) < 1 or len(path2) < 1:
            return float('inf')
        
        start1, end1 = path1[0], path1[-1]
        start2, end2 = path2[0], path2[-1]
        
        # Check all combinations of endpoints
        distances = [
            math.hypot(start1[0] - start2[0], start1[1] - start2[1]),  # start-start
            math.hypot(start1[0] - end2[0], start1[1] - end2[1]),      # start-end
            math.hypot(end1[0] - start2[0], end1[1] - start2[1]),      # end-start
            math.hypot(end1[0] - end2[0], end1[1] - end2[1])           # end-end
        ]
        return min(distances)
    
    def shape_similarity(path1, path2):
        """Calculate shape similarity between two paths using normalized length and direction."""
        if len(path1) < 2 or len(path2) < 2:
            return 0
        
        # Calculate path lengths
        len1, len2 = path_length(path1), path_length(path2)
        if len1 == 0 or len2 == 0:
            return 0
        
        # Calculate overall direction vectors
        dir1 = (path1[-1][0] - path1[0][0], path1[-1][1] - path1[0][1])
        dir2 = (path2[-1][0] - path2[0][0], path2[-1][1] - path2[0][1])
        
        # Normalize direction vectors
        mag1 = math.hypot(dir1[0], dir1[1])
        mag2 = math.hypot(dir2[0], dir2[1])
        
        if mag1 == 0 or mag2 == 0:
            return 0
        
        dir1_norm = (dir1[0] / mag1, dir1[1] / mag1)
        dir2_norm = (dir2[0] / mag2, dir2[1] / mag2)
        
        # Calculate dot product for direction similarity
        dot_product = dir1_norm[0] * dir2_norm[0] + dir1_norm[1] * dir2_norm[1]
        direction_similarity = max(0, dot_product)  # Only positive similarity
        
        # Length similarity (shorter path should be at least 70% of longer path)
        length_ratio = min(len1, len2) / max(len1, len2)
        length_similarity = length_ratio if length_ratio > 0.7 else 0
        
        # Combined similarity (weighted average)
        return 0.6 * direction_similarity + 0.4 * length_similarity
    
    unique_paths = []
    
    for path in paths:
        is_duplicate = False
        
        for existing_path in unique_paths:
            # Check endpoint distance first (faster)
            if endpoint_distance(path, existing_path) <= endpoint_tolerance:
                # If endpoints are close, check shape similarity
                similarity = shape_similarity(path, existing_path)
                if similarity >= shape_similarity_threshold:
                    is_duplicate = True
                    break
        
        if not is_duplicate:
            unique_paths.append(path)
    
    return unique_paths


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
def process_svg(svg_file, paper_w, paper_h):
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
        off_x = -min_x*scale - (svg_w*scale)/2
        off_y = -min_y*scale - (svg_h*scale)/2
        subpaths = []
        for path in paths:
            for sub in path.continuous_subpaths():
                pts = []
                for seg in sub:
                    length = seg.length(error=1e-5)
                    if length<=0: continue
                    # Use a reasonable number of points for curves, fewer for lines
                    n = max(int(math.ceil((length*scale)/2.0)), 2) if not isinstance(seg, Line) else 2
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
st.title("Vectorizer & CSV Converter for Turtle Plotter")
method = st.sidebar.selectbox("Choose Input Method:", ["Upload SVG","Edge Detection","Centerline Extraction"])
st.sidebar.markdown("### Paper size (mm)")
paper_w = st.sidebar.number_input("Width",10.0,5000.0,100.0)
paper_h = st.sidebar.number_input("Height",10.0,5000.0,100.0)

# common simplification control
epsilon = st.sidebar.slider("Simplify tolerance (mm)",0.0,10.0,0.3,0.1)

# duplicate removal controls (for image processing methods)
if method in ["Edge Detection", "Centerline Extraction"]:
    st.sidebar.markdown("### Duplicate Removal")
    endpoint_tolerance = st.sidebar.slider("Endpoint tolerance (mm)", 0.5, 10.0, 3.0, 0.5,
                                         help="Maximum distance between endpoints to consider paths similar")
    shape_similarity_threshold = st.sidebar.slider("Shape similarity threshold", 0.5, 1.0, 0.8, 0.05,
                                                 help="Threshold for shape similarity (higher = more strict)")

if method=="Upload SVG":
    st.header("SVG to CSV")
    svg_file = st.file_uploader("Upload SVG",type=["svg"])
    if svg_file and st.button("Run"):
        raw = process_svg(svg_file,paper_w,paper_h)
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
            k = st.sidebar.slider("Blur strength",1,31,3,2,
                                help="Higher values reduce noise but may lose fine details")
            t1 = st.sidebar.slider("Weak edge threshold",0,255,100,
                                 help="Lower values detect more edges but may include noise")
            t2 = st.sidebar.slider("Strong edge threshold",0,255,200,
                                 help="Higher values only detect very clear edges")
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
            # Display inverted mask for better visibility (processing still uses original)
            display_mask = cv2.bitwise_not(proc)
            st.image(display_mask,width=300)
        if st.button("Generate CSV"):
            cnts,_ = cv2.findContours(proc,cv2.RETR_LIST,cv2.CHAIN_APPROX_NONE)
            h,w=proc.shape;scale=min(paper_w/w,paper_h/h)
            paths=[]
            for c in cnts:
                pts=c.squeeze()
                if pts.ndim!=2: continue
                paths.append([(round(p[0]*scale-(w*scale)/2,1),round((h-p[1])*scale-(h*scale)/2,1)) for p in pts])
            
            # Show original path count
            st.info(f"Found {len(paths)} original paths")
            
            # Remove duplicates
            unique_paths = remove_duplicate_paths(paths, endpoint_tolerance, shape_similarity_threshold)
            st.info(f"After duplicate removal: {len(unique_paths)} unique paths")
            
            # Simplify paths
            simp=[rdp(sp,epsilon) for sp in unique_paths]
            ordered=sort_coordinates(simp)
            
            st.subheader("Preview of Simplified & Sorted Paths")
            fig2=preview_paths(ordered,paper_w,paper_h)
            st.pyplot(fig2,use_container_width=True)
            csv2="\n".join([";".join(f"{x},{y}" for x,y in sp) for sp in ordered])
            st.download_button("Download CSV",data=csv2,file_name="points.csv",mime="text/csv")

st.markdown("---")
st.markdown("*Made with ❤️ by Craft Robot Workshop*")