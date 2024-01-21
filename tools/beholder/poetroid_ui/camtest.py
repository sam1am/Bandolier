import cv2

def test_camera(camera_index):
    cap = cv2.VideoCapture(camera_index)
    if not cap.isOpened():
        print(f"Error: Could not open camera at index {camera_index}.")
        return

    # Warm-up the camera, capture a few frames to allow the camera's auto-exposure to adjust
    for _ in range(10):
        ret, frame = cap.read()
        if not ret:
            print("Error: Could not read frame from the camera.")
            cap.release()
            return

    # Now that the camera has warmed up, let's use the latest frame
    cv2.imshow(f'Camera Test - Index {camera_index}', frame)
    print("Press 'q' to close the window")
    
    while True:
        if cv2.waitKey(1) & 0xFF == ord('q'):  # Press 'q' to close the window
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    test_camera(0)
    # If index 0 didn't work, try the next one
    # test_camera(1)
