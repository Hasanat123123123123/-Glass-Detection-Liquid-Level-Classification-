# -*- coding: utf-8 -*-
"""Assignment_02DL.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1v_XyHc94kfnfvKZ31vf1vCK8M1DxpzSH
"""

import os
import shutil
from sklearn.model_selection import train_test_split

from roboflow import Roboflow
rf = Roboflow(api_key="PNlE3kRSgrex4aXZi03W")
project = rf.workspace("mian-muhammad-hasanat-dxtd6").project("glass-level-lequid-detection")
version = project.version(2)
dataset = version.download("yolov11")

pip install roboflow

# Commented out IPython magic to ensure Python compatibility.
# %pip install ultralytics supervision roboflow
import ultralytics
ultralytics.checks()

!yolo task=detect mode=train model=yolo11s.pt data={dataset.location}/data.yaml epochs=10 imgsz=640 plots=True

from IPython.display import Image as IPyImage

HOME = '/content'

IPyImage(filename=f'{HOME}/runs/detect/train/val_batch0_pred.jpg', width=600)

!yolo task=detect mode=predict model={HOME}/runs/detect/train/weights/best.pt conf=0.25 source={dataset.location}//content/glass-level-lequid-detection-2/test save=True

project.version(dataset.version).deploy(model_type="yolov11", model_path=f"{HOME}/runs/detect/train/")

!pip install inference

pip install scikit-learn

pip install pyyaml

!yolo task=detect mode=predict model={HOME}/runs/detect/train/weights/best.pt conf=0.25 source={dataset.location}/ /content/glass-level-lequid-detection-2/test save=True

import os, random, cv2
import supervision as sv
import IPython
import inference

# Define API key directly
api_key = "PNlE3kRSgrex4aXZi03W"

# Correct the model initialization
model_id = project.id.split("/")[1] + "/" + dataset.version
model = inference.get_model(model_id, api_key)

# Correct the location of test set images
test_set_loc = os.path.join(dataset.location, "/content/glass-level-lequid-detection-2/test/images")  # Ensure correct path
test_images = os.listdir(test_set_loc)

# Run inference on 4 random test images, or fewer if fewer images are available
for img_name in random.sample(test_images, min(4, len(test_images))):
    print("Running inference on " + img_name)

    # Load image
    image = cv2.imread(os.path.join(test_set_loc, img_name))

    # Perform inference
    results = model.infer(image, confidence=0.4, overlap=30)[0]
    detections = sv.Detections.from_inference(results)

    # Annotate boxes and labels
    box_annotator = sv.BoxAnnotator()
    label_annotator = sv.LabelAnnotator()
    annotated_image = box_annotator.annotate(scene=image, detections=detections)
    annotated_image = label_annotator.annotate(scene=annotated_image, detections=detections)

    # Display annotated image
    _, ret = cv2.imencode('.jpg', annotated_image)
    i = IPython.display.Image(data=ret)
    IPython.display.display(i)

import cv2
import supervision as sv

def live_webcam_inference(model, confidence=0.4, overlap=30):
    # Open webcam
    cap = cv2.VideoCapture(0)  # Use 0 for the default camera

    if not cap.isOpened():
        print("Error: Unable to access the webcam")
        return

    print("Press 'q' to quit.")
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Error: Unable to read frame from webcam")
            break

        # Perform inference
        results = model.infer(frame, confidence=confidence, overlap=overlap)[0]
        detections = sv.Detections.from_inference(results)

        # Annotate detections
        box_annotator = sv.BoxAnnotator()
        annotated_frame = box_annotator.annotate(scene=frame, detections=detections)

        # Display annotated frame
        cv2.imshow("Live Webcam Inference", annotated_frame)

        # Exit on 'q' key press
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

def video_inference(model, input_video_path, output_video_path, confidence=0.4, overlap=30):
    # Open the video file
    cap = cv2.VideoCapture(input_video_path)

    if not cap.isOpened():
        print("Error: Unable to open the video file")
        return

    # Get video properties
    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = int(cap.get(cv2.CAP_PROP_FPS))

    # Define the codec and create a VideoWriter object
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_video_path, fourcc, fps, (frame_width, frame_height))

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        # Perform inference
        results = model.infer(frame, confidence=confidence, overlap=overlap)[0]
        detections = sv.Detections.from_inference(results)

        # Annotate detections
        box_annotator = sv.BoxAnnotator()
        annotated_frame = box_annotator.annotate(scene=frame, detections=detections)

        # Write annotated frame to output video
        out.write(annotated_frame)

    cap.release()
    out.release()
    print(f"Annotated video saved at {output_video_path}")

import tkinter as tk
from tkinter import filedialog

def start_gui(model):
    def run_webcam_inference():
        live_webcam_inference(model)

    def run_video_inference():
        input_video_path = filedialog.askopenfilename(title="Select Video File")
        if input_video_path:
            output_video_path = filedialog.asksaveasfilename(defaultextension=".mp4", title="Save Annotated Video As")
            if output_video_path:
                video_inference(model, input_video_path, output_video_path)

    # Create the main window
    root = tk.Tk()
    root.title("Inference Demo")

    # Create buttons
    webcam_button = tk.Button(root, text="Run Webcam Inference", command=run_webcam_inference)
    webcam_button.pack(pady=10)

    video_button = tk.Button(root, text="Run Video Inference", command=run_video_inference)
    video_button.pack(pady=10)

    # Run the GUI loop
    root.mainloop()

!pip install gradio

import os
import inference

# Initialize the model
api_key = "PNlE3kRSgrex4aXZi03W"
model_id = project.id.split("/")[1] + "/" + dataset.version
model = inference.get_model(model_id, api_key)

# Start the GUI
start_gui(model)