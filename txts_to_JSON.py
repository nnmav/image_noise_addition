import os
import json
import argparse

def txts_to_JSON(input_dir, output_file):
    data = {}

    # Loop through all txt files in the directory
    for filename in os.listdir(input_dir):
        if filename.endswith(".txt"):
            timestamp = filename.split('.')[0]
            with open(os.path.join(input_dir, filename), 'r') as f:
                lines = f.readlines()
                values = [line.strip().split() for line in lines]
                values = [[float(val) for val in value] for value in values]
                data[timestamp] = values

    # Write the collected data to a JSON file
    with open(output_file, 'w') as json_file:
        json.dump(data, json_file, indent=4)

    print(f"Data has been successfully written to {output_file}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert txt files to JSON")
    parser.add_argument("input_dir", help="Directory containing the txt files")
    parser.add_argument("output_file", help="Output JSON file")
    args = parser.parse_args()

    txts_to_JSON(args.input_dir, args.output_file)