import cv2
import threading
import tkinter as tk
from tkinter import messagebox
import time

# Load the pre-trained Haar Cascade model
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

running = False

# Stability filter variables
previous_faces = []
stable_faces = []
frame_count = 0

# Function to start detection
def start_detection():
    global running
    running = True
    thread = threading.Thread(target=detect_faces)
    thread.start()

# Function to stop detection
def stop_detection():
    global running
    running = False
    messagebox.showinfo("Info", "Face Detection Stopped!")

# Function for stabilized face detection
def detect_faces():
    global previous_faces, stable_faces, frame_count

    video = cv2.VideoCapture(0)
    previous_faces = []
    stable_faces = []
    frame_count = 0

    while running:
        ret, frame = video.read()
        if not ret:
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Detect faces with tuned parameters for better accuracy
        faces = face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.2,
            minNeighbors=7,
            minSize=(80, 80)
        )

        frame_count += 1

        # Stability filter: check if face positions are similar in consecutive frames
        if frame_count % 2 == 0:  # every 2nd frame
            stable_faces = []
            for (x, y, w, h) in faces:
                for (px, py, pw, ph) in previous_faces:
                    if abs(x - px) < 30 and abs(y - py) < 30:
                        stable_faces.append((x, y, w, h))
                        break
            previous_faces = faces

        # Draw only stable faces
        for (x, y, w, h) in stable_faces:
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

        # Show the number of detected stable faces
        face_count = len(stable_faces)
        text = f"Faces Detected: {face_count}"
        cv2.putText(frame, text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 0, 0), 2)

        cv2.imshow("Stable Face Detection", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    video.release()
    cv2.destroyAllWindows()

# GUI Setup
window = tk.Tk()
window.title("🧠 Stable Face Detection App")
window.geometry("400x320")
window.config(bg="#e3f2fd")

title = tk.Label(window, text="Stable Face Detection", font=("Arial", 18, "bold"), bg="#e3f2fd", fg="#0d47a1")
title.pack(pady=20)

start_btn = tk.Button(window, text="Start Detection", font=("Arial", 12, "bold"),
                      bg="#4CAF50", fg="white", command=start_detection)
start_btn.pack(pady=10)

stop_btn = tk.Button(window, text="Stop Detection", font=("Arial", 12, "bold"),
                     bg="#f44336", fg="white", command=stop_detection)
stop_btn.pack(pady=10)

exit_btn = tk.Button(window, text="Exit", font=("Arial", 12, "bold"),
                     bg="#9E9E9E", fg="white", command=window.destroy)
exit_btn.pack(pady=10)

info = tk.Label(window, text="Press 'q' in camera window to close it.", font=("Arial", 10),
                bg="#e3f2fd", fg="#333")
info.pack(pady=20)

window.mainloop()
