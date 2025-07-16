import xml.etree.ElementTree as ET
from IPython.display import SVG, display
import numpy as np

def polyline_to_svg_path(points: list[tuple[float,float]]) -> str:
    coords = [f"{x:.1f},{y:.1f}" for x, y in points]
    return "M " + " L ".join(coords)

def create_svg(
    polylines: list[np.ndarray],
    width: int,
    height: int,
    stroke: str = 'black',
    stroke_width: int = 1
) -> str:
    """
    polylines: list of (N,2) ndarray in (X,Y) coords
    returns: SVG XML string
    """
    svg = ET.Element(
        'svg',
        xmlns="http://www.w3.org/2000/svg",
        version="1.1",
        width=str(width),
        height=str(height),
        viewBox=f"0 0 {width} {height}",
        preserveAspectRatio="xMinYMin meet"
    )
    for pts in polylines:
        d = polyline_to_svg_path(pts)
        ET.SubElement(
            svg, 'path',
            d=d,
            fill="none",
            stroke=stroke,
            **{'stroke-width': str(stroke_width)}
        )
    return ET.tostring(svg).decode()
