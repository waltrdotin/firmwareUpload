
import os
import requests
import sqlite3
from dotenv import load_dotenv
import uuid
from hashlib import sha256
from datetime import datetime, timedelta, timezone

load_dotenv()
API_TOKEN = os.getenv('API_TOKEN')
USER_ID = os.getenv('USER_ID')


def get_local_mac_uuid() -> int:
    """
    Gets a MAC address associated with the local machine using the uuid module.
    """
    mac_num = uuid.getnode()
    return mac_num

def auth_token():
    assert API_TOKEN is not None, "API_TOKEN is None"
    now = datetime.now(tz=timezone.utc)
    now_utc = now.replace(tzinfo=None)
    now_utc -= timedelta(minutes=now_utc.minute, seconds=now_utc.second, microseconds=now_utc.microsecond)
    raw_token = f'{API_TOKEN} {int(now_utc.timestamp())}'
    encoded_token = sha256(raw_token.encode('utf-8')).hexdigest()
    return encoded_token

def get_headers() -> dict:
    assert USER_ID is not None, "USER_ID is None"
    return {
            "Authorization": f"Token {auth_token()}",
            "User": USER_ID,
            "Content-Type": "application/json",
            "User-Agent": f"WaltrSystemAgent/pi/{get_local_mac_uuid()}"
    }



def get_current_path() -> str:
    path = str(__file__)
    return os.path.dirname(path) 

def create_folder_if_not_exists(folder_path):
    os.makedirs(folder_path, exist_ok=True)
    print(f"Folder '{folder_path}' is ready!")
    return

class LocalStorage:
    def __init__(self) -> None:
        current_path = get_current_path()
        self.conn = sqlite3.connect(f'{current_path}/binfile.db')
        self.cursor = self.conn.cursor()
        self.table_name = 'ota'
        self.file_path = current_path + "/binfile"
        self.cursor.execute(f'''CREATE TABLE IF NOT EXISTS {self.table_name}
                     (device_type text, version text, path text)''')
        self.conn.commit()
        create_folder_if_not_exists(self.file_path)

    def get_version(self, _type: str) -> dict:
        keys = ['device_type', 'version', 'path']
        columns = ', '.join(keys)
        statement = f'''SELECT {columns} FROM {self.table_name} WHERE device_type = ?'''
        self.cursor.execute(statement, (_type,))
        output = self.cursor.fetchone()
        response = dict()
        if output is None:
            return response
        for i, k in enumerate(keys):
            response[k] = output[i]
        return response

    def get_all(self) -> dict:
        keys = ['device_type', 'version', 'path']
        columns = ', '.join(keys)
        statement = f"SELECT {columns} FROM {self.table_name}"
        self.cursor.execute(statement)
        output = self.cursor.fetchall()
        response = dict()
        for item in output:
            tmp = dict()
            for i, k in enumerate(keys):
                tmp[k] = item[i]
            response[item[0]] = tmp
        return response


    def insert(self, device_type: str, version: str, path: str):
        statement = f'''INSERT INTO {self.table_name} (device_type, version, path) VALUES (?, ?, ?)'''
        self.cursor.execute(statement, (device_type, version, path))
        self.conn.commit()
        print(f"Add new version for {device_type} version: {version}, path: {path}")
        return

    def update_version(self, device_type: str, new_version: str, new_path: str):
        statement = f"UPDATE {self.table_name} SET version = ?, path = ? WHERE device_type = ?"
        self.cursor.execute(statement, (new_version, new_path, device_type))
        self.conn.commit()
        print(f"Updated version for {device_type} to {new_version}")
        return


def download_file_to_folder(url: str, file_path: str) -> bool:
    response = requests.get(url, stream=True)
    if response.status_code == 200:
        with open(file_path, 'wb') as file:
            for chunk in response.iter_content(1024):
                file.write(chunk)
        print(f"File downloaded successfully to {file_path}")
        return True
    else:
        print(f"Failed to download file. Status code: {response.status_code}")
        return False

def get_bin_files(storage: LocalStorage):
    response = requests.get("https://api.waltr.in/v1/ota/latest", headers=get_headers(), timeout=5)
    if response.status_code != 200:
        print(response.text)
        return
    latest_version = response.json()
    local_version = storage.get_all()
    print(local_version)
    for k, v in latest_version.items():
        file_path = storage.file_path + f"/{k}.bin"
        new_bin_file = False
        if local_version.get(k):
            if v['version'] == local_version[k]['version']:
                continue
            new_bin_file = download_file_to_folder(url=v['url'], file_path=file_path)
            if new_bin_file:
                storage.update_version(k, v['version'], file_path)
        else:
            new_bin_file = download_file_to_folder(url=v['url'], file_path=file_path)
            if new_bin_file:
                storage.insert(k, v['version'], file_path)
        print(storage.get_all())
    return


