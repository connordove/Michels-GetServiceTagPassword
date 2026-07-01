import requests
import certifi
import os
import subprocess
import shutil
import hashlib
import time
import sys

REPO = "connordove/Michels-GetServiceTagPassword"
APP_NAME = "Michels - Get LAPS History.exe"
TEMP_NAME = "NEW Michels - Get LAPS History.exe"
BACKUP_NAME = "BACKUP Michels - Get LAPS History.exe"
VERSION_FILE = "../dist/version.txt"

def get_current_version():
    if not os.path.exists(VERSION_FILE):
        return "0.0.0"
    with open(VERSION_FILE) as f:
        return f.read().strip()

def save_version(version):
    with open(VERSION_FILE, "w") as f:
        f.write(version)

def sha256(file_path):
    h = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()

def get_latest_release():
    url = f"https://api.github.com/repos/{REPO}/releases/latest"
    r = requests.get(url, timeout=10, verify=get_cert_path())

    if r.status_code != 200:
        raise Exception("GitHub API error")

    data = r.json()
    version = data["tag_name"]

    exe_url = None
    hash_url = None

    for asset in data["assets"]:
        if asset["name"].endswith(".exe"):
            exe_url = asset["browser_download_url"]
        elif "sha256" in asset["name"]:
            hash_url = asset["browser_download_url"]

    return version, exe_url, hash_url

def download_file(url, path):
    r = requests.get(url, stream=True, timeout=30, verify=get_cert_path())
    with open(path, "wb") as f:
        for chunk in r.iter_content(8192):
            f.write(chunk)


def update_app(exe_url, hash_url, new_version):
    print("Downloading latest version...")

    download_file(exe_url, TEMP_NAME)

    if hash_url:
        print("Verifying file integrity...")
        download_file(hash_url, "hash.txt")

        with open("hash.txt") as f:
            expected_hash = f.read().strip()

        actual_hash = sha256(TEMP_NAME)

        if actual_hash != expected_hash:
            raise Exception("Hash mismatch! Possible tampering.")

    # backup current version
    if os.path.exists(APP_NAME):
        print("Crating backup...")
        shutil.copy(APP_NAME, BACKUP_NAME)

    time.sleep(1)

    # replace
    if os.path.exists(APP_NAME):
        os.remove(APP_NAME)

    shutil.move(TEMP_NAME, APP_NAME)

    save_version(new_version)

    print("Update successful.")

def rollback():
    print("Rolling back...")
    if os.path.exists(BACKUP_NAME):
        if os.path.exists(APP_NAME):
            os.remove(APP_NAME)
        shutil.move(BACKUP_NAME, APP_NAME)

def run_app():
    try:
        subprocess.Popen([APP_NAME], shell=False)
        print(f"Successfully launched {APP_NAME}")
    except Exception as e:
        print(f"Error: {e}")
        rollback()


def get_cert_path():
    if getattr(sys, 'frozen', False):
        # Running inside PyInstaller bundle
        return os.path.join(sys._MEIPASS, 'cacert.pem')
    else:
        return certifi.wher


def main():
    try:
        current_version = get_current_version()
        latest_version, exe_url, hash_url = get_latest_release()

        print(f"{current_version} -> {latest_version}")

        if exe_url and latest_version != current_version:
            update_app(exe_url, hash_url, latest_version)

    except Exception as e:
        print("Update failed:", e)
        rollback()

    run_app()

if __name__ == "__main__":
    main()