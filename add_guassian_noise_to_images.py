import shutil

import cv2
import numpy as np
import os
import glob
import time
import argparse

# Define functions for differential privacy noise addition
def calculate_sensitivity_rgb_images(image_data):
    return np.max(image_data)


# Function to blur a region of the image
def blur_region(image, startX, startY, endX, endY):
    startX = max(0, startX)
    startY = max(0, startY)
    endX = min(image.shape[1], endX)
    endY = min(image.shape[0], endY)

    roi = image[startY:endY, startX:endX]

    if roi.size == 0:
        return image

    blurred_roi = cv2.GaussianBlur(roi, (99, 99), 30)
    image[startY:endY, startX:endX] = blurred_roi
    return image

def draw_bounding_boxes(image, boxes):
    for (x, y, w, h) in boxes:
        cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)
    return image

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

if __name__ == "__main__":
    argparser = argparse.ArgumentParser(description='Add Laplacian noise to images based on detection boxes')
    argparser.add_argument('image_directory', type=str,  help='Path to the directory containing images')
    argparser.add_argument('detection_directory', type=str, help='Path to the directory containing detection results')
    argparser.add_argument('output_directory', type=str, help='Path to the directory to save the output images')
    argparser.add_argument("method", type=str, help="Method to use for detection (2d or 3d)")

    args = argparser.parse_args()

    METHOD = args.method

    image_directory = args.image_directory
    detection_directory = args.detection_directory
    output_directory = args.output_directory
    os.makedirs(output_directory, exist_ok=True)

    detection_paths = glob.glob(os.path.join(detection_directory, "*.txt"))

    # Initialize counters and lists for statistics
    images_processed = 0
    total_images = len([f for f in os.listdir(image_directory)])  # Count number of images to be processed
    blurred_images = 0
    errors = []

    # Start timer
    start_time = time.time()

    # Process each detection file in the directory
    for detection_path in detection_paths:
        images_processed += 1
        print(f"\rProgress: {(100 * images_processed / total_images):.2f}%", end=" ")
        error_msg = None
        try:
            image_path = os.path.join(image_directory, os.path.basename(detection_path).replace('.txt', '.png'))
            image = read_image(image_path, METHOD)

            output_path = os.path.join(output_directory, os.path.basename(image_path))

            boxes = []
            confidences = []
            with open(detection_path, 'r') as f:
                for line in f:
                    x, y, w, h = map(int, line.strip().split()[:4])
                    boxes.append((x, y, w, h))
                    confidences.append(float(line.strip().split()[4]))

            indices = cv2.dnn.NMSBoxes(boxes, confidences, score_threshold=0.5, nms_threshold=0.4)
            detected_boxes = []
            if len(indices) > 0:
                for i in indices.flatten():
                    x, y, w, h = boxes[i]
                    detected_boxes.append((x, y, w, h))
                    image = blur_region(image, x, y, x + w, y + h)
                cv2.imwrite(output_path, image)
            else:
                shutil.copy(image_path, output_path)

        except Exception as e:
            error_msg = f"Error processing {detection_path}: {str(e)}"
            errors.append(error_msg)

    # Stop timer
    end_time = time.time()

    # Print detailed statistics
    print(f"Total images processed: {images_processed}")
    print(f"Images with detected humans and blurred: {blurred_images}")
    print(f"Percentage of images with detected humans: {(blurred_images / images_processed) * 100:.2f}%")
    print(f"Error processing images: {len(errors)}")
    print(f"Time taken: {end_time - start_time:.2f} seconds")

    # Optional: Save the list of errors to a file
    with open(os.path.join(output_directory, 'errors.log'), 'w') as f:
        for item in errors:
            f.write("%s\n" % item)

    print("All images have been processed and noise added based on detection boxes.")