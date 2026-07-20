import os
import hashlib
from typing import List, Dict, Any, Optional

class FileSystemAgent:
    """Specialized agent managing local workspace file systems and indexes."""

    async def execute(self, command: str, parameters: Dict[str, Any]) -> bool:
        """Entrypoint called by the Orchestrator scheduler."""
        cmd_lower = command.lower()
        if cmd_lower == "list_directory":
            parameters["result"] = await self.list_directory(parameters.get("path", ""))
            return True
        elif cmd_lower == "search_files":
            parameters["result"] = await self.search_files(
                parameters.get("path", ""), 
                parameters.get("extension", "")
            )
            return True
        elif cmd_lower == "delete_duplicates":
            deleted = await self.delete_duplicates(parameters.get("path", ""))
            parameters["result"] = deleted
            return True
        return False

    async def list_directory(self, path: str) -> List[str]:
        """Lists directory entries safely confined to POSIX folder checks."""
        if not path:
            # Default to the primary project workspace
            path = os.path.abspath(os.path.expanduser("~/Downloads/kuch bhi"))
            
        if not os.path.exists(path) or not os.path.isdir(path):
            return []
            
        try:
            return os.listdir(path)
        except Exception:
            return []

    async def search_files(self, path: str, extension: str) -> List[str]:
        """Recursively walks a target directory tree filtering entries by extension."""
        if not path:
            path = os.path.abspath(os.path.expanduser("~/Downloads/kuch bhi"))
            
        if not os.path.exists(path) or not os.path.isdir(path):
            return []
            
        ext_clean = extension.lower().strip()
        if not ext_clean.startswith("."):
            ext_clean = f".{ext_clean}"
            
        matches = []
        try:
            for root, _, files in os.walk(path):
                for file in files:
                    if file.lower().endswith(ext_clean):
                        matches.append(os.path.join(root, file))
            return matches
        except Exception:
            return []

    async def delete_duplicates(self, path: str) -> List[str]:
        """Scans workspace directory, computes MD5 file hashes, and prunes duplicates."""
        if not path:
            path = os.path.abspath(os.path.expanduser("~/Downloads/kuch bhi"))
            
        if not os.path.exists(path) or not os.path.isdir(path):
            return []
            
        hash_registry = {}  # Map of md5 -> list of file paths
        deleted_files = []
        
        try:
            # Walk directory trees gathering MD5 hashes
            for root, _, files in os.walk(path):
                for file in files:
                    file_path = os.path.join(root, file)
                    try:
                        file_hash = self._calculate_md5(file_path)
                        if file_hash:
                            if file_hash in hash_registry:
                                hash_registry[file_hash].append(file_path)
                            else:
                                hash_registry[file_hash] = [file_path]
                    except Exception:
                        pass
            
            # Prune duplicate items
            for file_hash, paths in hash_registry.items():
                if len(paths) > 1:
                    # Sort by path length and creation time to keep the original copy
                    paths.sort(key=lambda p: (len(p), os.path.getctime(p)))
                    original = paths[0]
                    duplicates = paths[1:]
                    
                    for duplicate in duplicates:
                        try:
                            os.remove(duplicate)
                            deleted_files.append(duplicate)
                        except Exception:
                            pass
            return deleted_files
        except Exception:
            return []

    def _calculate_md5(self, file_path: str) -> Optional[str]:
        """Computes the MD5 checksum of a target file."""
        hash_md5 = hashlib.md5()
        try:
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except Exception:
            return None
