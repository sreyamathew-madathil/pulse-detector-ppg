# Pulse Detector — Real-Time Heart Rate from a Webcam (PPG)

A Python application that measures your heart rate in real time using nothing but a standard webcam — no extra hardware required. It works by detecting the same tiny light-absorption changes in your skin that smartwatches and hospital pulse oximeters use, a technique called **photoplethysmography (PPG)**.

## How It Works

Every heartbeat pushes a pulse of blood through the capillaries in your fingertip. More blood means more light absorbed by the skin; less blood means more light reflected. A webcam can actually pick up this subtle brightness change — invisible to the eye, but detectable through signal processing.

**The pipeline:**
1. **Capture** — read live video frames from the webcam
2. **Extract** — isolate a small region of interest and average its green color channel each frame (green shows the strongest pulsatile signal)
3. **Filter** — apply a bandpass filter (0.7–3 Hz) to isolate the frequency range of realistic human heart rates (40–180 BPM) and remove noise from lighting drift and hand movement
4. **Detect** — find peaks in the filtered signal, each representing one heartbeat
5. **Calculate** — convert beats-per-window into beats-per-minute (BPM), continuously updating on a rolling time window

## Demo

*(Add a screenshot or short GIF of the live BPM reading here — this is the first thing people will look at.)*

## Tech Stack

- **Python 3**
- **OpenCV** — webcam access and image handling
- **NumPy** — numerical operations on pixel data
- **SciPy** — bandpass filtering (`butter`, `filtfilt`) and peak detection (`find_peaks`)
- **Matplotlib** — signal visualization during development

## How to Run

1. Clone this repository:
   ```
   git clone https://github.com/sreyamathew-madathil/pulse-detector-ppg.git
   cd pulse-detector-ppg
   ```
2. Install the required libraries:
   ```
   pip install opencv-python numpy scipy matplotlib
   ```
3. Run the live detector:
   ```
   python pulse_extract.py
   ```
4. When prompted, place your fingertip fully over the green box on screen and hold still. After a few seconds, your live BPM reading will appear on the video feed. Press `q` to quit.

## Validation

Estimated BPM was cross-checked against a manual pulse count (radial artery, 15-second count × 4) and matched within 1 BPM (72 manual vs. 71.9 detected) under steady, well-lit conditions.

## Known Limitations

This is an educational project, not a medical device, and has some real, documented limitations discovered during testing:

- **Auto-exposure interference:** many consumer webcams gradually adjust exposure/gain to stabilize the image. Once "locked in," this can suppress the very small pulsatile brightness changes the algorithm relies on, weakening the signal over longer recordings.
- **Motion sensitivity:** even small finger movements introduce noise that can be mistaken for signal without careful filtering and peak-height thresholds.
- **Lighting dependency:** results are noticeably better under consistent, moderate lighting; both very bright light (sensor saturation) and dim light (weak signal) degrade accuracy.
- **Not a diagnostic tool:** this project demonstrates the underlying signal-processing technique and is not validated for any clinical or medical use.

## Background

Built as a self-directed project to apply biomedical signal processing concepts — the same PPG principle used in real pulse oximeters and smartwatches — using only free, open-source tools. This was also a first hands-on project in Python, OpenCV, and digital signal filtering.

## Future Improvements

- Add signal quality detection to auto-flag unreliable readings
- Explore additional color channels or multi-region averaging for more robust extraction
- Package as a simple web app for easier sharing and demonstration
