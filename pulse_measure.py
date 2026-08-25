import cv2
import numpy as np
import time
from scipy.signal import butter, filtfilt, find_peaks

cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Could not open webcam.")
    exit()

box_size = 100
warmup_seconds = 5
measure_seconds = 15  # length of the actual measurement

print(f"Warming up camera for {warmup_seconds} seconds...")
warmup_end = time.time() + warmup_seconds
while time.time() < warmup_end:
    ret, frame = cap.read()
    if not ret:
        break
    height, width, _ = frame.shape
    x1 = width // 2 - box_size // 2
    y1 = height // 2 - box_size // 2
    x2 = x1 + box_size
    y2 = y1 + box_size
    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
    remaining = int(warmup_end - time.time()) + 1
    cv2.putText(frame, f"Get ready... {remaining}", (20, 40),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
    cv2.imshow("Pulse Measurement", frame)
    cv2.waitKey(1)

print(f"Measuring for {measure_seconds} seconds. Hold your finger steady!")

green_values = []
timestamps = []
measure_start = time.time()

while time.time() - measure_start < measure_seconds:
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
    green_values.append(green_avg)
    timestamps.append(time.time())

    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
    remaining = measure_seconds - (time.time() - measure_start)
    cv2.putText(frame, f"Measuring... {remaining:.0f}s left", (20, 40),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    cv2.putText(frame, "Hold completely still", (20, height - 20),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
    cv2.imshow("Pulse Measurement", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# --- Process the full measurement as one clean signal ---
green_values = np.array(green_values)
timestamps = np.array(timestamps)
span = timestamps[-1] - timestamps[0]
fps = len(green_values) / span if span > 0 else 0

final_bpm = None

if fps > 0 and len(green_values) > 30:
    nyquist = fps / 2
    low = 0.7 / nyquist
    high = 3.0 / nyquist

    if 0 < low < high < 1:
        b, a = butter(N=3, Wn=[low, high], btype='band')
        filtered = filtfilt(b, a, green_values)

        min_distance = max(1, int(fps * 60 / 180))
        min_height = np.std(filtered) * 0.3
        peaks, _ = find_peaks(filtered, distance=min_distance, height=min_height)

        if len(peaks) > 1:
            final_bpm = (len(peaks) / span) * 60

# --- Show the final result, held on screen ---
result_end = time.time() + 6  # show result for 6 seconds
while time.time() < result_end:
    ret, frame = cap.read()
    if not ret:
        break

    if final_bpm is not None:
        text = f"Final reading: {final_bpm:.1f} BPM"
        color = (0, 255, 0)
    else:
        text = "Could not get a reliable reading - try again"
        color = (0, 0, 255)

    cv2.putText(frame, text, (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.9, color, 2)
    cv2.putText(frame, "Press 'q' to close", (20, frame.shape[0] - 20),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
    cv2.imshow("Pulse Measurement", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()

if final_bpm is not None:
    print(f"\nFINAL RESULT: {final_bpm:.1f} BPM")
else:
    print("\nCould not get a reliable reading. Try again with steadier hand / better lighting.")
