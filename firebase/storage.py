from fastapi import HTTPException
from firebase.config import firebase

storage = firebase.storage()

def upload_file(file_path, destination):
    try:
        storage.child(destination).put(file_path)
    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=400, detail="Failed to upload file")