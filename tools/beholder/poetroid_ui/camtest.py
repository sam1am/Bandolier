import cv2

def test_camera(camera_index):
    cap = cv2.VideoCapture(camera_index)
    if not cap.isOpened():
        print(f"Error: Could not open camera at index {camera_index}.")
        return

    ret, frame = cap.read()
    cap.release()

    if not ret:
        print("Error: Could not read frame from the camera.")
        return

    cv2.imshow(f'Camera Test - Index {camera_index}', frame)
    cv2.waitKey(0)  # Wait for a key press to close the window
    cv2.destroyAllWindows()

if __name__ == "__main__":
    # First, try the most common index which is 0.
    test_camera(1)
    # If nothing displays, you can uncomment the next line to try with index 1,
    # if you believe that could be the correct index as mentioned previously.
    # test_camera(1)
