import os
from typing import List


class FileLoader:
    def __init__(self, directory_path: str, allowed_extensions: List[str]):
        """
        Initialize FileLoader with the directory path and allowed file extensions.

        :param directory_path: Path to the folder to scan.
        :param allowed_extensions: List of allowed file extensions (e.g. [".txt", ".pdf"])
        """
        self.directory_path = directory_path
        self.allowed_extensions = [ext.lower() for ext in allowed_extensions]

    def is_valid_extension(self, filename: str) -> bool:
        """
        Check if a file has a valid extension.

        :param filename: Name of the file to check.
        :return: True if extension is valid, else False.
        """
        _, ext = os.path.splitext(filename)
        return ext.lower() in self.allowed_extensions

    def load_files(self) -> List[str]:
        """
        Load all files in the directory matching the allowed extensions.

        :return: List of matching file paths.
        """
        matched_files = []

        try:
            if not os.path.exists(self.directory_path):
                raise FileNotFoundError(f"Directory not found: {self.directory_path}")

            for root, _, files in os.walk(self.directory_path):
                for file in files:
                    try:
                        if self.is_valid_extension(file):
                            matched_files.append(os.path.join(root, file))
                    except Exception as file_error:
                        print(f"⚠️ Skipping file due to error: {file} — {file_error}")

        except Exception as e:
            print(f"❌ Error while scanning directory: {e}")

        return matched_files


# Example usage:
if __name__ == "__main__":
    loader = FileLoader(directory_path="/path/to/your/folder", allowed_extensions=[".txt", ".pdf"])
    files = loader.load_files()
    print(files)
