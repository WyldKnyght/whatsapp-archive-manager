import os

def write_folder_tree(root_dir, file, excluded_dirs=None, indent=''):
    excluded_dirs = set(excluded_dirs or [])
    try:
        entries = sorted(e for e in os.listdir(root_dir) if not e.startswith('.DS_Store'))
    except PermissionError:
        return
    entries = [e for e in entries if e not in excluded_dirs]
    for idx, entry in enumerate(entries):
        full_path = os.path.join(root_dir, entry)
        is_last = idx == len(entries) - 1
        branch = '└── ' if is_last else '├── '
        line = indent + branch + entry + '\n'
        file.write(line)
        if os.path.isdir(full_path):
            next_indent = indent + ('    ' if is_last else '│   ')
            write_folder_tree(full_path, file, excluded_dirs=excluded_dirs, indent=next_indent)

if __name__ == "__main__":
    # Set root to project root (adjust how many .. as needed)
    root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
    print(f"Scanning from root: {root}")
    excluded = {'.git', 'venv', '.venv', '__pycache__', '.vs', 'node_modules', '.idea', 'Include', 'Lib', 'Scripts', 'bin'}
    
    # OUTPUT FILE IN .myfiles FOLDER:
    myfiles_folder = os.path.join(root, '.myfiles/extracts')
    os.makedirs(myfiles_folder, exist_ok=True)  # Ensure .myfiles exists
    output_path = os.path.join(myfiles_folder, 'project_structure.txt')

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(os.path.basename(root) + '\n')
        write_folder_tree(root, f, excluded_dirs=excluded)
    print(f"\nProject structure written to {output_path}")
