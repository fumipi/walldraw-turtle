import numpy as np

def to_csv(polylines: list[np.ndarray]) -> str:
    """
    polylines: list of (N,2) ndarray in (X,Y) mm coords
    returns: text where each polyline is one line,
             points are "x,y" joined by ";".
    """
    lines = []
    for path in polylines:
        # format each point as "x.y,y.y" with 1 decimal place
        pts = [f"{x:.1f},{y:.1f}" for x, y in path]
        # join with semicolons
        lines.append(";".join(pts))
    # join polylines with newlines
    return "\n".join(lines)

def to_gcode(
    polylines: list[np.ndarray],
    feedrate: int = 1000
) -> str:
    """
    polylines: list of (N,2) ndarray in (X,Y) coords
    returns: G-code text with G0/G1 commands
    """
    g = []
    g.append("G21 ; set units to mm")
    for pts in polylines:
        for i, (x, y) in enumerate(pts):
            cmd = "G0" if i == 0 else "G1"
            g.append(f"{cmd} X{x:.1f} Y{y:.1f} F{feedrate}")
    return "\n".join(g)
