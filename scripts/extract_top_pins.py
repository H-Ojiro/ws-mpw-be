#!/usr/bin/env python3

import argparse
import sys
from pathlib import Path
import pya

TARGET_LAYER = 81
TARGET_DATATYPE = 10


def extract_top_pins_klayout(
    gds_path, target_layer=81, target_datatype=10, cell_name=None
):
    """Extracts text labels/pins from a specified cell (or top cell) in a GDS/GDS.GZ file."""
    gds_file = Path(gds_path)
    if not gds_file.is_file():
        raise FileNotFoundError(f"GDS file not found: {gds_path}")

    # Initialize layout database
    layout = pya.Layout()

    print(f"Reading layout: {gds_file} ...")
    layout.read(str(gds_file))

    # Select target cell
    if cell_name:
        cell = layout.cell(cell_name)
        if cell is None:
            available_cells = [c.name for c in layout.top_cells()]
            print(
                f"Error: Specified cell '{cell_name}' not found in layout.\n"
                f"Top-level cell(s) available: {available_cells}"
            )
            return [], None
    else:
        top_cells = layout.top_cells()
        if not top_cells:
            print("Error: No top-level cell found in the layout.")
            return [], None
        cell = top_cells[0]

    cell_name = cell.name
    print(f"Extracting pins from cell: '{cell_name}'")

    pins = []

    # Map target layer/datatype to KLayout layer index
    layer_index = layout.layer(target_layer, target_datatype)

    # Iterate over text objects in the selected cell
    for shape in cell.shapes(layer_index):
        if shape.is_text():
            text = shape.text
            # Convert database units (DBU) to microns
            dbu = layout.dbu
            x = text.x * dbu
            y = text.y * dbu

            pins.append(
                {
                    "name": text.string,
                    "layer": target_layer,
                    "datatype": target_datatype,
                    "x": x,
                    "y": y,
                }
            )

    return pins, cell_name


def main():
    parser = argparse.ArgumentParser(
        description="Extract top-level pin labels from a GDS/GDS.GZ file."
    )
    parser.add_argument("gds_input", help="Path to input GDS/GDS.GZ file")
    parser.add_argument(
        "output_file",
        nargs="?",
        default="pin.list",
        help="Path to output pin list file (default: pin.list)",
    )
    parser.add_argument(
        "-t",
        "--top-cell",
        dest="top_cell",
        default=None,
        help="Name of the top cell to inspect (optional, auto-detects by default)",
    )

    args = parser.parse_args()

    try:
        pins, target_cell_name = extract_top_pins_klayout(
            gds_path=args.gds_input,
            target_layer=TARGET_LAYER,
            target_datatype=TARGET_DATATYPE,
            cell_name=args.top_cell,
        )
    except Exception as e:
        print(f"Error reading layout: {e}")
        sys.exit(1)

    if target_cell_name is None:
        sys.exit(1)

    if not pins:
        print(
            f"No pin labels found matching Layer {TARGET_LAYER}, Datatype {TARGET_DATATYPE} in cell '{target_cell_name}'."
        )
        return

    # Write results to output file and stdout
    with open(args.output_file, "w") as f:
        header = f"# Pins for Cell: '{target_cell_name}' (Filter: Layer {TARGET_LAYER}, Datatype {TARGET_DATATYPE})\n"
        columns = f"{'PIN_NAME':<25} {'LAYER':<8} {'DATATYPE':<10} {'X_POS (um)':<14} {'Y_POS (um)':<14}\n"
        separator = "-" * 75 + "\n"

        f.write(header + columns + separator)
        print("\nExtracted Pins:")
        print(columns + separator, end="")

        for pin in sorted(pins, key=lambda x: x["name"]):
            line = f"{pin['name']:<25} {pin['layer']:<8} {pin['datatype']:<10} {pin['x']:<14.3f} {pin['y']:<14.3f}"
            print(line)
            f.write(line + "\n")

    print(
        f"\nSuccessfully saved {len(pins)} pins to output file: '{args.output_file}'"
    )


if __name__ == "__main__":
    main()
