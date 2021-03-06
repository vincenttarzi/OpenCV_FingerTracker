import cv2
import numpy as np
import time
import mouse
import HandTracker as htm

hand_hist = None
traverse_point = []
total_rectangle = 9
hand_rect_one_x = None
hand_rect_one_y = None

hand_rect_two_x = None
hand_rect_two_y = None

display_width = 1920
display_height = 1080

prev_x = None
prev_y = None

wpercent = 100
hpercent = 100

firstRun = True

f = [False, False, False, False, False, False]

lmb_start = 0
rmb_start = 0
scrUp_start = 0
scrDown_start = 0

def rescale_frame(frame, wpercent, hpercent):
    width = int(frame.shape[1] * wpercent / 100)
    height = int(frame.shape[0] * hpercent / 100)
    return cv2.resize(frame, (width, height), interpolation=cv2.INTER_AREA)


def contours(hist_mask_image):
    gray_hist_mask_image = cv2.cvtColor(hist_mask_image, cv2.COLOR_BGR2GRAY)
    ret, thresh = cv2.threshold(gray_hist_mask_image, 0, 255, 0)
    cont, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    return cont

def draw_rect(frame):
    rows, cols, _ = frame.shape
    global total_rectangle, hand_rect_one_x, hand_rect_one_y, hand_rect_two_x, hand_rect_two_y

    hand_rect_one_x = np.array(
        [6 * rows / 20, 6 * rows / 20, 6 * rows / 20, 9 * rows / 20, 9 * rows / 20, 9 * rows / 20, 12 * rows / 20,
         12 * rows / 20, 12 * rows / 20], dtype=np.uint32)

    hand_rect_one_y = np.array(
        [9 * cols / 20, 10 * cols / 20, 11 * cols / 20, 9 * cols / 20, 10 * cols / 20, 11 * cols / 20, 9 * cols / 20,
         10 * cols / 20, 11 * cols / 20], dtype=np.uint32)

    hand_rect_two_x = hand_rect_one_x + 10
    hand_rect_two_y = hand_rect_one_y + 10

    for i in range(total_rectangle):
        cv2.rectangle(frame, (hand_rect_one_y[i], hand_rect_one_x[i]),
                      (hand_rect_two_y[i], hand_rect_two_x[i]),
                      (0, 255, 0), 1)

    return frame


def hand_histogram(frame):
    global hand_rect_one_x, hand_rect_one_y

    hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    roi = np.zeros([90, 10, 3], dtype=hsv_frame.dtype)

    for i in range(total_rectangle):
        roi[i * 10: i * 10 + 10, 0: 10] = hsv_frame[hand_rect_one_x[i]:hand_rect_one_x[i] + 10,
                                          hand_rect_one_y[i]:hand_rect_one_y[i] + 10]

    hand_hist = cv2.calcHist([roi], [0, 1], None, [180, 256], [0, 180, 0, 256])
    return cv2.normalize(hand_hist, hand_hist, 0, 255, cv2.NORM_MINMAX)


def hist_masking(frame, hist):
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    dst = cv2.calcBackProject([hsv], [0, 1], hist, [0, 180, 0, 256], 1)

    disc = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (31, 31))
    cv2.filter2D(dst, -1, disc, dst)

    ret, thresh = cv2.threshold(dst, 150, 255, cv2.THRESH_BINARY)

    # thresh = cv2.dilate(thresh, None, iterations=5)

    thresh = cv2.merge((thresh, thresh, thresh))

    return cv2.bitwise_and(frame, thresh)


def centroid(max_contour):
    moment = cv2.moments(max_contour)
    if moment['m00'] != 0:
        cx = int(moment['m10'] / moment['m00'])
        cy = int(moment['m01'] / moment['m00'])
        return cx, cy
    else:
        return None


def farthest_point(defects, contour, centroid):
    if defects is not None and centroid is not None:
        s = defects[:, 0][:, 0]
        cx, cy = centroid

        x = np.array(contour[s][:, 0][:, 0], dtype=np.float)
        y = np.array(contour[s][:, 0][:, 1], dtype=np.float)

        xp = cv2.pow(cv2.subtract(x, cx), 2)
        yp = cv2.pow(cv2.subtract(y, cy), 2)
        dist = cv2.sqrt(cv2.add(xp, yp))

        dist_max_i = np.argmax(dist)

        if dist_max_i < len(s):
            farthest_defect = s[dist_max_i]
            farthest_point = tuple(contour[farthest_defect][0])
            return farthest_point
        else:
            return None


def draw_circles(frame, traverse_point):
    if traverse_point is not None:
        for i in range(len(traverse_point)):
            cv2.circle(frame, traverse_point[i], int(5 - (5 * i * 3) / 100), [0, 255, 255], -1)


def distance(x1,y1,x2,y2):
    return ((x1 - x2)**2 + (y1 - y2)**2)**0.5

def manage_image_opr(frame, hand_hist, handPoints):
    global firstRun, prev_x, prev_y, f, lmb_start, rmb_start, scrUp_start, scrDown_start
    # hist_mask_image = hist_masking(frame, hand_hist)

    # hist_mask_image = cv2.erode(hist_mask_image, None, iterations=2)
    # hist_mask_image = cv2.dilate(hist_mask_image, None, iterations=2)

    # contour_list = contours(hist_mask_image)
    # max_cont = max(contour_list, key=cv2.contourArea)

    # cnt_centroid = centroid(max_cont)
    # cv2.circle(frame, cnt_centroid, 5, [255, 0, 255], -1)

    x_pad_hi = int(frame.shape[1] * wpercent / 100)
    x_pad_lo = x_pad_hi / 5
    x_pad_hi = x_pad_hi - x_pad_lo
    y_pad_hi = int(frame.shape[0] * wpercent / 100)
    y_pad_lo = y_pad_hi / 3
    y_pad_hi = y_pad_hi - y_pad_lo


    # if max_cont is not None:
        # hull = cv2.convexHull(max_cont, returnPoints=False)
        # defects = cv2.convexityDefects(max_cont, hull)
    if(firstRun == True):
        firstRun = False
        # prev_x = cnt_centroid[0]
        # prev_y = cnt_centroid[1]
        centerX = handPoints[0][1] + handPoints[1][1] + handPoints[17][1]
        centerX /= 3
        centerY = handPoints[0][2] + handPoints[1][2] + handPoints[17][2]
        centerY /= 3
        prev_x = centerX
        prev_y = centerY

    if(f[1] == True):
        if(lmb_start == 0):
            lmb_start = time.time()
        if(time.time() - lmb_start >= 1):
            mouse.click('left')
            lmb_start = 0
    else:
        lmb_start = 0

    if(f[2] == True):
        if(rmb_start == 0):
            rmb_start = time.time()
        if(time.time() - rmb_start >= 1):
            mouse.click('right')
            rmb_start = 0
    else:
        rmb_start = 0

    if(f[4] == True):
        if(scrUp_start == 0):
            scrUp_start = time.time()
        if(time.time() - scrUp_start >= 0.2):
            mouse.wheel(1)
            scrUp_start = 0
    else:
        scrUp_start = 0

    if(f[5] == True):
        if(scrDown_start == 0):
            scrDown_start = time.time()
        if(time.time() - scrDown_start >= 0.2):
            mouse.wheel(-1)
            scrDown_start = 0
    else:
        scrDown_start = 0

    # if(distance(cnt_centroid[0], cnt_centroid[1], prev_x, prev_y) < x_pad_lo
    #     and (distance(cnt_centroid[0], cnt_centroid[1], prev_x, prev_y) > x_pad_lo / 50)):
    #
    #     prev_x = cnt_centroid[0]
    #     prev_y = cnt_centroid[1]
    #
    #     mouse_x = cnt_centroid[0] - x_pad_lo
    #     mouse_y = cnt_centroid[1] - y_pad_lo
    #
    #     mouse.move(mouse_x * (display_width / (x_pad_hi - x_pad_lo)), mouse_y * (display_height / (y_pad_hi - y_pad_lo)))
    try:
        centerX = handPoints[0][1] + handPoints[1][1] + handPoints[17][1]
        centerX /= 3
        centerY = handPoints[0][2] + handPoints[1][2] + handPoints[17][2]
        centerY /= 3
        d = distance(centerX, centerY, prev_x, prev_y)
        if x_pad_lo > d > x_pad_lo/50:
            prev_x = centerX
            prev_y = centerY
            mouse_x = centerX - x_pad_lo
            mouse_y = centerY - y_pad_lo
            mouse.move(mouse_x * (display_width / (x_pad_hi - x_pad_lo)), mouse_y * (display_height / (y_pad_hi - y_pad_lo)))
    except IndexError:
        pass


def main():
    global hand_hist, f
    is_hand_hist_created = False
    capture = cv2.VideoCapture(0)

    detector = htm.handDetector(detectionCon=0.75)
    tipIds = [4, 8, 12, 16, 20]

    while capture.isOpened():
        pressed_key = cv2.waitKey(1)
        _, frame = capture.read()
        frame = cv2.flip(frame, 1)

        img = detector.findHands(frame)
        lmList = detector.findPosition(img, draw=False)

        if pressed_key & 0xFF == ord('z'):
            # Remnant from the histogram approach
            is_hand_hist_created = True

        if is_hand_hist_created:
            manage_image_opr(frame, hand_hist, lmList)
            if len(lmList) != 0:
                fingers = []

                # Thumb
                if lmList[tipIds[0]][1] < lmList[tipIds[0] - 1][1]:
                    fingers.append(1)
                else:
                    fingers.append(0)

                # 4 Fingers
                for id in range(1, 5):
                    if lmList[tipIds[id]][2] < lmList[tipIds[id] - 2][2]:
                        fingers.append(1)
                    else:
                        fingers.append(0)

                totalFingers = fingers.count(1)
                for i in range(0,6):
                    if totalFingers == i:
                        f[i] = True
                    else:
                        f[i] = False

        cv2.imshow("Live Feed", rescale_frame(frame, wpercent, hpercent))

        if pressed_key == 27:
            break

    cv2.destroyAllWindows()
    capture.release()


if __name__ == '__main__':
    main()
