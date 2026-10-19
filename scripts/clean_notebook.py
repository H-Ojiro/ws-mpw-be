#!/usr/bin/env python3
import sys
import os
import nbformat
import re

def strip_to_repo_path(path):
    """
    Given a path or URL, if it contains '/blob/', strip everything up to
    and including the branch name after '/blob/'.
    Example:
    https://github.com/user/repo/blob/main/notebooks/images/foo.png
    => notebooks/images/foo.png
    """
    if "/blob/" in path:
        parts = path.split("/blob/", 1)[1].split("/", 1)
        if len(parts) == 2:
            # parts[0] = branch name, parts[1] = path after branch
            return parts[1]
    return path

def make_relative_path_from_blob(notebook_path, img_path):
    """
    Convert GitHub blob URL or absolute path to a relative path from notebook.
    """
    repo_rel_path = strip_to_repo_path(img_path)
    # Convert to absolute path assuming repo root is current working directory
    abs_img_path = os.path.abspath(repo_rel_path)
    notebook_dir = os.path.dirname(os.path.abspath(notebook_path))
    try:
        rel_path = os.path.relpath(abs_img_path, start=notebook_dir)
    except ValueError:
        # On Windows if drives differ, fallback to repo_rel_path as-is
        rel_path = repo_rel_path
    return rel_path

def process_notebook(nb_path):
    changed = False
    nb = nbformat.read(nb_path, as_version=nbformat.NO_CONVERT)

    for cell in nb.cells:
        if cell.cell_type == "markdown":
            # Replace markdown image links ![alt](path)
            def replace_match(match):
                nonlocal changed
                alt_text, img_path = match.groups()
                new_path = make_relative_path_from_blob(nb_path, img_path)
                if img_path != new_path:
                    changed = True
                    return f"![{alt_text}]({new_path})"
                return match.group(0)

            cell.source = re.sub(r'!\[([^\]]*)\]\(([^)]+)\)', replace_match, cell.source)

    if changed:
        nbformat.write(nb, nb_path)
        print(f"Cleaned image paths in: {nb_path}")
    return changed

def main():
    any_changes = False
    for nb_file in sys.argv[1:]:
        if nb_file.endswith(".ipynb"):
            if process_notebook(nb_file):
                any_changes = True
    sys.exit(0 if any_changes else 0)

if __name__ == "__main__":
    main()

