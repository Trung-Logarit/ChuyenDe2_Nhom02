import numpy as np
import cv2
import os

def scale_to_0_255(img):
    min_val = np.min(img)
    max_val = np.max(img)
    new_img = (img - min_val) / (max_val - min_val + 1e-6)
    new_img *= 255
    return new_img.astype(np.uint8)

def save_step(name, img):
    cv2.imwrite(name, img)
    print("Saved:", name)

def my_canny(img, low, high, sobel_size=3, is_L2_gradient=False):

    # =============================
    # STEP 1 – Gaussian Blur
    # =============================
    smooth = cv2.GaussianBlur(img, (5, 5), 0)
    save_step("step1_blur.jpg", smooth)

    # =============================
    # STEP 2 – Sobel Gx, Gy
    # =============================
    Gx = cv2.Sobel(smooth, cv2.CV_64F, 1, 0, ksize=sobel_size)
    Gy = cv2.Sobel(smooth, cv2.CV_64F, 0, 1, ksize=sobel_size)

    save_step("step2_gx.jpg", scale_to_0_255(np.abs(Gx)))
    save_step("step2_gy.jpg", scale_to_0_255(np.abs(Gy)))

    # =============================
    # STEP 3 – Gradient Magnitude
    # =============================
    if is_L2_gradient:
        mag = np.sqrt(Gx * Gx + Gy * Gy)
    else:
        mag = np.abs(Gx) + np.abs(Gy)

    save_step("step3_gradient.jpg", scale_to_0_255(mag))

    # =============================
    # STEP 4 – Gradient Angle
    # =============================
    angle = np.arctan2(Gy, Gx) * 180 / np.pi
    save_step("step4_raw_angle.jpg", scale_to_0_255(np.abs(angle)))

    # Quantize angle
    ang = np.abs(angle)
    ang_q = ang.copy()
    ang_q[ang <= 22.5] = 0
    ang_q[(ang > 22.5) & (ang <= 67.5)] = 45
    ang_q[(ang > 67.5) & (ang <= 112.5)] = 90
    ang_q[(ang > 112.5) & (ang <= 157.5)] = 135
    ang_q[ang > 157.5] = 0

    save_step("step5_angle_quantized.jpg", scale_to_0_255(ang_q))

    # =============================
    # STEP 5 – Non-maximum Suppression
    # =============================
    h, w = img.shape
    nms = np.zeros_like(mag)

    for y in range(1, h - 1):
        for x in range(1, w - 1):
            a = ang_q[y, x]
            m = mag[y, x]

            if a == 0:
                p1, p2 = mag[y, x-1], mag[y, x+1]
            elif a == 45:
                p1, p2 = mag[y-1, x+1], mag[y+1, x-1]
            elif a == 90:
                p1, p2 = mag[y-1, x], mag[y+1, x]
            else:  # 135
                p1, p2 = mag[y-1, x-1], mag[y+1, x+1]

            if m >= p1 and m >= p2:
                nms[y, x] = m

    save_step("step6_nms.jpg", scale_to_0_255(nms))

    # =============================
    # STEP 6 – Double Threshold
    # =============================
    strong = (nms >= high).astype(np.uint8)
    weak   = ((nms >= low) & (nms < high)).astype(np.uint8)

    # visualization: strong=255, weak=128
    dt_vis = strong * 255 + weak * 128
    save_step("step7_double_threshold.jpg", dt_vis)

    # =============================
    # STEP 7 – Hysteresis
    # =============================
    final = strong.copy()

    for y in range(1, h - 1):
        for x in range(1, w - 1):
            if weak[y, x]:
                if np.any(strong[y-1:y+2, x-1:x+2]):
                    final[y, x] = 1

    save_step("step8_hysteresis.jpg", scale_to_0_255(final))

    return scale_to_0_255(final)


# =============================
# RUN
# =============================
img = cv2.imread("frame_20_original.jpg", 0)
result = my_canny(img, low=30, high=90)

save_step("final_my_canny.jpg", result)
save_step("opencv_canny.jpg", cv2.Canny(img, 30, 90))
