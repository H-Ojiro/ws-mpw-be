import nbformat
from pathlib import Path
import re

def clean_image_paths(nb_path):
    nb = nbformat.read(nb_path, as_version=nbformat.NO_CONVERT)
    changed = False

    for cell in nb.cells:
        if cell.cell_type == "markdown":
            original = cell.source
            # Rewrite GitHub blob URLs to relative
            cell.source = re.sub(
                r"https://github\.com/[^/]+/[^/]+/blob/[^/]+/((?:[^?#)]+))\?raw=true",
                r"\1",
                cell.source,
            )
            if cell.source != original:
                changed = True

    if changed:
        nbformat.write(nb, nb_path)
        print(f"Cleaned: {nb_path}")

def main():
    for path in Path(".").rglob("*.ipynb"):
        clean_image_paths(path)

if __name__ == "__main__":
    main()

