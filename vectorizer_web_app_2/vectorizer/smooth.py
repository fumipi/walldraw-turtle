import numpy as np

def chaikin_curve(points: np.ndarray, iterations: int) -> np.ndarray:
    """
    Chaikin smoothing.
    points: (N,2) ndarray
    iterations: number of times to apply
    """
    pts = points.copy()
    for _ in range(iterations):
        new_pts = []
        for i in range(len(pts) - 1):
            p0, p1 = pts[i], pts[i+1]
            q = 0.75*p0 + 0.25*p1
            r = 0.25*p0 + 0.75*p1
            new_pts.extend([q, r])
        pts = np.array(new_pts)
    return pts

def rdp(points: np.ndarray, epsilon: float) -> np.ndarray:
    """
    再帰版 Douglas–Peucker.
    """
    if len(points) < 3:
        return points.copy()
    start, end = points[0], points[-1]
    line = end - start
    norm = np.hypot(*line)
    if norm == 0:
        dists = np.hypot(*(points - start).T)
    else:
        proj = ((points - start) @ line) / (norm**2)
        proj_pts = np.outer(proj, line) + start
        dists = np.hypot(*(points - proj_pts).T)
    idx = np.argmax(dists)
    if dists[idx] > epsilon:
        left = rdp(points[:idx+1], epsilon)
        right = rdp(points[idx:], epsilon)
        return np.vstack([left[:-1], right])
    else:
        return np.vstack([start, end])

def rdp_iterative(points: np.ndarray, epsilon: float) -> np.ndarray:
    """
    イテレーティブ版 Douglas–Peucker（再帰限界回避用フォールバック）。
    """
    N = len(points)
    if N < 3:
        return points.copy()
    stack = [(0, N-1)]
    keep = np.zeros(N, dtype=bool)
    keep[0] = keep[-1] = True

    while stack:
        start, end = stack.pop()
        segment = points[start:end+1]
        line = points[end] - points[start]
        norm = np.hypot(*line)
        if norm == 0:
            dists = np.hypot(*(segment - points[start]).T)
        else:
            proj = ((segment - points[start]) @ line) / (norm**2)
            proj_pts = np.outer(proj, line) + points[start]
            dists = np.hypot(*(segment - proj_pts).T)
        idx_rel = np.argmax(dists[1:-1]) + 1
        idx = start + idx_rel
        if dists[idx_rel] > epsilon:
            keep[idx] = True
            stack.append((start, idx))
            stack.append((idx, end))

    return points[keep]

def simplify_paths(points: np.ndarray, epsilon: float) -> np.ndarray:
    """
    再帰版 RDP を試し、RecursionError 発生時はイテレーティブ版にフォールバック。
    """
    try:
        return rdp(points, epsilon)
    except RecursionError:
        return rdp_iterative(points, epsilon)
