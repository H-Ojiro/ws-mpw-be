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

layout = pya.Layout()
layout.read(input_oas)  # format inferred from extension

print(f"Convert {input_oas} to {output_gds} with top {top_cell}")

if top_cell:
    if layout.cell(top_cell) is None:
        raise SystemExit(f'Top cell "{top_cell}" not found.')
    options = pya.SaveLayoutOptions()
    options.clear_cells()
    options.keep_instances = False

    visited = set()

    def select_cells(cell):
        # Ignore this cell and everything below it
        if "_FILL" in cell.name:
            return

        if cell.cell_index() in visited:
            return
        visited.add(cell.cell_index())

        # Add this cell only
        options.add_this_cell(cell.cell_index())

        # Explicitly descend into its children
        for inst in cell.each_inst():
            select_cells(layout.cell(inst.cell_index))

    select_cells(layout.cell(top_cell))

    options.write_context_info = True
    layout.write(output_gds, options)
    print(f"Written {output_gds} with top {top_cell}")
    wrapper_list = layout.cells("*_project_wrapper")
    with open("user_top", "w") as wrapper_file:
        for wrapper_cell in wrapper_list:
            wrapper_file.write(f"{wrapper_cell.name}\n")

else:
    layout.write(output_gds)
    if os.path.exists(output_gds):
        print(f"Written {output_gds}")
    else:
        raise SystemExit(f'Failed to write "{output_gds}".')
