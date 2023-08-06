import numpy as np
import cv2
import time
import os

from pathlib import Path

# Path Configuration


# Window Configuration
cv2.namedWindow('Detection', cv2.WINDOW_AUTOSIZE)
cv2.moveWindow('Detection', 800, 50)

# cv2.namedWindow('Binarization', cv2.WINDOW_AUTOSIZE)
# cv2.moveWindow('Binarization', 50, 50)


def drone_data():
    DATA_DIR = Path(Path(__file__).resolve()).parents[2]/'data'
    data = str(DATA_DIR/'drone_360p.mp4')
    return data


def open_cam(video_capture=0, open_file=False, file=None):
    # FROM FILE
    if open_file:
        if file is None:
            print('File path: None')
        cap = cv2.VideoCapture(file)
        print('Processing file:', file)
    else:
        # FROM CAMERA
        cap = cv2.VideoCapture(0)

    #  Check is opening
    if cap.isOpened() is False:
        print('Error opening video straming or file')
    else:
        return cap


def distance(p0, p1, mode='euclid'):
    x0, x1 = p0[0], p1[0]
    y0, y1 = p0[1], p1[1]

    formula = {
        'euclid': np.sqrt(np.power(x0-x1, 2) + np.power(y0-y1, 2)),
        'city_block': np.abs(x0-x1) + np.abs(y0-y1),
    }

    if mode not in formula:
        mode = 'euclid'

    return formula[mode].astype(np.float)


def object_centroid(points):
    px, py = 0, 0
    num_points = len(points)
    for p in points:
        p = p[0]
        px += p[0]
        py += p[1]
    centroid = (
        int(px/num_points),
        int(py/num_points)
    )

    return centroid


def nearest_object(frame_data, edge_threshold=600, center_position='center'):
    """
        Nearest object: to find object by distance from aimimg point
        is_open_file -> Use to select source of data
        edge_threshold -> if the value high, it'll looking only explicitly edge
    """
    frame = frame_data
    # CONVERT VIDEO CHANNEL BGR TO GRAY
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # EDEGE DETECTION
    edge_gray = cv2.Canny(
        gray,
        threshold1=edge_threshold,
        threshold2=400
    )
    ret, thresh = cv2.threshold(edge_gray, cv2.THRESH_OTSU, 255, 0)
    # cv2.imshow('Binarization', thresh)

    # FIND CONTOURS
    im, contours, hierarchy = cv2.findContours(
        thresh,
        cv2.RETR_TREE,
        cv2.CHAIN_APPROX_SIMPLE
    )

    # SET Aiming
    max_y, max_x = gray.shape
    if center_position == 'center':
        frame_center = (max_x//2, max_y//2)
    elif center_position == 'bottom':
        frame_center = (max_x//2, max_y)
    elif center_position == 'top':
        frame_center = (max_x, max_y//2)

    cv2.circle(frame, frame_center, 10, (0, 0, 255), -1)

    # Draw line from frame center to object centroid
    centroid_set, radius_set = [], []
    for points in contours:
        centroid = object_centroid(points)
        radius = distance(frame_center, centroid, mode='euclid')
        centroid_set.append(centroid)
        radius_set.append(radius)

    if len(radius_set) > 0:
        min_distance_index = np.argmin(radius_set)
        target_centroid = centroid_set[min_distance_index]
    else:
        min_distance_index = 0
        target_centroid = (frame_center)
    cv2.line(frame, frame_center, target_centroid, (255, 0, 0), 2)
    cv2.circle(frame, target_centroid, 5, (0, 0, 255), -1)

    return frame, target_centroid,


def integration(is_open_file=True, edge_threshold=600):
    """
        Integrate functions to find nearest object and show displays
    """
    cap = open_cam(open_file=is_open_file, file=drone_data())

    while cap.isOpened():
        # READ VIDEO FRAME
        ret, frame = cap.read()

        if ret is True:
            frame, centroid = nearest_object(
                frame_data=frame,
                center_position='bottom',
                edge_threshold=edge_threshold
            )
            cv2.imshow('Detection', frame)

        # QUIT KEYS
        if cv2.waitKey(36) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()


def main():
    integration(False, edge_threshold=200)


if __name__ == '__main__':
    main()
