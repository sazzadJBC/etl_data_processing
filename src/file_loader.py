import os

def load_files_by_format(directory_path, allowed_extensions):
    """
    Scan a directory and return paths of files matching given extensions.

    :param directory_path: Path to the folder to scan.
    :param allowed_extensions: List of allowed file extensions (e.g. [".txt", ".pdf"])
    :return: List of file paths matching allowed extensions.
    """
    matched_files = []

    for root, dirs, files in os.walk(directory_path):
        for file in files:
            _, ext = os.path.splitext(file)
            if ext.lower() in [e.lower() for e in allowed_extensions]:
                file_path = os.path.join(root, file)
                matched_files.append(file_path)

    return matched_files

if __name__ == "__main__":
    folder_path = "/home/mhossain/Documents/SevenSix/etl_data_extraction/data/s3_downloads/"
    formats = [ ".txt" ]
    
    files = load_files_by_format(folder_path, formats)
    print("Found files:")
    for f in files:
        print(f)
