import cv2

# Open the default webcam (0 usually means your built-in/primary camera)
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Could not open webcam. Try changing the number in VideoCapture(0) to 1.")
else:
    print("Webcam opened successfully! Press 'q' to quit.")

while True:
    # Read one frame from the webcam
    ret, frame = cap.read()

    if not ret:
        print("Failed to grab frame.")
        break

    # Show that frame in a window titled "Webcam Feed"
    cv2.imshow("Webcam Feed", frame)

    # Wait 1 millisecond for a keypress; if it's 'q', break the loop
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the webcam and close the window
cap.release()
cv2.destroyAllWindows()