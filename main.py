import shutil
from pathlib import Path

CATEGORIES = {
    "Images": [".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg"],
    "Documents": [".pdf", ".docx", ".doc", ".txt", ".xlsx", ".pptx", ".csv"],
    "Archives": [".zip", ".tar", ".gz", ".rar", ".7z"],
    "Audio": [".mp3", ".wav", ".aac", ".flac"],
    "Video": [".mp4", ".mkv", ".mov", ".avi"],
    "Code_and_Data": [".json", ".py", ".html", ".css", ".js", ".sql"],
    "Executables": [".exe", ".msi", ".dmg", ".pkg", ".deb"],
}

# Ignore extensions of active/incomplete downloads
IGNORE_EXTENSIONS = {".crdownload", ".part", ".tmp"}

# Ignore specific critical or locked application files
IGNORE_FILENAMES = {
    "log.txt",
    "telegram.exe",
    "updater.exe",
    "unins000.exe",
    "unins000.dat",
}

# Ignore system/app folders and our own target category folders
IGNORE_FOLDERS = {
    "tdata",
    "images",
    "documents",
    "archives",
    "audio",
    "video",
    "code_and_data",
    "executables",
    "others",
}


def organize_downloads(downloads_path: Path):
    if not downloads_path.exists():
        print(f"Directory not found: {downloads_path}")
        return

    ext_to_folder = {
        ext.lower(): folder
        for folder, exts in CATEGORIES.items()
        for ext in exts
    }

    for item in downloads_path.iterdir():
        # 1. Skip protected folders
        if item.is_dir() and item.name.lower() in IGNORE_FOLDERS:
            continue

        # 2. Skip all other directories and hidden files
        if not item.is_file() or item.name.startswith("."):
            continue

        # 3. Skip ignored files and active downloads
        if item.name.lower() in IGNORE_FILENAMES:
            continue

        ext = item.suffix.lower()
        if ext in IGNORE_EXTENSIONS:
            continue

        target_folder_name = ext_to_folder.get(ext, "Others")
        target_dir = downloads_path / target_folder_name
        target_dir.mkdir(exist_ok=True)

        destination = target_dir / item.name

        # Prevent overwriting
        if destination.exists():
            stem = item.stem
            counter = 1
            while destination.exists():
                destination = target_dir / f"{stem}_{counter}{ext}"
                counter += 1

        # Safe move
        try:
            shutil.move(str(item), str(destination))
            print(f"Moved: {item.name} -> {target_folder_name}/")
        except PermissionError:
            print(f"Skipped (locked by another process): {item.name}")
        except OSError as e:
            print(f"Skipped (OS error): {item.name} -> {e}")


if __name__ == "__main__":
    downloads_dir = Path.home() / "Downloads"
    telegram_dir = downloads_dir / "Telegram Desktop"

    print("--- Organizing Downloads ---")
    organize_downloads(downloads_dir)

    if telegram_dir.exists():
        print("\n--- Organizing Telegram Desktop ---")
        organize_downloads(telegram_dir)