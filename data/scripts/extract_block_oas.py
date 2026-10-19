#!/usr/bin/env python3

import argparse
import klayout.db as db


def extract_cell(input_oas: str, output_oas: str, cell_name: str) -> None:
    src = db.Layout()
    src.read(input_oas)

    src_cell = src.cell(cell_name)
    if src_cell is None:
        raise ValueError(f"Cell '{cell_name}' not found in {input_oas}")

    dst = db.Layout()
    dst.dbu = src.dbu

    dst_top = dst.create_cell(src_cell.name)

    cell_mapping = db.CellMapping()
    cell_mapping.for_single_cell_full(
        src,
        src_cell.cell_index(),
        dst,
        dst_top.cell_index(),
    )

    dst.copy_tree_shapes(src, cell_mapping)

    dst.write(output_oas)

    print(
        f"Extracted cell '{cell_name}' "
        f"from '{input_oas}' "
        f"to '{output_oas}'"
    )


def parse_args():
    parser = argparse.ArgumentParser(
        description="Extract a cell hierarchy from an OASIS file."
    )

    parser.add_argument(
        "-i",
        "--input",
        required=True,
        help="Input OASIS file",
    )

    parser.add_argument(
        "-c",
        "--cell",
        required=True,
        help="Cell name to extract",
    )

    parser.add_argument(
        "-o",
        "--output",
        required=True,
        help="Output OASIS file",
    )

    return parser.parse_args()


def main():
    args = parse_args()

    extract_cell(
        input_oas=args.input,
        output_oas=args.output,
        cell_name=args.cell,
    )


if __name__ == "__main__":
    main()
