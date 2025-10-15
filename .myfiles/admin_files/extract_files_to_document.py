import os

SOURCE_DIR = "src"  # Adjust as needed
OUTPUT_FILE_PATTERN = ".myfiles/extracts/src_files_part{}.txt"
INCLUDE_EXTS = [
    ".py", ".txt", ".md", ".env", ".json", ".yaml", ".css",
    ".js", ".jsx", ".ts", ".tsx", ".html"
]
EXCLUDE_DIRS = [
    "node_modules", "dist", "build", ".git", "__pycache__",
    "system", "venv", "migrations"
]
EXCLUDE_FILES = ["package-lock.json", "yarn.lock", ".DS_Store"]  # Add any others
SIZE_LIMIT = 50_000  # bytes per output file

def should_include(filename):
    _, ext = os.path.splitext(filename)
    # Skip specific files even if their extension matches
    if filename in EXCLUDE_FILES:
        return False
    return ext in INCLUDE_EXTS and not filename.startswith(".")

outfile_index = 1
written_size = 0
outfile = open(OUTPUT_FILE_PATTERN.format(outfile_index), "w", encoding="utf-8")

for root, dirs, files in os.walk(SOURCE_DIR):
    dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
    for fname in files:
        if should_include(fname):
            fpath = os.path.join(root, fname)
            header = "\n" + "="*80 + "\n" + f"## FILE: {fpath}\n\n"
            try:
                with open(fpath, "r", encoding="utf-8") as infile:
                    filedata = infile.read()
            except Exception as e:
                filedata = f"\n[Could not read file: {e}]\n"
            data_to_write = header + filedata
            if written_size + len(data_to_write.encode('utf-8')) > SIZE_LIMIT:
                outfile.close()
                outfile_index += 1
                outfile = open(OUTPUT_FILE_PATTERN.format(outfile_index), "w", encoding="utf-8")
                written_size = 0
            outfile.write(data_to_write)
            written_size += len(data_to_write.encode('utf-8'))

outfile.close()
print(f"Exported files split across part files up to {SIZE_LIMIT} bytes each.")
