import cv2
import numpy as np
import logging
from pathlib import Path
from dataclasses import dataclass
from typing import Tuple, Optional, List
from concurrent.futures import ProcessPoolExecutor
from tqdm import tqdm  # Professional Progress Bar

# ================= CONFIGURATION =================
@dataclass
class Config:
    """Central configuration for the pipeline."""
    INPUT_DIR: Path = Path(r"C:\Users\vipin\Downloads\ProductizeTech - AI Fulltime Assignment-20251122T062524Z-1-001\ProductizeTech - AI Fulltime Assignment\Task 1 - RGB Thermal Overlay Algorithm\input-images")
    OUTPUT_DIR: Path = Path(r"C:\Users\vipin\Downloads\ProductizeTech - AI Fulltime Assignment-20251122T062524Z-1-001\ProductizeTech - AI Fulltime Assignment\Task 1 - RGB Thermal Overlay Algorithm\task_1_output")
    
    # Alignment Parameters
    SCALE_RANGE: Tuple[float, float] = (0.90, 1.11)
    SCALE_STEP: float = 0.02
    
    # Visual Parameters
    ALPHA: float = 0.6  # RGB Intensity
    BETA: float = 0.4   # Thermal Intensity
    COLORMAP: int = cv2.COLORMAP_JET
    
    # System
    MAX_WORKERS: int = 4  # Adjust based on your CPU cores

# ================= LOGGING SETUP =================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("alignment_pipeline.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ================= CORE ENGINE =================
class AlignmentEngine:
    """
    Encapsulates all logic for Image Registration and Overlay.
    """

    @staticmethod
    def extract_skeleton(img: np.ndarray) -> np.ndarray:
        """
        Extracts vertical structural elements (poles) using adaptive thresholds.
        """
        if len(img.shape) == 3:
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        else:
            gray = img.copy()

        # 1. Noise Reduction (Gaussian Blur)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)

        # 2. Dynamic Range Normalization
        norm = cv2.normalize(blurred, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)

        # 3. Vertical Edge Detection (Sobel Y-axis ignored)
        sobelx = cv2.Sobel(norm, cv2.CV_64F, 1, 0, ksize=3)
        abs_sobelx = np.absolute(sobelx)
        skeleton = np.uint8(abs_sobelx)

        # 4. Adaptive Thresholding
        # Calculates median to set dynamic threshold floor
        v = np.median(skeleton)
        lower = int(max(40, (1.0 - 0.33) * v))
        _, binary = cv2.threshold(skeleton, lower, 255, cv2.THRESH_BINARY)

        # 5. Morphological Cleanup
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
        clean = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel)

        return clean

    @classmethod
    def find_optimal_alignment(cls, rgb_img: np.ndarray, thermal_raw: np.ndarray, config: Config) -> np.ndarray:
        """
        Performs Multi-Scale Template Matching to find best alignment.
        Returns the aligned thermal image (same size as RGB).
        """
        h_rgb, w_rgb = rgb_img.shape[:2]
        
        # Pre-calculate RGB skeleton once
        skel_rgb = cls.extract_skeleton(rgb_img)

        best_result = {
            "score": -1.0,
            "scale": 1.0,
            "loc": (0, 0),
            "offset": (0, 0)
        }

        # Generate scales
        scales = np.arange(config.SCALE_RANGE[0], config.SCALE_RANGE[1], config.SCALE_STEP)

        for scale in scales:
            # Resize thermal
            t_w, t_h = int(w_rgb * scale), int(h_rgb * scale)
            thermal_scaled = cv2.resize(thermal_raw, (t_w, t_h))
            
            skel_thermal = cls.extract_skeleton(thermal_scaled)

            # Crop Template (Center 50%)
            th, tw = skel_thermal.shape
            crop_h, crop_w = int(th * 0.5), int(tw * 0.5)
            cy, cx = th // 2, tw // 2
            
            # ROI Coordinates
            y1, y2 = cy - crop_h // 2, cy + crop_h // 2
            x1, x2 = cx - crop_w // 2, cx + crop_w // 2
            
            template = skel_thermal[y1:y2, x1:x2]

            # Validation
            if template.shape[0] >= h_rgb or template.shape[1] >= w_rgb:
                continue

            # Template Matching
            res = cv2.matchTemplate(skel_rgb, template, cv2.TM_CCOEFF_NORMED)
            _, max_val, _, max_loc = cv2.minMaxLoc(res)

            if max_val > best_result["score"]:
                best_result = {
                    "score": max_val,
                    "scale": scale,
                    "loc": max_loc,          # Top-left in RGB
                    "offset": (x1, y1)       # Top-left in Thermal Scaled
                }

        # --- RECONSTRUCTION ---
        final_w = int(w_rgb * best_result["scale"])
        final_h = int(h_rgb * best_result["scale"])
        thermal_best = cv2.resize(thermal_raw, (final_w, final_h))
        
        aligned_thermal = np.zeros((h_rgb, w_rgb), dtype=np.uint8)
        
        match_x, match_y = best_result["loc"]
        off_x, off_y = best_result["offset"]
        
        start_x = match_x - off_x
        start_y = match_y - off_y
        
        # Calculate Intersection
        src_x1 = max(0, -start_x)
        src_y1 = max(0, -start_y)
        src_x2 = min(final_w, w_rgb - start_x)
        src_y2 = min(final_h, h_rgb - start_y)
        
        dst_x1 = max(0, start_x)
        dst_y1 = max(0, start_y)
        dst_x2 = min(w_rgb, start_x + final_w)
        dst_y2 = min(h_rgb, start_y + final_h)
        
        if (dst_x2 > dst_x1) and (dst_y2 > dst_y1):
            aligned_thermal[dst_y1:dst_y2, dst_x1:dst_x2] = thermal_best[src_y1:src_y2, src_x1:src_x2]
            
        return aligned_thermal

    @staticmethod
    def create_smart_overlay(rgb: np.ndarray, aligned_thermal: np.ndarray, config: Config) -> np.ndarray:
        """
        Creates an overlay that preserves RGB sky clarity using masking.
        """
        # Contrast Enhancement (CLAHE)
        clahe = cv2.createCLAHE(clipLimit=4.0, tileGridSize=(8,8))
        enhanced = clahe.apply(aligned_thermal)
        
        # Apply Colormap
        thermal_color = cv2.applyColorMap(enhanced, config.COLORMAP)
        
        # Smart Masking: Only blend where thermal data exists (> 5 pixel value)
        # This keeps the sky blue instead of blending it with black thermal background
        mask = aligned_thermal > 5
        
        output = rgb.copy()
        
        # Extract Regions of Interest
        roi_rgb = output[mask]
        roi_thermal = thermal_color[mask]
        
        # Alpha Blending
        blended = cv2.addWeighted(roi_rgb, config.ALPHA, roi_thermal, config.BETA, 0)
        
        # Apply back
        output[mask] = blended
        return output

# ================= WORKER FUNCTION =================
def process_single_pair(file_path: Path) -> str:
    """
    Worker function for Multiprocessing.
    Returns status string.
    """
    try:
        config = Config() # Load defaults
        
        # Path Management
        base_name = file_path.name.replace("_Z.JPG", "")
        thermal_name = base_name + "_T.JPG"
        thermal_path = file_path.parent / thermal_name
        
        if not thermal_path.exists():
            return f"[SKIP] Missing Thermal: {base_name}"
            
        # Read Images
        rgb = cv2.imread(str(file_path))
        thermal_raw = cv2.imread(str(thermal_path), cv2.IMREAD_GRAYSCALE)
        
        if rgb is None or thermal_raw is None:
            return f"[ERR ] Read Failed: {base_name}"
            
        # --- PIPELINE EXECUTION ---
        engine = AlignmentEngine()
        
        # 1. Alignment
        aligned_gray = engine.find_optimal_alignment(rgb, thermal_raw, config)
        
        # 2. Overlay
        final_result = engine.create_smart_overlay(rgb, aligned_gray, config)
        
        # 3. Save
        output_path = config.OUTPUT_DIR / "output" / f"{base_name}_AT.JPG"
        cv2.imwrite(str(output_path), final_result)
        
        return f"[OK  ] Processed: {base_name}"

    except Exception as e:
        return f"[FAIL] Exception {base_name}: {str(e)}"

# ================= MAIN ENTRY POINT =================
if __name__ == "__main__":
    # Setup Directories
    cfg = Config()
    (cfg.OUTPUT_DIR / "output").mkdir(parents=True, exist_ok=True)
    
    # Gather Files
    rgb_files = [f for f in cfg.INPUT_DIR.glob("*_Z.JPG")]
    
    logger.info(f"Starting pipeline on {len(rgb_files)} image pairs...")
    logger.info(f"Using {cfg.MAX_WORKERS} CPU cores.")
    
    # Run Parallel Processing
    with ProcessPoolExecutor(max_workers=cfg.MAX_WORKERS) as executor:
        results = list(tqdm(executor.map(process_single_pair, rgb_files), total=len(rgb_files), unit="img"))
        
    # Final Report
    logger.info("--- Processing Summary ---")
    for res in results:
        if "[FAIL]" in res or "[ERR ]" in res:
            logger.error(res)
        elif "[SKIP]" in res:
            logger.warning(res)
            
    logger.info(f"Output saved to: {cfg.OUTPUT_DIR}")