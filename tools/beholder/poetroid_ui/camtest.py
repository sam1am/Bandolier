import cv2
import time

def test_camera(camera_index):
    cap = cv2.VideoCapture(camera_index)
    if not cap.isOpened():
        print(f"Error: Could not open camera at index {camera_index}.")
        return
    
    warm_up_time = 2  # seconds
    start_time = time.time()
    
    print("Warming up the camera...")
    while time.time() - start_time < warm_up_time:
        ret, frame = cap.read()
        if not ret:
            print("Error: Could not read frame from the camera during warm-up.")
            cap.release()
            return
    
    # After the warm-up, capture one frame to display
    ret, frame = cap.read()
    if not ret:
        print("Error: Failed to capture the frame.")
        cap.release()
        return
    
    # Display the captured frame
    cv2.imshow(f'Camera Test - Index {camera_index}', frame)
    
    # Press any key to exit
    print("Press any key to close the window")
    cv2.waitKey(0)
    
    # Cleanup
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    # Replace with the correct camera index
    camera_index = 1
    test_camera(camera_index)
    # Repeat with different indices, if necessary
