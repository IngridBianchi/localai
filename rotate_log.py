import os
import shutil

LOG_FILE = "sophie.log"
MAX_SIZE_MB = 1
MAX_BACKUPS = 3

def rotate_log():
    if not os.path.exists(LOG_FILE):
        print("No existe el archivo de log.")
        return

    size_mb = os.path.getsize(LOG_FILE) / (1024 * 1024)
    if size_mb < MAX_SIZE_MB:
        print(f"Log actual ({size_mb:.2f} MB) no necesita rotación.")
        return

    # Borrar el backup más viejo si existe
    oldest = f"{LOG_FILE}.{MAX_BACKUPS}"
    if os.path.exists(oldest):
        os.remove(oldest)

    # Renombrar backups existentes
    for i in range(MAX_BACKUPS - 1, 0, -1):
        src = f"{LOG_FILE}.{i}"
        dst = f"{LOG_FILE}.{i + 1}"
        if os.path.exists(src):
            shutil.move(src, dst)

    # Renombrar el log actual
    shutil.move(LOG_FILE, f"{LOG_FILE}.1")
    open(LOG_FILE, "w").close()
    print("Rotación completada.")

if __name__ == "__main__":
    rotate_log()
