#!/usr/bin/env python3
import argparse
import klayout.db as db


def extract_oasis_block(
    input_file, output_file, bbox, max_hier_level, cell_name=None, target_layers=None
):
    """Extracts layout blocks with low memory overhead using KLayout streaming options."""
    print(f"Loading OASIS file (optimized options): {input_file}...")

    # Configure reader options to save memory
    load_options = db.LoadLayoutOptions()
    load_options.create_other_layers = True

    # OPTIMIZATION: If you only care about specific layers (e.g., [ [1,0], [2,0] ]), 
    # you can filter them here to drastically drop memory usage.
    if target_layers:
        load_options.layer_map.clear()
        for i, (layer, datatype) in enumerate(target_layers):
            load_options.layer_map.map(db.LayerInfo(layer, datatype), i + 1)

    layout = db.Layout()
    layout.read(input_file, load_options)

    # Determine top cell
    if cell_name:
        top_cell = layout.cell(cell_name)
        if not top_cell:
            raise ValueError(f"Cell '{cell_name}' not found in layout.")
    else:
        top_cells = layout.top_cells()
        if not top_cells:
            raise ValueError("No top cells found in the layout.")
        top_cell = top_cells[0]

    print(f"Target top cell: {top_cell.name}")

    # Create output layout and map layers
    out_layout = db.Layout()
    out_layout.dbu = layout.dbu

    layer_mapping = {}
    for layer_id in layout.layer_indexes():
        layer_info = layout.get_info(layer_id)
        new_layer_id = out_layout.insert_layer(layer_info)
        layer_mapping[layer_id] = new_layer_id

    out_top = out_layout.create_cell(top_cell.name)

    # Handle bounding box
    dbu = layout.dbu
    if bbox:
        box = db.Box(
            int(bbox[0] / dbu),
            int(bbox[1] / dbu),
            int(bbox[2] / dbu),
            int(bbox[3] / dbu),
        )
        print(f"Extracting window: {box} (DBU) with max level: {max_hier_level}")
    else:
        box = top_cell.bbox()
        print(f"No bounding box specified. Using full layout boundary: {box} (DBU) with max level: {max_hier_level}")

    # Memory-efficient recursive function using native shape insertion instead of heavy Region objects
    def process_hierarchy(
        src_cell, dest_cell, current_transform, current_level
    ):
        # 1. Copy shapes safely layer by layer
        for src_layer_id, dest_layer_id in layer_mapping.items():
            shapes = src_cell.shapes(src_layer_id)
            if shapes.is_empty():
                continue

            if current_level >= max_hier_level:
                # Use lightweight box clipping instead of loading a full db.Region where possible
                transformed_box = box.transformed(db.DCplxTrans(current_transform, dbu))
                # Iterate through shapes individually to minimize RAM allocation peaks
                for shape in shapes.each():
                    if shape.bbox().overlaps(transformed_box):
                        dest_cell.shapes(dest_layer_id).insert(shape)
            else:
                # Direct shape duplication without intermediate Python-heavy processing
                dest_cell.shapes(dest_layer_id).insert(shapes)

        # 2. Traverse child instances if below max depth
        if current_level < max_hier_level:
            for inst in src_cell.each_inst():
                trans = inst.cplx_trans
                inst_bbox = inst.cell.bbox().transformed(trans)

                if inst_bbox.overlaps(box):
                    child_cell_name = inst.cell.name
                    dest_child_cell = out_layout.cell(child_cell_name)
                    if not dest_child_cell:
                        dest_child_cell = out_layout.create_cell(child_cell_name)

                    dest_cell.insert(db.CellInstArray(dest_child_cell.cell_index(), inst.trans))

                    process_hierarchy(
                        inst.cell,
                        dest_child_cell,
                        current_transform * trans,
                        current_level + 1,
                    )

    print("Processing hierarchy with low-memory configuration...")
    process_hierarchy(top_cell, out_top, db.ICplxTrans(), 0)

    print(f"Writing extracted layout to: {output_file}...")
    out_layout.write(output_file)
    print("Extraction completed successfully!")


def main():
    parser = argparse.ArgumentParser(description="Low-memory OASIS block and hierarchy extractor.")
    parser.add_argument("-i", "--input", required=True, help="Input OASIS file path")
    parser.add_argument("-o", "--output", required=True, help="Output OASIS file path")
    parser.add_argument("-b", "--bbox", type=float, nargs=4, default=None, metavar=("XMIN", "YMIN", "XMAX", "YMAX"), help="Bounding box in microns")
    parser.add_argument("-m", "--max-level", type=int, default=99, help="Maximum hierarchical level")
    parser.add_argument("-c", "--cell", default=None, help="Top cell name")

    args = parser.parse_args()

    extract_oasis_block(
        input_file=args.input,
        output_file=args.output,
        bbox=args.bbox,
        max_hier_level=args.max_level,
        cell_name=args.cell,
    )


if __name__ == "__main__":
    main()
