# Run with: klayout -b -r oasis2gds.py -rd input_oas=... -rd output_gds=... [-rd top_cell=...]
#   via ChatGPT
#   License GPLv2
#   (C) ChipFoundry developed by D. Mitch Bailey

import os
import pya

if not input_oas or not output_gds:
    raise SystemExit("Usage: -rd input_oas=<file.oas> -rd output_gds=<file.gds> [-rd top_cell=TOP]")

if not os.path.isfile(input_oas):
    raise FileNotFoundError("Input not found: " + input_oas)

# Determine the directory of the output GDS so cell.list is saved alongside it
output_dir = os.path.dirname(output_gds)
cell_list_path = os.path.join(output_dir, "cell.list") if output_dir else "cell.list"

layout = pya.Layout()
layout.read(input_oas)  # format inferred from extension

print(f"Convert {input_oas} to {output_gds} with top {top_cell}")


# Helper function to write cell.list file
def write_cell_list(cell_names, filepath):
    """Writes a list of cell names to a text file, sorted alphabetically."""
    with open(filepath, "w") as f:
        for name in sorted(set(cell_names)):
            f.write(f"{name}\n")
    print(f"Written cell list to {filepath}")


if top_cell:
    if layout.cell(top_cell) is None:
        raise SystemExit(f'Top cell "{top_cell}" not found.')
    options = pya.SaveLayoutOptions()
    options.clear_cells()
    options.keep_instances = False

    visited = set()
    exported_cell_names = []

    def exclude_fill(cell):
        # Ignore this cell and everything below it
        if "_FILL" in cell.name:
            return

        if cell.cell_index() in visited:
            return
        visited.add(cell.cell_index())

        # Track the exported cell name
        exported_cell_names.append(cell.name)

        # Add this cell only
        options.add_this_cell(cell.cell_index())

        # Explicitly descend into its children
        for inst in cell.each_inst():
            exclude_fill(layout.cell(inst.cell_index))

    exclude_fill(layout.cell(top_cell))

    options.write_context_info = True
    layout.write(output_gds, options)
    print(f"Written {output_gds} with top {top_cell}")

    # Write cell.list in the same directory as output_gds
    write_cell_list(exported_cell_names, cell_list_path)

    wrapper_list = layout.cells("*_project_wrapper")
    user_top_path = os.path.join(output_dir, "user_top") if output_dir else "user_top"
    with open(user_top_path, "w") as wrapper_file:
        for wrapper_cell in wrapper_list:
            wrapper_file.write(f"{wrapper_cell.name}\n")

else:
    layout.write(output_gds)
    if os.path.exists(output_gds):
        print(f"Written {output_gds}")

        # Write cell.list in the same directory as output_gds
        all_cell_names = [cell.name for cell in layout.each_cell()]
        write_cell_list(all_cell_names, cell_list_path)
    else:
        raise SystemExit(f'Failed to write "{output_gds}".')
