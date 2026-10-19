#! /usr/bin/env python3

"""
apply_json_to_layout
Uses klayout to modify the "input_layout" file according to the instructions
in the "json_file" and writes the results to "output_layout".
"""

import argparse
from typing import Any
import json
import pya


def delete_object(cell: dict, action: dict[str, Any], shapes: Any) -> None:
    if action["type"] == "label":
        for shape_it in list(shapes.each()):
            if (shape_it.is_text() and shape_it.text.string == action["text"]
                    and shape_it.text.trans.disp.x == action["x"]
                    and shape_it.text.trans.disp.y == action["y"]):
                shapes.erase(shape_it)

    elif action["type"] == "box":
        x1, y1, x2, y2 = action["coords"]
        for shape_it in list(shapes.each()):
            if shape_it.is_box():
                box = shape_it.box()
                if (box.left == x1 and box.right == x2
                        and box.bottom == y1 and box.top == y2):
                    shapes.erase(shape_it)

    else:
        pass


def add_object(cell: Any, action: dict[str, Any], shapes: Any) -> None:
    if action["type"] == "box":
        x1, y1, x2, y2 = action["coords"]
        shapes.insert(pya.Box(x1, y1, x2, y2))

    elif action["type"] == "polygon":
        iter_coordinates = iter(action["coords"])
        points = []
        for x, y in zip(iter_coordinates, iter_coordinates):
            points.append(pya.Point(x, y))
        shapes.insert(pya.Polygon(points))

    elif action["type"] == "label":
        shapes.insert(pya.Text(action["text"], pya.Trans(action["x"], action["y"])))

    else:
        pass


def apply_json_to_layout(input_layout: str, json_file: str, output_layout: str) -> None:
    layout = pya.Layout()
    layout.read(input_layout)

    with open(json_file) as f:
        updates = json.load(f)

    for cell_name, actions in updates["cells"].items():
        print(f"Processing cell: {cell_name}")
        cell = layout.cell(cell_name)

        for action in actions:

            if "comment" in action:  # skip comments
                continue

            layer_num = action["layer"][0]
            datatype = action["layer"][1]

            # Find or create layer
            layer_index = layout.find_layer(layer_num, datatype)
            if layer_index is None:  # create layer index if it doesn't exist
                layer_index = layout.insert_layer(pya.LayerInfo(layer_num, datatype))

            shapes = cell.shapes(layer_index)

            if action["action"] == "delete":
                delete_object(cell, action, shapes)

            elif action["action"] == "erase_layer":
                for s in list(shapes.each()):
                    shapes.erase(s)

            elif action["action"] == "add":
                add_object(cell, action, shapes)

    layout.write(output_layout)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Applies the changes described in a json file to a gds/oas file')
    parser.add_argument('--input_file', '-i', required=True, help='Input layout file')
    parser.add_argument('--json_file', '-j', required=True, help='JSON instruction file')
    parser.add_argument('--output_file', '-o', required=True, help='Output layout file')
    args = parser.parse_args()

    apply_json_to_layout(args.input_file, args.json_file, args.output_file)
