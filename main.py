import os
import shutil

# Adjust these paths
SOURCE_DIR = os.path.join(os.path.dirname(__file__), "data")
TARGET_DIR = "/mnt/stunning-volume"

def copy_files_to_volume():
    if not os.path.exists(SOURCE_DIR):
        print(f"❌ Source directory does not exist: {SOURCE_DIR}")
        return

    if not os.path.exists(TARGET_DIR):
        os.makedirs(TARGET_DIR)
        print(f"📁 Created target directory: {TARGET_DIR}")

    count = 0
    for filename in os.listdir(SOURCE_DIR):
        source_file = os.path.join(SOURCE_DIR, filename)
        target_file = os.path.join(TARGET_DIR, filename)

        if os.path.isfile(source_file):
            shutil.copy2(source_file, target_file)
            count += 1

    print(f"✅ Copied {count} files from {SOURCE_DIR} to {TARGET_DIR}")

if __name__ == "__main__":
    copy_files_to_volume()
