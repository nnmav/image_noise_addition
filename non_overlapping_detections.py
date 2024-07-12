import argparse
import json
from nnmavmath import geometry
import matplotlib.pyplot as plt


def group_overlapping_detections(rectangles: geometry.Quadrilateral) -> list[geometry.Quadrilateral]:
    overlapping_rectangles = [[rectangles.pop(0)]]
    while len(rectangles) > 0:
        for i in range(len(overlapping_rectangles)):
            for j in range(len(overlapping_rectangles[i])):
                to_transfer = []
                for k in range(len(rectangles)):
                    if overlapping_rectangles[i][j].overlaps(rectangles[k]):
                        to_transfer.append(k)
                to_transfer = sorted(to_transfer, reverse=True)
                for idx in to_transfer:
                    overlapping_rectangles[i].append(rectangles.pop(idx))

        if len(rectangles) > 0:
            overlapping_rectangles.append([rectangles.pop(0)])
    return overlapping_rectangles


def clean_up_rectangles(rectangles: list[geometry.Quadrilateral], verbose=False):
    i = 0
    to_delete = []
    rectangles = sorted(rectangles, key=lambda rect: rect.area, reverse=True)
    while i < len(rectangles):
        print(f"Cleaning up rectangles: {i}/{len(rectangles)}", end="\r") if verbose else None
        if i in to_delete:
            i += 1
            continue
        j = i + 1
        while j < len(rectangles):
            # if i != j:
            if j in to_delete:
                j += 1
                continue
            if rectangles[i].encloses_quad(rectangles[j]) or rectangles[i].equals(rectangles[j]):
                to_delete.append(j)
            j += 1
        i += 1
    to_delete = sorted(list(set(to_delete)), reverse=True)
    for idx in to_delete:
        del rectangles[idx]
    return rectangles


def split_rectangles(rectangles: list[geometry.Quadrilateral], verbose=False):
    vertical_sides = []
    horizontal_sides = []
    for quad in rectangles:
        for side in quad.sides:
            if side.is_vertical:
                hor_rect_segs = list(set([seg for rect in rectangles for seg in rect.sides if
                                          (seg.is_horizontal and seg != side and rect != quad)]))
                side_as_line = geometry.Line2D.from_segment(side)
                for q_side in hor_rect_segs:
                    if side_as_line.intersects_segment(q_side, include_endpoints=False) and side not in vertical_sides:
                        vertical_sides.append(side)

            elif side.is_horizontal:
                vert_rect_segs = list(set([seg for rect in rectangles for seg in rect.sides if
                                           (seg.is_vertical and seg != side and rect != quad)]))
                side_as_line = geometry.Line2D.from_segment(side)
                for q_side in vert_rect_segs:
                    if side_as_line.intersects_segment(q_side, include_endpoints=False) and side not in horizontal_sides: horizontal_sides.append(side)

    print(f"Vertical Sides: {len(vertical_sides)}") if verbose else None
    print(f"Horizontal Sides: {len(horizontal_sides)}") if verbose else None
    rects_split_vertically = []
    for rect in rectangles:
        rects_split_vertically.extend(rect.split_quad_by_lines(vertical_sides))

    print(f"Rects split vertically: {len(rects_split_vertically)}") if verbose else None
    all_rects = []
    for rect in rects_split_vertically:
        all_rects.extend(rect.split_quad_by_lines(horizontal_sides))

    print(f"Rects split horizontally: {len(all_rects)}") if verbose else None
    return all_rects


def non_overlapping_rects(rectangles: list[geometry.Quadrilateral], verbose=False):
    """
    Takes a list of bounding boxes and returns a list of non-overlapping bounding boxes.

    Args:
        rectangles (list): A list of geometry.Quadrilateral

    Returns:
        list: A list of non-overlapping geometry.Quadrilateral
    """

    # Clean up the rectangles
    print("Rectangles before first cleanup:", len(rectangles)) if verbose else None
    rectangles = clean_up_rectangles(rectangles)
    print("Rectangles after first cleanup:", len(rectangles)) if verbose else None

    new_rects = split_rectangles(rectangles)

    print(f"Final rects before cleaning up: {len(new_rects)}") if verbose else None
    new_rects = clean_up_rectangles(new_rects)
    print(f"Final rects after cleaning up: {len(new_rects)}") if verbose else None
    print("New Rects Length: ", len(new_rects)) if verbose else None

    return new_rects


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Takes a json file with 'timestamp':[rectangle bounding boxes] and returns a json file with non-overlapping bounding boxes.")
    parser.add_argument("detections_json_file", type=str, help="Path to the file with detection results in JSON format")
    parser.add_argument("output_detections_file", type=str, help="Path to the file for saving detection results in JSON format")
    parser.add_argument("--verbose", action="store_true", default=False, help="Print verbose output")

    args = parser.parse_args()
    detections_json_file = args.detections_json_file
    output_detections_file = args.output_detections_file

    # Load the detections from the JSON file
    with open(detections_json_file, 'r') as f:
        detection_data = json.load(f)

    geometry.GeometryConfig.set_origin('topleft')
    new_detection_data = {}
    prog_counter = 0
    for timestamp, detections_list in detection_data.items():
        prog_counter += 1
        print(f"Progress: {prog_counter}/{len(detection_data)}", end="\r") if not args.verbose else None

    #     detections_list = [
    #     [
    #         388.0,
    #         419.0,
    #         35.0,
    #         107.0,
    #         0.7515738010406494
    #     ],
    #     [
    #         387.0,
    #         418.0,
    #         36.0,
    #         108.0,
    #         0.8143460154533386
    #     ],
    #     [
    #         387.0,
    #         418.0,
    #         36.0,
    #         108.0,
    #         0.8237391710281372
    #     ],
    #     [
    #         418.0,
    #         384.0,
    #         68.0,
    #         227.0,
    #         0.841672420501709
    #     ],
    #     [
    #         417.0,
    #         383.0,
    #         70.0,
    #         228.0,
    #         0.9171590209007263
    #     ],
    #     [
    #         353.0,
    #         404.0,
    #         34.0,
    #         119.0,
    #         0.7031125426292419
    #     ],
    #     [
    #         382.0,
    #         419.0,
    #         40.0,
    #         107.0,
    #         0.8884963393211365
    #     ],
    #     [
    #         416.0,
    #         384.0,
    #         74.0,
    #         225.0,
    #         0.9644925594329834
    #     ],
    #     [
    #         417.0,
    #         384.0,
    #         74.0,
    #         224.0,
    #         0.9666333794593811
    #     ],
    #     [
    #         418.0,
    #         385.0,
    #         73.0,
    #         223.0,
    #         0.9598330855369568
    #     ],
    #     [
    #         598.0,
    #         369.0,
    #         106.0,
    #         306.0,
    #         0.9890244007110596
    #     ],
    #     [
    #         599.0,
    #         369.0,
    #         105.0,
    #         306.0,
    #         0.9896005988121033
    #     ],
    #     [
    #         599.0,
    #         368.0,
    #         105.0,
    #         307.0,
    #         0.9892266392707825
    #     ],
    #     [
    #         196.0,
    #         353.0,
    #         170.0,
    #         468.0,
    #         0.783186674118042
    #     ],
    #     [
    #         194.0,
    #         348.0,
    #         175.0,
    #         480.0,
    #         0.8403423428535461
    #     ],
    #     [
    #         190.0,
    #         368.0,
    #         171.0,
    #         480.0,
    #         0.8097853660583496
    #     ],
    #     [
    #         190.0,
    #         365.0,
    #         170.0,
    #         484.0,
    #         0.8070376515388489
    #     ],
    #     [
    #         197.0,
    #         362.0,
    #         170.0,
    #         493.0,
    #         0.9946788549423218
    #     ],
    #     [
    #         197.0,
    #         359.0,
    #         170.0,
    #         497.0,
    #         0.9954067468643188
    #     ],
    #     [
    #         600.0,
    #         374.0,
    #         102.0,
    #         301.0,
    #         0.9915356040000916
    #     ],
    #     [
    #         186.0,
    #         375.0,
    #         179.0,
    #         477.0,
    #         0.8241384029388428
    #     ],
    #     [
    #         187.0,
    #         373.0,
    #         177.0,
    #         476.0,
    #         0.835101842880249
    #     ],
    #     [
    #         194.0,
    #         365.0,
    #         177.0,
    #         485.0,
    #         0.9956250786781311
    #     ],
    #     [
    #         195.0,
    #         364.0,
    #         176.0,
    #         484.0,
    #         0.9955061078071594
    #     ]
    # ]

        # Convert the bounding boxes to rectangles
        detections = [detection[:4] for detection in detections_list]

        rectangles = [geometry.Quadrilateral.rectangle(x, y, width, height) for x, y, width, height in detections]

        # Sort Rectangles by area
        rectangles = sorted(rectangles, key=lambda rect: rect.area, reverse=True)

        # Group overlapping rectangles
        grouped_overlapping_rectangles = group_overlapping_detections(rectangles)

        print(f"Overlapping rectangles: {len(grouped_overlapping_rectangles)}") if args.verbose else None

        new_rectangles = []
        i=0
        for overlapping_rectangles in grouped_overlapping_rectangles:
            i+=1
            print(f"====== Group number: {i} =======") if args.verbose else None
            new_rectangles.extend(non_overlapping_rects(overlapping_rectangles, args.verbose))
            print(f"================================\n\n") if args.verbose else None

        print(f"Final Rectangles: {len(new_rectangles)}") if args.verbose else None

        # Convert the rectangles back to bounding boxes
        new_detections = [(rect.A.x, rect.A.y, rect.width, rect.height) for rect in new_rectangles]

        # Save the non-overlapping detections to the output JSON file
        new_detection_data[timestamp] = new_detections

        # Free up memory
        del rectangles
        del new_rectangles
        del grouped_overlapping_rectangles
        del detections


    with open(output_detections_file, 'w') as f:
        json.dump(new_detection_data, f)
    print(f"Saved non-overlapping detections to {output_detections_file}")
