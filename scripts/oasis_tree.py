#!/usr/bin/env python3

"""
Export the cell hierarchy of an OASIS file to a text file.

Examples
--------
# Export full hierarchy
python oasis_tree.py \
    -i design.oas \
    -o hierarchy.txt

# Export hierarchy up to depth 2
python oasis_tree.py \
    -i design.oas \
    -o hierarchy.txt \
    -d 2

# Use a specific top cell
python oasis_tree.py \
    -i design.oas \
    -t TOP \
    -o hierarchy.txt

Depth definition:
    0 : top cell only
    1 : top cell + direct children
    2 : include grandchildren
   -1 : unlimited (default)
"""

import argparse
import klayout.db as db


def write_hierarchy(
    cell,
    layout,
    outfile,
    max_depth=-1,
    current_depth=0,
    prefix="",
    visited=None,
):
    """
    Write hierarchy tree recursively using memory-efficient state management.
    """
    if visited is None:
        visited = set()

    # Prevent infinite loops in cyclic graphs or double reporting of identical branches
    cell_idx = cell.cell_index()
    if cell_idx in visited:
        outfile.write(f"{prefix}[already visited]\n")
        return

    visited.add(cell_idx)

    if max_depth >= 0 and current_depth >= max_depth:
        visited.remove(cell_idx)  # Clean up state backtracking for sibling traversal
        return

    # Collect unique child cells referenced by instances
    children = []
    seen = set()

    for inst in cell.each_inst():
        # FIXED: inst.cell_index is an attribute property in KLayout Python API
        child_idx = inst.cell_index
        if child_idx not in seen:
            seen.add(child_idx)
            child = layout.cell(child_idx)
            if child:
                children.append(child)

    for i, child in enumerate(children):
        is_last = i == len(children) - 1

        branch = "└── " if is_last else "├── "
        child_prefix = prefix + ("    " if is_last else "│   ")

        outfile.write(f"{prefix}{branch}{child.name}\n")

        write_hierarchy(
            child,
            layout,
            outfile,
            max_depth=max_depth,
            current_depth=current_depth + 1,
            prefix=child_prefix,
            visited=visited,
        )

    # Backtrack visitation set so sibling nodes down other branches can be properly traversed
    visited.remove(cell_idx)


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

    parser.add_argument(
        "-d",
        "--depth",
        type=int,
        default=-1,
        help=(
            "Maximum hierarchy depth "
            "(-1=unlimited, 0=top only, "
            "1=children, 2=grandchildren, ...)"
        ),
    )

    args = parser.parse_args()

    print(f"Loading layout from {args.input}...")
    layout = db.Layout()
    layout.read(args.input)

    if args.top:
        top_cell = layout.cell(args.top)

        if top_cell is None:
            raise ValueError(
                f"Top cell '{args.top}' not found."
            )
    else:
        top_cells = list(layout.top_cells())

        if not top_cells:
            raise RuntimeError(
                "No top cells found in layout."
            )

        top_cell = top_cells[0]

    print(f"Exporting hierarchy for top cell: {top_cell.name}...")
    with open(args.output, "w", encoding="utf-8") as f:
        f.write(f"{top_cell.name}\n")

        write_hierarchy(
            top_cell,
            layout,
            f,
            max_depth=args.depth,
            current_depth=0,
        )

    print(f"Hierarchy successfully written to: {args.output}")


if __name__ == "__main__":
    main()
