import argparse

import cv2
import numpy as np
import os
import glob
import time

def load_yolo(model_path, config_path):
    net = cv2.dnn.readNet(model_path, config_path)
    layer_names = net.getLayerNames()
    output_layers_names = [layer_names[i - 1] for i in net.getUnconnectedOutLayers()]
    return net, output_layers_names

def read_image(image_path, method):
    if not method in ['2d', '3d']:
        raise ValueError("Invalid method. Choose either '2d' or '3d'.")
    if method == '2d':
        image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    else:
        image = cv2.imread(image_path)

    if image is None:
        raise Exception(f"Error reading {image_path}")

    if method == '2d':
        image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)

    return image

def detect_human_bodies(image_path, yolo_net, output_layers_names, method):
    image = read_image(image_path, method)

    blob = cv2.dnn.blobFromImage(image, 0.00392, (416, 416), (0, 0, 0), True, crop=False)
    yolo_net.setInput(blob)
    detections = yolo_net.forward(output_layers_names)

    human_bodies = []
    for detection in detections:
        for attr in detection:
            scores = attr[5:]
            class_id = np.argmax(scores)
            confidence = scores[class_id]
            if confidence > 0.7:
                center_x = int(attr[0] * image.shape[1])
                center_y = int(attr[1] * image.shape[0])
                w = int(attr[2] * image.shape[1])
                h = int(attr[3] * image.shape[0])
                x = center_x - w // 2
                y = center_y - h // 2
                if class_id == 0:
                    human_bodies.append((x, y, w, h, confidence))

    return human_bodies

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Detect human bodies in images using YOLOv4")
    parser.add_argument("images_directory", type=str, help="Path to the directory containing images to be processed")
    parser.add_argument("output_detections_directory", type=str, help="Path to the directory for saving detection results")
    parser.add_argument("method", type=str, help="Method to use for detection (2d or 3d)", default="2d")
    parser.add_argument("--model_file", type=str, help="Path to the YOLOv4 model weights file", default="parameters/yolov4.weights")
    parser.add_argument("--config_file", type=str, help="Path to the YOLOv4 model configuration file", default="parameters/yolov4.cfg")

    args = parser.parse_args()

    METHOD = args.method
    model_path = args.model_file
    config_path = args.config_file
    images_directory = args.images_directory
    output_detections_directory = args.output_detections_directory
    os.makedirs(output_detections_directory, exist_ok=True)
    yolo_net, output_layers_names = load_yolo(model_path, config_path)

    # Get list of all images in the directory
    image_paths = glob.glob(os.path.join(images_directory, "*.png"))

    # Initialize counters and lists for statistics
    images_processed = 0
    total_images = len([f for f in os.listdir(images_directory)])  # Count number of images to be processed
    total_detections = 0
    errors = []

    # Start timer
    start_time = time.time()

    # Process each image in the directory
    for image_path in image_paths:
        error_msg=None
        images_processed += 1
        print(f"\rProgress: {(100 * images_processed / total_images):.2f}%", end="")
        try:
            human_bodies = detect_human_bodies(image_path, yolo_net, output_layers_names, method=METHOD)
            if human_bodies:
                total_detections += len(human_bodies)
                detection_path = os.path.join(output_detections_directory, os.path.basename(image_path).replace('.png', '.txt'))
                with open(detection_path, 'w') as f:
                    for (x, y, w, h, confidence) in human_bodies:
                        f.write(f"{x} {y} {w} {h} {confidence}\n")
            else:
                error_msg = "No human bodies detected"

        except Exception as e:
            error_msg = str(e)

        if error_msg:
            print(f"\nError processing {image_path}: {error_msg}")
            errors.append(f"{image_path}: {error_msg}")

    # Stop timer
    end_time = time.time()

    # Print detailed statistics
    print(f"Total images processed: {images_processed}")
    print(f"Total detections made: {total_detections}")
    print(f"Average detections per image: {total_detections / images_processed:.2f}")
    print(f"Error processing images: {len(errors)}")
    print(f"Time taken: {end_time - start_time:.2f} seconds")

    # Optional: Save the list of errors to a file
    with open(os.path.join(output_detections_directory, 'errors.log'), 'w') as f:
        for item in errors:
            f.write("%s\n" % item)

    print("All images have been processed and detection results are saved.")

