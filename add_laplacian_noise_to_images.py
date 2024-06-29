import cv2
import numpy as np
import os
import glob
import time
import argparse

# Define functions for differential privacy noise addition
def calculate_sensitivity_rgb_images(image_data):
    return np.max(image_data)

def add_noise_differential_privacy_rgb_images_laplace(image_data, epsilon):
    sensitivity = calculate_sensitivity_rgb_images(image_data)
    scale = sensitivity / epsilon
    laplace_noise = np.random.laplace(scale=scale, size=image_data.shape)
    noisy_image_data = image_data + laplace_noise
    noisy_image_data = np.clip(noisy_image_data, 0, 255)
    return noisy_image_data

def read_image(image_path, method):
    if not method in ['2d', '3d']:
        print("Invalid method. Choose either '2d' or '3d'")
        return None
    if method == '2d':
        image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    else:
        image = cv2.imread(image_path)

    if image is None:
        print(f"Error reading {image_path}")
        return None

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

    METHOD=args.method

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
        print(f"\rProgress: {(100 * images_processed / total_images):.2f}%", end="")
        try:
            image_path = os.path.join(image_directory, os.path.basename(detection_path).replace('.txt', '.png'))
            image = read_image(image_path, METHOD)
            if image is None:
                error_msg = f"Error reading {image_path}"
                raise Exception(error_msg)

            human_bodies = []
            with open(detection_path, 'r') as f:
                for line in f:
                    x, y, w, h = map(int, line.strip().split())
                    human_bodies.append((x, y, w, h))

            if human_bodies:
                blurred_images += 1
                for (x, y, w, h) in human_bodies:
                    x, y, w, h = int(x), int(y), int(w), int(h)
                    if w > 0 and h > 0 and x >= 0 and y >= 0 and x + w <= image.shape[1] and y + h <= image.shape[0]:
                        roi = image[y:y + h, x:x + w]
                        noisy_roi = add_noise_differential_privacy_rgb_images_laplace(roi, epsilon=0.01)
                        image[y:y + h, x:x + w] = noisy_roi

                output_path = os.path.join(output_directory, os.path.basename(image_path))
                cv2.imwrite(output_path, image)

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
    with open(os.path.join(output_directory, 'errors.txt'), 'w') as f:
        for item in errors:
            f.write("%s\n" % item)

    print("All images have been processed and noise added based on detection boxes.")