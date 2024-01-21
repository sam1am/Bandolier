import cv2

def stream_camera(camera_index):
    cap = cv2.VideoCapture(camera_index)
    if not cap.isOpened():
        print(f"Error: Could not open camera at index {camera_index}.")
        return

    print("Streaming... Press 'q' to quit.")
    
    while True:
        # Capture a single frame
        ret, frame = cap.read()
        if not ret:
            print("Error: Could not read frame from the camera.")
            break
        
        # Display the resulting frame
        cv2.imshow(f'Camera Live Feed - Index {camera_index}', frame)
        
        # If 'q' is pressed on the keyboard, exit the loop
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # When everything done, release the capture
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    # Start streaming from the first camera index detected
    stream_camera(1)
    # If index 0 didn't work, you can try other indices like 1, 2, etc.
    # stream_camera(1)
    # stream_camera(2)
