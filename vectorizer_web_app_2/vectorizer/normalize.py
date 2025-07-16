import numpy as np

def normalize_polylines(
    raw_polylines: list[np.ndarray],
    img_shape: tuple[int,int],
    scale: float = 1.0,
    origin: str = 'top_left'
) -> list[np.ndarray]:
    """
    raw_polylines: list of (N,2) ndarray in (x, y) pixel coords
    img_shape: (height, width)
    scale: pixel→unit (e.g. mm)
    origin: 'top_left', 'center', or 'bottom_left'
    returns: list of (M,2) ndarray in (X, Y) unit coords
    """
    h, w = img_shape[:2]
    out: list[np.ndarray] = []
    for pts in raw_polylines:
        xs = pts[:,0].astype(float) * scale
        ys = pts[:,1].astype(float) * scale

        if origin == 'center':
            xs -= (w*scale)/2
            ys  = (h*scale)/2 - ys
        elif origin == 'bottom_left':
            ys = ys  # (0 at bottom); assume skel was produced with origin upper
        # else: 'top_left' のまま (0,0)=左上)

        out.append(np.vstack([xs, ys]).T)
    return out
