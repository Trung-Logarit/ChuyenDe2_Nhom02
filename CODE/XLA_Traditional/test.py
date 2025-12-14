import cv2
import numpy as np
from skimage.filters import threshold_otsu
import time

# ============================================================
# Gaussian + Canny edge
# ============================================================
def canny_edges(gray, low=30, high=90):
    blur = cv2.GaussianBlur(gray, (5,5), 1.0)
    return cv2.Canny(blur, low, high)

# ============================================================
# Build trapezoid ROI
# ============================================================
def build_trapezoid_roi(img_shape,
                        top_width_ratio=0.035,
                        bottom_width_ratio=0.40,
                        height_ratio=0.57,
                        bottom_crop_ratio=0.78,
                        horizontal_shift_ratio=-0.012):
    """
    horizontal_shift_ratio:
        - âm  -> dời ROI sang trái
        - dương -> dời ROI sang phải
        - 0    -> căn giữa
    """
    h, w = img_shape[:2]

    # toạ độ theo chiều cao
    top_y = int(h * height_ratio)
    bottom_y = int(h * bottom_crop_ratio)

    # độ rộng trên và dưới
    half_top = int(w * top_width_ratio * 0.5)
    half_bot = int(w * bottom_width_ratio * 0.5)

    # tâm ROI (dời sang trái/phải theo ratio)
    cx = int(w * (0.5 + horizontal_shift_ratio))

    # bốn điểm của ROI
    pts = np.array([
        [cx - half_top, top_y],
        [cx + half_top, top_y],
        [cx + half_bot, bottom_y],
        [cx - half_bot, bottom_y]
    ], dtype=np.int32)

    return pts

# ============================================================
# Apply mask ROI
# ============================================================
def apply_roi_mask(img, roi_pts):
    mask = np.zeros_like(img)
    cv2.fillPoly(mask, [roi_pts], 255)
    masked = cv2.bitwise_and(img, mask)
    return masked, mask

# ============================================================
# Sobel + morphology (vehicle edges)
# ============================================================
def sobel_morph_edges(gray):
    blur = cv2.GaussianBlur(gray, (5,5), 1.0)
    sobelx = cv2.Sobel(blur, cv2.CV_64F, 1, 0, ksize=3)
    sobely = cv2.Sobel(blur, cv2.CV_64F, 0, 1, ksize=3)
    sobel = np.abs(sobelx) + np.abs(sobely)
    sobel = sobel.astype(np.uint8)

    # Otsu threshold
    th_val = threshold_otsu(sobel)
    th = (sobel > th_val).astype(np.uint8) * 255
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5,5))
    opened = cv2.morphologyEx(th, cv2.MORPH_OPEN, kernel)
    return opened

# ============================================================
# Compute average slope for lane lines
# ============================================================
def average_lines(lines, img_shape):
    left, right = [], []
    h, w = img_shape[:2]
    y1 = h - 1
    y2 = int(h * 0.62)

    if lines is None:
        return None, None

    for line in lines:
        x1,y1_,x2,y2_ = line[0]
        if x2 == x1:
            continue
        slope = (y2_ - y1_) / (x2 - x1)
        if abs(slope) < 0.5:
            continue
        intercept = y1_ - slope*x1

        if slope < 0:
            left.append([slope, intercept])
        else:
            right.append([slope, intercept])

    def make_line(avg):
        m,b = avg
        x1 = int((y1 - b) / m)
        x2 = int((y2 - b) / m)
        return (x1,y1, x2,y2)

    left_line = make_line(np.mean(left,axis=0)) if len(left)>0 else None
    right_line = make_line(np.mean(right,axis=0)) if len(right)>0 else None
    return left_line, right_line

# ============================================================
# Draw lane lines on image
# ============================================================
def overlay_lane(frame, left_line, right_line):
    img = frame.copy()
    if left_line:
        x1,y1,x2,y2 = left_line
        cv2.line(img,(x1,y1),(x2,y2),(255,0,0),6)
    if right_line:
        x1,y1,x2,y2 = right_line
        cv2.line(img,(x1,y1),(x2,y2),(0,255,0),6)
    return img

# ============================================================
# MAIN
# ============================================================
def main():
    cap = cv2.VideoCapture("car.mp4")
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter("output/lane_vehicle_output.mp4", fourcc, 30,
                          (int(cap.get(3)), int(cap.get(4))))

    frame_idx = 0
    total_time = 0
    correct_detections = 0  # Đếm số frame phát hiện lane

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        frame_idx += 1
        start = time.time()

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        edge_lane = canny_edges(gray)
        roi_pts = build_trapezoid_roi(gray.shape)
        edges_roi, _ = apply_roi_mask(edge_lane, roi_pts)

        lines = cv2.HoughLinesP(edges_roi, 1, np.pi/180, threshold=40,
                                minLineLength=20, maxLineGap=200)
        left_line, right_line = average_lines(lines, frame.shape)

        if frame_idx == 20:
            # Vẽ ROI lên bản sao của frame gốc
            frame_with_roi = frame.copy()
            cv2.polylines(frame_with_roi, [roi_pts], True, (0, 255, 255), 3)  # Màu vàng, độ dày 3px
            cv2.imwrite(f"frame_{frame_idx}_original.jpg", frame)
            cv2.imwrite(f"frame_{frame_idx}_gray.jpg", gray)
            cv2.imwrite(f"frame_{frame_idx}_canny.jpg", edge_lane)
            cv2.imwrite(f"frame_{frame_idx}_roi.jpg", edges_roi)
            print(f"HoughLinesP output at frame {frame_idx}: {lines}")
            cv2.imwrite(f"frame_{frame_idx}_overlay.jpg", result)
        veh_edges = sobel_morph_edges(gray)
        result = overlay_lane(frame, left_line, right_line)
        out.write(result)

        # Accuracy estimation: nếu phát hiện ít nhất một lane
        if left_line and right_line:
            correct_detections += 1
            # Tạo thư mục nếu chưa có
            save_dir = "output/detected_frames"
            import os
            os.makedirs(save_dir, exist_ok=True)

            # Lưu frame với overlay lane
            cv2.imwrite(f"{save_dir}/frame_{frame_idx}.jpg", result)
        else:
            # Tạo thư mục nếu chưa có
            save_dir = "output2/not_detected_frames"
            import os
            os.makedirs(save_dir, exist_ok=True)

            # Lưu frame với overlay lane
            cv2.imwrite(f"{save_dir}/frame_{frame_idx}.jpg", result)
        total_time += (time.time() - start)

    cap.release()
    out.release()
    cv2.destroyAllWindows()

    # ==========================
    # FINAL SUMMARY OUTPUT
    # ==========================
    avg_time = (total_time / frame_idx) * 1000      # ms/frame
    fps_final = frame_idx / total_time
    accuracy_ratio = correct_detections / frame_idx

    print("\n=============================")
    print("     PROCESSING SUMMARY     ")
    print("=============================")
    print(f"Số frame : {frame_idx}")
    print(f"Tổng thời gian xử lý  : {total_time:.2f} seconds")
    print(f"Thời gian trung bình mỗi frame    : {avg_time:.2f} ms")
    print(f"FPS trung bình             : {fps_final:.2f}")
    print(f"Đúng:            : {correct_detections:.2f}")
    print(f"Phần trăm chính xác        : {accuracy_ratio:.4f}")
    print("=============================\n")

if __name__ == "__main__":
    main()