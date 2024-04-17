import torch.nn.functional as F
import torch
import numpy as np
import cv2
import math

def fov2focal(fov, pixels):
    return pixels / (2 * math.tan(fov / 2))
def focal2fov(focal, pixels):
    return 2 * math.atan(pixels / (2 * focal))
def unproject(c2w, K, points2d, depth):
    """
    c2w: (4, 4)
    K: (3, 3)
    points2d: (N, 2) - (x, y) in the range [0; (W,H)]
    depth: (H, W)
    """

    point_depth = depth[points2d[:, 1].long(), points2d[:, 0].long()] # (N,)
    d = torch.cat((points2d, torch.ones((points2d.shape[0], 1)).to(points2d.device)), dim=-1) # (N, 3)
    d = d @ K.inverse().T # (N, 3)
    # d = d / d.norm(1, keepdim=True) # (N, 3)
    d = d @ c2w[:3, :3].T # (N, 3)
    camera_pos = c2w[:3, 3] # (3,)

    points3d = d * point_depth[:, None] + camera_pos[None, :] # (N, 3)

    return points3d

def to_homogeneous(v):
    if type(v) is np.ndarray:
        v = np.concatenate((v, np.ones((*v.shape[:-1], 1))), axis=-1)
    elif type(v) is torch.Tensor:
        v = torch.cat((v, torch.ones((*v.shape[:-1], 1)).to(v.device)), dim=-1)
    return v

def get_points(img,
               sel_pix):
    # draw points
    points = []
    for idx, point in enumerate(sel_pix):
        if idx % 2 == 0:
            # draw a red circle at the handle point
            cv2.circle(img, tuple(point), 10, (255, 0, 0), -1)
        else:
            # draw a blue circle at the handle point
            cv2.circle(img, tuple(point), 10, (0, 0, 255), -1)
        points.append(tuple(point))
        # draw an arrow from handle point to target point
        if len(points) == 2:
            cv2.arrowedLine(img, points[0], points[1], (255, 255, 255), 4, tipLength=0.5)
            points = []
    return img if isinstance(img, np.ndarray) else np.array(img)