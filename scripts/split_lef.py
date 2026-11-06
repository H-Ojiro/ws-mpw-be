#!/usr/bin/env python3

import os
import re
import sys


def split_lef(input_file_path):
    if not os.path.exists(input_file_path):
        print(f"Error: File '{input_file_path}' does not exist.")
        sys.exit(1)

    with open(input_file_path, "r") as f:
        content = f.read()

    # 1. Extract the shared top-level header properties if they exist
    header_match = re.search(r"^(.*?)(?=MACRO)", content, re.DOTALL)
    header_text = header_match.group(1).strip() if header_match else ""

    # 2. Find all individual MACRO blocks matching from 'MACRO <name>' to 'END <name>'
    macro_pattern = re.compile(r"(MACRO\s+(\w+).*?END\s+\2)", re.DOTALL)
    macros = macro_pattern.findall(content)

    if not macros:
        print("No macros detected in the specified file.")
        return

    print(f"Found {len(macros)} macros. Splitting files...")

    # 3. Create a unique .lef file for each macro block
    for macro_body, macro_name in macros:
        output_filename = f"{macro_name}.lef"

        with open(output_filename, "w") as out_file:
            # Add header declarations if found
            if header_text:
                out_file.write(header_text + "\n\n")

            # Write the macro content cleanly
            out_file.write(macro_body.strip() + "\n\n")

            # Properly terminate the library syntax
            out_file.write("END LIBRARY\n")

        print(f"  --> Saved: {output_filename}")

    print("\nSuccessfully divided all macros!")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python split_lef.py <path_to_combined_lef_file>")
        sys.exit(1)

    split_lef(sys.argv[1])

