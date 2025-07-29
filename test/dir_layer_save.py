import os
import csv

def generate_directory_csv(root_path, root_label="セブンシックス株式会社 Dropbox", output_csv="output.csv"):
    rows = []

    for dirpath, dirnames, filenames in os.walk(root_path):
        # Relative path from root
        rel_path = os.path.relpath(dirpath, root_path)
        if rel_path == ".":
            continue

        # Get path parts
        parts = rel_path.split(os.sep)

        # ⛔ Skip nested directories under メーカー別
        if "メーカー別" in parts or :
            idx = parts.index("メーカー別")
            # If there are any levels deeper than メーカー別 (i.e., nested)
            if len(parts) > idx + 1:
                continue

        # Build 6-layer structure
        layers = parts[:6] + [""] * (6 - len(parts))

        # # Add files
        # if filenames:
        #     for file in filenames:
        #         rows.append([root_label] + layers + [file])
        # else:
        rows.append([root_label] + layers + [""])

    # Write to CSV
    with open(output_csv, mode="w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerow(["Root folder", "Layer 2", "Layer 3", "Layer 4", "Layer 5", "Layer 6", "File type"])
        writer.writerows(rows)

    print(f"[✅ DONE] {len(rows)} rows saved to {output_csv}")

# Example usage
generate_directory_csv("data/s3_downloads", root_label="セブンシックス株式会社 Dropbox", output_csv="dropbox_structure.csv")
