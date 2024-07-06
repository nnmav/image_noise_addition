import cv2
import numpy as np
import os
import glob
import time
import argparse
import json

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

def add_noise_differential_privacy_rgb_images_gaussian(image_data, epsilon):
    sensitivity = calculate_sensitivity_rgb_images(image_data)
    scale = sensitivity / epsilon
    gaussian_noise = np.random.normal(scale=scale, size=image_data.shape)
    noisy_image_data = image_data + gaussian_noise
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
    argparser.add_argument('json_file', type=str, help='Path to the JSON file containing detection results')
    argparser.add_argument('output_directory', type=str, help='Path to the directory to save the output images')
    argparser.add_argument("method", type=str, help="Method to use for detection (2d or 3d)")
    argparser.add_argument("noise_type", type=str, choices=['laplacian', 'gaussian'], help="Type of noise to add (laplacian or gaussian)")
    argparser.add_argument("--epsilon", type=float, default=0.01, help="Epsilon value for differential privacy")

    args = argparser.parse_args()

    METHOD=args.method
    epsilon = args.epsilon
    noise_type = args.noise_type
    image_directory = args.image_directory
    json_file = args.json_file
    output_directory = args.output_directory

    os.makedirs(output_directory, exist_ok=True)

    print(f"\nAdding Laplacian noise: {image_directory} -> {output_directory} based on detection boxes in {json_file}")
    print(f"Method: {METHOD}")
    print(f"Epsilon: {epsilon}")

    # Load the JSON file
    with open(json_file, 'r') as f:
        detection_data = json.load(f)

    # Initialize counters and lists for statistics
    images_processed = 0
    total_images = len([f for f in os.listdir(image_directory)])  # Count number of images to be processed
    blurred_images = 0
    errors = []

    # Start timer
    start_time = time.time()

    # Process each detection file in the directory
    for timestamp, detections in detection_data.items():
        images_processed += 1
        print(f"\rProgress: {(100 * images_processed / total_images):.2f}%", end=" ")
        try:
            image_path = os.path.join(image_directory, f"{timestamp}.png")
            image = read_image(image_path, METHOD)

            if len(detections[0]) > 4:
                human_bodies = [(int(x), int(y), int(w), int(h)) for x, y, w, h, confidence in detections]
            else:
                human_bodies = [(int(x), int(y), int(w), int(h)) for x, y, w, h in detections]

            if human_bodies:
                blurred_images += 1
                for (x, y, w, h) in human_bodies:
                    x, y, w, h = int(x), int(y), int(w), int(h)
                    roi = image[
                          max(0, y):min(y + h, image.shape[0]),
                          max(0, x):min(x + w, image.shape[1])
                          ]
                    if noise_type == 'laplacian':
                        noisy_roi = add_noise_differential_privacy_rgb_images_laplace(roi, epsilon=epsilon)
                    else:
                        noisy_roi = add_noise_differential_privacy_rgb_images_gaussian(roi, epsilon=epsilon)
                    image[max(0,y):min(y + h,image.shape[0]), max(0,x):min(x + w,image.shape[1])] = noisy_roi

                output_path = os.path.join(output_directory, os.path.basename(image_path))
                cv2.imwrite(output_path, image)

        except Exception as e:
            print(f"Error processing {timestamp}: {str(e)}")
            errors.append(str(e))



    # Stop timer
    end_time = time.time()

    # Print detailed statistics
    print(f"\nTotal images processed: {images_processed}")
    print(f"Images with detected humans and blurred: {blurred_images}")
    print(f"Percentage of images with detected humans: {(blurred_images / total_images) * 100:.2f}%")
    print(f"Error processing images: {len(errors)}")
    print(f"Time taken: {end_time - start_time:.2f} seconds")

    # Optional: Save the list of errors to a file
    with open(os.path.join(output_directory, 'errors.log'), 'w') as f:
        for item in errors:
            f.write("%s\n" % item)

    print("All images have been processed and noise added based on detection boxes.")