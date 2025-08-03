import os
import shutil

REPO_DATA_DIR = "./data"  # Git-tracked folder
VOLUME_DATA_DIR = "/mnt/volume"  # Railway volume

# Ensure volume directory exists
os.makedirs(VOLUME_DATA_DIR, exist_ok=True)

# Copy data only if not already in the volume
for filename in os.listdir(REPO_DATA_DIR):
    src_path = os.path.join(REPO_DATA_DIR, filename)
    dest_path = os.path.join(VOLUME_DATA_DIR, filename)
    if not os.path.exists(dest_path):
        shutil.copy(src_path, dest_path)

# Use the volume data path going forward
DATA_DIR = VOLUME_DATA_DIR
