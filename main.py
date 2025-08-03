import os
import shutil

SOURCE = "data"
TARGET = "/mnt/stunning-volume"

def migrate():
    os.makedirs(TARGET, exist_ok=True)
    moved = 0
    for file in os.listdir(SOURCE):
        if file.endswith(".json"):
            src = os.path.join(SOURCE, file)
            dst = os.path.join(TARGET, file)
            if not os.path.exists(dst):
                shutil.copyfile(src, dst)
                moved += 1
    print(f"✅ Moved {moved} files to volume.")

if __name__ == "__main__":
    migrate()
