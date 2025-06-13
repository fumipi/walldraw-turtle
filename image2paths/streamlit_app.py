import streamlit as st
import requests
import tempfile
import os
import matplotlib.pyplot as plt
from svgpathtools import svg2paths2, Path, Line, CubicBezier, QuadraticBezier
import xml.etree.ElementTree as ET
import math
import numpy as np
import warnings
import time
import json
from datetime import datetime

# Constants
MARGIN_MM = 50 # 50mm safety margin

# セッション状態の初期化
if 'csv_content' not in st.session_state:
    st.session_state.csv_content = None
if 'csv_filename' not in st.session_state:
    st.session_state.csv_filename = None
if 'robot_connected' not in st.session_state:
    st.session_state.robot_connected = False
if 'position_tracking' not in st.session_state:
    st.session_state.position_tracking = False
if 'drawing_active' not in st.session_state:
    st.session_state.drawing_active = False
if 'last_update_time' not in st.session_state:
    st.session_state.last_update_time = time.time()
if 'position_history' not in st.session_state:
    st.session_state.position_history = []

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

        # オフセット計算（左下原点）
        offset_x = -svg_min_x * scale_factor
        offset_y = 0

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

        # パスの処理（path_sortingの部分を削除）
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
    ax.set_xlim(0, paper_width_mm)
    ax.set_ylim(0, paper_height_mm)
    ax.set_aspect('equal')
    ax.set_xlabel('X (mm)', fontsize=10)
    ax.set_ylabel('Y (mm)', fontsize=10)
    ax.set_title('Robot Drawing Preview', fontsize=12)
    ax.tick_params(axis='both', which='major', labelsize=8)
    ax.grid(True, linestyle='--', linewidth=0.5, alpha=0.7)

    for subpath in coordinates:
        if len(subpath) > 1:
            x_vals = [point[0] for point in subpath]
            y_vals = [point[1] for point in subpath]
            ax.plot(x_vals, y_vals, linewidth=0.5, color='black')

    return fig

def get_robot_position():
    """カメラAPIからロボットの位置情報を取得"""
    try:
        response = requests.get('http://192.168.43.119:8000/position', timeout=1)
        if response.ok:
            return response.json()
    except Exception as e:
        pass
    return None

def add_position_to_preview(fig, position_data, external_position_enabled=False):
    """プレビューにロボットの位置と向きを追加"""
    ax = fig.gca()
    
    # Draw the position history trace
    if st.session_state.position_history:
        x_history = [pos['x'] for pos in st.session_state.position_history]
        y_history = [pos['y'] for pos in st.session_state.position_history]
        ax.plot(x_history, y_history, '-', color='red', alpha=0.5, linewidth=1, label='Robot Path')

    # Draw current position
    if position_data and 'x' in position_data and 'y' in position_data:
        color = 'red' if external_position_enabled else 'gray'
        ax.plot(position_data['x'], position_data['y'], 'o', color=color, markersize=8)
        if 'angle' in position_data:
            angle_rad = math.radians(position_data['angle'])
            arrow_length = 20  # mm
            dx = arrow_length * math.cos(angle_rad)
            dy = arrow_length * math.sin(angle_rad)
            ax.arrow(position_data['x'], position_data['y'], dx, dy,
                     head_width=5, head_length=10, fc=color, ec=color, alpha=0.7)
        
        # Add current position to history
        st.session_state.position_history.append({
            'x': position_data['x'],
            'y': position_data['y'],
            'timestamp': datetime.now()
        })
        
        # Optionally, limit history length to prevent memory issues (e.g., keep last 2000 points)
        if len(st.session_state.position_history) > 2000:
            st.session_state.position_history = st.session_state.position_history[-2000:]

        info_text = f"Position: ({position_data['x']:.1f}, {position_data['y']:.1f})"
        if 'angle' in position_data:
            info_text += f"\nAngle: {position_data['angle']:.1f}°"
        if 'detected_points' in position_data:
            info_text += f"\nDetected Points: {position_data['detected_points']}"
    else:
        info_text = "Position: not available"
    info_text += f"\nExternal Position: {'Enabled' if external_position_enabled else 'Disabled'}"
    ax.text(0.02, 0.98, info_text, transform=ax.transAxes, verticalalignment='top', fontsize=8)

# --- Streamlitアプリのレイアウト ---
st.title("🚗✏️__ Drawing Robot Controller")
st.markdown("""
This application controls a drawing robot that can reproduce SVG images. You can:
- Convert SVG files into robot-compatible drawing paths
- Preview the drawing before execution
- Control the robot's drawing operations
- Enable external position tracking for precise drawing
""")

# ファイルアップロード・変換パラメータ
st.markdown("## File Uploader")
uploaded_svg = st.file_uploader("Upload an SVG file", type=["svg"])

st.markdown("## Conversion Parameters")
paper_sizes = {
    "Custom (1050x 750 mm)": (1050, 750),
    "A0 (1189 x 841 mm)": (1189, 841),
    "A1 (841 x 594 mm)": (841, 594),
    "A2 (594 x 420 mm)": (594, 420),
    "A3 (420 x 297 mm)": (420, 297),
    "A4 (297 x 210 mm)": (297, 210),
    "Custom": (None, None)
}
paper_size_option = st.selectbox("Select Paper Size", list(paper_sizes.keys()))
if paper_size_option != "Custom":
    paper_width_mm, paper_height_mm = paper_sizes[paper_size_option]
else:
    paper_width_mm = st.number_input("Paper Width (mm, long edge)", min_value=10.0, max_value=5000.0, value=594.0)
    paper_height_mm = st.number_input("Paper Height (mm, short edge)", min_value=10.0, max_value=5000.0, value=420.0)

col1, col2 = st.columns(2)
with col1:
    use_margin = st.checkbox("Add safety margin(50mm)", value=True)

curve_division_length_mm = st.number_input("Curve Division Length (mm)", min_value=0.1, max_value=1000.0, value=10.0)
line_division_length_mm = st.number_input("Line Division Length (mm)", min_value=0.1, max_value=1000.0, value=100.0)

# SVG変換とCSV生成
if uploaded_svg:
    st.subheader("Uploaded SVG File")
    st.write(f"Filename: {uploaded_svg.name}")
    if st.button("Convert SVG to CSV"):
        with st.spinner("Processing SVG..."):
            try:
                csv_filename = "points.csv"
                effective_width = paper_width_mm - (2 * MARGIN_MM) if use_margin else paper_width_mm
                effective_height = paper_height_mm - (2 * MARGIN_MM) if use_margin else paper_height_mm
                coordinates, csv_filename, needs_rotation = process_svg(
                    svg_file=uploaded_svg,
                    paper_width_mm=effective_width,
                    paper_height_mm=effective_height,
                    curve_division_length_mm=curve_division_length_mm,
                    line_division_length_mm=line_division_length_mm,
                    output_filename=csv_filename
                )

                if use_margin:
                    # Apply margin to coordinates
                    coordinates = [[(x + MARGIN_MM, y + MARGIN_MM) for x, y in subpath] for subpath in coordinates]
                
                # Update CSV file with final coordinates
                csv_content = ""
                for subpath in coordinates:
                    point_strs = ['{},{}'.format(x, y) for x, y in subpath]
                    line_str = ';'.join(point_strs)
                    csv_content += line_str + '\n'
                with open(csv_filename, 'w') as file:
                    file.write(csv_content)

                st.session_state.csv_content = coordinates
                st.session_state.csv_filename = csv_filename
                st.session_state.needs_rotation = needs_rotation
                st.success("SVG successfully converted to CSV!")
            except Exception as e:
                st.error(f"Error processing SVG: {e}")

# --- プレビュー部分 ---
if st.session_state.csv_content:
    st.subheader("Robot Drawing Preview")
    preview_placeholder = st.empty()
    
    # 初回描画とその後の更新のための関数
    def update_preview():
        position_data = get_robot_position() if (st.session_state.robot_connected or st.session_state.drawing_active) else None
        
        fig = preview_paths(
            coordinates=st.session_state.csv_content,
            paper_width_mm=paper_width_mm,
            paper_height_mm=paper_height_mm,
            needs_rotation=getattr(st.session_state, 'needs_rotation', False)
        )
        
        if use_margin:
            ax = plt.gca()
            margin_rect = plt.Rectangle((0, 0), paper_width_mm, paper_height_mm, facecolor='lightgray', alpha=0.3)
            safe_rect = plt.Rectangle((MARGIN_MM, MARGIN_MM), paper_width_mm - 2 * MARGIN_MM, paper_height_mm - 2 * MARGIN_MM, facecolor='white')
            ax.add_patch(margin_rect)
            ax.add_patch(safe_rect)
            
        if position_data:
            add_position_to_preview(
                fig,
                position_data,
                external_position_enabled=st.session_state.position_tracking
            )
            
        # プレビューを更新
        preview_placeholder.pyplot(fig)
        plt.close(fig)
    
    # 初回描画
    update_preview()

# --- 制御パネル ---
st.markdown("---")
st.markdown("## Robot Control Panel")
st.markdown("### Connection Settings")
robot_address = st.text_input(
    "Robot Hostname or IP",
    value="192.168.43.120",
    help="使用するホスト名（例: picotaro.local）またはIPアドレスを入力してください。"
)

if st.button("Connect to Robot"):
    try:
        response = requests.post(f"http://{robot_address}/upload", data="", timeout=5)
        if response.ok:
            st.session_state.robot_connected = True
            st.success(f"Successfully connected to robot at {robot_address}")
            if st.session_state.csv_content:  # プレビューが存在する場合のみ更新
                update_preview()
        else:
            st.session_state.robot_connected = False
            st.error(f"Failed to connect to robot (Status: {response.status_code})")
    except Exception as e:
        st.session_state.robot_connected = False
        st.error(f"Error connecting to robot: {e}")

st.markdown("### Drawing Controls")
if st.session_state.robot_connected:
    upload_url = f"http://{robot_address}/upload"
    start_url = f"http://{robot_address}/start"
    stop_url = f"http://{robot_address}/stop"
    abs_on_url = f"http://{robot_address}/abs_on"
    abs_off_url = f"http://{robot_address}/abs_off"

    if st.session_state.csv_content:
        if st.button("Upload Drawing Data"):
            try:
                with open(st.session_state.csv_filename, 'r') as f:
                    csv_data = f.read()
                max_retries = 3
                retry_delay = 1
                for attempt in range(max_retries):
                    try:
                        headers = {'Content-Type': 'text/csv', 'Connection': 'close'}
                        response = requests.post(upload_url, data=csv_data, headers=headers, timeout=10)
                        if response.ok:
                            st.success("Drawing data successfully uploaded to the robot!")
                            break
                        else:
                            if attempt < max_retries - 1:
                                time.sleep(retry_delay)
                                continue
                            st.error(f"Error uploading file. Status code: {response.status_code}")
                    except requests.exceptions.RequestException as e:
                        if attempt < max_retries - 1:
                            time.sleep(retry_delay)
                            continue
                        st.error(f"Connection error on attempt {attempt + 1}: {e}")
            except Exception as e:
                st.error(f"An error occurred while uploading the drawing data: {e}")
    else:
        st.info("Convert an SVG file first to enable upload")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Enable External Position"):
            try:
                response = requests.post(abs_on_url)
                if response.ok:
                    st.session_state.position_tracking = True
                    st.success("External position tracking enabled!")
                    update_preview()  # プレビューの更新のみ
                else:
                    st.error("Failed to enable external position")
            except Exception as e:
                st.error(f"Error: {e}")

    with col2:
        if st.button("Disable External Position"):
            try:
                response = requests.post(abs_off_url)
                if response.ok:
                    st.session_state.position_tracking = False
                    st.success("External position tracking disabled!")
                    update_preview()  # プレビューの更新のみ
                else:
                    st.error("Failed to disable external position")
            except Exception as e:
                st.error(f"Error: {e}")

    col3, col4 = st.columns(2)
    with col3:
        if st.button("Start Drawing"):
            try:
                response = requests.post(start_url)
                if response.ok:
                    st.success("Robot has started drawing!")
                    st.session_state.drawing_active = True
                    # 定期更新の開始
                    while st.session_state.drawing_active:
                        current_time = time.time()
                        if current_time - st.session_state.last_update_time > 1.0:
                            st.session_state.last_update_time = current_time
                            update_preview()
                        time.sleep(0.1)  # CPU負荷軽減のための短い待機
                else:
                    st.error("Failed to start drawing")
            except Exception as e:
                st.error(f"Error: {e}")

    with col4:
        if st.button("Stop Drawing"):
            try:
                response = requests.post(stop_url)
                if response.ok:
                    st.success("Robot drawing stopped!")
                    st.session_state.drawing_active = False  # 定期更新を停止
                else:
                    st.error("Failed to stop drawing")
            except Exception as e:
                st.error(f"Error: {e}")

    if st.button("Clear Position History"):
        st.session_state.position_history = []
        st.success("Position history cleared!")
        update_preview()

else:
    st.button("Upload Drawing Data", disabled=True)
    col1, col2 = st.columns(2)
    with col1:
        st.button("Enable External Position", disabled=True)
    with col2:
        st.button("Disable External Position", disabled=True)
    col3, col4 = st.columns(2)
    with col3:
        st.button("Start Drawing", disabled=True)
    with col4:
        st.button("Stop Drawing", disabled=True)
    st.info("Connect to the robot to enable controls")

st.markdown("""
---
*Developed with ❤️ by Team Ithaca*
""")
