import numpy as np
import cv2
import time
import os

from pathlib import Path

# Path Configuration
DATA_DIR = Path(Path(__file__).resolve()).parents[1]/'data'
data = str(DATA_DIR/'drone_360p.mp4')

# Window Configuration
cv2.namedWindow('Binarization', cv2.WINDOW_AUTOSIZE)
cv2.namedWindow('Detection', cv2.WINDOW_AUTOSIZE)
cv2.moveWindow('Binarization', 50, 50)
cv2.moveWindow('Detection', 800, 50)


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


def main():
    cap = open_cam(open_file=False, file=data)
    while(cap.isOpened()):
        # READ VIDEO FRAME
        ret, frame = cap.read()

        if ret is True:
            # CONVERT VIDEO CHANNEL BGR TO GRAY
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            # EDEGE DETECTION
            high_detail = 300
            edge_gray = cv2.Canny(gray, threshold1=high_detail, threshold2=550)
            ret, thresh = cv2.threshold(edge_gray, cv2.THRESH_OTSU, 128, 0)
            cv2.imshow('Binarization', thresh)
            # FIND CONTOURS
            im, contours, hierarchy = cv2.findContours(
                thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE
            )
        else:
            continue
        # SET Boundary
        max_y, max_x = gray.shape
        frame_center = (max_x//2, max_y//2)
        cv2.circle(frame, frame_center, 5, (0, 0, 255), -1)

        # Draw line from frame center to object centroid
        for points in contours:
            centroid = object_centroid(points)
            radius = distance(frame_center, centroid)

            if radius < 150 and centroid[1] >= frame_center[1]:
                cv2.line(frame, frame_center, centroid, (255, 0, 0), 1)

        draw_contour = cv2.drawContours(frame, contours, -1, (0, 255, 0), 3)

        # SHOW VIDEO
        cv2.imshow('Detection', draw_contour)

        # QUIT KEYS
        if cv2.waitKey(36) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == '__main__':
    main()
