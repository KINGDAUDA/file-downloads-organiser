# Automated Downloads & Media Organizer

A lightweight, zero-dependency Python background utility designed to automatically organize your `Downloads` and `Telegram Desktop` directories into clean, categorized folders by file type.

Built with Python's standard library (`pathlib` and `shutil`), it handles file collision renaming, ignores active browser downloads, protects critical app/system folders, and runs silently in the background via Windows Task Scheduler.

---

## Features

- **Zero External Dependencies:** Built entirely with Python standard libraries (`pathlib`, `shutil`).
- **Multi-Directory Support:** Automatically scans both your standard user `Downloads` directory and `Telegram Desktop` media downloads.
- **Active Download Safety:** Automatically ignores browser partial files (`.crdownload`, `.part`, `.tmp`) to prevent corrupting active transfers.
- **Application & Session Protection:** Protects Telegram binary and session assets (`tdata`, `Telegram.exe`, `Updater.exe`, `unins000.*`, `log.txt`) from being moved or locked.
- **Duplicate Collision Handling:** Automatically resolves name collisions by appending `_1`, `_2`, etc., avoiding file overwrites.
- **Locked File Resilience:** Gracefully catches Windows process locks (`WinError 32` / `PermissionError`) and logs them without crashing the entire run.
- **Silent Background Execution:** Compatible with `pythonw.exe` for headless execution via Windows Task Scheduler without popping up terminal windows.

---

## File Categorization Rules

Files are organized into destination directories based on the following extension map:

| Target Folder | File Extensions Included |
|---|---|
| `Images` | `.jpg`, `.jpeg`, `.png`, `.gif`, `.webp`, `.svg` |
| `Documents` | `.pdf`, `.docx`, `.doc`, `.txt`, `.xlsx`, `.pptx`, `.csv` |
| `Archives` | `.zip`, `.tar`, `.gz`, `.rar`, `.7z` |
| `Audio` | `.mp3`, `.wav`, `.aac`, `.flac` |
| `Video` | `.mp4`, `.mkv`, `.mov`, `.avi` |
| `Code_and_Data` | `.json`, `.py`, `.html`, `.css`, `.js`, `.sql` |
| `Executables` | `.exe`, `.msi`, `.dmg`, `.pkg`, `.deb` |
| `Others` | Any unmapped extension |

---

## Script Implementation

Save the following as `organize_downloads.py`:

```python
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

        # 2. Skip all other subdirectories and hidden/system files
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

        # Prevent overwriting if a file with the same name exists
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
```

---

## Manual Execution & Verification

Run the script manually in your command terminal:

```bash
python organize_downloads.py
```

Verify that files in `C:\Users\<YourUser>\Downloads` and `C:\Users\<YourUser>\Downloads\Telegram Desktop` are routed to their designated subfolders without touching `Telegram.exe`, `tdata`, or active download markers.

---

## Setting Up Windows Task Scheduler (Automation)

To run this organizer automatically in the background on Windows:

### Step 1: Find your `pythonw.exe` path
Open Command Prompt and run:
```cmd
where pythonw
```
Copy the output path (e.g., `C:\Users\<Username>\AppData\Local\Programs\Python\Python311\pythonw.exe`).

### Step 2: Create the Task
1. Press `Win + S`, search for **Task Scheduler**, and open it.
2. In the right panel, click **Create Task...** (not Basic Task).
3. **General Tab:**
   - **Name:** `Downloads File Organizer`
   - Select **Run only when user is logged on**.
4. **Triggers Tab:**
   - Click **New...**
   - Set **Begin the task** to `On a schedule` or `At log on`.
   - Set frequency to **Daily**, and check **Repeat task every:** `1 hour` for a duration of `Indefinitely`.
5. **Actions Tab:**
   - Click **New...**
   - **Action:** `Start a program`
   - **Program/script:** Path to `pythonw.exe` in double quotes:
     ```text
     "C:\Users\<Username>\AppData\Local\Programs\Python\Python311\pythonw.exe"
     ```
   - **Add arguments (optional):** Full path to your `.py` script in double quotes:
     ```text
     "C:\Users\<Username>\scripts\organize_downloads.py"
     ```
   - **Start in (optional):** The parent folder containing the script **WITHOUT quotes**:
     ```text
     C:\Users\<Username>\scripts
     ```
     *(Note: Putting quotation marks in the "Start in" field triggers the error "The directory name is invalid" `0x8007010B`).*
6. **Conditions Tab:**
   - Uncheck **Start the task only if the computer is on AC power** (allows it to run on battery).
7. Click **OK** to save the task.

---

## Troubleshooting

| Error Code / Message | Cause | Solution |
|---|---|---|
| `The directory name is invalid (0x8007010B)` | Quotes were placed in the Task Scheduler **Start in (optional)** field, or it points to a file rather than a folder. | Remove all quotation marks from the **Start in** field and ensure it points to the containing directory. |
| `This task has not yet run. (0x041303)` | The task was saved successfully, but its scheduled trigger time hasn't arrived yet. | Right-click the task and select **Run** to force-trigger and verify. |
| `PermissionError: [WinError 32]` | Another application has an exclusive lock on a file (e.g., `log.txt`). | Ensure `log.txt` is in `IGNORE_FILENAMES`. The script's `try...except` block will safely catch and skip locked files. |
| Telegram Desktop opens to QR Code / Logged out | `Telegram.exe` and `tdata` were moved from their installation folder. | Move `Telegram.exe`, `Updater.exe`, `unins000.*`, and `tdata` into `%APPDATA%\Telegram Desktop`. Ensure `IGNORE_FILENAMES` and `IGNORE_FOLDERS` include them. |

---

## Customization

To add custom file formats or folders, update the `CATEGORIES` dictionary at the top of `organize_downloads.py`:

```python
CATEGORIES["Design"] = [".psd", ".ai", ".fig", ".sketch"]
CATEGORIES["Ebooks"] = [".epub", ".mobi", ".azw3"]
```