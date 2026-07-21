import os
import shutil
from typing import Dict, Any, List

class DesktopAutomationFramework:
    """Automates folder organization, desktop cleaning, and automated tasks."""

    async def organize_folder(self, target_dir: str) -> Dict[str, Any]:
        """Organizes a folder by grouping files into extension-specific folders (Documents, Images, Archives, Code)."""
        if not os.path.exists(target_dir):
            return {"status": "ERROR", "error": f"Target directory [{target_dir}] does not exist."}

        moved_counts = {"Documents": 0, "Images": 0, "Archives": 0, "Code": 0, "Others": 0}

        ext_map = {
            "Documents": [".pdf", ".docx", ".txt", ".xlsx", ".pptx", ".md"],
            "Images": [".png", ".jpg", ".jpeg", ".gif", ".svg"],
            "Archives": [".zip", ".tar", ".gz", ".rar", ".7z"],
            "Code": [".py", ".js", ".ts", ".html", ".css", ".rs", ".go", ".json"]
        }

        try:
            for item in os.listdir(target_dir):
                item_path = os.path.join(target_dir, item)
                if os.path.isdir(item_path):
                    continue

                ext = os.path.splitext(item)[1].lower()
                destination = "Others"
                for group, extensions in ext_map.items():
                    if ext in extensions:
                        destination = group
                        break

                dest_dir = os.path.join(target_dir, destination)
                os.makedirs(dest_dir, exist_ok=True)
                shutil.move(item_path, os.path.join(dest_dir, item))
                moved_counts[destination] += 1

            return {
                "status": "SUCCESS",
                "organized_directory": target_dir,
                "metrics": moved_counts
            }
        except Exception as e:
            return {"status": "FAILED", "error": str(e)}
