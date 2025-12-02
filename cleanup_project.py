import os
import shutil
import re
import logging
from pathlib import Path
from typing import List, Set

# --- CONFIGURATION ---

# Directories to create if they don't exist
REQUIRED_DIRS = [
    "api",
    "web-dashboard",
    "scripts",
    "assets/images/raw",
    "assets/json_prompts",
    "docs",
    "_TO_REVIEW_TRASH",  # Safety net folder
]

# Junk directories to remove explicitly
JUNK_DIRS = [
    "__pycache__",
    ".pytest_cache",
]

# Junk files to remove
JUNK_FILES = [
    ".DS_Store",
    "Thumbs.db",
]

# Files that should NEVER be moved or deleted
PROTECTED_FILES = {
    "main.py",
    "requirements.txt",
    "README.md",
    ".env",
    ".env.example",
    ".gitignore",
    "cleanup_project.py",
    "docker-compose.yml",
    "Dockerfile",
    "package.json",      # Often in root in some monorepos or during migration
    "tsconfig.json",
    "next.config.js",
    ".eslintrc.json",
    "postcss.config.js",
    "tailwind.config.js",
}

# Regex patterns for duplicate files (e.g., "image (1).jpg", "script copy.py")
DUPLICATE_PATTERNS = [
    r".*\s\(\d+\)\.[^.]+$",   # e.g., file (1).txt
    r".*\scopy\.[^.]+$",      # e.g., file copy.txt
    r".*_\d{14}\.[^.]+$",     # e.g., timestamped backups like file_20231010120000.txt
    r".*_final\.[^.]+$",      # e.g., script_final.py (often messy)
    r".*_v\d+\.[^.]+$",       # e.g., script_v1.py
]

# --- SETUP LOGGING ---
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("SmartAPD-Cleaner")


class ProjectCleaner:
    def __init__(self, root_path: str = "."):
        self.root = Path(root_path).resolve()
        self.stats = {
            "moved": 0,
            "deleted": 0,
            "trashed": 0,
            "errors": 0
        }

    def run(self):
        logger.info(f"Starting cleanup in: {self.root}")
        
        # 1. Create Structure
        self._ensure_structure()
        
        # 2. Deep Clean (Recursive)
        self._clean_system_junk()
        
        # 3. Organize Root Files
        self._organize_root_files()
        
        # 4. Final Report
        self._print_report()

    def _ensure_structure(self):
        """Creates necessary folders if they don't exist."""
        for dir_name in REQUIRED_DIRS:
            dir_path = self.root / dir_name
            if not dir_path.exists():
                try:
                    dir_path.mkdir(parents=True, exist_ok=True)
                    logger.info(f"Created directory: {dir_name}/")
                except Exception as e:
                    logger.error(f"Failed to create {dir_name}: {e}")
                    self.stats["errors"] += 1

    def _clean_system_junk(self):
        """Recursively removes cache folders and temp files."""
        logger.info("Scanning for system junk and caches...")
        
        # Walk top-down
        for current_dir, dirs, files in os.walk(self.root):
            current_path = Path(current_dir)
            
            # Skip node_modules to save time and avoid permission issues
            if "node_modules" in dirs:
                dirs.remove("node_modules")
            if ".git" in dirs:
                dirs.remove(".git")
            if ".venv" in dirs:
                dirs.remove(".venv")

            # Remove Directories
            for d in list(dirs):
                if d in JUNK_DIRS:
                    full_path = current_path / d
                    self._safe_delete(full_path)
                    dirs.remove(d) # Stop walking into deleted dir

            # Remove Files
            for f in files:
                if f in JUNK_FILES or f.endswith(".log"):
                    full_path = current_path / f
                    self._safe_delete(full_path)

    def _organize_root_files(self):
        """Scans the ROOT directory only and moves files to appropriate folders."""
        logger.info("Organizing root directory assets...")
        
        for item in self.root.iterdir():
            if not item.is_file():
                continue

            # SKIP PROTECTED
            if item.name in PROTECTED_FILES or item.name.startswith("."):
                continue

            # 1. DUPLICATE DETECTION
            if self._is_potential_duplicate(item.name):
                self._move_file(item, self.root / "_TO_REVIEW_TRASH", "Potential Duplicate")
                self.stats["trashed"] += 1
                continue

            # 2. ASSET CLASSIFICATION
            suffix = item.suffix.lower()

            # Images
            if suffix in ['.jpg', '.jpeg', '.png', '.webp', '.svg', '.gif', '.bmp']:
                self._move_file(item, self.root / "assets/images/raw", "Image Asset")
            
            # JSON Prompts/Configs (excluding key configs caught by PROTECTED_FILES)
            elif suffix == '.json':
                self._move_file(item, self.root / "assets/json_prompts", "JSON Data")

            # Documentation
            elif suffix in ['.md', '.txt', '.pdf', '.docx']:
                self._move_file(item, self.root / "docs", "Document")

            # Standalone Python Scripts (Not main.py)
            elif suffix == '.py':
                self._move_file(item, self.root / "scripts", "Python Script")

    def _is_potential_duplicate(self, filename: str) -> bool:
        """Checks if filename matches common duplicate patterns."""
        for pattern in DUPLICATE_PATTERNS:
            if re.match(pattern, filename, re.IGNORECASE):
                return True
        return False

    def _safe_delete(self, path: Path):
        """Safely deletes a file or directory."""
        try:
            if path.is_dir():
                shutil.rmtree(path)
                logger.info(f"Deleted folder: {path.name}")
            else:
                path.unlink()
                logger.info(f"Deleted file: {path.name}")
            self.stats["deleted"] += 1
        except Exception as e:
            logger.warning(f"Could not delete {path.name}: {e}")
            self.stats["errors"] += 1

    def _move_file(self, source: Path, dest_dir: Path, reason: str):
        """Moves a file to destination, handling name collisions safely."""
        try:
            if not dest_dir.exists():
                dest_dir.mkdir(parents=True, exist_ok=True)

            target = dest_dir / source.name
            
            # Handle collision by appending timestamp if target exists
            if target.exists():
                import time
                timestamp = int(time.time())
                target = dest_dir / f"{source.stem}_{timestamp}{source.suffix}"

            shutil.move(str(source), str(target))
            logger.info(f"[{reason}] Moved: {source.name} -> {dest_dir.name}/")
            self.stats["moved"] += 1
        except Exception as e:
            logger.error(f"Failed to move {source.name}: {e}")
            self.stats["errors"] += 1

    def _print_report(self):
        print("\n" + "="*40)
        print("       CLEANUP COMPLETE")
        print("="*40)
        print(f"Files Moved      : {self.stats['moved']}")
        print(f"Junk Deleted     : {self.stats['deleted']}")
        print(f"Trashed (Review) : {self.stats['trashed']}")
        print(f"Errors           : {self.stats['errors']}")
        print("="*40)
        if self.stats['trashed'] > 0:
            print(f"ACTION REQUIRED: Check '_TO_REVIEW_TRASH' folder for potential duplicates!")
        print("\n")


if __name__ == "__main__":
    cleaner = ProjectCleaner()
    cleaner.run()
