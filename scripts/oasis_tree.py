#!/usr/bin/env python3

import argparse
import klayout.db as db


def write_hierarchy(cell, layout, outfile, indent="", visited=None):
    if visited is None:
        visited = set()

    outfile.write(f"{indent}{cell.name}\n")

    if cell.cell_index() in visited:
        outfile.write(f"{indent}  [already visited]\n")
        return

    visited.add(cell.cell_index())

    children = []
    seen = set()

    for inst in cell.each_inst():
        child = layout.cell(inst.cell_index)

        if child.cell_index() not in seen:
            children.append(child)
            seen.add(child.cell_index())

    for i, child in enumerate(children):
        is_last = i == len(children) - 1

        branch = "└── " if is_last else "├── "
        next_indent = (
            indent + "    "
            if is_last
            else indent + "│   "
        )

        outfile.write(f"{indent}{branch}{child.name}\n")

        write_hierarchy(
            child,
            layout,
            outfile,
            next_indent,
            visited.copy(),
        )


def main():
    parser = argparse.ArgumentParser(
        description="Export OASIS hierarchy tree to a text file."
    )

    parser.add_argument(
        "-i",
        "--input",
        required=True,
        help="Input OASIS file",
    )

    parser.add_argument(
        "-o",
        "--output",
        default="hierarchy.txt",
        help="Output text file (default: hierarchy.txt)",
    )

    parser.add_argument(
        "-t",
        "--top",
        help="Top cell name (default: first top cell)",
    )

    args = parser.parse_args()

    layout = db.Layout()
    layout.read(args.input)

    if args.top:
        top = layout.cell(args.top)
        if top is None:
            raise ValueError(
                f"Top cell '{args.top}' not found."
            )
    else:
        tops = list(layout.top_cells())
        if not tops:
            raise RuntimeError("No top cells found.")
        top = tops[0]

    with open(args.output, "w", encoding="utf-8") as f:
        write_hierarchy(top, layout, f)

    print(f"Hierarchy exported to {args.output}")


if __name__ == "__main__":
    main()

