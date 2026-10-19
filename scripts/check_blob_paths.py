#!/usr/bin/env python3
import sys
import os
import nbformat
import re

def contains_blob_path(nb_path):
    nb = nbformat.read(nb_path, as_version=nbformat.NO_CONVERT)
    pattern = re.compile(r'/blob/[^)]*raw=1')
    for cell in nb.cells:
        if cell.cell_type == "markdown":
            if pattern.search(cell.source):
                return True
    return False

def main():
    found_files = []
    for root, _, files in os.walk('.'):
        for f in files:
            if f.endswith('.ipynb'):
                path = os.path.join(root, f)
                if contains_blob_path(path):
                    found_files.append(path)

    if found_files:
        print("ERROR: Found absolute repo paths for raw data in the following notebooks:")
        for f in found_files:
            print(f" - {f}")
        sys.exit(1)
    else:
        print("No absolute /blob/ paths found in notebooks.")
        sys.exit(0)

if __name__ == "__main__":
    main()

