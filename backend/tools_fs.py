import os
from pathlib import Path
from tools_web import web_search, read_url



WORKSPACE_ROOT = os.path.abspath("workspace")

def set_workspace_root(path):
    global WORKSPACE_ROOT
    WORKSPACE_ROOT = os.path.abspath(path)
    if not os.path.exists(WORKSPACE_ROOT):
        os.makedirs(WORKSPACE_ROOT)

def _get_safe_path(path):
    if not path: return WORKSPACE_ROOT
    p = Path(path)
    if p.is_absolute():
        return path
    return str(Path(WORKSPACE_ROOT) / p)

def list_files(**kwargs):
    # Accept 'dir_path', 'path', or default to '.'
    dir_path = kwargs.get('dir_path') or kwargs.get('path') or "."
    try:
        full_path = _get_safe_path(dir_path)
        if not os.path.exists(full_path):
            return f"Error: Path {dir_path} does not exist."
        files = os.listdir(full_path)
        return "\n".join(files) if files else "Empty directory."
    except Exception as e:
        return f"Error listing files: {str(e)}"

def list_files_json(dir_path="."):
    try:
        full_path = _get_safe_path(dir_path)
        if not os.path.exists(full_path): return []
        items = []
        for name in os.listdir(full_path):
            if name.startswith('.'): continue
            items.append({"name": name, "path": name, "isDir": os.path.isdir(os.path.join(full_path, name))})
        return items
    except: return []

def read_file(**kwargs):
    path = kwargs.get('file_path') or kwargs.get('path') or kwargs.get('filename')
    if not path: return "Error: No file path provided."
    try:
        full_path = _get_safe_path(path)
        with open(full_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        return f"Error reading file: {str(e)}"

def write_file(**kwargs):
    path = kwargs.get('file_path') or kwargs.get('path') or kwargs.get('filename')
    content = kwargs.get('content', '')
    if not path: return "Error: No file path provided."
    try:
        full_path = _get_safe_path(path)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return f"Successfully wrote to {path}"
    except Exception as e:
        return f"Error writing file: {str(e)}"

TOOLS = {
    "list_files": list_files,
    "list_dir": list_files,
    "read_file": read_file,
    "write_file": write_file,
    "web_search": web_search,
    "read_url": read_url
}


