import os
from config import IMAGE_FOLDER, MAX_STORAGE_PERCENT, DELETE_PERCENT
from database import get_connection


def get_folder_size(folder_path):
    total_size = 0

    for dirpath, dirnames, filenames in os.walk(folder_path):
        for filename in filenames:
            file_path = os.path.join(dirpath, filename)

            if os.path.isfile(file_path):
                total_size += os.path.getsize(file_path)

    return total_size


def get_disk_usage_percent(folder_path):
    disk = os.statvfs(folder_path)

    total_space = disk.f_blocks * disk.f_frsize
    free_space = disk.f_bavail * disk.f_frsize
    used_space = total_space - free_space

    return (used_space / total_space) * 100


def delete_oldest_events():
    conn = get_connection()

    total_events = conn.execute(
        "SELECT COUNT(*) AS count FROM detections"
    ).fetchone()["count"]

    if total_events == 0:
        conn.close()
        print("[STORAGE] Nu exista evenimente de sters.")
        return

    delete_count = int(total_events * DELETE_PERCENT / 100)

    if delete_count < 1:
        delete_count = 1

    old_events = conn.execute(
        """
        SELECT id, image_path
        FROM detections
        ORDER BY detected_at ASC
        LIMIT ?
        """,
        (delete_count,)
    ).fetchall()

    for event in old_events:
        image_path = event["image_path"]

        if os.path.exists(image_path):
            os.remove(image_path)
            print(f"[STORAGE] Imagine stearsa: {image_path}")

        conn.execute(
            "DELETE FROM detections WHERE id = ?",
            (event["id"],)
        )

    conn.commit()
    conn.close()

    print(f"[STORAGE] Evenimente sterse: {delete_count}")


def cleanup_storage_if_needed():
    if not os.path.exists(IMAGE_FOLDER):
        os.makedirs(IMAGE_FOLDER)

    usage_percent = get_disk_usage_percent(IMAGE_FOLDER)

    print(f"[STORAGE] Disc utilizat: {usage_percent:.2f}%")

    if usage_percent >= MAX_STORAGE_PERCENT:
        print("[STORAGE] Prag depasit. Se sterg date vechi.")
        delete_oldest_events()
    else:
        print("[STORAGE] Spatiu suficient.")
