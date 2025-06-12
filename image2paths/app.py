import streamlit as st
import tempfile
import os
import matplotlib.pyplot as plt
from svgpathtools import svg2paths2, Path, Line, CubicBezier, QuadraticBezier
import xml.etree.ElementTree as ET
import math

# Constants
DEFAULT_SIZE = 100  # Default drawing area size in mm

# --- SVG処理関数 ---
def process_svg(svg_file, paper_width_mm, paper_height_mm, curve_division_length_mm, line_division_length_mm, output_filename="output_points.csv"):
    """
    SVGファイルを読み込み、ロボット用のCSVファイルに変換します。
    座標系は左下原点、上方向にプラスのY軸、右方向にプラスのX軸に設定されています。
    """
    # 一時ファイルに保存
    with tempfile.NamedTemporaryFile(delete=False, suffix='.svg') as tmp_svg:
        tmp_svg.write(svg_file.read())
        tmp_svg_path = tmp_svg.name

    try:
        tree = ET.parse(tmp_svg_path)
        root = tree.getroot()

        # viewBox属性の抽出
        viewbox = root.get('viewBox')
        if viewbox:
            viewbox_values = list(map(float, viewbox.strip().split()))
            svg_min_x, svg_min_y, svg_width, svg_height = viewbox_values
        else:
            svg_min_x = svg_min_y = 0.0
            svg_width = float(root.get('width', paper_width_mm))
            svg_height = float(root.get('height', paper_height_mm))

        # アスペクト比の計算
        svg_aspect_ratio = svg_width / svg_height
        paper_aspect_ratio = paper_width_mm / paper_height_mm

        # 90度回転の必要性判定
        needs_rotation = (svg_aspect_ratio < 1 and paper_aspect_ratio > 1) or (svg_aspect_ratio > 1 and paper_aspect_ratio < 1)

        # パスの抽出
        paths, attributes, svg_attr = svg2paths2(tmp_svg_path)

        # スケーリング係数の計算
        if needs_rotation:
            scale_x = paper_width_mm / svg_height
            scale_y = paper_height_mm / svg_width
        else:
            scale_x = paper_width_mm / svg_width
            scale_y = paper_height_mm / svg_height
        scale_factor = min(scale_x, scale_y)

        # オフセット計算（中心原点）
        if needs_rotation:
            offset_x = -svg_min_x * scale_factor - (paper_width_mm / 2)
            offset_y = -svg_min_y * scale_factor - (paper_height_mm / 2)
        else:
            offset_x = -svg_min_x * scale_factor - (paper_width_mm / 2)
            offset_y = -svg_min_y * scale_factor - (paper_height_mm / 2)

        all_subpaths = []
        for path in paths:
            subpaths = path.continuous_subpaths()
            for subpath in subpaths:
                points = []
                for segment in subpath:
                    if isinstance(segment, (Line, CubicBezier, QuadraticBezier)):
                        total_length = segment.length(error=1e-5)
                        if total_length == 0:
                            continue
                        scaled_length = total_length * scale_factor
                        division_length = line_division_length_mm if isinstance(segment, Line) else curve_division_length_mm
                        num_segments = max(int(math.ceil(scaled_length / division_length)), 1)
                        for i in range(num_segments):
                            t = i / num_segments
                            point = segment.point(t)
                            if needs_rotation:
                                x = point.imag * scale_factor + offset_x
                                y = point.real * scale_factor + offset_y
                            else:
                                x = point.real * scale_factor + offset_x
                                y = (svg_height - (point.imag - svg_min_y)) * scale_factor + offset_y
                            x = round(x * 10) / 10.0
                            y = round(y * 10) / 10.0
                            if not points or (x, y) != points[-1]:
                                points.append((x, y))
                        # 最終ポイントを追加
                        t = 1
                        point = segment.point(t)
                        if needs_rotation:
                            x = point.imag * scale_factor + offset_x
                            y = point.real * scale_factor + offset_y
                        else:
                            x = point.real * scale_factor + offset_x
                            y = (svg_height - (point.imag - svg_min_y)) * scale_factor + offset_y
                        x = round(x * 10) / 10.0
                        y = round(y * 10) / 10.0
                        if not points or (x, y) != points[-1]:
                            points.append((x, y))
                    else:
                        pass
                all_subpaths.append(points)

        # パスの処理
        final_subpaths = all_subpaths

        # Generate CSV content
        csv_content = ""
        for subpath in final_subpaths:
            point_strs = ['{},{}'.format(x, y) for x, y in subpath]
            line_str = ';'.join(point_strs)
            csv_content += line_str + '\n'

        with open(output_filename, 'w') as file:
            file.write(csv_content)

    finally:
        os.remove(tmp_svg_path)

    return final_subpaths, output_filename, needs_rotation

# --- プレビュー関数 ---
def preview_paths(coordinates, paper_width_mm, paper_height_mm, needs_rotation):
    """
    ロボット描画のプレビューを生成
    """
    fig, ax = plt.subplots(figsize=(8, 6))
    # Set limits to show centered coordinate system
    ax.set_xlim(-paper_width_mm/2, paper_width_mm/2)
    ax.set_ylim(-paper_height_mm/2, paper_height_mm/2)
    ax.set_aspect('equal')
    ax.set_xlabel('X (mm)', fontsize=10)
    ax.set_ylabel('Y (mm)', fontsize=10)
    ax.set_title('Drawing Preview', fontsize=12)
    ax.tick_params(axis='both', which='major', labelsize=8)
    ax.grid(True, linestyle='--', linewidth=0.5, alpha=0.7)

    # Add center point marker
    ax.plot(0, 0, 'r+', markersize=10, label='Center (0,0)')
    ax.legend()

    for subpath in coordinates:
        if len(subpath) > 1:
            x_vals = [point[0] for point in subpath]
            y_vals = [point[1] for point in subpath]
            ax.plot(x_vals, y_vals, linewidth=0.5, color='black')

    return fig

# --- Streamlitアプリのレイアウト ---
st.title("SVG to CSV Converter")
st.markdown("""
This application converts SVG files into robot-compatible drawing paths and provides a preview of the drawing.
""")

# ファイルアップロード・変換パラメータ
st.markdown("## File Uploader")
uploaded_svg = st.file_uploader("Upload an SVG file", type=["svg"])

st.markdown("## Drawing Area Settings")
# Drawing area size inputs (always visible, default 100mm)
paper_width_mm = st.number_input("Drawing Area Width (mm)", min_value=10.0, max_value=5000.0, value=100.0)
paper_height_mm = st.number_input("Drawing Area Height (mm)", min_value=10.0, max_value=5000.0, value=100.0)

curve_division_length_mm = st.number_input("Curve Division Length (mm)", min_value=0.1, max_value=1000.0, value=1.0)
line_division_length_mm = st.number_input("Line Division Length (mm)", min_value=0.1, max_value=1000.0, value=100.0)

# SVG変換とCSV生成
if uploaded_svg:
    st.subheader("Uploaded SVG File")
    st.write(f"Filename: {uploaded_svg.name}")
    if st.button("Convert SVG to CSV"):
        with st.spinner("Processing SVG..."):
            try:
                csv_filename = "points.csv"
                coordinates, csv_filename, needs_rotation = process_svg(
                    svg_file=uploaded_svg,
                    paper_width_mm=paper_width_mm,
                    paper_height_mm=paper_height_mm,
                    curve_division_length_mm=curve_division_length_mm,
                    line_division_length_mm=line_division_length_mm,
                    output_filename=csv_filename
                )
                
                # Update CSV file with final coordinates
                csv_content = ""
                for subpath in coordinates:
                    point_strs = ['{},{}'.format(x, y) for x, y in subpath]
                    line_str = ';'.join(point_strs)
                    csv_content += line_str + '\n'
                with open(csv_filename, 'w') as file:
                    file.write(csv_content)

                st.success("SVG successfully converted to CSV!")
                
                # Show preview
                st.subheader("Drawing Preview")
                fig = preview_paths(
                    coordinates=coordinates,
                    paper_width_mm=paper_width_mm,
                    paper_height_mm=paper_height_mm,
                    needs_rotation=needs_rotation
                )
                
                st.pyplot(fig)
                plt.close(fig)
                
                # Provide download link for CSV
                with open(csv_filename, 'r') as f:
                    csv_data = f.read()
                st.download_button(
                    label="Download CSV file",
                    data=csv_data,
                    file_name=csv_filename,
                    mime="text/csv"
                )
                
            except Exception as e:
                st.error(f"Error processing SVG: {e}")

st.markdown("""
---
*Developed with ❤️ by Team Ithaca*
""")
