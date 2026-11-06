#!/usr/bin/env python3

import sys
from pathlib import Path
import pya

TARGET_LAYER = 81
TARGET_DATATYPE = 10


def extract_top_pins_klayout(gds_path, target_layer=81, target_datatype=10):
    """Extracts top-level text labels/pins from a GDS/GDS.GZ file using KLayout pya."""
    gds_file = Path(gds_path)
    if not gds_file.is_file():
        raise FileNotFoundError(f"GDS file not found: {gds_path}")

    # Initialize layout database
    layout = pya.Layout()

    print(f"Reading layout: {gds_file} ...")
    layout.read(str(gds_file))

    # Identify top cell
    top_cells = layout.top_cells()
    if not top_cells:
        print("Error: No top-level cell found in the layout.")
        return [], None

    top_cell = top_cells[0]
    top_cell_name = top_cell.name
    print(f"Top cell identified: '{top_cell_name}'")

    pins = []

    # Map target layer/datatype to KLayout layer index
    layer_index = layout.layer(target_layer, target_datatype)

    # Iterate over text objects in the top cell
    for shape in top_cell.shapes(layer_index):
        if shape.is_text():  # Corrected line
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

    return pins, top_cell_name


def main():
    if len(sys.argv) < 2:
        print(
            "Usage: python extract_top_pins.py <input.gds.gz> [output_pins.txt]"
        )
        sys.exit(1)

    gds_input = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else "pin.list"

    try:
        pins, top_cell_name = extract_top_pins_klayout(
            gds_input, TARGET_LAYER, TARGET_DATATYPE
        )
    except Exception as e:
        print(f"Error reading layout: {e}")
        sys.exit(1)

    if not pins:
        print(
            f"No pin labels found matching Layer {TARGET_LAYER}, Datatype {TARGET_DATATYPE} in top cell."
        )
        return

    # Write results
    with open(output_file, "w") as f:
        header = f"# Top Pins for Cell: '{top_cell_name}' (Filter: Layer {TARGET_LAYER}, Datatype {TARGET_DATATYPE})\n"
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
        f"\nSuccessfully saved {len(pins)} pins to output file: '{output_file}'"
    )


if __name__ == "__main__":
    main()
