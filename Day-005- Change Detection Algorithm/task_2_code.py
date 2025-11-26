import cv2
import numpy as np
import os

# ----------------- PATHS -----------------
input_dir = r"C:\Users\vipin\Downloads\ProductizeTech - AI Fulltime Assignment-20251122T062524Z-1-001\ProductizeTech - AI Fulltime Assignment\Task 2 - Change Detection Algorithm\input-images"
output_dir = r"C:\Users\vipin\Downloads\ProductizeTech - AI Fulltime Assignment-20251122T062524Z-1-001\ProductizeTech - AI Fulltime Assignment\Task 2 - Change Detection Algorithm\task_2_output"

# Create main output folder
os.makedirs(output_dir, exist_ok=True)

# Create sub-folder for cropped changes (Dataset Creation)
crops_dir = os.path.join(output_dir, "crops")
os.makedirs(crops_dir, exist_ok=True)

# ----------------- HELPER: IMAGE ALIGNMENT -----------------
def align_images(img_ref, img_target):
    """
    Aligns img_target to match img_ref using ORB features.
    Fixes small camera shakes.
    """
    # Convert to grayscale
    gray_ref = cv2.cvtColor(img_ref, cv2.COLOR_BGR2GRAY)
    gray_target = cv2.cvtColor(img_target, cv2.COLOR_BGR2GRAY)
    
    # Detect ORB features
    orb = cv2.ORB_create(5000)
    kp1, des1 = orb.detectAndCompute(gray_ref, None)
    kp2, des2 = orb.detectAndCompute(gray_target, None)
    
    if des1 is None or des2 is None:
        return img_target # Cannot align

    # Match features
    matcher = cv2.DescriptorMatcher_create(cv2.DESCRIPTOR_MATCHER_BRUTEFORCE_HAMMING)
    matches = matcher.match(des1, des2, None)
    
    # Sort and keep top 15% matches
    matches = sorted(matches, key=lambda x: x.distance)
    good_matches = matches[:int(len(matches) * 0.15)]
    
    if len(good_matches) < 4:
        return img_target # Not enough matches to align

    # Extract location of good matches
    points1 = np.zeros((len(good_matches), 2), dtype=np.float32)
    points2 = np.zeros((len(good_matches), 2), dtype=np.float32)

    for i, match in enumerate(good_matches):
        points1[i, :] = kp1[match.queryIdx].pt
        points2[i, :] = kp2[match.trainIdx].pt

    # Find Homography
    h_matrix, _ = cv2.findHomography(points2, points1, cv2.RANSAC)
    
    if h_matrix is None:
        return img_target

    # Warp image
    height, width = img_ref.shape[:2]
    aligned_img = cv2.warpPerspective(img_target, h_matrix, (width, height))
    
    return aligned_img

# ----------------- MAIN PROCESSING -----------------
for file in os.listdir(input_dir):
    if file.endswith(".jpg") and "~2" not in file:
        base = file.replace(".jpg", "")
        before_path = os.path.join(input_dir, file)
        after_path = os.path.join(input_dir, base + "~2.jpg")

        if not os.path.exists(after_path):
            print(f"[WARNING] Missing after image for {base}")
            continue

        print(f"[PROCESSING] {base}")

        before = cv2.imread(before_path)
        after = cv2.imread(after_path)

        if before is None or after is None:
            print(f"[ERROR] Failed to read images for {base}")
            continue

        # Resize after image to match before image dimensions
        after = cv2.resize(after, (before.shape[1], before.shape[0]))

        # --- STEP 1: AUTO-ALIGNMENT (Fix Camera Shake) ---
        # This reduces false positives significantly
        try:
            after_aligned = align_images(before, after)
        except Exception as e:
            print(f"  [Log] Alignment skipped due to error: {e}")
            after_aligned = after

        # --- STEP 2: PRE-PROCESSING ---
        # Apply Gaussian blur to reduce noise
        before_blur = cv2.GaussianBlur(before, (5, 5), 0)
        after_blur = cv2.GaussianBlur(after_aligned, (5, 5), 0)
        
        gray_before = cv2.cvtColor(before_blur, cv2.COLOR_BGR2GRAY)
        gray_after = cv2.cvtColor(after_blur, cv2.COLOR_BGR2GRAY)

        # --- STEP 3: DIFFERENCE CALCULATION ---
        # Method 1: Absolute difference
        diff = cv2.absdiff(gray_before, gray_after)
        
        # Method 2: Color difference (catches changes even if brightness is same)
        diff_color = cv2.absdiff(before_blur, after_blur)
        diff_gray_from_color = cv2.cvtColor(diff_color, cv2.COLOR_BGR2GRAY)
        
        # Combine methods for robustness
        combined_diff = cv2.addWeighted(diff, 0.6, diff_gray_from_color, 0.4, 0)
        
        # --- STEP 4: THRESHOLDING ---
        _, thresh = cv2.threshold(combined_diff, 25, 255, cv2.THRESH_BINARY)
        
        # Adaptive threshold helps with shadows
        adaptive_thresh = cv2.adaptiveThreshold(
            combined_diff, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
            cv2.THRESH_BINARY, 11, 2
        )
        # Combine (OR operation)
        thresh = cv2.bitwise_and(thresh, adaptive_thresh)

        # --- STEP 5: CLEANING (MORPHOLOGY) ---
        # Remove small noise dots
        kernel = np.ones((3, 3), np.uint8)
        thresh = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel, iterations=1)
        # Fill gaps inside objects
        thresh = cv2.morphologyEx(thresh, cv2.MORPH_DILATE, kernel, iterations=2)

        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        output_img = after_aligned.copy()
        
        # Create a separate layer for Transparent Fill
        overlay = output_img.copy()
        
        change_detected = False
        change_count = 0
        changes_list = []

        # --- STEP 6: CONTOUR ANALYSIS & VISUALIZATION ---
        for cnt in contours:
            area = cv2.contourArea(cnt)
            
            # Filter small noise (Adjust '200' based on drone height)
            if area > 200:
                x, y, w, h = cv2.boundingRect(cnt)
                change_count += 1
                
                # --- A. CROP & SAVE (Dataset Creation) ---
                # Add margin to crop
                m = 10
                crop_y1, crop_y2 = max(0, y-m), min(after_aligned.shape[0], y+h+m)
                crop_x1, crop_x2 = max(0, x-m), min(after_aligned.shape[1], x+w+m)
                
                crop_img = after_aligned[crop_y1:crop_y2, crop_x1:crop_x2]
                crop_name = f"{base}_change_{change_count}.jpg"
                cv2.imwrite(os.path.join(crops_dir, crop_name), crop_img)
                
                # --- B. SETTINGS ---
                # Neon Green for visibility
                box_color = (0, 255, 0) 
                outline_color = (0, 0, 0)

                if area > 2000:
                    thickness = 4
                    label_size = "Large"
                elif area > 800:
                    thickness = 3
                    label_size = "Medium"
                else:
                    thickness = 2
                    label_size = "Small"

                # --- C. DRAW TRANSPARENT FILL ---
                # Draw filled rectangle on the overlay layer
                cv2.rectangle(overlay, (x, y), (x + w, y + h), box_color, -1)

                # --- D. DRAW THICK BORDERS ---
                # Draw Black Outline (Shadow) on original image logic
                # Note: We draw borders later after merging overlay to keep them sharp
                
                change_detected = True
                
                # Store visualization data for later loop
                changes_list.append({
                    'rect': (x, y, w, h),
                    'color': box_color,
                    'thickness': thickness,
                    'text': f"#{change_count} {label_size}"
                })

        # --- STEP 7: MERGE TRANSPARENCY ---
        # Blend the overlay (with filled boxes) and original image
        alpha = 0.3 # 30% transparency
        output_img = cv2.addWeighted(overlay, alpha, output_img, 1 - alpha, 0)

        # --- STEP 8: DRAW SHARP BORDERS & LABELS ON TOP ---
        for item in changes_list:
            x, y, w, h = item['rect']
            color = item['color']
            thick = item['thickness']
            text = item['text']
            
            # 1. Black Outline (Behind)
            cv2.rectangle(output_img, (x, y), (x+w, y+h), (0,0,0), thick+2)
            # 2. Green Border (Front)
            cv2.rectangle(output_img, (x, y), (x+w, y+h), color, thick)
            
            # Label Background
            font = cv2.FONT_HERSHEY_DUPLEX
            font_scale = 0.5
            (text_w, text_h), _ = cv2.getTextSize(text, font, font_scale, 1)
            
            label_y = y - 10 if y > 30 else y + h + 20
            
            # Draw label background (Black border, Green fill)
            cv2.rectangle(output_img, (x, label_y - text_h - 4), (x + text_w + 10, label_y + 6), (0,0,0), -1)
            cv2.rectangle(output_img, (x + 2, label_y - text_h - 2), (x + text_w + 8, label_y + 4), color, -1)
            
            # Draw Text
            cv2.putText(output_img, text, (x + 5, label_y), font, font_scale, (0,0,0), 1)

        # --- STEP 9: SAVE FINAL COMPOSITE ---
        before_label = cv2.resize(before, (output_img.shape[1], output_img.shape[0]))
        
        # Add titles
        cv2.putText(before_label, "Before", (30, 60), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 255), 4)
        cv2.putText(output_img, f"Changes: {change_count}", (30, 60), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 255, 0), 4)

        # Combine side-by-side
        combined = cv2.hconcat([before_label, output_img])

        output_path = os.path.join(output_dir, base + "~3_Final.jpg")
        cv2.imwrite(output_path, combined)
        print(f"[SAVED] {output_path} (Detected: {change_count})")

print("\n--- PROCESS COMPLETE ---")
print(f"Crops saved in: {crops_dir}")