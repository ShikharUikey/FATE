import os
import shutil
import zipfile
from typing import List, Dict, Any, Optional

class DesktopFileSystemEngine:
    """Manages file operations, searching, compression, and changes tracker."""

    async def create_file(self, file_path: str, content: str = "") -> bool:
        """Creates a new file with content."""
        try:
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, "w") as f:
                f.write(content)
            return True
        except Exception:
            return False

    async def delete_file(self, file_path: str, approved: bool = False) -> bool:
        """Deletes a file. Requires security approval flag to proceed."""
        if not approved:
            raise PermissionError("File deletion requires explicit Human-in-the-Loop (HITL) approval.")
        
        try:
            if os.path.exists(file_path):
                if os.path.isdir(file_path):
                    shutil.rmtree(file_path)
                else:
                    os.remove(file_path)
                return True
        except Exception:
            pass
        return False

    async def search_files(self, directory: str, query: str, limit: int = 50) -> List[str]:
        """Searches files inside directory matching query."""
        results = []
        if not os.path.exists(directory):
            return results

        for root, dirs, files in os.walk(directory):
            for file in files:
                if query.lower() in file.lower():
                    results.append(os.path.join(root, file))
                    if len(results) >= limit:
                        return results
        return results

    async def compress_zip(self, source_dir: str, output_zip_path: str) -> bool:
        """Compresses target directory into a ZIP archive."""
        try:
            with zipfile.ZipFile(output_zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root, dirs, files in os.walk(source_dir):
                    for file in files:
                        file_path = os.path.join(root, file)
                        rel_path = os.path.relpath(file_path, source_dir)
                        zipf.write(file_path, rel_path)
            return True
        except Exception:
            return False
