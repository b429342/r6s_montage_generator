# R6S Montage Generator

This project processes a **Rainbow Six Siege** gameplay video to automatically detect kills using OCR (Optical Character Recognition) on the kill feed. It extracts short clips around each detected kill, enabling fast creation of highlight montages.

---

## 🔧 How It Works

1. **Input a video** — currently by pasting a full file path (support for easier selection may come later).
2. **Frame processing**:
   - Uses OpenCV to enhance frames before OCR.
   - Steps include: cropping to kill feed → grayscaling → binary thresholding → resizing.
3. **Text detection**:
   - Every 4 seconds of footage is analyzed (to accommodate variable frame rates).
   - Tesseract OCR scans for the player's name in the kill feed.
4. **Kill detection**:
   - When the player’s name is detected, the timestamp is saved.
5. **Clip extraction**:
   - For each timestamp, FFmpeg extracts a clip that includes 5 seconds before and after the kill.
6. **Montage creation** (optional):
   - All clips can be concatenated into one final video using FFmpeg.

---

## 📁 Project Structure

- `r6montage.py` — core script to run the detection and clipping.
- `SiegeMontageOutputs/` — output folder containing:
  - `kill_clips/` — all extracted clips.
  - `kill_times.txt/` - holds all times where a kill happened. (optional)
  - `extracted_frames/` - all the frames extracted by opencv. (optional)
  - `extracted_text.txt` - all text that ocr extracted. (optional)
The optinal folders and files can be used for debugging and tweaking. If not debugging then comment out to be faster. 

---

## 🛠️ Features and Notes

- Processes one video at a time (batch/folder support planned).
- Uses a 4-second interval for frame sampling — this can cause timing issues if kills happen between samples.
- Debugging options like frame saving are available but can be toggled off.
- Aspect ratio is currently fixed (cropping is hardcoded). Will need to generalize with OpenCV’s drag-and-select UI for broader compatibility.

---

## ⚠️ Known Limitations

- **Frame skipping**: If a kill happens very close to a timestamp boundary, the clip might miss it.
- **Concatenation stutter**: Using `ffmpeg -c copy` can cause freezing between clips. Future versions may use re-encoding or transitions for smoother playback.
- **OCR accuracy**: Tesseract is not fully optimized and may miss some detections.

---

## 💡 Future Improvements

- GUI for selecting videos or folders.
- Smarter OCR handling (e.g. confidence filtering, multiple passes).
- Support for different resolutions/aspect ratios.
- Improved clip timing and precision.
- Smoother concatenation (via re-encoding or transitions).

---


