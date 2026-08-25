import cv2
import numpy as np
import time
from scipy.signal import butter, filtfilt, find_peaks

cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Could not open webcam.")
    exit()

print("Warming up camera for 5 seconds...")
warmup_end = time.time() + 5
while time.time() < warmup_end:
    ret, frame = cap.read()
    cv2.imshow("Warming up...", frame)
    cv2.waitKey(1)
cv2.destroyWindow("Warming up...")

# --- SETTINGS ---
window_seconds = 10        # how many seconds of data we analyze at once
update_every = 1.0         # recalculate BPM this often (seconds)
box_size = 100

green_values = []
timestamps = []
current_bpm = 0
last_update_time = time.time()
recording_start = time.time()
bpm_history = []  # stores recent BPM readings for smoothing

print("Live pulse detection running. Press 'q' to quit.")

while True:
    ret, frame = cap.read()
    if not ret:
        break

    height, width, _ = frame.shape
    x1 = width // 2 - box_size // 2
    y1 = height // 2 - box_size // 2
    x2 = x1 + box_size
    y2 = y1 + box_size

    roi = frame[y1:y2, x1:x2]
    green_avg = np.mean(roi[:, :, 1])
    now = time.time()

    green_values.append(green_avg)
    timestamps.append(now)

    # Keep only the last `window_seconds` worth of data (a "rolling window")
    while timestamps and (now - timestamps[0]) > window_seconds:
        timestamps.pop(0)
        green_values.pop(0)

    # Recalculate BPM periodically, only once we have enough data
    if (now - last_update_time) >= update_every and len(green_values) > 30:
        last_update_time = now

        signal = np.array(green_values)
        times = np.array(timestamps)
        span = times[-1] - times[0]
        fps = len(signal) / span if span > 0 else 0

        if fps > 0:
            nyquist = fps / 2
            low = 0.7 / nyquist
            high = 3.0 / nyquist
            # Guard against invalid filter ranges if fps is too low
            if 0 < low < high < 1:
                b, a = butter(N=3, Wn=[low, high], btype='band')
                filtered = filtfilt(b, a, signal)

                min_distance = max(1, int(fps * 60 / 180))
                min_height = np.std(filtered) * 0.3  # lowered from 0.5 to catch weaker beats
                peaks, _ = find_peaks(filtered, distance=min_distance, height=min_height)

                # Only trust readings once the rolling window is actually full,
                # and once we've been recording for at least window_seconds
                window_is_full = (time.time() - recording_start) >= window_seconds

                if len(peaks) > 1 and window_is_full:
                    raw_bpm = (len(peaks) / span) * 60

                    # Smooth the reading by averaging the last few calculations
                    # (this is what makes hospital monitors look steady instead of jumpy)
                    bpm_history.append(raw_bpm)
                    if len(bpm_history) > 5:
                        bpm_history.pop(0)
                    current_bpm = sum(bpm_history) / len(bpm_history)

    # Draw the ROI box
    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

    # Display the current BPM on the video feed
    still_filling = (time.time() - recording_start) < window_seconds
    if still_filling:
        text = "Calculating... (please hold still)"
    elif current_bpm > 0:
        text = f"BPM: {current_bpm:.1f}"
    else:
        text = "Calculating..."
    cv2.putText(frame, text, (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    cv2.putText(frame, "Place finger over box, hold still", (20, height - 20),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)

    cv2.imshow("Live Pulse Detector - press 'q' to quit", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
