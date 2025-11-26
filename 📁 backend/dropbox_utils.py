import json
import dropbox
from utils.config import DROPBOX_TOKEN, DROPBOX_FILE_PATH

def load_database():
    dbx = dropbox.Dropbox(DROPBOX_TOKEN)
    try:
        _, res = dbx.files_download(DROPBOX_FILE_PATH)
        data = json.loads(res.content.decode())
        return data
    except dropbox.exceptions.ApiError:
        return {"clients": []}

def save_database(data):
    dbx = dropbox.Dropbox(DROPBOX_TOKEN)
    dbx.files_upload(
        json.dumps(data).encode(),
        DROPBOX_FILE_PATH,
        mode=dropbox.files.WriteMode("overwrite")
    )
